from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.product import Product
from typing import Optional, List

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Product]:
        query = select(Product)
        if search:
            query = query.where(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        result = await self.session.execute(select(Product).where(Product.id == product_id))
        return result.scalars().first()
        
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        result = await self.session.execute(select(Product).where(Product.sku == sku))
        return result.scalars().first()

    async def create(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product
