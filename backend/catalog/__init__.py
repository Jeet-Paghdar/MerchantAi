"""
MerchantAI Catalog & Inventory Subsystem
Manages product listings, pricing matrices, margins, and semantic
search embeddings for the host merchant storefront.
"""
from catalog.models import Product, ProductResponse
from catalog.seed_data import seed_products

__all__ = ["Product", "ProductResponse", "seed_products"]

