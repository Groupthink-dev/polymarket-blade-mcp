"""Polymarket Blade MCP — read-only prediction market data server."""

from __future__ import annotations

import logging
import os
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from polymarket_mcp.client import PolymarketClient
from polymarket_mcp.formatters import (
    format_event,
    format_events,
    format_last_trade,
    format_leaderboard,
    format_market,
    format_markets,
    format_open_interest,
    format_orderbook,
    format_orderbooks_batch,
    format_price,
    format_price_history,
    format_prices_batch,
    format_search,
    format_sports,
    format_spread,
    format_spreads_batch,
    format_status,
    format_tags,
    format_tick_size,
    format_top_holders,
    format_volume,
)
from polymarket_mcp.models import PolymarketError, scrub_credentials

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Transport config
# ---------------------------------------------------------------------------

TRANSPORT = os.environ.get("POLYMARKET_MCP_TRANSPORT", "stdio").lower()
HTTP_HOST = os.environ.get("POLYMARKET_MCP_HOST", "0.0.0.0")
HTTP_PORT = int(os.environ.get("POLYMARKET_MCP_PORT", "8082"))

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "PolymarketBlade",
    instructions=(
        "Polymarket prediction market data — events, markets, orderbooks, prices, analytics. "
        "Read-only. All endpoints are public (no credentials required). "
        "Use pm_prices_batch for efficient multi-token price checks. "
        "Use pm_trending for market discovery. Use pm_events with tag filter to narrow scope."
    ),
)

# ---------------------------------------------------------------------------
# Singleton client
# ---------------------------------------------------------------------------

_client: PolymarketClient | None = None


def _get_client() -> PolymarketClient:
    global _client
    if _client is None:
        _client = PolymarketClient()
    return _client


def _error(e: PolymarketError) -> str:
    msg = scrub_credentials(str(e))
    if e.details:
        msg += f"\n{scrub_credentials(e.details)}"
    return f"Error: {msg}"


# ===================================================================
# SYSTEM
# ===================================================================


@mcp.tool()
async def pm_status() -> str:
    """API health, rate-limit stats, and server info. Call first to verify connectivity."""
    try:
        data = await _get_client().health()
        return format_status(data)
    except PolymarketError as e:
        return _error(e)


# ===================================================================
# DISCOVERY — Gamma API
# ===================================================================


