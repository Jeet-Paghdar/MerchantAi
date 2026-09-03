import razorpay
from config import settings

class RazorpayClient:
    def __init__(self):
        self.client = None
        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
            self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def create_order(self, amount_paise: int, receipt: str):
        if not self.client:
            return {"id": "fake_rp_order_id", "amount": amount_paise, "currency": "INR"}
        try:
            return self.client.order.create({"amount": amount_paise, "currency": "INR", "receipt": receipt})
        except Exception as e:
            raise Exception(f"Razorpay order creation failed: {str(e)}")

    def verify_payment(self, payment_id: str, order_id: str, signature: str):
        if not self.client:
            return True
        try:
            return self.client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
        except Exception:
            return False

    def fetch_payment(self, payment_id: str):
        if not self.client:
            return {"status": "captured"}
        try:
            return self.client.payment.fetch(payment_id)
        except Exception as e:
            raise Exception(f"Razorpay fetch failed: {str(e)}")

razorpay_client = RazorpayClient()