from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from database import get_db
from catalog.models import Product, ProductResponse

router = APIRouter(prefix="/catalog", tags=["Catalog"])

@router.get("", response_model=List[ProductResponse])
async def list_products(category: str = None, min_price: float = None, max_price: float = None, db: AsyncSession = Depends(get_db)):
    query = select(Product)
    if category:
        query = query.filter(Product.category == category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/search", response_model=List[ProductResponse])
async def search_products(q: str, db: AsyncSession = Depends(get_db)):
    query = select(Product).filter(Product.name.ilike(f"%{q}%") | Product.description.ilike(f"%{q}%"))
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/categories", response_model=List[str])
async def list_categories(db: AsyncSession = Depends(get_db)):
    query = select(Product.category).distinct()
    result = await db.execute(query)
    return [r for r in result.scalars().all()]

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Product).filter(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product