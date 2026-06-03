from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.services.auth_service import get_current_user
from app.db import get_db
from app.schemas.cart_schemas import ApplyCouponRequest, ApplyCouponResponse
from app.services.promotion_service import apply_coupon_to_cart

router = APIRouter(prefix="/promotions", tags=["promotions"])


@router.post("/apply", response_model=ApplyCouponResponse)
def apply_coupon(payload: ApplyCouponRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        info = apply_coupon_to_cart(db, current_user.id, payload.code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return ApplyCouponResponse(
        success=True,
        code=info["code"],
        discount_percent=info["discount_percent"],
        discount_amount=info["discount_amount"],
        total_after_discount=info["total_after"],
    )
