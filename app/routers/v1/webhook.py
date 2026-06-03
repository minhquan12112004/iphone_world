from fastapi import APIRouter, Depends, status

from app.config.odoo import get_odoo_client
from app.schemas.webhook import StockWebhookPayload, WebhookAckResponse
from app.services.odoo_xmlrpc import OdooXMLRPCClient
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhook/stock", tags=["webhook"])


def get_webhook_service(odoo_client: OdooXMLRPCClient = Depends(get_odoo_client)) -> WebhookService:
    return WebhookService(odoo_client)


@router.post("", response_model=WebhookAckResponse, status_code=status.HTTP_200_OK)
def handle_stock_webhook(
    payload: StockWebhookPayload,
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> WebhookAckResponse:
    return webhook_service.process_stock_webhook(payload)
