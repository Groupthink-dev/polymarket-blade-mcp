"""Token-efficient pipe-delimited formatters for Polymarket API responses."""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _pct(val: float | None) -> str:
    """Format as percentage: 0.65 → 65.0%"""
    if val is None:
        return "-"
    return f"{val * 100:.1f}%" if val <= 1.0 else f"{val:.1f}%"


def _usd(val: float | int | str | None) -> str:
    """Compact dollar formatting: 1234567 → $1.2M, 45000 → $45.0K"""
    if val is None:
        return "-"
    n = float(val)
    if n >= 1_000_000:
        return f"${n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"${n / 1_000:.1f}K"
    return f"${n:.2f}"


def _price(val: float | str | None) -> str:
    """Format price to 2 decimal places."""
    if val is None:
        return "-"
    return f"{float(val):.2f}"


def _ts(iso: str | None) -> str:
    """Extract date from ISO timestamp: 2026-04-10T15:00:00.000Z → 2026-04-10"""
    if not iso:
        return "-"
    return iso[:10] if len(iso) >= 10 else iso


def _trunc(text: str | None, max_len: int = 80) -> str:
    """Truncate long strings for display."""
    if not text:
        return ""
    return text[:max_len] + "..." if len(text) > max_len else text


def _safe_get(d: Any, *keys: str, default: Any = None) -> Any:
    """Nested dict access: _safe_get(d, 'a', 'b') → d['a']['b']"""
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d


# ---------------------------------------------------------------------------
# Discovery formatters
# ---------------------------------------------------------------------------


