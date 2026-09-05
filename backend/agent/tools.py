from catalog.models import Product
from checkout.models import Cart, CartItem, Order, OrderStatus
from database import AsyncSessionLocal
from sqlalchemy.future import select
from agent.bounds import BoundsChecker
from audit.logger import AuditLogger
from checkout.razorpay_client import razorpay_client

async def search_products(query: str, max_price: float = None, category: str = None) -> list:
    async with AsyncSessionLocal() as session:
        # Preserve the customer's requested product type even when the agent
        # sends a natural-language phrase rather than a catalog keyword.
        query_text = (query or "").lower()
        inferred_categories = {
            "phone": "Phones",
            "mobile": "Phones",
            "laptop": "Laptops",
            "headphone": "Audio",
            "earbud": "Audio",
            "speaker": "Audio",
        }
        if not category:
            category = next(
                (value for keyword, value in inferred_categories.items() if keyword in query_text),
                None,
            )

        stmt = select(Product)
        if category: stmt = stmt.filter(Product.category.ilike(f"%{category}%"))
        if max_price: stmt = stmt.filter(Product.price <= max_price)
        result = await session.execute(stmt)
        products = result.scalars().all()
        
        q = (query or "").lower().strip()
        matches = []
        for p in products:
            tags_str = " ".join(p.tags) if p.tags else ""
            if not q or q in p.name.lower() or q in (p.description or "").lower() or q in (p.category or "").lower() or q in tags_str.lower():
                matches.append(p)
        
        # For a broad request such as "phones under 15000", return only the
        # already filtered category—not unrelated devices. Related products are
        # offered separately after an item is added to the cart.
        if not matches and products:
            matches = products[:4]
            
        await AuditLogger.log("sys", "SEARCH_PRODUCTS", "agent", f"Searched products for '{query}'", input_data={"query": query})
        return [{
            "id": p.id, 
            "name": p.name, 
            "price": p.price, 
            "description": p.description, 
            "category": p.category, 
            "image_emoji": p.image_emoji or "🛍️"
        } for p in matches[:6]]

async def get_product_details(product_id: int) -> dict:
    async with AsyncSessionLocal() as session:
        p = await session.get(Product, product_id)
        return {"id": p.id, "name": p.name, "price": p.price, "description": p.description} if p else {}

async def add_to_cart(session_id: str, product_id: int = None, product_name: str = None, quantity: int = 1) -> dict:
    async with AsyncSessionLocal() as db:
        product = None
        if product_id:
            try:
                product = await db.get(Product, int(product_id))
            except Exception:
                product = None
                
        if not product and product_name:
            stmt = select(Product).filter(Product.name.ilike(f"%{product_name}%"))
            product = (await db.execute(stmt)).scalars().first()

        # Fallback if product_id was passed as name or string
        if not product and isinstance(product_id, str):
            stmt = select(Product).filter(Product.name.ilike(f"%{product_id}%"))
            product = (await db.execute(stmt)).scalars().first()

        if not product:
            return {"error": "Product not found in catalog"}
        
        qty = int(quantity) if quantity else 1
        
        cart = (await db.execute(select(Cart).filter(Cart.session_id == session_id))).scalars().first()
        if not cart:
            cart = Cart(session_id=session_id)
            db.add(cart)
            await db.commit()
            await db.refresh(cart)
            
        items = (await db.execute(select(CartItem).filter(CartItem.cart_id == cart.id))).scalars().all()
        cart_total = sum(i.price * i.quantity for i in items)
        cart_item_count = sum(i.quantity for i in items)
        
        bounds = BoundsChecker.check_add_to_cart(cart_total, product.price, qty, cart_item_count)
        if not bounds.passed:
            await AuditLogger.log(session_id, "BOUND_EXCEEDED", "agent", bounds.reason, bounds_check=bounds.__dict__)
            return {"error": bounds.reason}
            
        item = CartItem(cart_id=cart.id, product_id=product.id, quantity=qty, price=product.price)
        db.add(item)
        await db.commit()
        await AuditLogger.log(session_id, "ADD_TO_CART", "agent", f"Added {product.name} to cart", bounds_check=bounds.__dict__)
        
        # Proactively get upsells for this product
        related = await suggest_related(product.id)
        
        return {
            "success": True, 
            "product_name": product.name,
            "product_price": product.price,
            "cart_total": cart_total + (product.price * qty),
            "suggested_upsells": related
        }

