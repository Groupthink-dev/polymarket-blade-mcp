# polymarket-blade-mcp

Polymarket prediction market data — events, markets, orderbooks, prices, analytics.

Token-efficient, rate-limited MCP server for the [Sidereal](https://sidereal.cc) platform.

## Why another Polymarket MCP?

| Feature | **polymarket-blade-mcp** | prediction-mcp | IQAIcom | caiovicentino |
|---------|-------------------------|----------------|---------|---------------|
| Tools | **22** | 12 | 19 | 45 |
| Trading | Write gates (v2) | No | Ungated | Safety limits |
| Token efficiency | Pipe-delimited, batching | Cache + scoring | Raw JSON | Text formatting |
| Rate limiting | Per-endpoint token buckets | No | No | Configurable |
| Tests | **99** | 5,767 lines | Zero | 3,688 lines |
| Type safety | mypy strict | TypeScript | TypeScript | Pydantic |
| Auth required | **None** (public APIs) | None (PM) / API key (Kalshi) | Wallet key | Wallet key |
| Sidereal marketplace | Certified | Community | N/A | N/A |
| License | MIT | MIT | MIT | MIT |

## What this MCP covers

Three Polymarket APIs, all public (no credentials):

- **Gamma API** — events, markets, tags, search, sports (discovery)
- **CLOB API** — orderbooks, prices, midpoints, spreads, price history (pricing)
- **Data API** — open interest, top holders, leaderboard, volume (analytics)

## Quick Start

### Claude Code / Claude Desktop

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "uvx",
      "args": ["polymarket-blade-mcp"]
    }
  }
}
```

### From source

```bash
git clone https://github.com/Groupthink-dev/polymarket-blade-mcp
cd polymarket-blade-mcp
make install-dev
make run
```

## Configuration

All optional — the server works with zero configuration.

| Variable | Default | Description |
|----------|---------|-------------|
| `POLYMARKET_GAMMA_HOST` | `https://gamma-api.polymarket.com` | Override Gamma API host |
| `POLYMARKET_CLOB_HOST` | `https://clob.polymarket.com` | Override CLOB API host |
| `POLYMARKET_DATA_HOST` | `https://data-api.polymarket.com` | Override Data API host |
| `POLYMARKET_MCP_TRANSPORT` | `stdio` | Transport: `stdio` or `http` |
| `POLYMARKET_MCP_HOST` | `0.0.0.0` | HTTP transport bind address |
| `POLYMARKET_MCP_PORT` | `8082` | HTTP transport port |
| `POLYMARKET_MCP_API_TOKEN` | _(none)_ | Bearer token for HTTP auth |
| `POLYMARKET_WRITE_ENABLED` | `false` | Enable write operations (v2) |

## Tool Reference

### System (1)
| Tool | Description |
|------|-------------|
| `pm_status` | API health + rate-limit stats |

### Discovery (8)
| Tool | Description |
|------|-------------|
| `pm_events` | List/filter events (active, tag, limit, offset, order) |
| `pm_event` | Event detail by ID or slug |
| `pm_markets` | List/filter markets |
| `pm_market` | Market detail by ID or slug |
| `pm_search` | Keyword search across events + markets |
| `pm_categories` | List tags/categories |
| `pm_trending` | Featured/sampling markets |
| `pm_sports` | Sports categories |

### Pricing (7)
| Tool | Description |
|------|-------------|
| `pm_orderbook` | Order book with configurable depth (default 5) |
| `pm_price` | Best price for a token (BUY/SELL side) |
| `pm_prices_batch` | Batch prices for up to 20 tokens |
| `pm_spread` | Bid-ask spread |
| `pm_price_history` | Historical prices (fidelity: 1/5/60/360/1440 min) |
| `pm_last_trade` | Last trade price |
| `pm_tick_size` | Minimum tick size (0.1/0.01/0.001/0.0001) |

### Analytics (4)
| Tool | Description |
|------|-------------|
| `pm_open_interest` | Open interest for tokens |
| `pm_top_holders` | Top holders for a market |
| `pm_leaderboard` | Trader rankings by profit |
| `pm_volume` | Live event volume |

### Batch (2)
| Tool | Description |
|------|-------------|
| `pm_orderbooks_batch` | Batch orderbooks for up to 10 tokens |
| `pm_spreads_batch` | Batch spreads for up to 20 tokens |

## Security

- **Read-only v1** — no trading, no wallet keys, no credentials required
- **No SSRF** — every endpoint is explicitly mapped. No generic pass-through tools
- **Rate limiting** — per-endpoint token buckets matching Polymarket's documented limits
- **Credential scrubbing** — sensitive values stripped from error output
- **Write gates (v2)** — `POLYMARKET_WRITE_ENABLED` env + per-call `confirm=true` parameter
- **HTTP transport auth** — optional bearer token for remote deployment

## Rate Limits

Token-bucket rate limiter per endpoint group:

| Group | Limit / 10s | Endpoints |
|-------|-------------|-----------|
| `clob_general` | 9,000 | Health, tick-size |
| `clob_pricing` | 1,500 | Book, price, midpoint, spread |
| `clob_batch` | 500 | Batch books, prices, spreads |
| `clob_history` | 1,000 | Price history |
| `gamma_general` | 4,000 | Tags, sports |
| `gamma_discovery` | 300 | Events, markets, search |
| `data_general` | 1,000 | Open interest, leaderboard, trades |

## Development

```bash
make install-dev   # Install all dependencies
make test          # Run unit tests (99 tests)
make test-cov      # Tests with coverage report
make check         # Lint + format + typecheck
```

### Tech stack

- Python 3.12+ / FastMCP / httpx / Pydantic
- uv (package manager) / ruff (lint+format) / mypy (strict types) / pytest

## License

MIT
