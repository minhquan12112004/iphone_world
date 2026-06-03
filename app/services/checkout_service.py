import logging
from typing import Any
from sqlalchemy.orm import Session

from app.services.cart_service import fetch_cart_items_models
from app.models.cart_models import CartItem, Product
from app.services.odoo_xmlrpc import OdooXMLRPCClient, OdooRPCError

logger = logging.getLogger(__name__)


class CheckoutError(RuntimeError):
    pass


def checkout_and_sync(db: Session, user: Any, odoo: OdooXMLRPCClient) -> dict:
    """Checkout the current user's cart and sync to Odoo. Returns order info.

    - Fetch cart items from local DB
    - Ensure items exist
    - Ensure mapping to Odoo product IDs
    - Ensure partner exists or create
    - Create sale.order with order lines
    - On success delete local cart items
    """
    user_id = int(user.id)
    logger.info("Starting checkout for user_id=%s email=%s", user_id, getattr(user, "email", None))

    cart_items = fetch_cart_items_models(db, user_id)
    if not cart_items:
        logger.warning("Checkout attempted with empty cart for user_id=%s", user_id)
        raise CheckoutError("Cart is empty")

    # Map local cart items to Odoo product IDs and collect order lines
    order_lines = []
    for ci in cart_items:
        prod: Product | None = db.query(Product).filter(Product.id == ci.product_id).first()
        if not prod:
            logger.error("Product id=%s from cart not found in local DB", ci.product_id)
            raise CheckoutError(f"Product id {ci.product_id} not found locally")

        # Lookup product in Odoo by SKU
        try:
            product_ids = odoo.search("product.product", [["default_code", "=", prod.sku]], limit=1)
        except OdooRPCError as exc:
            logger.exception("Odoo product lookup failed for sku=%s: %s", prod.sku, exc)
            raise CheckoutError("Failed to verify product mapping in Odoo") from exc

        if not product_ids:
            logger.error("No product in Odoo matches SKU=%s", prod.sku)
            raise CheckoutError(f"Product SKU {prod.sku} not found in Odoo")

        odoo_product_id = int(product_ids[0])
        line = (0, 0, {"product_id": odoo_product_id, "product_uom_qty": ci.quantity, "price_unit": float(prod.price)})
        order_lines.append(line)

    # Ensure partner exists in Odoo (by email)
    partner_id = None
    user_email = getattr(user, "email", None)
    user_name = getattr(user, "name", None) or f"User {user_id}"
    try:
        if user_email:
            partners = odoo.search_read("res.partner", [["email", "=", user_email]], fields=["id"], limit=1)
            if partners:
                partner_id = int(partners[0]["id"])
        if not partner_id:
            # create partner
            values = {"name": user_name}
            if user_email:
                values["email"] = user_email
            partner_id = odoo.create("res.partner", values)
            logger.info("Created partner in Odoo partner_id=%s for user_id=%s", partner_id, user_id)
    except OdooRPCError as exc:
        logger.exception("Failed to ensure partner in Odoo for user %s: %s", user_id, exc)
        raise CheckoutError("Failed to ensure partner in Odoo") from exc

    # Build sale.order values
    order_values = {
        "partner_id": partner_id,
        "order_line": order_lines,
    }

    logger.info("Creating sale.order in Odoo for user_id=%s partner_id=%s lines=%d", user_id, partner_id, len(order_lines))
    try:
        order_id = odoo.create("sale.order", order_values)
    except OdooRPCError as exc:
        logger.exception("Failed to create sale.order in Odoo for user %s: %s", user_id, exc)
        raise CheckoutError("Failed to create order in Odoo") from exc

    # Optionally fetch order name
    try:
        order = odoo.search_read("sale.order", [["id", "=", order_id]], fields=["name"], limit=1)
        order_name = order[0]["name"] if order else None
    except Exception:
        logger.exception("Failed to fetch order name for order_id=%s", order_id)
        order_name = None

    # On success, delete local cart items in a DB transaction
    try:
        db.query(CartItem).filter(CartItem.user_id == user_id).delete(synchronize_session=False)
        db.commit()
    except Exception as exc:
        logger.exception("Failed to clear cart after successful order %s: %s", order_id, exc)
        # We do not rollback Odoo order here — but surface the problem
        raise CheckoutError("Order created but failed to clear local cart") from exc

    logger.info("Checkout completed for user_id=%s order_id=%s", user_id, order_id)
    return {"order_id": int(order_id), "order_name": order_name}