async def remove_from_cart(session_id: str, product_id: int) -> dict:
    async with AsyncSessionLocal() as db:
        cart = (await db.execute(select(Cart).filter(Cart.session_id == session_id))).scalars().first()
        if not cart: return {"error": "Cart not found"}
        
        item = (await db.execute(select(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id))).scalars().first()
        if not item: return {"error": "Item not found in cart"}
        
        await db.delete(item)
        await db.commit()
        await AuditLogger.log(session_id, "REMOVE_FROM_CART", "agent", "Removed item")
        return {"success": True}

async def view_cart(session_id: str) -> dict:
    async with AsyncSessionLocal() as db:
        cart = (await db.execute(select(Cart).filter(Cart.session_id == session_id))).scalars().first()
        if not cart: return {"items": [], "total": 0}
        items = (await db.execute(select(CartItem).filter(CartItem.cart_id == cart.id))).scalars().all()
        await AuditLogger.log(session_id, "VIEW_CART", "agent", "Viewed cart")
        return {"items": [{"product_id": i.product_id, "quantity": i.quantity, "price": i.price} for i in items], "total": sum(i.price * i.quantity for i in items)}

async def suggest_related(product_id: int) -> list:
    async with AsyncSessionLocal() as db:
        p = await db.get(Product, product_id)
        if not p or not p.related_product_ids: return []
        related = []
        for rid in p.related_product_ids:
            rp = await db.get(Product, rid)
            if rp: related.append({"id": rp.id, "name": rp.name, "price": rp.price})
        await AuditLogger.log("sys", "UPSELL_SUGGESTED", "agent", "Suggested related products")
        return related

async def apply_discount(session_id: str, discount_percent: float) -> dict:
    bounds = BoundsChecker.check_discount(discount_percent)
    if not bounds.passed:
         await AuditLogger.log(session_id, "BOUND_EXCEEDED", "agent", bounds.reason, bounds_check=bounds.__dict__)
         return {"error": bounds.reason}

    async with AsyncSessionLocal() as db:
        cart = (await db.execute(select(Cart).filter(Cart.session_id == session_id))).scalars().first()
        if cart:
            cart.discount_percent = discount_percent
            await db.commit()
            
    await AuditLogger.log(session_id, "DISCOUNT_APPLIED", "agent", f"Applied {discount_percent}% discount", bounds_check=bounds.__dict__)
    return {"success": True, "discount_percent": discount_percent, "message": f"{discount_percent}% discount applied successfully!"}

async def create_order(session_id: str) -> dict:
    async with AsyncSessionLocal() as db:
        cart = (await db.execute(select(Cart).filter(Cart.session_id == session_id))).scalars().first()
        if not cart: return {"error": "Cart not found"}
        items = (await db.execute(select(CartItem).filter(CartItem.cart_id == cart.id))).scalars().all()
        if not items: return {"error": "Cart is empty"}
        
        subtotal = sum(i.price * i.quantity for i in items)
        discount_pct = getattr(cart, 'discount_percent', 0.0) or 0.0
        discount_amount = round(subtotal * (discount_pct / 100.0), 2)
        amount = max(1.0, round(subtotal - discount_amount, 2))
        
        bounds = BoundsChecker.check_create_order(amount)
        if not bounds.passed:
            await AuditLogger.log(session_id, "BOUND_EXCEEDED", "agent", bounds.reason, bounds_check=bounds.__dict__)
            return {"error": bounds.reason}
            
        rp_order = razorpay_client.create_order(int(amount * 100), f"receipt_{cart.id}")
        order = Order(session_id=session_id, cart_id=cart.id, razorpay_order_id=rp_order["id"], amount=amount)
        db.add(order)
        await db.commit()
        await db.refresh(order)
        await AuditLogger.log(
            session_id, 
            "CREATE_ORDER", 
            "agent", 
            f"Created order with subtotal ₹{subtotal}, discount {discount_pct}% (-₹{discount_amount}), final ₹{amount}", 
            gate_check={"gated": True, "passed": True}, 
            bounds_check=bounds.__dict__
        )
        return {
            "order_id": order.id, 
            "razorpay_order_id": rp_order["id"], 
            "subtotal": subtotal,
            "discount_percent": discount_pct,
            "discount_amount": discount_amount,
            "amount": amount
        }

async def check_payment_status(order_id: int) -> dict:
    async with AsyncSessionLocal() as db:
        order = await db.get(Order, order_id)
        return {"status": order.status if order else "not_found"}

TOOLS_REGISTRY = {
    "search_products": search_products,
    "get_product_details": get_product_details,
    "add_to_cart": add_to_cart,
    "remove_from_cart": remove_from_cart,
    "view_cart": view_cart,
    "suggest_related": suggest_related,
    "apply_discount": apply_discount,
    "create_order": create_order,
    "check_payment_status": check_payment_status
}
