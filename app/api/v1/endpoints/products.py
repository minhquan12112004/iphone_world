from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.core.redis_client import get_redis
from redis.asyncio import Redis
from app.schemas.product import ProductResponse
from app.services.product_service import ProductService

router = APIRouter()

@router.get("", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    product_service = ProductService(session, redis)
    return await product_service.get_products(skip, limit, search)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    product_service = ProductService(session, redis)
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
