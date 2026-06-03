from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.order import Order, OrderItem
from typing import List, Optional

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, order: Order, items: List[OrderItem]) -> Order:
        self.session.add(order)
        await self.session.flush() # To get order.id for items
        
        for item in items:
            item.order_id = order.id
            self.session.add(item)
            
        await self.session.commit()
        await self.session.refresh(order)
        
        # Load items and product for response
        query = select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).where(Order.id == order.id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_orders_by_user(self, user_id: int) -> List[Order]:
        query = select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        query = select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).where(Order.id == order_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update_status(self, order_id: int, status: str, odoo_order_id: Optional[int] = None) -> Order:
        order = await self.get_by_id(order_id)
        if order:
            order.status = status
            if odoo_order_id:
                order.odoo_order_id = odoo_order_id
            await self.session.commit()
            await self.session.refresh(order)
        return order
