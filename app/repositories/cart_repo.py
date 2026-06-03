from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.cart import CartItem, Coupon
from typing import Optional, List

class CartRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_items_by_user(self, user_id: int) -> List[CartItem]:
        query = select(CartItem).options(selectinload(CartItem.product)).where(CartItem.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_item(self, user_id: int, product_id: int) -> Optional[CartItem]:
        query = select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def add_or_update_item(self, user_id: int, product_id: int, quantity: int) -> CartItem:
        item = await self.get_item(user_id, product_id)
        if item:
            item.quantity = quantity
        else:
            item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
            self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        # Load product for response
        query = select(CartItem).options(selectinload(CartItem.product)).where(CartItem.id == item.id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def remove_item(self, user_id: int, product_id: int):
        item = await self.get_item(user_id, product_id)
        if item:
            await self.session.delete(item)
            await self.session.commit()

    async def clear_cart(self, user_id: int):
        items = await self.get_items_by_user(user_id)
        for item in items:
            await self.session.delete(item)
        await self.session.commit()

    async def get_coupon_by_code(self, code: str) -> Optional[Coupon]:
        result = await self.session.execute(select(Coupon).where(Coupon.code == code))
        return result.scalars().first()
