from datetime import datetime
from sqlalchemy.orm import Session
from app.models.cart_models import Coupon
from app.services.cart_service import list_cart_items


def apply_coupon_to_cart(db: Session, user_id: int, code: str) -> dict:
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    if not coupon:
        raise ValueError("Coupon not found")
    if not coupon.is_active:
        raise ValueError("Coupon not active")
    if coupon.valid_until and coupon.valid_until < datetime.utcnow():
        raise ValueError("Coupon expired")

    items, subtotal = list_cart_items(db, user_id)
    discount_amount = subtotal * (float(coupon.discount_percent) / 100.0)
    total_after = max(0.0, subtotal - discount_amount)
    return {
        "code": coupon.code,
        "discount_percent": float(coupon.discount_percent),
        "discount_amount": float(discount_amount),
        "total_after": float(total_after),
    }