def format_events(data: list[dict[str, Any]]) -> str:
    """Format event list — one line per event."""
    if not data:
        return "(no events)"
    lines = ["id | title | active | markets | volume | liquidity | end"]
    for ev in data:
        markets = ev.get("markets", [])
        parts = [
            str(ev.get("id", "-")),
            _trunc(ev.get("title", "-"), 60),
            "active" if ev.get("active") else "closed",
            f"markets={len(markets)}",
        ]
        vol = ev.get("volume")
        if vol:
            parts.append(f"vol={_usd(vol)}")
        liq = ev.get("liquidity")
        if liq:
            parts.append(f"liq={_usd(liq)}")
        end = ev.get("endDate") or ev.get("end_date_iso")
        if end:
            parts.append(f"end={_ts(end)}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def format_event(data: dict[str, Any]) -> str:
    """Format single event detail."""
    lines = []
    lines.append(f"id={data.get('id')} | {data.get('title', '-')}")
    desc = data.get("description")
    if desc:
        lines.append(f"  description: {_trunc(desc, 200)}")

    for market in data.get("markets", []):
        outcomes = market.get("outcomes", [])
        outcome_str = ", ".join(outcomes) if outcomes else "-"
        parts = [f"  market={market.get('id', '-')}", _trunc(market.get("question", "-"), 60)]
        tokens = market.get("clobTokenIds", [])
        if tokens:
            parts.append(f"tokens={','.join(tokens[:2])}")
        outc_prices = market.get("outcomePrices")
        if outc_prices and isinstance(outc_prices, list):
            price_strs = [_price(p) for p in outc_prices[:4]]
            parts.append(f"prices=[{','.join(price_strs)}]")
        parts.append(f"outcomes=[{outcome_str}]")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def format_markets(data: list[dict[str, Any]]) -> str:
    """Format market list — one line per market."""
    if not data:
        return "(no markets)"
    lines = ["id | question | outcomes | prices | volume | liquidity"]
    for m in data:
        outcomes = m.get("outcomes", [])
        parts = [
            str(m.get("id", "-")),
            _trunc(m.get("question", "-"), 60),
        ]
        if outcomes:
            parts.append(f"outcomes=[{','.join(str(o) for o in outcomes[:4])}]")
        outc_prices = m.get("outcomePrices")
        if outc_prices and isinstance(outc_prices, list):
            price_strs = [_price(p) for p in outc_prices[:4]]
            parts.append(f"prices=[{','.join(price_strs)}]")
        vol = m.get("volume")
        if vol:
            parts.append(f"vol={_usd(vol)}")
        liq = m.get("liquidity")
        if liq:
            parts.append(f"liq={_usd(liq)}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def format_market(data: dict[str, Any]) -> str:
    """Format single market detail."""
    lines = []
    parts = [f"id={data.get('id', '-')}", _trunc(data.get("question", "-"), 80)]
    outcomes = data.get("outcomes", [])
    if outcomes:
        parts.append(f"outcomes=[{','.join(str(o) for o in outcomes[:4])}]")
    outc_prices = data.get("outcomePrices")
    if outc_prices and isinstance(outc_prices, list):
        price_strs = [_price(p) for p in outc_prices[:4]]
        parts.append(f"prices=[{','.join(price_strs)}]")
    lines.append(" | ".join(parts))

    for field in ("volume", "liquidity", "startDate", "endDate", "description"):
        val = data.get(field)
        if val:
            if field in ("volume", "liquidity"):
                lines.append(f"  {field}={_usd(val)}")
            elif field in ("startDate", "endDate"):
                lines.append(f"  {field}={_ts(val)}")
            else:
                lines.append(f"  {field}: {_trunc(str(val), 200)}")

    tokens = data.get("clobTokenIds", [])
    if tokens:
        lines.append(f"  clobTokenIds=[{','.join(tokens)}]")
    return "\n".join(lines)


def format_search(data: list[dict[str, Any]] | dict[str, Any]) -> str:
    """Format search results."""
    items = data if isinstance(data, list) else data.get("data", data.get("results", [data]))
    if not items:
        return "(no results)"
    lines = []
    for item in items:
        title = item.get("title") or item.get("question") or item.get("name") or "-"
        parts = [_trunc(title, 60)]
        if item.get("id"):
            parts.insert(0, str(item["id"]))
        if item.get("slug"):
            parts.append(f"slug={item['slug']}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def format_tags(data: list[dict[str, Any]]) -> str:
    """Format tag/category list."""
    if not data:
        return "(no tags)"
    lines = ["id | label | slug"]
    for tag in data:
        lines.append(f"{tag.get('id', '-')} | {tag.get('label', '-')} | {tag.get('slug', '-')}")
    return "\n".join(lines)


def format_sports(data: list[dict[str, Any]]) -> str:
    """Format sports list."""
    if not data:
        return "(no sports)"
    lines = []
    for sport in data:
        lines.append(f"{sport.get('name', '-')} | slug={sport.get('slug', '-')}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Pricing formatters
# ---------------------------------------------------------------------------


def format_orderbook(data: dict[str, Any], depth: int = 5) -> str:
    """Format order book with configurable depth."""
    lines = []
    token_id = data.get("asset_id") or data.get("market") or "-"
    lines.append(f"token={token_id}")

    bids = data.get("bids", [])[:depth]
    asks = data.get("asks", [])[:depth]

    if bids:
        bid_strs = [f"{_price(b.get('price'))}@{_usd(b.get('size'))}" for b in bids]
        lines.append(f"  BID: {' | '.join(bid_strs)}")
    else:
        lines.append("  BID: (empty)")

    if asks:
        ask_strs = [f"{_price(a.get('price'))}@{_usd(a.get('size'))}" for a in asks]
        lines.append(f"  ASK: {' | '.join(ask_strs)}")
    else:
        lines.append("  ASK: (empty)")

    return "\n".join(lines)


def format_price(data: dict[str, Any]) -> str:
    """Format single price response."""
    return f"price={_price(data.get('price'))} | token={data.get('token_id', '-')}"


def format_prices_batch(data: list[dict[str, Any]]) -> str:
    """Format batch prices — one line per token."""
    if not data:
        return "(no prices)"
    lines = []
    for item in data:
        token = item.get("token_id") or item.get("asset_id") or "-"
        lines.append(f"{token} | {_price(item.get('price'))}")
    return "\n".join(lines)


def format_spread(data: dict[str, Any]) -> str:
    """Format bid-ask spread."""
    return f"spread={_price(data.get('spread'))} | bid={_price(data.get('bid'))} | ask={_price(data.get('ask'))}"


def format_price_history(data: list[dict[str, Any]]) -> str:
    """Format historical prices — compact date|price pairs."""
    if not data:
        return "(no history)"
    lines = ["timestamp | price"]
    for point in data:
        ts = point.get("t") or point.get("timestamp") or "-"
        price = point.get("p") or point.get("price")
        lines.append(f"{ts} | {_price(price)}")
    return "\n".join(lines)


def format_last_trade(data: dict[str, Any]) -> str:
    """Format last trade price."""
    return f"last_trade={_price(data.get('price'))} | token={data.get('token_id', '-')}"


def format_tick_size(data: dict[str, Any]) -> str:
    """Format tick size."""
    return f"tick_size={data.get('minimum_tick_size', '-')}"


def format_orderbooks_batch(data: list[dict[str, Any]], depth: int = 5) -> str:
    """Format batch orderbooks."""
    if not data:
        return "(no orderbooks)"
    return "\n---\n".join(format_orderbook(book, depth) for book in data)


def format_spreads_batch(data: list[dict[str, Any]]) -> str:
    """Format batch spreads — one line per token."""
    if not data:
        return "(no spreads)"
    lines = []
    for item in data:
        token = item.get("token_id") or item.get("asset_id") or "-"
        sp, bid, ask = _price(item.get("spread")), _price(item.get("bid")), _price(item.get("ask"))
        lines.append(f"{token} | spread={sp} | bid={bid} | ask={ask}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Analytics formatters
# ---------------------------------------------------------------------------


def format_open_interest(data: Any) -> str:
    """Format open interest."""
    if isinstance(data, list):
        lines = []
        for item in data:
            token = item.get("token_id") or item.get("asset_id") or "-"
            lines.append(f"{token} | oi={_usd(item.get('open_interest'))}")
        return "\n".join(lines) if lines else "(no data)"
    return f"open_interest={_usd(data.get('open_interest') if isinstance(data, dict) else data)}"


def format_top_holders(data: list[dict[str, Any]]) -> str:
    """Format top holders."""
    if not data:
        return "(no holders)"
    lines = ["rank | address | position"]
    for i, holder in enumerate(data, 1):
        addr = holder.get("address", "-")
        short_addr = f"{addr[:6]}...{addr[-4:]}" if len(addr) > 12 else addr
        pos = holder.get("position") or holder.get("amount")
        lines.append(f"{i} | {short_addr} | {_usd(pos)}")
    return "\n".join(lines)


def format_leaderboard(data: list[dict[str, Any]] | dict[str, Any]) -> str:
    """Format trader leaderboard."""
    items = data if isinstance(data, list) else data.get("data", data.get("leaderboard", []))
    if not items:
        return "(no leaderboard data)"
    lines = ["rank | address | profit | volume | markets"]
    for item in items:
        addr = item.get("address", "-")
        short_addr = f"{addr[:6]}...{addr[-4:]}" if len(addr) > 12 else addr
        parts = [
            str(item.get("rank", "-")),
            short_addr,
        ]
        profit = item.get("profit") or item.get("pnl")
        if profit is not None:
            parts.append(f"profit={_usd(profit)}")
        vol = item.get("volume")
        if vol is not None:
            parts.append(f"vol={_usd(vol)}")
        markets = item.get("totalMarkets") or item.get("markets_traded")
        if markets is not None:
            parts.append(f"markets={markets}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def format_volume(data: Any) -> str:
    """Format volume response."""
    if isinstance(data, dict):
        return f"volume={_usd(data.get('volume'))}"
    return f"volume={_usd(data)}"


def format_status(data: dict[str, Any]) -> str:
    """Format system status."""
    lines = ["Polymarket Blade MCP — read-only v1"]
    clob = data.get("clob")
    if clob:
        lines.append(f"  CLOB: {clob}")

    rates = data.get("rate_limits", {})
    if rates:
        lines.append("  Rate limits:")
        for group, info in rates.items():
            lines.append(f"    {group}: {info.get('available', '?')}/{info.get('capacity', '?')}")
    return "\n".join(lines)
