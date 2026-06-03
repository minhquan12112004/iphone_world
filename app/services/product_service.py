import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.repositories.product_repo import ProductRepository
from app.repositories.category_repo import CategoryRepository
from app.schemas.product import WebhookStockPayload, WebhookCategoryPayload, WebhookProductPayload, WebhookOdooIDPayload
from typing import Optional, List
from app.models.product import Product
from app.models.category import Category
from app.services.odoo_xmlrpc import OdooXMLRPCClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, session: AsyncSession, redis: Redis):
        self.product_repo = ProductRepository(session)
        self.category_repo = CategoryRepository(session)
        self.redis = redis
        self.odoo_client = OdooXMLRPCClient(
            base_url=settings.odoo_url,
            db=settings.odoo_db,
            username=settings.odoo_username,
            password=settings.odoo_password,
            timeout=settings.odoo_rpc_timeout
        )

    async def get_products(self, skip: int, limit: int, search: Optional[str]) -> List[Product]:
        cache_key = f"products_list:{skip}:{limit}"
        if not search:
            cached = await self.redis.get(cache_key)
            if cached:
                pass
        
        products = await self.product_repo.get_all(skip, limit, search)
        return products

    async def get_product(self, product_id: int) -> Optional[Product]:
        return await self.product_repo.get_by_id(product_id)

    async def _clear_product_cache(self):
        keys = await self.redis.keys("products_list:*")
        if keys:
            await self.redis.delete(*keys)

    async def process_webhook(self, payload: WebhookStockPayload):
        product = await self.product_repo.get_by_sku(payload.sku)
        if product:
            if payload.new_stock_qty is not None:
                product.stock_qty = payload.new_stock_qty
            if payload.new_price is not None:
                product.price = payload.new_price
            await self.product_repo.update(product)
            await self._clear_product_cache()

    async def sync_product_from_odoo(self, payload: WebhookOdooIDPayload) -> Optional[Product]:
        # Call Odoo XMLRPC in a thread to prevent blocking the async loop
        odoo_products = await asyncio.to_thread(
            self.odoo_client.search_read,
            "product.template",
            [["id", "=", payload.odoo_id]],
            ["default_code", "name", "list_price", "qty_available", "categ_id", "description"],
            1
        )

        if not odoo_products:
            logger.warning(f"Product with odoo_id {payload.odoo_id} not found in Odoo.")
            return None

        odoo_product = odoo_products[0]
        sku = odoo_product.get("default_code") or str(payload.odoo_id)
        name = odoo_product.get("name", "Unknown Product")
        price = odoo_product.get("list_price", 0.0)
        stock_qty = odoo_product.get("qty_available", 0.0)
        description = odoo_product.get("description")
        if isinstance(description, bool) and not description:
            description = None # Odoo returns False for empty text fields
            
        categ_id = None
        odoo_category = odoo_product.get("categ_id")
        if odoo_category and isinstance(odoo_category, list) and len(odoo_category) == 2:
            cat_odoo_id, cat_name = odoo_category
            category = await self.category_repo.get_by_odoo_id(cat_odoo_id)
            if category:
                if category.name != cat_name:
                    category.name = cat_name
                    await self.category_repo.update(category)
                categ_id = category.id
            else:
                new_category = Category(odoo_id=cat_odoo_id, name=cat_name)
                created_category = await self.category_repo.create(new_category)
                categ_id = created_category.id

        product = await self.product_repo.get_by_sku(sku)
        if product:
            product.name = name
            product.price = price
            product.stock_qty = int(stock_qty)
            product.description = description
            if categ_id is not None:
                product.category_id = categ_id
            updated_product = await self.product_repo.update(product)
        else:
            new_product = Product(
                sku=sku,
                name=name,
                price=price,
                stock_qty=int(stock_qty),
                description=description,
                category_id=categ_id
            )
            updated_product = await self.product_repo.create(new_product)
        
        await self._clear_product_cache()
        return updated_product

    async def sync_category_from_odoo(self, payload: WebhookOdooIDPayload) -> Optional[Category]:
        odoo_categories = await asyncio.to_thread(
            self.odoo_client.search_read,
            "product.category",
            [["id", "=", payload.odoo_id]],
            ["name"],
            1
        )

        if not odoo_categories:
            logger.warning(f"Category with odoo_id {payload.odoo_id} not found in Odoo.")
            return None

        odoo_category = odoo_categories[0]
        cat_name = odoo_category.get("name", "Unknown Category")

        category = await self.category_repo.get_by_odoo_id(payload.odoo_id)
        if category:
            category.name = cat_name
            return await self.category_repo.update(category)
        else:
            new_category = Category(odoo_id=payload.odoo_id, name=cat_name)
            return await self.category_repo.create(new_category)

    async def process_product_webhook(self, payload: WebhookProductPayload) -> Product:
        category_id = None
        if payload.category_odoo_id:
            category = await self.category_repo.get_by_odoo_id(payload.category_odoo_id)
            if category:
                category_id = category.id

        product = await self.product_repo.get_by_sku(payload.sku)
        if product:
            product.name = payload.name
            product.price = payload.price
            product.stock_qty = payload.stock_qty
            if payload.description is not None:
                product.description = payload.description
            if category_id is not None:
                product.category_id = category_id
            updated_product = await self.product_repo.update(product)
        else:
            new_product = Product(
                sku=payload.sku,
                name=payload.name,
                price=payload.price,
                stock_qty=payload.stock_qty,
                description=payload.description,
                category_id=category_id
            )
            updated_product = await self.product_repo.create(new_product)
        
        await self._clear_product_cache()
        return updated_product

