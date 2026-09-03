from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import Base
import enum

class OrderStatus(str, enum.Enum):
    created = "created"
    payment_pending = "payment_pending"
    paid = "paid"
    failed = "failed"
    recovered = "recovered"

class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    discount_percent = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    product_id = Column(Integer)
    quantity = Column(Integer)
    price = Column(Float)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    razorpay_order_id = Column(String)
    amount = Column(Float)
    currency = Column(String, default="INR")
    status = Column(Enum(OrderStatus), default=OrderStatus.created)
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    razorpay_payment_id = Column(String)
    razorpay_signature = Column(String)
    amount = Column(Float)
    status = Column(String)
    failure_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrderResponse(BaseModel):
    id: int
    session_id: str
    amount: float
    status: OrderStatus
    razorpay_order_id: str
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class CartItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    session_id: str
    items: List[CartItemResponse] = []
    class Config:
        from_attributes = True