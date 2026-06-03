from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StockWebhookPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_type: str = Field(..., min_length=1, max_length=100)
    record_model: str = Field(default="stock.picking", min_length=1, max_length=100)
    record_id: int | None = Field(default=None, gt=0)
    sku: str | None = Field(default=None, max_length=100)
    quantity: float | None = Field(default=None)
    occurred_at: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class WebhookAckResponse(BaseModel):
    success: bool
    received_event: str
    message: str
    matched_product_id: int | None = None
