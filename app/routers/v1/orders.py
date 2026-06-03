from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session

from app.config.odoo import get_odoo_client
from app.schemas.order import OrderCreateRequest, OrderCreateResponse
from app.services.odoo_xmlrpc import OdooXMLRPCClient
from app.services.order_service import OrderService
from app.services.checkout_service import checkout_and_sync, CheckoutError
from app.services.auth_service import get_current_user
from app.db import get_db


router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_service(odoo_client: OdooXMLRPCClient = Depends(get_odoo_client)) -> OrderService:
    return OrderService(odoo_client)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def checkout(
    payload: OrderCreateRequest | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    odoo_client: OdooXMLRPCClient = Depends(get_odoo_client),
) -> dict:
    """Checkout current user's cart and sync to Odoo. Payload (OrderCreateRequest) is optional; we build order from cart."""
    try:
        result = checkout_and_sync(db, current_user, odoo_client)
    except CheckoutError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return result


@router.get("", response_model=list[dict], status_code=status.HTTP_200_OK)
def list_orders(
    limit: int = Query(20, ge=1, le=100),
    order_service: OrderService = Depends(get_order_service),
) -> list[dict]:
    """List latest sale orders (basic fields)."""
    return order_service.list_orders(limit=limit)