@mcp.tool()
async def pm_events(
    active: Annotated[bool | None, Field(description="Filter active (True) or closed (False) events")] = True,
    tag: Annotated[str | None, Field(description="Filter by tag slug (e.g. 'politics', 'crypto')")] = None,
    limit: Annotated[int, Field(description="Max results (1-100)", ge=1, le=100)] = 25,
    offset: Annotated[int, Field(description="Pagination offset", ge=0)] = 0,
    order: Annotated[str | None, Field(description="Sort field (e.g. 'volume', 'liquidity', 'startDate')")] = None,
) -> str:
    """List prediction events with filters. Returns title, market count, volume, liquidity."""
    try:
        data = await _get_client().list_events(active=active, limit=limit, offset=offset, order=order)
        return format_events(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_event(
    id_or_slug: Annotated[str, Field(description="Event ID (numeric) or slug (hyphenated)")],
) -> str:
    """Get event detail including all markets, outcomes, and current prices."""
    try:
        data = await _get_client().get_event(id_or_slug)
        return format_event(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_markets(
    limit: Annotated[int, Field(description="Max results (1-100)", ge=1, le=100)] = 25,
    offset: Annotated[int, Field(description="Pagination offset", ge=0)] = 0,
    active: Annotated[bool | None, Field(description="Filter active markets")] = None,
    closed: Annotated[bool | None, Field(description="Filter closed markets")] = None,
    order: Annotated[str | None, Field(description="Sort field")] = None,
) -> str:
    """List markets with filters. Returns question, outcomes, prices, volume."""
    try:
        data = await _get_client().list_markets(limit=limit, offset=offset, active=active, closed=closed, order=order)
        return format_markets(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_market(
    id_or_slug: Annotated[str, Field(description="Market ID (numeric) or slug (hyphenated)")],
) -> str:
    """Get market detail: question, outcomes, prices, volume, liquidity, CLOB token IDs."""
    try:
        data = await _get_client().get_market(id_or_slug)
        return format_market(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_search(
    query: Annotated[str, Field(description="Search query (e.g. 'US election', 'Bitcoin price')")],
) -> str:
    """Search events and markets by keyword."""
    try:
        data = await _get_client().search(query)
        return format_search(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_categories() -> str:
    """List all tags/categories for filtering events and markets."""
    try:
        data = await _get_client().list_tags()
        return format_tags(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_trending() -> str:
    """Get featured/trending markets — good starting point for discovery."""
    try:
        data = await _get_client().get_sampling_markets()
        return format_markets(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_sports() -> str:
    """List sports categories available on Polymarket."""
    try:
        data = await _get_client().list_sports()
        return format_sports(data)
    except PolymarketError as e:
        return _error(e)


# ===================================================================
# PRICING — CLOB API
# ===================================================================


@mcp.tool()
async def pm_orderbook(
    token_id: Annotated[str, Field(description="CLOB token ID (from market detail clobTokenIds)")],
    depth: Annotated[int, Field(description="Number of price levels to show", ge=1, le=50)] = 5,
) -> str:
    """Get order book for a token — bid/ask levels with size."""
    try:
        data = await _get_client().get_book(token_id)
        return format_orderbook(data, depth)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_price(
    token_id: Annotated[str, Field(description="CLOB token ID")],
    side: Annotated[str, Field(description="BUY or SELL")] = "BUY",
) -> str:
    """Get best price for a token on the given side."""
    try:
        data = await _get_client().get_price(token_id, side.upper())
        return format_price(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_prices_batch(
    token_ids: Annotated[str, Field(description="Comma-separated CLOB token IDs (max 20)")],
    side: Annotated[str, Field(description="BUY or SELL")] = "BUY",
) -> str:
    """Batch prices for multiple tokens — efficient for scan workflows."""
    try:
        ids = [t.strip() for t in token_ids.split(",") if t.strip()][:20]
        data = await _get_client().get_prices(ids, side.upper())
        return format_prices_batch(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_spread(
    token_id: Annotated[str, Field(description="CLOB token ID")],
) -> str:
    """Get bid-ask spread for a token."""
    try:
        data = await _get_client().get_spread(token_id)
        return format_spread(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_price_history(
    token_id: Annotated[str, Field(description="CLOB token ID")],
    fidelity: Annotated[int, Field(description="Interval in minutes: 1, 5, 60, 360, 1440")] = 60,
) -> str:
    """Historical prices for a token at configurable granularity."""
    try:
        data = await _get_client().get_price_history(token_id, fidelity)
        return format_price_history(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_last_trade(
    token_id: Annotated[str, Field(description="CLOB token ID")],
) -> str:
    """Get last trade price for a token."""
    try:
        data = await _get_client().get_last_trade_price(token_id)
        return format_last_trade(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_tick_size(
    token_id: Annotated[str, Field(description="CLOB token ID")],
) -> str:
    """Get minimum tick size for a market (0.1, 0.01, 0.001, or 0.0001)."""
    try:
        data = await _get_client().get_tick_size(token_id)
        return format_tick_size(data)
    except PolymarketError as e:
        return _error(e)


# ===================================================================
# ANALYTICS — Data API
# ===================================================================


@mcp.tool()
async def pm_open_interest(
    token_ids: Annotated[str, Field(description="Comma-separated CLOB token IDs")],
) -> str:
    """Get open interest for tokens."""
    try:
        ids = [t.strip() for t in token_ids.split(",") if t.strip()]
        data = await _get_client().get_open_interest(ids)
        return format_open_interest(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_top_holders(
    token_id: Annotated[str, Field(description="CLOB token ID")],
    limit: Annotated[int, Field(description="Max holders to show", ge=1, le=50)] = 10,
) -> str:
    """Get top holders for a market token."""
    try:
        data = await _get_client().get_top_holders(token_id, limit)
        return format_top_holders(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_leaderboard(
    limit: Annotated[int, Field(description="Max entries", ge=1, le=100)] = 25,
    offset: Annotated[int, Field(description="Pagination offset", ge=0)] = 0,
) -> str:
    """Trader leaderboard — ranked by profit."""
    try:
        data = await _get_client().get_leaderboard(limit, offset)
        return format_leaderboard(data)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_volume(
    event_id: Annotated[str, Field(description="Event ID")],
) -> str:
    """Get live trading volume for an event."""
    try:
        data = await _get_client().get_volume(event_id)
        return format_volume(data)
    except PolymarketError as e:
        return _error(e)


# ===================================================================
# BATCH — for scan workflows
# ===================================================================


@mcp.tool()
async def pm_orderbooks_batch(
    token_ids: Annotated[str, Field(description="Comma-separated CLOB token IDs (max 10)")],
    depth: Annotated[int, Field(description="Order book depth per token", ge=1, le=20)] = 5,
) -> str:
    """Batch orderbooks for multiple tokens — efficient for scanning."""
    try:
        ids = [t.strip() for t in token_ids.split(",") if t.strip()][:10]
        data = await _get_client().get_books(ids)
        return format_orderbooks_batch(data, depth)
    except PolymarketError as e:
        return _error(e)


@mcp.tool()
async def pm_spreads_batch(
    token_ids: Annotated[str, Field(description="Comma-separated CLOB token IDs (max 20)")],
) -> str:
    """Batch spreads for multiple tokens."""
    try:
        ids = [t.strip() for t in token_ids.split(",") if t.strip()][:20]
        data = await _get_client().get_spreads(ids)
        return format_spreads_batch(data)
    except PolymarketError as e:
        return _error(e)


# ===================================================================
# Entry point
# ===================================================================


def main() -> None:
    """Run the Polymarket Blade MCP server."""
    if TRANSPORT == "http":
        from starlette.middleware import Middleware

        from polymarket_mcp.auth import BearerAuthMiddleware

        mcp.run(
            transport="streamable-http",
            host=HTTP_HOST,
            port=HTTP_PORT,
            middleware=[Middleware(BearerAuthMiddleware)],
        )
    else:
        mcp.run(transport="stdio")
