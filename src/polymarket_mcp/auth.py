"""Optional bearer-token middleware for HTTP transport."""

from __future__ import annotations

import os
import secrets

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


def get_bearer_token() -> str | None:
    """Return the expected bearer token, or ``None`` if auth is disabled."""
    return os.environ.get("POLYMARKET_MCP_API_TOKEN", "").strip() or None


class BearerAuthMiddleware:
    """Starlette ASGI middleware — validates ``Authorization: Bearer <token>``."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        expected = get_bearer_token()
        if expected is None:
            await self.app(scope, receive, send)
            return

        headers: dict[bytes, bytes] = dict(scope.get("headers", []))
        auth_value = headers.get(b"authorization", b"").decode()

        if not auth_value.startswith("Bearer "):
            resp = JSONResponse({"error": "Missing Authorization header"}, status_code=401)
            await resp(scope, receive, send)
            return

        provided = auth_value[7:]
        if not secrets.compare_digest(provided, expected):
            resp = JSONResponse({"error": "Invalid bearer token"}, status_code=401)
            await resp(scope, receive, send)
            return

        await self.app(scope, receive, send)
