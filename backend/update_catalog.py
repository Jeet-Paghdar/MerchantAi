import asyncio
from database import init_db, AsyncSessionLocal
from catalog.seed_data import products_data
from catalog.models import Product
from sqlalchemy.future import select

async def run():
    await init_db()
    async with AsyncSessionLocal() as s:
        for p in products_data:
            stmt = select(Product).filter(Product.name == p['name'])
            res = await s.execute(stmt)
            existing = res.scalars().first()
            if not existing:
                s.add(Product(**p))
        await s.commit()
    print("Catalog updated successfully!")

if __name__ == "__main__":
    asyncio.run(run())
