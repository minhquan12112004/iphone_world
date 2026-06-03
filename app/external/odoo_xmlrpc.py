import xmlrpc.client
import asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class OdooClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OdooClient, cls).__new__(cls)
            cls._instance.url = settings.odoo_url
            cls._instance.db = settings.odoo_db
            cls._instance.username = settings.odoo_username
            cls._instance.password = settings.odoo_password
            cls._instance.uid = None
            cls._instance.models = None
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if not self.uid:
                logger.error("Failed to authenticate with Odoo")
            else:
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        except Exception as e:
            logger.error(f"Error connecting to Odoo: {e}")

    async def execute_kw(self, model: str, method: str, *args, **kwargs):
        if not self.uid or not self.models:
            self._init_client()
            if not self.uid:
                raise Exception("Cannot connect to Odoo")

        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(
                None,
                lambda: self.models.execute_kw(
                    self.db, self.uid, self.password,
                    model, method, args, kwargs
                )
            )
        except Exception as e:
            logger.error(f"Odoo execute_kw error ({model}.{method}): {e}")
            raise

    async def search_or_create_partner(self, email: str, name: str) -> int:
        """
        Check if partner exists by email, if not create one.
        Returns partner_id.
        """
        partner_ids = await self.execute_kw(
            'res.partner', 'search',
            [[['email', '=', email]]]
        )
        if partner_ids:
            return partner_ids[0]
        
        # Create new partner
        partner_id = await self.execute_kw(
            'res.partner', 'create',
            [{'name': name, 'email': email}]
        )
        return partner_id

    async def create_sale_order(self, partner_id: int, order_lines: List[Dict[str, Any]]) -> int:
        """
        Create sale order and lines.
        order_lines format: [{'product_id': odoo_product_id, 'product_uom_qty': qty}]
        Returns sale_order_id.
        """
        # Note: in Odoo, product_id in sale order line usually refers to product.product
        lines = []
        for line in order_lines:
            lines.append((0, 0, {
                'product_id': line['product_id'],
                'product_uom_qty': line['product_uom_qty']
            }))

        order_id = await self.execute_kw(
            'sale.order', 'create',
            [{
                'partner_id': partner_id,
                'order_line': lines
            }]
        )
        return order_id

    async def get_product_by_sku(self, sku: str) -> Optional[int]:
        """
        Search for product by default_code (SKU) in Odoo.
        Returns product.product ID.
        """
        product_ids = await self.execute_kw(
            'product.product', 'search',
            [[['default_code', '=', sku]]]
        )
        return product_ids[0] if product_ids else None

odoo_client = OdooClient()
