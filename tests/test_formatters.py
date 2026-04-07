"""Tests for pipe-delimited formatters."""

from __future__ import annotations

from polymarket_mcp.formatters import (
    _pct,
    _price,
    _trunc,
    _ts,
    _usd,
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

# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_pct_normal(self) -> None:
        assert _pct(0.65) == "65.0%"

    def test_pct_none(self) -> None:
        assert _pct(None) == "-"

    def test_usd_millions(self) -> None:
        assert _usd(2_500_000) == "$2.5M"

    def test_usd_thousands(self) -> None:
        assert _usd(45_000) == "$45.0K"

    def test_usd_small(self) -> None:
        assert _usd(42.5) == "$42.50"

    def test_usd_none(self) -> None:
        assert _usd(None) == "-"

    def test_price_normal(self) -> None:
        assert _price(0.625) == "0.62"

    def test_price_none(self) -> None:
        assert _price(None) == "-"

    def test_ts_iso(self) -> None:
        assert _ts("2026-04-10T15:00:00.000Z") == "2026-04-10"

    def test_ts_none(self) -> None:
        assert _ts(None) == "-"

    def test_trunc_short(self) -> None:
        assert _trunc("hello", 10) == "hello"

    def test_trunc_long(self) -> None:
        assert _trunc("a" * 100, 10) == "a" * 10 + "..."

    def test_trunc_none(self) -> None:
        assert _trunc(None) == ""


# ---------------------------------------------------------------------------
# Discovery formatter tests
# ---------------------------------------------------------------------------


class TestDiscoveryFormatters:
    def test_format_events(self) -> None:
        result = format_events(SAMPLE_EVENTS)
        assert "Bitcoin" in result
        assert "vol=$2.5M" in result
        assert "markets=1" in result

    def test_format_events_empty(self) -> None:
        assert format_events([]) == "(no events)"

    def test_format_event(self) -> None:
        result = format_event(SAMPLE_EVENT)
        assert "id=1001" in result
        assert "market=5001" in result
        assert "prices=" in result

    def test_format_markets(self) -> None:
        result = format_markets(SAMPLE_MARKETS)
        assert "Bitcoin" in result
        assert "vol=$2.5M" in result

    def test_format_markets_empty(self) -> None:
        assert format_markets([]) == "(no markets)"

    def test_format_market(self) -> None:
        result = format_market(SAMPLE_MARKET)
        assert "id=5001" in result
        assert "outcomes=" in result
        assert "clobTokenIds=" in result

    def test_format_search(self) -> None:
        result = format_search(SAMPLE_SEARCH)
        assert "Bitcoin" in result

    def test_format_search_empty(self) -> None:
        assert format_search([]) == "(no results)"

    def test_format_tags(self) -> None:
        result = format_tags(SAMPLE_TAGS)
        assert "Politics" in result
        assert "Crypto" in result

    def test_format_tags_empty(self) -> None:
        assert format_tags([]) == "(no tags)"

    def test_format_sports(self) -> None:
        result = format_sports(SAMPLE_SPORTS)
        assert "NFL" in result
        assert "NBA" in result

    def test_format_sports_empty(self) -> None:
        assert format_sports([]) == "(no sports)"


# ---------------------------------------------------------------------------
# Pricing formatter tests
# ---------------------------------------------------------------------------


class TestPricingFormatters:
    def test_format_orderbook(self) -> None:
        result = format_orderbook(SAMPLE_ORDERBOOK, depth=3)
        assert "BID:" in result
        assert "ASK:" in result
        assert "0.62" in result
        assert "0.63" in result

    def test_format_orderbook_empty_bids(self) -> None:
        data = {"asset_id": "tok", "bids": [], "asks": []}
        result = format_orderbook(data)
        assert "(empty)" in result

    def test_format_orderbook_depth_limit(self) -> None:
        result = format_orderbook(SAMPLE_ORDERBOOK, depth=1)
        lines = result.strip().split("\n")
        bid_line = [line for line in lines if "BID:" in line][0]
        # Should only have 1 price level
        assert bid_line.count("@") == 1

    def test_format_price(self) -> None:
        result = format_price(SAMPLE_PRICE)
        assert "price=0.62" in result
        assert "tok_abc123" in result

    def test_format_prices_batch(self) -> None:
        result = format_prices_batch(SAMPLE_PRICES_BATCH)
        assert "tok_abc123" in result
        assert "tok_def456" in result
        assert "0.62" in result
        assert "0.38" in result

    def test_format_prices_batch_empty(self) -> None:
        assert format_prices_batch([]) == "(no prices)"

    def test_format_spread(self) -> None:
        result = format_spread(SAMPLE_SPREAD)
        assert "spread=0.01" in result
        assert "bid=0.62" in result
        assert "ask=0.63" in result

    def test_format_price_history(self) -> None:
        result = format_price_history(SAMPLE_PRICE_HISTORY)
        assert "0.45" in result
        assert "0.52" in result
        assert "timestamp | price" in result

    def test_format_price_history_empty(self) -> None:
        assert format_price_history([]) == "(no history)"

    def test_format_last_trade(self) -> None:
        result = format_last_trade(SAMPLE_LAST_TRADE)
        assert "0.62" in result
        assert "tok_abc123" in result

    def test_format_tick_size(self) -> None:
        result = format_tick_size(SAMPLE_TICK_SIZE)
        assert "0.01" in result

    def test_format_orderbooks_batch(self) -> None:
        result = format_orderbooks_batch([SAMPLE_ORDERBOOK, SAMPLE_ORDERBOOK])
        assert result.count("BID:") == 2
        assert "---" in result

    def test_format_orderbooks_batch_empty(self) -> None:
        assert format_orderbooks_batch([]) == "(no orderbooks)"

    def test_format_spreads_batch(self) -> None:
        data = [
            {"token_id": "tok1", "spread": 0.01, "bid": 0.62, "ask": 0.63},
            {"token_id": "tok2", "spread": 0.02, "bid": 0.70, "ask": 0.72},
        ]
        result = format_spreads_batch(data)
        assert "tok1" in result
        assert "tok2" in result

    def test_format_spreads_batch_empty(self) -> None:
        assert format_spreads_batch([]) == "(no spreads)"


# ---------------------------------------------------------------------------
# Analytics formatter tests
# ---------------------------------------------------------------------------


class TestAnalyticsFormatters:
    def test_format_open_interest_list(self) -> None:
        result = format_open_interest(SAMPLE_OPEN_INTEREST)
        assert "tok_abc123" in result
        assert "$150.0K" in result

    def test_format_open_interest_dict(self) -> None:
        result = format_open_interest({"open_interest": 50000})
        assert "$50.0K" in result

    def test_format_top_holders(self) -> None:
        result = format_top_holders(SAMPLE_TOP_HOLDERS)
        assert "0x1234" in result
        assert "0xabcd" in result

    def test_format_top_holders_empty(self) -> None:
        assert format_top_holders([]) == "(no holders)"

    def test_format_leaderboard(self) -> None:
        result = format_leaderboard(SAMPLE_LEADERBOARD)
        assert "0x1111" in result
        assert "profit=$500.0K" in result

    def test_format_leaderboard_empty(self) -> None:
        assert format_leaderboard([]) == "(no leaderboard data)"

    def test_format_volume(self) -> None:
        result = format_volume(SAMPLE_VOLUME)
        assert "$2.5M" in result


# ---------------------------------------------------------------------------
# Status formatter tests
# ---------------------------------------------------------------------------


class TestStatusFormatter:
    def test_format_status(self) -> None:
        result = format_status(SAMPLE_STATUS)
        assert "Polymarket Blade MCP" in result
        assert "CLOB: OK" in result
        assert "clob_general" in result
