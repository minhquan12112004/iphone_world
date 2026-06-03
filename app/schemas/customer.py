from pydantic import BaseModel, Field


class CustomerCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=32)
    vat: str | None = Field(default=None, max_length=32)
    street: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=128)


class CustomerResponse(BaseModel):
    success: bool
    partner_id: int
    message: str
