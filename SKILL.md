---
name: polymarket-blade-mcp
description: Polymarket prediction market data — events, markets, orderbooks, prices, analytics
version: "0.1.0"
permissions:
  read:
    - pm_status
    - pm_events
    - pm_event
    - pm_markets
    - pm_market
    - pm_search
    - pm_categories
    - pm_trending
    - pm_sports
    - pm_orderbook
    - pm_price
    - pm_prices_batch
    - pm_spread
    - pm_price_history
    - pm_last_trade
    - pm_tick_size
    - pm_open_interest
    - pm_top_holders
    - pm_leaderboard
    - pm_volume
    - pm_orderbooks_batch
    - pm_spreads_batch
  write: []
---

# Polymarket Blade MCP — Skill Guide

Read-only prediction market data from Polymarket. No credentials required.

## Token Efficiency Rules (MANDATORY)

1. **Start with `pm_status`** — confirms API connectivity and rate-limit headroom in one call
2. **Use `pm_prices_batch` for scans** — one call for up to 20 tokens instead of 20 separate `pm_price` calls
3. **Limit orderbook depth** — default 5 levels. Use `depth=3` for quick checks, only `depth=20+` for deep analysis
4. **Use `pm_trending` for discovery** — curated featured markets, much smaller than unfiltered `pm_events`
5. **Filter events by tag** — `pm_events(tag="politics")` instead of fetching all and filtering client-side
6. **Use fidelity on price history** — `fidelity=1440` (daily) for long-range, `fidelity=1` (minutely) only for recent
7. **Batch spreads too** — `pm_spreads_batch` for multiple tokens instead of individual `pm_spread` calls

## Quick Start

1. **Check connectivity:** `pm_status`
2. **Find markets:** `pm_search(query="US election")` or `pm_trending`
3. **Get event detail:** `pm_event(id_or_slug="us-presidential-election-2028")`
4. **Check prices:** `pm_prices_batch(token_ids="tok1,tok2,tok3")`
5. **Analyse depth:** `pm_orderbook(token_id="tok1", depth=10)`

## Tool Reference

### System (1 tool)
| Tool | Cost | Description |
|------|------|-------------|
| `pm_status` | Low | API health + rate-limit stats |

### Discovery (8 tools)
| Tool | Cost | Description |
|------|------|-------------|
| `pm_events` | Medium | List/filter events (active, tag, limit, offset) |
| `pm_event` | Low | Event detail by ID or slug |
| `pm_markets` | Medium | List/filter markets |
| `pm_market` | Low | Market detail by ID or slug |
| `pm_search` | Medium | Keyword search across events + markets |
| `pm_categories` | Low | List tags/categories |
| `pm_trending` | Low | Featured/sampling markets |
| `pm_sports` | Low | Sports categories |

### Pricing (7 tools)
| Tool | Cost | Description |
|------|------|-------------|
| `pm_orderbook` | Medium | Order book with configurable depth |
| `pm_price` | Low | Best price for a token |
| `pm_prices_batch` | Medium | Batch prices for up to 20 tokens |
| `pm_spread` | Low | Bid-ask spread |
| `pm_price_history` | Medium | Historical prices with fidelity control |
| `pm_last_trade` | Low | Last trade price |
| `pm_tick_size` | Low | Minimum tick size |

### Analytics (4 tools)
| Tool | Cost | Description |
|------|------|-------------|
| `pm_open_interest` | Low | Open interest for tokens |
| `pm_top_holders` | Low | Top holders for a market |
| `pm_leaderboard` | Low | Trader rankings by profit |
| `pm_volume` | Low | Live event volume |

### Batch (2 tools)
| Tool | Cost | Description |
|------|------|-------------|
| `pm_orderbooks_batch` | Medium | Batch orderbooks for up to 10 tokens |
| `pm_spreads_batch` | Medium | Batch spreads for up to 20 tokens |

## Workflow Examples

### Market Research
```
pm_search(query="Bitcoin price")
pm_event(id_or_slug="<event_id>")
pm_orderbook(token_id="<token_id>", depth=10)
pm_price_history(token_id="<token_id>", fidelity=60)
```

### Odds Scanning
```
pm_trending
pm_prices_batch(token_ids="tok1,tok2,tok3,...,tok20")
pm_spreads_batch(token_ids="tok1,tok2,tok3,...,tok20")
```

### Closing-Soon Monitoring
```
pm_events(active=True, order="endDate", limit=10)
pm_prices_batch(token_ids="<tokens from events>")
```

## Output Format

All tools return pipe-delimited text, one entity per line:
```
id | title | active | markets=2 | vol=$2.5M | liq=$800.0K | end=2026-06-30
```

Orderbooks use indented bid/ask lines:
```
token=tok_abc123
  BID: 0.62@$5.0K | 0.61@$3.0K | 0.60@$1.5K
  ASK: 0.63@$4.0K | 0.64@$2.5K | 0.65@$1.0K
```

## Security Notes

- **Read-only v1** — no trading, no wallet keys, no credentials
- **No credentials required** — all Polymarket public APIs are open
- **Rate limiting** — token-bucket per endpoint group, matching Polymarket's documented limits
- **Write gates** — infrastructure present for v2 trading (POLYMARKET_WRITE_ENABLED + confirm parameter)
