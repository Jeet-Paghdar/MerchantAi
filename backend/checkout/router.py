from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from database import get_db
from checkout.models import Cart, CartItem, Order, Payment, OrderStatus, OrderResponse, CartResponse, CartItemResponse
from catalog.models import Product
from checkout.razorpay_client import razorpay_client
from config import settings
from audit.logger import AuditLogger

router = APIRouter(prefix="/checkout", tags=["Checkout"])

@router.get("/config")
async def get_checkout_config():
    return {"razorpay_key_id": settings.RAZORPAY_KEY_ID}

class AddToCartRequest(BaseModel):
    session_id: str
    product_id: int
    quantity: int = 1

class CreateOrderRequest(BaseModel):
    session_id: str

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/create-order", response_model=OrderResponse)
async def create_order(req: CreateOrderRequest, db: AsyncSession = Depends(get_db)):
    cart = (await db.execute(select(Cart).filter(Cart.session_id == req.session_id))).scalars().first()
    if not cart:
        raise HTTPException(status_code=400, detail="Cart not found")
    
    items = (await db.execute(select(CartItem).filter(CartItem.cart_id == cart.id))).scalars().all()
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    subtotal = sum(item.price * item.quantity for item in items)
    discount_pct = getattr(cart, 'discount_percent', 0.0) or 0.0
    discount_amount = round(subtotal * (discount_pct / 100.0), 2)
    amount = max(1.0, round(subtotal - discount_amount, 2))
    
    rp_order = razorpay_client.create_order(int(amount * 100), receipt=f"receipt_{cart.id}")
    
    order = Order(
        session_id=req.session_id,
        cart_id=cart.id,
        razorpay_order_id=rp_order["id"],
        amount=amount,
        status=OrderStatus.payment_pending
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order

@router.post("/verify-payment")
async def verify_payment(req: VerifyPaymentRequest, db: AsyncSession = Depends(get_db)):
    order = (await db.execute(select(Order).filter(Order.razorpay_order_id == req.razorpay_order_id))).scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    is_valid = razorpay_client.verify_payment(req.razorpay_payment_id, req.razorpay_order_id, req.razorpay_signature)
    
    payment = Payment(
        order_id=order.id,
        razorpay_payment_id=req.razorpay_payment_id,
        razorpay_signature=req.razorpay_signature,
        amount=order.amount,
        status="captured" if is_valid else "failed"
    )
    db.add(payment)
    
    if is_valid:
        order.status = OrderStatus.paid
        await AuditLogger.log(
            order.session_id,
            "PAYMENT_VERIFIED",
            "razorpay_gateway",
            f"Verified HMAC signature for Razorpay payment {req.razorpay_payment_id}. Amount: ₹{order.amount}",
            razorpay_api_call={"order_id": req.razorpay_order_id, "payment_id": req.razorpay_payment_id, "valid": True},
            gate_check={"gated": True, "passed": True},
            status="success"
        )
    else:
        order.status = OrderStatus.failed
        await AuditLogger.log(
            order.session_id,
            "PAYMENT_FAILED",
            "razorpay_gateway",
            f"Invalid Razorpay payment signature for order {req.razorpay_order_id}",
            razorpay_api_call={"order_id": req.razorpay_order_id, "payment_id": req.razorpay_payment_id, "valid": False},
            status="failure"
        )
        
    await db.commit()
    return {"status": "success" if is_valid else "failed"}

@router.get("/orders", response_model=List[OrderResponse])
async def list_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).order_by(Order.created_at.desc()))
    return result.scalars().all()

@router.get("/order/{order_id}/status", response_model=OrderResponse)
async def get_order_status(order_id: int, db: AsyncSession = Depends(get_db)):
    order = (await db.execute(select(Order).filter(Order.id == order_id))).scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/cart/add")
async def add_to_cart(req: AddToCartRequest, db: AsyncSession = Depends(get_db)):
    product = (await db.execute(select(Product).filter(Product.id == req.product_id))).scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    cart = (await db.execute(select(Cart).filter(Cart.session_id == req.session_id))).scalars().first()
    if not cart:
        cart = Cart(session_id=req.session_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        
    item = (await db.execute(select(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == req.product_id))).scalars().first()
    if item:
        item.quantity += req.quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=req.product_id, quantity=req.quantity, price=product.price)
        db.add(item)
        
    await db.commit()
    return {"status": "success", "cart_id": cart.id}

async def _fetch_cart_impl(session_id: str, db: AsyncSession):
    if not session_id:
        return CartResponse(id=0, session_id="", items=[])
    cart = (await db.execute(select(Cart).filter(Cart.session_id == session_id))).scalars().first()
    if not cart:
        return CartResponse(id=0, session_id=session_id, items=[])
    items = (await db.execute(select(CartItem).filter(CartItem.cart_id == cart.id))).scalars().all()
    
    return CartResponse(
        id=cart.id,
        session_id=cart.session_id,
        items=[CartItemResponse(product_id=i.product_id, quantity=i.quantity, price=i.price) for i in items]
    )

@router.get("/cart/{session_id}", response_model=CartResponse)
async def get_cart_by_path(session_id: str, db: AsyncSession = Depends(get_db)):
    return await _fetch_cart_impl(session_id, db)

@router.get("/cart", response_model=CartResponse)
async def get_cart_by_query(session_id: str = "", db: AsyncSession = Depends(get_db)):
    return await _fetch_cart_impl(session_id, db)
