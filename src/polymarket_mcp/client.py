"""Async Polymarket API client — Gamma, CLOB, and Data endpoints."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from polymarket_mcp.models import APIError, PolymarketError, RateLimitError, resolve_config, scrub_credentials
from polymarket_mcp.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30.0


class PolymarketClient:
    """Unified client for Polymarket Gamma, CLOB, and Data APIs (read-only)."""

    def __init__(self) -> None:
        self._config = resolve_config()
        self._http: httpx.AsyncClient | None = None
        self._rate_limiter = RateLimiter()

    # ------------------------------------------------------------------
    # HTTP internals
    # ------------------------------------------------------------------

    def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
        return self._http

    async def _call(self, base: str, path: str, group: str, params: dict[str, Any] | None = None) -> Any:
        """Rate-limited GET request."""
        await self._rate_limiter.acquire(group)
        url = f"{base}{path}"
        try:
            resp = await self._get_http().get(url, params=params)
        except httpx.TimeoutException as e:
            raise PolymarketError(f"Request timed out: {path}") from e
        except httpx.HTTPError as e:
            raise PolymarketError(scrub_credentials(f"HTTP error: {e}")) from e

        if resp.status_code == 429:
            raise RateLimitError(f"Rate limited on {path}")
        if resp.status_code >= 400:
            detail = resp.text[:500] if resp.text else ""
            raise APIError(
                f"API error {resp.status_code} on {path}",
                status_code=resp.status_code,
                details=scrub_credentials(detail),
            )
        return resp.json()

    async def _call_post(self, base: str, path: str, group: str, body: Any) -> Any:
        """Rate-limited POST request (for CLOB batch endpoints)."""
        await self._rate_limiter.acquire(group)
        url = f"{base}{path}"
        try:
            resp = await self._get_http().post(url, json=body)
        except httpx.TimeoutException as e:
            raise PolymarketError(f"Request timed out: {path}") from e
        except httpx.HTTPError as e:
            raise PolymarketError(scrub_credentials(f"HTTP error: {e}")) from e

        if resp.status_code == 429:
            raise RateLimitError(f"Rate limited on {path}")
        if resp.status_code >= 400:
            detail = resp.text[:500] if resp.text else ""
            raise APIError(
                f"API error {resp.status_code} on {path}",
                status_code=resp.status_code,
                details=scrub_credentials(detail),
            )
        return resp.json()

    # Convenience wrappers per API base
    async def _gamma(self, path: str, params: dict[str, Any] | None = None, group: str = "gamma_discovery") -> Any:
        return await self._call(self._config.gamma_host, path, group, params)

    async def _clob(self, path: str, params: dict[str, Any] | None = None, group: str = "clob_pricing") -> Any:
        return await self._call(self._config.clob_host, path, group, params)

    async def _clob_post(self, path: str, body: Any, group: str = "clob_batch") -> Any:
        return await self._call_post(self._config.clob_host, path, group, body)

    async def _data(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self._call(self._config.data_host, path, "data_general", params)

    # ------------------------------------------------------------------
    # System
    # ------------------------------------------------------------------

    async def health(self) -> dict[str, Any]:
        """CLOB health check + rate limiter stats."""
        ok = await self._clob("/ok", group="clob_general")
        return {"clob": ok, "rate_limits": self._rate_limiter.stats()}

    # ------------------------------------------------------------------
    # Gamma API — Discovery
    # ------------------------------------------------------------------

    async def list_events(
        self,
        active: bool | None = True,
        closed: bool | None = None,
        limit: int = 25,
        offset: int = 0,
        tag_id: int | None = None,
        order: str | None = None,
        ascending: bool | None = None,
    ) -> Any:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if active is not None:
            params["active"] = str(active).lower()
        if closed is not None:
            params["closed"] = str(closed).lower()
        if tag_id is not None:
            params["tag_id"] = tag_id
        if order is not None:
            params["order"] = order
        if ascending is not None:
            params["ascending"] = str(ascending).lower()
        return await self._gamma("/events", params)

    async def get_event(self, id_or_slug: str) -> Any:
        # Slugs contain hyphens; IDs are numeric
        if id_or_slug.isdigit():
            return await self._gamma(f"/events/{id_or_slug}")
        return await self._gamma(f"/events/slug/{id_or_slug}")

    async def list_markets(
        self,
        limit: int = 25,
        offset: int = 0,
        clob_token_ids: list[str] | None = None,
        condition_ids: list[str] | None = None,
        active: bool | None = None,
        closed: bool | None = None,
        tag_id: int | None = None,
        order: str | None = None,
        ascending: bool | None = None,
    ) -> Any:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if clob_token_ids:
            params["clob_token_ids"] = ",".join(clob_token_ids)
        if condition_ids:
            params["condition_ids"] = ",".join(condition_ids)
        if active is not None:
            params["active"] = str(active).lower()
        if closed is not None:
            params["closed"] = str(closed).lower()
        if tag_id is not None:
            params["tag_id"] = tag_id
        if order is not None:
            params["order"] = order
        if ascending is not None:
            params["ascending"] = str(ascending).lower()
        return await self._gamma("/markets", params)

    async def get_market(self, id_or_slug: str) -> Any:
        if id_or_slug.isdigit():
            return await self._gamma(f"/markets/{id_or_slug}")
        return await self._gamma(f"/markets/slug/{id_or_slug}")

    async def search(self, query: str) -> Any:
        return await self._gamma("/public-search", {"query": query})

    async def list_tags(self) -> Any:
        return await self._gamma("/tags", group="gamma_general")

    async def list_sports(self) -> Any:
        return await self._gamma("/sports", group="gamma_general")

    async def get_sampling_markets(self) -> Any:
        return await self._clob("/sampling-simplified-markets", group="clob_general")

    # ------------------------------------------------------------------
    # CLOB API — Pricing
    # ------------------------------------------------------------------

    async def get_book(self, token_id: str) -> Any:
        return await self._clob("/book", {"token_id": token_id})

    async def get_books(self, token_ids: list[str]) -> Any:
        return await self._clob_post("/books", token_ids)

    async def get_price(self, token_id: str, side: str) -> Any:
        return await self._clob("/price", {"token_id": token_id, "side": side})

    async def get_prices(self, token_ids: list[str], side: str) -> Any:
        return await self._clob_post("/prices", {"token_ids": token_ids, "side": side})

    async def get_midpoint(self, token_id: str) -> Any:
        return await self._clob("/midpoint", {"token_id": token_id})

    async def get_spread(self, token_id: str) -> Any:
        return await self._clob("/spread", {"token_id": token_id})

    async def get_spreads(self, token_ids: list[str]) -> Any:
        return await self._clob_post("/spreads", token_ids)

    async def get_price_history(
        self,
        token_id: str,
        fidelity: int = 60,
        start_ts: int | None = None,
        end_ts: int | None = None,
    ) -> Any:
        params: dict[str, Any] = {"market": token_id, "interval": fidelity}
        if start_ts is not None:
            params["startTs"] = start_ts
        if end_ts is not None:
            params["endTs"] = end_ts
        return await self._clob("/prices-history", params, group="clob_history")

    async def get_last_trade_price(self, token_id: str) -> Any:
        return await self._clob("/last-trade-price", {"token_id": token_id})

    async def get_tick_size(self, token_id: str) -> Any:
        return await self._clob("/tick-size", {"token_id": token_id}, group="clob_general")

    # ------------------------------------------------------------------
    # Data API — Analytics
    # ------------------------------------------------------------------

    async def get_open_interest(self, clob_token_ids: list[str]) -> Any:
        return await self._data("/open-interest", {"clob_token_ids": ",".join(clob_token_ids)})

    async def get_top_holders(self, token_id: str, limit: int = 10) -> Any:  # noqa: ANN401
        return await self._data("/top-holders", {"token_id": token_id, "limit": limit})

    async def get_leaderboard(self, limit: int = 25, offset: int = 0) -> Any:  # noqa: ANN401
        return await self._data("/leaderboard", {"limit": limit, "offset": offset})

    async def get_volume(self, event_id: str) -> Any:  # noqa: ANN401
        return await self._data("/volume", {"event_id": event_id})
