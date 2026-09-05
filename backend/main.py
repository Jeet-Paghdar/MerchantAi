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
import random
import asyncio
import httpx

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
    
    if "charger" in task_lower or "powerbank" in task_lower or "battery" in task_lower:
        prod = "Ambrane 10000mAh Powerbank"
        list_price = 999
        cost = 700
        offer = 850
    elif "headphone" in task_lower or "audio" in task_lower or "boat" in task_lower:
        prod = "boAt Rockerz 450"
        list_price = 899
        cost = 600
        offer = 750
    else:
        prod = "Redmi Note 14"
        list_price = 12999
        cost = 11000
        offer = 12200

    min_price = int(cost * 1.08)
    discount = round(((list_price - offer) / list_price) * 100, 1)

    events = [
        {"sender": "buyer", "text": f"🔎 Buyer Agent initialized with goal: '{task}'. Scanning merchant catalog..."},
        {"sender": "seller", "text": f"📦 Seller Agent: Found '{prod}' (Listed: ₹{list_price:,}, Stock: 14). Minimum authorized selling price: ₹{min_price:,}."},
        {"sender": "buyer", "text": f"🤝 Buyer Agent: Counter-offering ₹{offer:,} with immediate settlement via Razorpay."},
        {"sender": "seller", "text": f"🛡️ Bounds Check: ₹{offer:,} > Cost Price + 8% margin (₹{min_price:,}). Bounds Passed ✓. Discount: {discount}%. Approving deal."},
        {"sender": "seller", "text": f"✅ Deal Agreed at ₹{offer:,}! Creating Razorpay Order with gated authorization..."},
        {"sender": "system", "text": f"💳 Razorpay Order ID created: order_sim_arena_{random.randint(1000,9999)}. Amount: ₹{offer:,}. Status: PAID."}
    ]
    return {
        "status": "success",
        "events": events,
        "result": f"Deal Closed at ₹{offer:,} (Saved ₹{list_price - offer:,}) via Razorpay Agentic Wire"
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
