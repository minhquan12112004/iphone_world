from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.order import OrderResponse
from app.services.order_service import OrderService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("", response_model=OrderResponse)
async def create_order(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    order_service = OrderService(session)
    return await order_service.checkout(current_user, background_tasks)

@router.get("", response_model=List[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    order_service = OrderService(session)
    return await order_service.get_user_orders(current_user.id)
