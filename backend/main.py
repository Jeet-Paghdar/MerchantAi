from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from catalog.seed_data import seed_products
from catalog.router import router as catalog_router
from checkout.router import router as checkout_router
from audit.router import router as audit_router
from campaigns.router import router as campaigns_router
from pydantic import BaseModel
from agent.core import AgentCore
from agent.bounds import BoundsChecker
from audit.logger import AuditLogger
from catalog.models import Product
from checkout.models import Cart, CartItem, Order, OrderStatus, Payment
from checkout.razorpay_client import razorpay_client
from config import settings
from database import AsyncSessionLocal
from sqlalchemy.future import select
import asyncio
import httpx
import re
import uuid

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="MerchantAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog_router, prefix="/api")
app.include_router(checkout_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(campaigns_router, prefix="/api")

async def keepalive():
    """
    Silent background task: pings own /api/health every 10 minutes.
    Prevents Render free-tier cold starts by keeping the server warm.
    Only activates when RENDER_EXTERNAL_URL is set (i.e. in production).
    Completely invisible to the frontend.
    """
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "").strip()
    if not base_url:
        return  # Not on Render, skip (local dev)
    
    await asyncio.sleep(60)  # wait 1 min after startup before first ping
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.get(f"{base_url}/api/health")
        except Exception:
            pass  # silently ignore any errors
        await asyncio.sleep(600)  # ping every 10 minutes

@app.on_event("startup")
async def startup_event():
    await init_db()
    await seed_products()
    asyncio.create_task(keepalive())  # start keepalive silently in background


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    agent = AgentCore(req.session_id)
    response = await agent.process_message(req.message)
    return response

class ArenaStartRequest(BaseModel):
    task: str

@app.post("/api/arena/start")
async def arena_start(req: ArenaStartRequest):
    return {"status": "started", "messages": [{"role": "buyer", "content": req.task}]}

@app.get("/api/arena/simulate")
async def arena_simulate(task: str = "Buy me the best phone under ₹15,000"):
    task_lower = task.lower()

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return {
            "status": "failed",
            "events": [{"sender": "seller", "text": "⚠️ Razorpay test keys are required before an Arena deal can create a real payment order."}],
            "result": {"reason": "Razorpay test-mode configuration is missing."},
        }

    category = "Accessories" if any(term in task_lower for term in ("charger", "powerbank", "battery")) else \
        "Audio" if any(term in task_lower for term in ("headphone", "audio", "earbud", "speaker")) else \
        "Laptops" if "laptop" in task_lower else "Phones"
    budget_match = re.search(r"(?:under|below|within)\s*₹?\s*([\d,]+)", task_lower)
    budget = float(budget_match.group(1).replace(",", "")) if budget_match else None

    async with AsyncSessionLocal() as db:
        statement = select(Product).filter(Product.category == category, Product.stock > 0)
        if budget:
            statement = statement.filter(Product.price <= budget)
        product = (await db.execute(statement.order_by(Product.price.desc()))).scalars().first()
        if not product:
            return {
                "status": "failed",
                "events": [{"sender": "seller", "text": f"⚠️ No in-stock {category.lower()} matched the buyer agent's request."}],
                "result": {"reason": "No eligible catalog item found."},
            }

        min_price = round(product.cost_price * 1.08, 2)
        offer = max(min_price, round(product.price * 0.94, 2))
        bounds = BoundsChecker.check_negotiate(offer, product.cost_price)
        discount = round(((product.price - offer) / product.price) * 100, 1)
        session_id = f"arena_{uuid.uuid4().hex}"
        cart = Cart(session_id=session_id)
        db.add(cart)
        await db.flush()
        db.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=1, price=offer))

        try:
            rp_order = razorpay_client.create_order(int(offer * 100), receipt=f"arena_{cart.id}")
        except Exception as error:
            return {
                "status": "failed",
                "events": [{"sender": "seller", "text": "⚠️ The seller accepted the deal, but Razorpay could not create the payment order."}],
                "result": {"reason": str(error)},
            }

        order = Order(
            session_id=session_id,
            cart_id=cart.id,
            razorpay_order_id=rp_order["id"],
            amount=offer,
            status=OrderStatus.payment_pending,
        )
        db.add(order)
        await db.flush()

        # Buildathon demo only: the buyer-side payment provider is represented
        # by a deterministic simulated verification event. A production flow
        # must call Razorpay Checkout and verify its returned HMAC signature.
        simulated_payment_id = f"pay_arena_sim_{uuid.uuid4().hex[:12]}"
        db.add(Payment(
            order_id=order.id,
            razorpay_payment_id=simulated_payment_id,
            razorpay_signature="simulated_buildathon_verification",
            amount=offer,
            status="simulated_verified",
        ))
        order.status = OrderStatus.paid
        await db.commit()
        await db.refresh(order)

    await AuditLogger.log(
        session_id,
        "ARENA_ORDER_CREATED",
        "seller_agent",
        f"Buyer agent offer for {product.name} passed seller bounds. A Razorpay test-mode order was created and settled with simulated Buildathon payment verification.",
        bounds_check=bounds.__dict__,
        gate_check={"buyer_authorization_required": True, "simulated_for_demo": True, "passed": True},
        razorpay_api_call={"order_id": order.razorpay_order_id, "payment_id": simulated_payment_id, "amount": order.amount, "verification": "simulated_buildathon_demo"},
    )

    events = [
        {"sender": "buyer", "text": f"🔎 Buyer Agent initialized with goal: '{task}'. Scanning merchant catalog..."},
        {"sender": "seller", "text": f"📦 Seller Agent: Found '{product.name}' (Listed: ₹{product.price:,.0f}, Stock: {product.stock}). Minimum authorized selling price: ₹{min_price:,.0f}."},
        {"sender": "buyer", "text": f"🤝 Buyer Agent: Counter-offering ₹{offer:,} with immediate settlement via Razorpay."},
        {"sender": "seller", "text": f"🛡️ Bounds Check: ₹{offer:,} ≥ Cost Price + 8% margin (₹{min_price:,.0f}). Bounds Passed ✓. Discount: {discount}%. Approving deal."},
        {"sender": "seller", "text": f"✅ Deal accepted at ₹{offer:,}. A real Razorpay test-mode order has been created."},
        {"sender": "seller", "text": "🧪 Buildathon demo: simulated buyer-side payment verification recorded. The merchant order is now settled locally."},
    ]
    return {
        "status": "success",
        "events": events,
        "result": f"Deal settled at ₹{offer:,.0f} (Saved ₹{product.price - offer:,.0f}) — simulated Razorpay test-mode payment verification for the Buildathon demo."
    }

# Mount static files from frontend build if available
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
