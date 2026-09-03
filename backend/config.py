import os
from pydantic_settings import BaseSettings

# Look for .env in current dir or root dir
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))

class Settings(BaseSettings):
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    GEMINI_API_KEY: str = ""
    class Config:
        env_file = env_path
        extra = "ignore"

settings = Settings()
MAX_CART_ITEMS = 10
MAX_ORDER_AMOUNT = 50000
MAX_SINGLE_ITEM_QTY = 5
MAX_DISCOUNT_PERCENT = 15
MAX_NEGOTIATION_ROUNDS = 3