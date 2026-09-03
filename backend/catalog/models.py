from sqlalchemy import Column, Integer, String, Float, JSON
from pydantic import BaseModel
from typing import List, Optional
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    cost_price = Column(Float)
    stock = Column(Integer)
    image_emoji = Column(String)
    tags = Column(JSON)
    related_product_ids = Column(JSON)

class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    description: str
    price: float
    cost_price: float
    stock: int
    image_emoji: str
    tags: List[str]
    related_product_ids: List[int]
    class Config:
        from_attributes = True

class CatalogQuery(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None

class CatalogResponse(BaseModel):
    products: List[ProductResponse]
    total: int