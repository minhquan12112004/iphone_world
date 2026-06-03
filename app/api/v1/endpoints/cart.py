from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.cart import CartResponse, CartItemCreate
from app.services.cart_service import CartService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    cart_service = CartService(session)
    return await cart_service.get_cart(current_user.id)

@router.post("/items", response_model=CartResponse)
async def add_item_to_cart(
    item_in: CartItemCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    cart_service = CartService(session)
    return await cart_service.add_item(current_user.id, item_in)

@router.delete("/items/{product_id}", response_model=CartResponse)
async def remove_item_from_cart(
    product_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    cart_service = CartService(session)
    return await cart_service.remove_item(current_user.id, product_id)
