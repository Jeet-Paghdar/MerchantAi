from sqlalchemy.future import select
from database import AsyncSessionLocal
from catalog.models import Product

products_data = [
    {"name": "Redmi Note 14", "category": "Phones", "description": "Latest affordable smartphone", "price": 12999.0, "cost_price": 11000.0, "stock": 50, "image_emoji": "📱", "tags": ["smartphone", "android", "redmi"], "related_product_ids": [4, 7]},
    {"name": "boAt Rockerz 450", "category": "Audio", "description": "Wireless Bluetooth Headphones", "price": 899.0, "cost_price": 600.0, "stock": 100, "image_emoji": "🎧", "tags": ["audio", "wireless", "headphones"], "related_product_ids": [1, 9]},
    {"name": "Logitech M235", "category": "Accessories", "description": "Wireless Mouse", "price": 449.0, "cost_price": 300.0, "stock": 200, "image_emoji": "🖱️", "tags": ["mouse", "wireless", "logitech"], "related_product_ids": [6]},
    {"name": "Samsung Galaxy M14", "category": "Phones", "description": "Reliable smartphone", "price": 14990.0, "cost_price": 13000.0, "stock": 40, "image_emoji": "📱", "tags": ["smartphone", "samsung"], "related_product_ids": [7, 8]},
    {"name": "Sony WF-1000XM4", "category": "Audio", "description": "Premium earbuds", "price": 19990.0, "cost_price": 16000.0, "stock": 20, "image_emoji": "🎵", "tags": ["audio", "earbuds", "sony"], "related_product_ids": [1, 4]},
    {"name": "Dell XPS 13", "category": "Laptops", "description": "Premium ultrabook", "price": 95000.0, "cost_price": 85000.0, "stock": 10, "image_emoji": "💻", "tags": ["laptop", "dell"], "related_product_ids": [3]},
    {"name": "Ambrane 10000mAh Powerbank", "category": "Accessories", "description": "Portable charger", "price": 999.0, "cost_price": 700.0, "stock": 150, "image_emoji": "🔋", "tags": ["powerbank"], "related_product_ids": [1, 4]},
    {"name": "Spigen Phone Cover", "category": "Accessories", "description": "Durable phone case", "price": 499.0, "cost_price": 300.0, "stock": 200, "image_emoji": "📱", "tags": ["case"], "related_product_ids": [1, 4]},
    {"name": "JBL Flip 5", "category": "Audio", "description": "Waterproof speaker", "price": 6999.0, "cost_price": 5500.0, "stock": 30, "image_emoji": "🔊", "tags": ["audio", "speaker", "jbl"], "related_product_ids": [1, 4]},
    {"name": "MacBook Air M2", "category": "Laptops", "description": "Apple laptop", "price": 105000.0, "cost_price": 95000.0, "stock": 15, "image_emoji": "💻", "tags": ["laptop", "apple"], "related_product_ids": [11, 12]},
    {"name": "Apple Magic Mouse", "category": "Accessories", "description": "Mouse for Mac", "price": 7500.0, "cost_price": 6000.0, "stock": 40, "image_emoji": "🖱️", "tags": ["mouse", "apple"], "related_product_ids": [10]},
    {"name": "USB-C to HDMI Adapter", "category": "Accessories", "description": "Display adapter", "price": 1499.0, "cost_price": 900.0, "stock": 80, "image_emoji": "🔌", "tags": ["adapter"], "related_product_ids": [6, 10]},
    {"name": "OnePlus 11R", "category": "Phones", "description": "High performance smartphone", "price": 39999.0, "cost_price": 35000.0, "stock": 25, "image_emoji": "📱", "tags": ["smartphone", "oneplus"], "related_product_ids": [5, 7]},
    {"name": "Realme Buds Air 3", "category": "Audio", "description": "TWS Earbuds", "price": 1999.0, "cost_price": 1500.0, "stock": 60, "image_emoji": "🎧", "tags": ["audio", "earbuds"], "related_product_ids": [13, 1]},
    {"name": "HP Pavilion 14", "category": "Laptops", "description": "Everyday laptop", "price": 55000.0, "cost_price": 49000.0, "stock": 20, "image_emoji": "💻", "tags": ["laptop", "hp"], "related_product_ids": [3]},
    {"name": "SanDisk 64GB Pen Drive", "category": "Accessories", "description": "USB Drive", "price": 450.0, "cost_price": 300.0, "stock": 300, "image_emoji": "💾", "tags": ["storage", "usb"], "related_product_ids": [6, 15]},
    {"name": "Nothing Phone (1)", "category": "Phones", "description": "Unique design smartphone", "price": 29999.0, "cost_price": 26000.0, "stock": 20, "image_emoji": "📱", "tags": ["smartphone", "nothing"], "related_product_ids": [7, 14]},
    {"name": "Mi Smart Band 7", "category": "Accessories", "description": "Fitness tracker", "price": 2499.0, "cost_price": 2000.0, "stock": 100, "image_emoji": "⌚", "tags": ["wearable", "fitness"], "related_product_ids": [1, 4]}
]

async def seed_products():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product))
        if len(result.scalars().all()) == 0:
            for p_data in products_data:
                product = Product(**p_data)
                session.add(product)
            await session.commit()