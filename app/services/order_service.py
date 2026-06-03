import asyncio
import logging
import uuid
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.order_repo import OrderRepository
from app.repositories.cart_repo import CartRepository
from app.external.odoo_xmlrpc import odoo_client
from app.models.order import Order, OrderItem
from app.models.user import User

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.cart_repo = CartRepository(session)

    async def sync_order_to_odoo(self, order_id: int, user_email: str, user_name: str, items: list):
        # We need a new session for background task since the original one might be closed
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            repo = OrderRepository(session)
            try:
                # 1. Search or create partner
                partner_id = await odoo_client.search_or_create_partner(user_email, user_name)
                
                # 2. Build order lines
                odoo_lines = []
                for item in items:
                    # In a real app, you'd map your product SKU to Odoo product_id
                    # Here we fetch product_id by SKU
                    odoo_product_id = await odoo_client.get_product_by_sku(item.product.sku)
                    if odoo_product_id:
                        odoo_lines.append({
                            'product_id': odoo_product_id,
                            'product_uom_qty': item.quantity
                        })
                    else:
                        logger.warning(f"Product SKU {item.product.sku} not found in Odoo. Skipping line.")
                
                if not odoo_lines:
                    raise Exception("No valid product lines to sync to Odoo")

                # 3. Create sale order
                odoo_order_id = await odoo_client.create_sale_order(partner_id, odoo_lines)
                
                # 4. Update order status
                await repo.update_status(order_id, status="SYNCED", odoo_order_id=odoo_order_id)
                logger.info(f"Successfully synced order {order_id} to Odoo as sale order {odoo_order_id}")

            except Exception as e:
                logger.error(f"Failed to sync order {order_id} to Odoo: {e}")
                await repo.update_status(order_id, status="FAILED")

    async def checkout(self, user: User, background_tasks: BackgroundTasks) -> Order:
        cart_items = await self.cart_repo.get_items_by_user(user.id)
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        total_amount = sum(item.quantity * item.product.price for item in cart_items if item.product)
        
        # Check stock again before checkout
        for item in cart_items:
            if item.quantity > item.product.stock_qty:
                raise HTTPException(status_code=400, detail=f"Not enough stock for product {item.product.name}")

        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        order = Order(
            user_id=user.id,
            order_number=order_number,
            total_amount=total_amount,
            status="PENDING"
        )
        
        order_items = []
        for item in cart_items:
            order_items.append(OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
                product=item.product # Keep ref for sync
            ))

        # Create Order in DB
        created_order = await self.order_repo.create_order(order, order_items)

        # Clear cart
        await self.cart_repo.clear_cart(user.id)

        # Schedule background task to sync to Odoo
        background_tasks.add_task(
            self.sync_order_to_odoo,
            created_order.id,
            user.email,
            user.name,
            created_order.items
        )

        return created_order

    async def get_user_orders(self, user_id: int):
        return await self.order_repo.get_orders_by_user(user_id)
