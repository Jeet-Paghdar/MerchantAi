from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from campaigns.orchestrator import CampaignOrchestrator
from campaigns.models import CampaignStats
from checkout.models import Cart, CartItem, Order
from catalog.models import Product
from database import get_db
from audit.logger import AuditLogger
import uuid

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])
orchestrator = CampaignOrchestrator()

@router.get("/dashboard", response_model=CampaignStats)
async def dashboard():
    stats = await orchestrator.get_dashboard_stats()
    return CampaignStats(**stats)

@router.post("/trigger-recovery")
async def trigger_recovery(db: AsyncSession = Depends(get_db)):
    # 1. Find the latest cart
    result = await db.execute(select(Cart).order_by(Cart.updated_at.desc()))
    cart = result.scalars().first()
    
    if not cart:
        return {"status": "error", "message": "No carts exist to recover."}

    # 2. Check if it has an order
    order_result = await db.execute(select(Order).filter(Order.cart_id == cart.id))
    order = order_result.scalars().first()

    # 3. Find cart items
    items_result = await db.execute(select(CartItem).filter(CartItem.cart_id == cart.id))
    items = items_result.scalars().all()
    
    if not items:
        # Generate dummy item for demo if cart is empty
        prod_name = "Redmi Note 14"
        cart_total = 12999
    else:
        prod = await db.get(Product, items[0].product_id)
        prod_name = prod.name if prod else f"Item {items[0].product_id}"
        cart_total = sum(i.price * i.quantity for i in items)

    # 4. Generate dynamic discount and WhatsApp message
    discount_percent = 12
    discount_amt = cart_total * (discount_percent / 100)
    final_price = cart_total - discount_amt
    
    recovery_link = f"https://techbazaar.in/recover/{uuid.uuid4().hex[:8]}"
    whatsapp_message = (
        f"Hi there! 👋\n"
        f"We noticed you left the '{prod_name}' in your TechBazaar cart.\n"
        f"Complete your purchase in the next 2 hours and get {discount_percent}% OFF!\n"
        f"Your new price: ₹{final_price:,.2f} (Was ₹{cart_total:,.2f})\n\n"
        f"Click to checkout: {recovery_link}"
    )

    # 5. Log to Audit Trail
    await AuditLogger.log(
        session_id=cart.session_id,
        action_type="CAMPAIGN_DISPATCHED",
        actor="campaign_orchestrator",
        reasoning=f"Cart inactive. Triggered urgency nudge with {discount_percent}% bound discount to recover ₹{final_price:,.2f}.",
        output_data={"message": whatsapp_message, "channel": "WhatsApp", "discount_applied": discount_percent},
        status="success"
    )

    return {
        "status": "success",
        "message": whatsapp_message,
        "discount_applied": discount_percent
    }