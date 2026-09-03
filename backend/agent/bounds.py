from dataclasses import dataclass
from config import MAX_CART_ITEMS, MAX_ORDER_AMOUNT, MAX_SINGLE_ITEM_QTY, MAX_DISCOUNT_PERCENT

@dataclass
class BoundsResult:
    passed: bool
    reason: str
    limit: float
    actual: float

class BoundsChecker:
    @staticmethod
    def check_add_to_cart(cart_total: float, item_price: float, item_qty: int, cart_item_count: int) -> BoundsResult:
        if cart_item_count + item_qty > MAX_CART_ITEMS:
            return BoundsResult(False, "Max cart items exceeded", MAX_CART_ITEMS, cart_item_count + item_qty)
        if item_qty > MAX_SINGLE_ITEM_QTY:
            return BoundsResult(False, "Max quantity per item exceeded", MAX_SINGLE_ITEM_QTY, item_qty)
        if cart_total + (item_price * item_qty) > MAX_ORDER_AMOUNT:
            return BoundsResult(False, "Max order amount exceeded", MAX_ORDER_AMOUNT, cart_total + (item_price * item_qty))
        return BoundsResult(True, "OK", 0, 0)

    @staticmethod
    def check_create_order(amount: float) -> BoundsResult:
        if amount > MAX_ORDER_AMOUNT:
            return BoundsResult(False, "Max order amount exceeded", MAX_ORDER_AMOUNT, amount)
        return BoundsResult(True, "OK", MAX_ORDER_AMOUNT, amount)

    @staticmethod
    def check_discount(discount_percent: float) -> BoundsResult:
        if discount_percent > MAX_DISCOUNT_PERCENT:
            return BoundsResult(False, "Max discount exceeded", MAX_DISCOUNT_PERCENT, discount_percent)
        return BoundsResult(True, "OK", MAX_DISCOUNT_PERCENT, discount_percent)

    @staticmethod
    def check_negotiate(offered_price: float, cost_price: float, min_margin: float = 0.08) -> BoundsResult:
        min_allowed_price = cost_price * (1 + min_margin)
        if offered_price < min_allowed_price:
            return BoundsResult(False, "Below minimum allowed margin", min_allowed_price, offered_price)
        return BoundsResult(True, "OK", min_allowed_price, offered_price)