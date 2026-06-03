from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.product import ProductResponse

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: ProductResponse

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_number: str
    total_amount: float
    status: str
    odoo_order_id: Optional[int]
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
