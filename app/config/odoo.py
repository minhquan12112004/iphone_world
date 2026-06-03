from functools import lru_cache
import logging

from app.config.settings import get_settings
from app.services.odoo_xmlrpc import OdooXMLRPCClient

logger = logging.getLogger(__name__)


@lru_cache
def get_odoo_client() -> OdooXMLRPCClient:
    settings = get_settings()
    logger.info("Initializing Odoo XML-RPC client for %s", settings.odoo_url)
    return OdooXMLRPCClient(
        base_url=settings.odoo_url,
        db=settings.odoo_db,
        username=settings.odoo_username,
        password=settings.odoo_password,
        timeout=settings.odoo_rpc_timeout,
    )
