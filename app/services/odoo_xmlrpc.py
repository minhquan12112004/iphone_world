from __future__ import annotations

import logging
from dataclasses import dataclass
from http.client import HTTPConnection
from typing import Any
from urllib.parse import urljoin
from xmlrpc.client import Fault, ProtocolError, ServerProxy, Transport


logger = logging.getLogger(__name__)


class TimeoutTransport(Transport):
    def __init__(self, timeout: int) -> None:
        super().__init__()
        self.timeout = timeout

    def make_connection(self, host: str) -> HTTPConnection:
        return HTTPConnection(host, timeout=self.timeout)


class OdooRPCError(RuntimeError):
    pass


class OdooAuthenticationError(OdooRPCError):
    pass


@dataclass(slots=True)
class OdooXMLRPCClient:
    base_url: str
    db: str
    username: str
    password: str
    timeout: int = 30

    def _common_url(self) -> str:
        return urljoin(self.base_url.rstrip("/") + "/", "xmlrpc/2/common")

    def _object_url(self) -> str:
        return urljoin(self.base_url.rstrip("/") + "/", "xmlrpc/2/object")

    def _common_proxy(self) -> ServerProxy:
        return ServerProxy(self._common_url(), allow_none=True, transport=TimeoutTransport(self.timeout))

    def _object_proxy(self) -> ServerProxy:
        return ServerProxy(self._object_url(), allow_none=True, transport=TimeoutTransport(self.timeout))

    def authenticate(self) -> int:
        logger.debug("Authenticating against Odoo database=%s user=%s", self.db, self.username)
        try:
            uid = self._common_proxy().authenticate(self.db, self.username, self.password, {})
        except (Fault, ProtocolError, OSError) as exc:
            raise OdooAuthenticationError(f"Failed to authenticate with Odoo: {exc}") from exc

        if not uid:
            raise OdooAuthenticationError("Odoo authentication returned no user ID")

        return uid

    def execute_kw(self, model: str, method: str, args: list[Any] | None = None, kwargs: dict[str, Any] | None = None) -> Any:
        uid = self.authenticate()
        payload_args = args or []
        payload_kwargs = kwargs or {}

        logger.debug(
            "Executing Odoo RPC model=%s method=%s args=%s kwargs_keys=%s",
            model,
            method,
            payload_args,
            list(payload_kwargs.keys()),
        )

        try:
            return self._object_proxy().execute_kw(self.db, uid, self.password, model, method, payload_args, payload_kwargs)
        except (Fault, ProtocolError, OSError) as exc:
            raise OdooRPCError(f"Odoo RPC call failed for {model}.{method}: {exc}") from exc

    def search(self, model: str, domain: list[Any], limit: int | None = None, order: str | None = None) -> list[int]:
        kwargs: dict[str, Any] = {}
        if limit is not None:
            kwargs["limit"] = limit
        if order is not None:
            kwargs["order"] = order
        result = self.execute_kw(model, "search", [domain], kwargs)
        return list(result)

    def search_read(
        self,
        model: str,
        domain: list[Any],
        fields: list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        kwargs: dict[str, Any] = {}
        if fields is not None:
            kwargs["fields"] = fields
        if limit is not None:
            kwargs["limit"] = limit
        result = self.execute_kw(model, "search_read", [domain], kwargs)
        return list(result)

    def create(self, model: str, values: dict[str, Any]) -> int:
        logger.info("Sending data to Odoo model=%s payload=%s", model, values)
        result = self.execute_kw(model, "create", [values])
        return int(result)
