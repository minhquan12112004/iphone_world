from fastapi import APIRouter
from app.api.v1.endpoints import products, webhook, cart, promotions, orders, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(promotions.router, prefix="/promotions", tags=["promotions"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
