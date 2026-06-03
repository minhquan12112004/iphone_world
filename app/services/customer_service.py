import logging

from app.schemas.customer import CustomerCreateRequest, CustomerResponse
from app.services.odoo_xmlrpc import OdooXMLRPCClient

logger = logging.getLogger(__name__)


class CustomerService:
    def __init__(self, odoo_client: OdooXMLRPCClient) -> None:
        self._odoo = odoo_client

    def create_customer(self, payload: CustomerCreateRequest) -> CustomerResponse:
        partner_values = {
            "name": payload.name,
            "email": payload.email,
            "phone": payload.phone,
            "vat": payload.vat,
            "street": payload.street,
            "city": payload.city,
        }

        logger.info("Preparing to push customer to Odoo: %s", partner_values)
        partner_id = self._odoo.create("res.partner", partner_values)

        logger.info("Customer created in Odoo partner_id=%s", partner_id)
        return CustomerResponse(
            success=True,
            partner_id=partner_id,
            message="Customer pushed to Odoo successfully",
        )
