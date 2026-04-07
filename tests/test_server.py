"""Tests for MCP server tool execution."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from polymarket_mcp.models import PolymarketError
from polymarket_mcp.server import (
    pm_categories,
    pm_event,
    pm_events,
    pm_last_trade,
    pm_leaderboard,
    pm_market,
    pm_markets,
    pm_open_interest,
    pm_orderbook,
    pm_orderbooks_batch,
    pm_price,
    pm_price_history,
    pm_prices_batch,
    pm_search,
    pm_sports,
    pm_spread,
    pm_spreads_batch,
    pm_status,
    pm_tick_size,
    pm_top_holders,
    pm_trending,
    pm_volume,
)

from .conftest import (
    SAMPLE_EVENT,
    SAMPLE_EVENTS,
    SAMPLE_LAST_TRADE,
    SAMPLE_LEADERBOARD,
    SAMPLE_MARKET,
    SAMPLE_MARKETS,
    SAMPLE_OPEN_INTEREST,
    SAMPLE_ORDERBOOK,
    SAMPLE_PRICE,
    SAMPLE_PRICE_HISTORY,
    SAMPLE_PRICES_BATCH,
    SAMPLE_SEARCH,
    SAMPLE_SPORTS,
    SAMPLE_SPREAD,
    SAMPLE_STATUS,
    SAMPLE_TAGS,
    SAMPLE_TICK_SIZE,
    SAMPLE_TOP_HOLDERS,
    SAMPLE_VOLUME,
)


def _mock_client(**overrides: AsyncMock) -> AsyncMock:
    """Create a mock PolymarketClient with default return values."""
    client = AsyncMock()
    client.health.return_value = SAMPLE_STATUS
    client.list_events.return_value = SAMPLE_EVENTS
    client.get_event.return_value = SAMPLE_EVENT
    client.list_markets.return_value = SAMPLE_MARKETS
    client.get_market.return_value = SAMPLE_MARKET
    client.search.return_value = SAMPLE_SEARCH
    client.list_tags.return_value = SAMPLE_TAGS
    client.list_sports.return_value = SAMPLE_SPORTS
    client.get_sampling_markets.return_value = SAMPLE_MARKETS
    client.get_book.return_value = SAMPLE_ORDERBOOK
    client.get_books.return_value = [SAMPLE_ORDERBOOK]
    client.get_price.return_value = SAMPLE_PRICE
    client.get_prices.return_value = SAMPLE_PRICES_BATCH
    client.get_spread.return_value = SAMPLE_SPREAD
    client.get_spreads.return_value = [SAMPLE_SPREAD]
    client.get_price_history.return_value = SAMPLE_PRICE_HISTORY
    client.get_last_trade_price.return_value = SAMPLE_LAST_TRADE
    client.get_tick_size.return_value = SAMPLE_TICK_SIZE
    client.get_open_interest.return_value = SAMPLE_OPEN_INTEREST
    client.get_top_holders.return_value = SAMPLE_TOP_HOLDERS
    client.get_leaderboard.return_value = SAMPLE_LEADERBOARD
    client.get_volume.return_value = SAMPLE_VOLUME
    for k, v in overrides.items():
        setattr(client, k, v)
    return client


@pytest.fixture
def mock_client() -> AsyncMock:
    client = _mock_client()
    with patch("polymarket_mcp.server._get_client", return_value=client):
        yield client


# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------


class TestPmStatus:
    @pytest.mark.asyncio
    async def test_returns_status(self, mock_client: AsyncMock) -> None:
        result = await pm_status()
        assert "Polymarket Blade MCP" in result
        assert "CLOB" in result

    @pytest.mark.asyncio
    async def test_handles_error(self) -> None:
        client = _mock_client()
        client.health.side_effect = PolymarketError("connection failed")
        with patch("polymarket_mcp.server._get_client", return_value=client):
            result = await pm_status()
        assert "Error" in result
        assert "connection failed" in result


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


class TestDiscovery:
    @pytest.mark.asyncio
    async def test_pm_events(self, mock_client: AsyncMock) -> None:
        result = await pm_events()
        assert "Bitcoin" in result
        mock_client.list_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_pm_event(self, mock_client: AsyncMock) -> None:
        result = await pm_event(id_or_slug="1001")
        assert "id=1001" in result
        mock_client.get_event.assert_called_once_with("1001")

    @pytest.mark.asyncio
    async def test_pm_markets(self, mock_client: AsyncMock) -> None:
        result = await pm_markets()
        assert "Bitcoin" in result

    @pytest.mark.asyncio
    async def test_pm_market(self, mock_client: AsyncMock) -> None:
        result = await pm_market(id_or_slug="5001")
        assert "id=5001" in result

    @pytest.mark.asyncio
    async def test_pm_search(self, mock_client: AsyncMock) -> None:
        result = await pm_search(query="Bitcoin")
        assert "Bitcoin" in result

    @pytest.mark.asyncio
    async def test_pm_categories(self, mock_client: AsyncMock) -> None:
        result = await pm_categories()
        assert "Politics" in result

    @pytest.mark.asyncio
    async def test_pm_trending(self, mock_client: AsyncMock) -> None:
        result = await pm_trending()
        assert "Bitcoin" in result

    @pytest.mark.asyncio
    async def test_pm_sports(self, mock_client: AsyncMock) -> None:
        result = await pm_sports()
        assert "NFL" in result


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------


class TestPricing:
    @pytest.mark.asyncio
    async def test_pm_orderbook(self, mock_client: AsyncMock) -> None:
        result = await pm_orderbook(token_id="tok_abc123")
        assert "BID:" in result
        assert "ASK:" in result

    @pytest.mark.asyncio
    async def test_pm_price(self, mock_client: AsyncMock) -> None:
        result = await pm_price(token_id="tok_abc123")
        assert "0.62" in result

    @pytest.mark.asyncio
    async def test_pm_prices_batch(self, mock_client: AsyncMock) -> None:
        result = await pm_prices_batch(token_ids="tok_abc123,tok_def456")
        assert "tok_abc123" in result
        assert "tok_def456" in result

    @pytest.mark.asyncio
    async def test_pm_spread(self, mock_client: AsyncMock) -> None:
        result = await pm_spread(token_id="tok_abc123")
        assert "spread=" in result

    @pytest.mark.asyncio
    async def test_pm_price_history(self, mock_client: AsyncMock) -> None:
        result = await pm_price_history(token_id="tok_abc123")
        assert "0.45" in result

    @pytest.mark.asyncio
    async def test_pm_last_trade(self, mock_client: AsyncMock) -> None:
        result = await pm_last_trade(token_id="tok_abc123")
        assert "0.62" in result

    @pytest.mark.asyncio
    async def test_pm_tick_size(self, mock_client: AsyncMock) -> None:
        result = await pm_tick_size(token_id="tok_abc123")
        assert "0.01" in result

    @pytest.mark.asyncio
    async def test_pm_orderbooks_batch(self, mock_client: AsyncMock) -> None:
        result = await pm_orderbooks_batch(token_ids="tok_abc123")
        assert "BID:" in result

    @pytest.mark.asyncio
    async def test_pm_spreads_batch(self, mock_client: AsyncMock) -> None:
        result = await pm_spreads_batch(token_ids="tok1,tok2")
        assert "spread=" in result


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


class TestAnalytics:
    @pytest.mark.asyncio
    async def test_pm_open_interest(self, mock_client: AsyncMock) -> None:
        result = await pm_open_interest(token_ids="tok_abc123")
        assert "tok_abc123" in result

    @pytest.mark.asyncio
    async def test_pm_top_holders(self, mock_client: AsyncMock) -> None:
        result = await pm_top_holders(token_id="tok_abc123")
        assert "0x1234" in result

    @pytest.mark.asyncio
    async def test_pm_leaderboard(self, mock_client: AsyncMock) -> None:
        result = await pm_leaderboard()
        assert "profit=" in result

    @pytest.mark.asyncio
    async def test_pm_volume(self, mock_client: AsyncMock) -> None:
        result = await pm_volume(event_id="1001")
        assert "$2.5M" in result


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_api_error_formatted(self) -> None:
        client = _mock_client()
        client.list_events.side_effect = PolymarketError("API down", details="503 Service Unavailable")
        with patch("polymarket_mcp.server._get_client", return_value=client):
            result = await pm_events()
        assert "Error" in result
        assert "API down" in result
        assert "503" in result
