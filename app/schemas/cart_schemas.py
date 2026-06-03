from pydantic import BaseModel, Field
from typing import List


class CartItemCreate(BaseModel):
    sku: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


class CartItemUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=0)


class CartItemResponse(BaseModel):
    sku: str
    name: str
    price: float
    quantity: int
    line_total: float


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    subtotal: float
    coupon_code: str | None = None
    discount: float | None = None
    total: float


class ApplyCouponRequest(BaseModel):
    code: str = Field(..., min_length=1)


class ApplyCouponResponse(BaseModel):
    success: bool
    code: str
    discount_percent: float
    discount_amount: float
    total_after_discount: float
