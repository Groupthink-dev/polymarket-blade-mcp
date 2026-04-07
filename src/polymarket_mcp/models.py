"""Configuration, enums, exceptions, and gate logic for Polymarket Blade MCP."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GAMMA_HOST_DEFAULT = "https://gamma-api.polymarket.com"
CLOB_HOST_DEFAULT = "https://clob.polymarket.com"
DATA_HOST_DEFAULT = "https://data-api.polymarket.com"


@dataclass(frozen=True)
class ProviderConfig:
    """Polymarket API host configuration.  All public — no credentials needed for v1."""

    gamma_host: str = GAMMA_HOST_DEFAULT
    clob_host: str = CLOB_HOST_DEFAULT
    data_host: str = DATA_HOST_DEFAULT


def resolve_config() -> ProviderConfig:
    """Build config from environment variables.  Never raises — all fields have defaults."""
    return ProviderConfig(
        gamma_host=os.environ.get("POLYMARKET_GAMMA_HOST", "").strip() or GAMMA_HOST_DEFAULT,
        clob_host=os.environ.get("POLYMARKET_CLOB_HOST", "").strip() or CLOB_HOST_DEFAULT,
        data_host=os.environ.get("POLYMARKET_DATA_HOST", "").strip() or DATA_HOST_DEFAULT,
    )


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class PolymarketError(Exception):
    """Base error for all Polymarket API failures."""

    def __init__(self, message: str, details: str = "") -> None:
        super().__init__(message)
        self.details = details


class APIError(PolymarketError):
    """Non-retryable API error (4xx except 429, 5xx)."""

    def __init__(self, message: str, status_code: int = 0, details: str = "") -> None:
        super().__init__(message, details)
        self.status_code = status_code


class RateLimitError(PolymarketError):
    """429 Too Many Requests."""


# ---------------------------------------------------------------------------
# Write / Confirm Gates (v2 forward-compatibility)
# ---------------------------------------------------------------------------


def is_write_enabled() -> bool:
    """Check whether write operations are enabled via environment."""
    return os.environ.get("POLYMARKET_WRITE_ENABLED", "").lower() == "true"


def check_write_gate() -> str | None:
    """Return an error message if writes are disabled, else ``None``."""
    if not is_write_enabled():
        return "Error: Write operations are disabled. Set POLYMARKET_WRITE_ENABLED=true to enable."
    return None


def check_confirm_gate(confirm: bool, action: str) -> str | None:
    """Return an error message if *confirm* is ``False``, else ``None``."""
    if not confirm:
        return f"Error: {action} involves real funds. Set confirm=true to proceed."
    return None


# ---------------------------------------------------------------------------
# Credential / URL scrubbing
# ---------------------------------------------------------------------------

_SCRUB_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(Authorization:\s*Bearer\s+)\S+", re.IGNORECASE), r"\1****"),
    (re.compile(r"(api[_-]?key=)\S+", re.IGNORECASE), r"\1****"),
    (re.compile(r"(secret=)\S+", re.IGNORECASE), r"\1****"),
]


def scrub_credentials(text: str) -> str:
    """Strip sensitive values from error messages."""
    for pattern, repl in _SCRUB_PATTERNS:
        text = pattern.sub(repl, text)
    return text
