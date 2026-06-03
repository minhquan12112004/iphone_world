from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.product import ProductResponse

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_amount: float

class CouponApply(BaseModel):
    code: str

class PromotionResponse(BaseModel):
    discount_amount: float
    new_total_amount: float
