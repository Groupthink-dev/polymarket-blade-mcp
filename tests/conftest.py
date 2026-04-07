"""Shared fixtures for Polymarket Blade MCP tests."""

from __future__ import annotations

from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Sample API responses
# ---------------------------------------------------------------------------

SAMPLE_EVENTS: list[dict[str, Any]] = [
    {
        "id": "1001",
        "title": "Will Bitcoin hit $100K by June?",
        "active": True,
        "volume": 2_500_000,
        "liquidity": 800_000,
        "endDate": "2026-06-30T00:00:00.000Z",
        "markets": [
            {
                "id": "5001",
                "question": "Will Bitcoin hit $100K by June 2026?",
                "outcomes": ["Yes", "No"],
                "outcomePrices": [0.62, 0.38],
                "clobTokenIds": ["tok_abc123", "tok_def456"],
            }
        ],
    },
    {
        "id": "1002",
        "title": "US Presidential Election 2028",
        "active": True,
        "volume": 15_000_000,
        "liquidity": 3_000_000,
        "endDate": "2028-11-05T00:00:00.000Z",
        "markets": [],
    },
]

SAMPLE_EVENT: dict[str, Any] = SAMPLE_EVENTS[0]

SAMPLE_MARKETS: list[dict[str, Any]] = [
    {
        "id": "5001",
        "question": "Will Bitcoin hit $100K by June 2026?",
        "outcomes": ["Yes", "No"],
        "outcomePrices": [0.62, 0.38],
        "volume": 2_500_000,
        "liquidity": 800_000,
        "clobTokenIds": ["tok_abc123", "tok_def456"],
    },
]

SAMPLE_MARKET: dict[str, Any] = SAMPLE_MARKETS[0]

SAMPLE_ORDERBOOK: dict[str, Any] = {
    "asset_id": "tok_abc123",
    "bids": [
        {"price": 0.62, "size": 5000},
        {"price": 0.61, "size": 3000},
        {"price": 0.60, "size": 1500},
    ],
    "asks": [
        {"price": 0.63, "size": 4000},
        {"price": 0.64, "size": 2500},
        {"price": 0.65, "size": 1000},
    ],
}

SAMPLE_PRICE: dict[str, Any] = {"price": 0.62, "token_id": "tok_abc123"}

SAMPLE_PRICES_BATCH: list[dict[str, Any]] = [
    {"token_id": "tok_abc123", "price": 0.62},
    {"token_id": "tok_def456", "price": 0.38},
]

SAMPLE_SPREAD: dict[str, Any] = {"spread": 0.01, "bid": 0.62, "ask": 0.63}

SAMPLE_PRICE_HISTORY: list[dict[str, Any]] = [
    {"t": 1712000000, "p": 0.45},
    {"t": 1712086400, "p": 0.52},
    {"t": 1712172800, "p": 0.58},
]

SAMPLE_LAST_TRADE: dict[str, Any] = {"price": 0.625, "token_id": "tok_abc123"}

SAMPLE_TICK_SIZE: dict[str, Any] = {"minimum_tick_size": 0.01}

SAMPLE_TAGS: list[dict[str, Any]] = [
    {"id": 1, "label": "Politics", "slug": "politics"},
    {"id": 2, "label": "Crypto", "slug": "crypto"},
    {"id": 3, "label": "Sports", "slug": "sports"},
]

SAMPLE_SPORTS: list[dict[str, Any]] = [
    {"name": "NFL", "slug": "nfl"},
    {"name": "NBA", "slug": "nba"},
]

SAMPLE_SEARCH: list[dict[str, Any]] = [
    {"id": "1001", "title": "Will Bitcoin hit $100K by June?", "slug": "bitcoin-100k-june"},
]

SAMPLE_OPEN_INTEREST: list[dict[str, Any]] = [
    {"token_id": "tok_abc123", "open_interest": 150000},
]

SAMPLE_TOP_HOLDERS: list[dict[str, Any]] = [
    {"address": "0x1234567890abcdef1234567890abcdef12345678", "position": 50000},
    {"address": "0xabcdef1234567890abcdef1234567890abcdef12", "position": 30000},
]

SAMPLE_LEADERBOARD: list[dict[str, Any]] = [
    {
        "rank": 1,
        "address": "0x1111111111111111111111111111111111111111",
        "profit": 500000,
        "volume": 2000000,
        "totalMarkets": 150,
    },
    {
        "rank": 2,
        "address": "0x2222222222222222222222222222222222222222",
        "profit": 350000,
        "volume": 1500000,
        "totalMarkets": 100,
    },
]

SAMPLE_VOLUME: dict[str, Any] = {"volume": 2_500_000}

SAMPLE_STATUS: dict[str, Any] = {
    "clob": "OK",
    "rate_limits": {
        "clob_general": {"capacity": 9000, "available": 9000.0},
        "gamma_discovery": {"capacity": 300, "available": 300.0},
    },
}


@pytest.fixture(autouse=True)
def _clean_client() -> None:  # type: ignore[misc]
    """Reset singleton client between tests."""
    import polymarket_mcp.server as srv

    srv._client = None
