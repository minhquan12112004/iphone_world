from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    sku: str
    name: str
    price: float
    stock_qty: int
    description: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WebhookStockPayload(BaseModel):
    sku: str
    new_stock_qty: Optional[int] = None
    new_price: Optional[float] = None

class WebhookCategoryPayload(BaseModel):
    odoo_id: int
    name: str

class WebhookProductPayload(BaseModel):
    sku: str
    name: str
    price: float
    stock_qty: int
    description: Optional[str] = None
    category_odoo_id: Optional[int] = None

class WebhookOdooIDPayload(BaseModel):
    odoo_id: int
