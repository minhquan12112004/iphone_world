from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.cart import CouponApply, PromotionResponse
from app.services.cart_service import CartService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/apply", response_model=PromotionResponse)
async def apply_promotion(
    coupon_in: CouponApply,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    cart_service = CartService(session)
    return await cart_service.apply_coupon(current_user.id, coupon_in.code)
