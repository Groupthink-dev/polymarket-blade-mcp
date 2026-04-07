"""Token-bucket rate limiter matching Polymarket's per-endpoint limits."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Endpoint groups and their documented limits (requests per 10 seconds)
# ---------------------------------------------------------------------------

ENDPOINT_LIMITS: dict[str, int] = {
    "clob_general": 9_000,
    "clob_pricing": 1_500,
    "clob_batch": 500,
    "clob_history": 1_000,
    "gamma_general": 4_000,
    "gamma_discovery": 300,
    "data_general": 1_000,
}

REFILL_INTERVAL = 10.0  # seconds


# ---------------------------------------------------------------------------
# Token bucket
# ---------------------------------------------------------------------------


@dataclass
class _Bucket:
    capacity: int
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.monotonic)

    def __post_init__(self) -> None:
        self.tokens = float(self.capacity)

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        if elapsed >= REFILL_INTERVAL:
            self.tokens = float(self.capacity)
            self.last_refill = now
        elif elapsed > 0:
            fraction = elapsed / REFILL_INTERVAL
            self.tokens = min(float(self.capacity), self.tokens + fraction * self.capacity)
            self.last_refill = now

    def try_acquire(self) -> bool:
        """Try to consume one token.  Returns ``True`` on success."""
        self._refill()
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

    def wait_time(self) -> float:
        """Seconds until the next token is available."""
        self._refill()
        if self.tokens >= 1.0:
            return 0.0
        deficit = 1.0 - self.tokens
        return (deficit / self.capacity) * REFILL_INTERVAL


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------


class RateLimiter:
    """Per-endpoint-group token-bucket rate limiter."""

    def __init__(self) -> None:
        self._buckets: dict[str, _Bucket] = {group: _Bucket(capacity=limit) for group, limit in ENDPOINT_LIMITS.items()}

    async def acquire(self, group: str) -> None:
        """Wait until a token is available for *group*, then consume it."""
        bucket = self._buckets.get(group)
        if bucket is None:
            return  # unknown group — don't rate-limit
        while not bucket.try_acquire():
            await asyncio.sleep(bucket.wait_time())

    def stats(self) -> dict[str, dict[str, float | int]]:
        """Current token counts and capacities for diagnostics."""
        result: dict[str, dict[str, float | int]] = {}
        for group, bucket in self._buckets.items():
            bucket._refill()
            result[group] = {
                "capacity": bucket.capacity,
                "available": round(bucket.tokens, 1),
            }
        return result
