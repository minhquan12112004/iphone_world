from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.core.database import get_db
from app.core.redis_client import get_redis
from app.schemas.product import WebhookStockPayload, WebhookCategoryPayload, WebhookProductPayload, WebhookOdooIDPayload
from app.services.product_service import ProductService

router = APIRouter()

@router.post("/stock")
async def webhook_stock(
    payload: WebhookStockPayload,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    # In a real scenario, you should add authentication for this webhook
    product_service = ProductService(session, redis)
    await product_service.process_webhook(payload)
    return {"message": "Webhook stock processed successfully"}

@router.post("/categories")
async def webhook_category(
    payload: WebhookOdooIDPayload,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    product_service = ProductService(session, redis)
    await product_service.sync_category_from_odoo(payload)
    return {"message": f"Webhook category sync triggered for odoo_id {payload.odoo_id}"}

@router.post("/products")
async def webhook_product(
    payload: WebhookOdooIDPayload,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    product_service = ProductService(session, redis)
    await product_service.sync_product_from_odoo(payload)
    return {"message": f"Webhook product sync triggered for odoo_id {payload.odoo_id}"}

