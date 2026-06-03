from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.category import Category
from typing import Optional, List

class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_odoo_id(self, odoo_id: int) -> Optional[Category]:
        result = await self.session.execute(select(Category).where(Category.odoo_id == odoo_id))
        return result.scalars().first()

    async def create(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def update(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category
