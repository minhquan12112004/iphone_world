from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from app.services.auth_service import get_current_user
from app.db import get_db
from app.services.cart_service import list_cart_items, add_item_to_cart, update_cart_item
from app.schemas.cart_schemas import (
    CartItemCreate,
    CartItemResponse,
    CartResponse,
    CartItemUpdate,
)

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartResponse)
def get_cart(current_user=Depends(get_current_user), db: Session = Depends(get_db)) -> CartResponse:
    items, subtotal = list_cart_items(db, current_user.id)
    return CartResponse(items=items, subtotal=subtotal, total=subtotal)


@router.post("/items", status_code=status.HTTP_201_CREATED)
def add_item(payload: CartItemCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        item = add_item_to_cart(db, current_user.id, payload.sku, payload.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"success": True, "item_id": item.id}


@router.put("/items/{sku}")
def update_item(
    sku: str = Path(..., min_length=1),
    payload: CartItemUpdate | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    qty = payload.quantity if payload and payload.quantity is not None else None
    if qty is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="quantity is required")
    try:
        update_cart_item(db, current_user.id, sku, qty)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"success": True}
