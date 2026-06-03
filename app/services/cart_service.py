from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.cart_repo import CartRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.cart import CartItemCreate
from datetime import datetime, timezone

class CartService:
    def __init__(self, session: AsyncSession):
        self.cart_repo = CartRepository(session)
        self.product_repo = ProductRepository(session)

    async def get_cart(self, user_id: int):
        items = await self.cart_repo.get_items_by_user(user_id)
        total = sum(item.quantity * item.product.price for item in items if item.product)
        return {"items": items, "total_amount": total}

    async def add_item(self, user_id: int, item_in: CartItemCreate):
        product = await self.product_repo.get_by_id(item_in.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Determine current quantity in cart
        current_item = await self.cart_repo.get_item(user_id, item_in.product_id)
        current_qty = current_item.quantity if current_item else 0
        new_qty = current_qty + item_in.quantity

        if new_qty > product.stock_qty:
            raise HTTPException(status_code=400, detail=f"Cannot add {item_in.quantity} items. Only {product.stock_qty} in stock.")

        await self.cart_repo.add_or_update_item(user_id, item_in.product_id, new_qty)
        return await self.get_cart(user_id)

    async def remove_item(self, user_id: int, product_id: int):
        await self.cart_repo.remove_item(user_id, product_id)
        return await self.get_cart(user_id)

    async def apply_coupon(self, user_id: int, code: str):
        cart = await self.get_cart(user_id)
        if cart["total_amount"] == 0:
            raise HTTPException(status_code=400, detail="Cart is empty")

        coupon = await self.cart_repo.get_coupon_by_code(code)
        if not coupon or not coupon.is_active:
            raise HTTPException(status_code=400, detail="Invalid or inactive coupon")
        
        if coupon.valid_until and coupon.valid_until.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Coupon has expired")

        discount_amount = cart["total_amount"] * (coupon.discount_percent / 100)
        new_total = cart["total_amount"] - discount_amount

        return {
            "discount_amount": discount_amount,
            "new_total_amount": new_total
        }
