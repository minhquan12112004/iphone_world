import logging

from app.schemas.webhook import StockWebhookPayload, WebhookAckResponse
from app.services.odoo_xmlrpc import OdooXMLRPCClient

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self, odoo_client: OdooXMLRPCClient) -> None:
        self._odoo = odoo_client

    def process_stock_webhook(self, payload: StockWebhookPayload) -> WebhookAckResponse:
        logger.info("Received stock webhook from Odoo: %s", payload.model_dump())

        matched_product_id = None
        if payload.sku:
            logger.debug("Looking up product in Odoo by SKU=%s", payload.sku)
            product_ids = self._odoo.search("product.product", [["default_code", "=", payload.sku]], limit=1)
            matched_product_id = product_ids[0] if product_ids else None

        logger.info(
            "Webhook processed event_type=%s record_model=%s record_id=%s matched_product_id=%s",
            payload.event_type,
            payload.record_model,
            payload.record_id,
            matched_product_id,
        )

        return WebhookAckResponse(
            success=True,
            received_event=payload.event_type,
            message="Webhook accepted and normalized",
            matched_product_id=matched_product_id,
        )
