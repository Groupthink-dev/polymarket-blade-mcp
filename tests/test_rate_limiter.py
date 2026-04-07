"""Tests for token-bucket rate limiter."""

from __future__ import annotations

import time

import pytest

from polymarket_mcp.rate_limiter import ENDPOINT_LIMITS, RateLimiter, _Bucket


class TestBucket:
    def test_initial_tokens(self) -> None:
        bucket = _Bucket(capacity=100)
        assert bucket.tokens == 100.0

    def test_acquire_decrements(self) -> None:
        bucket = _Bucket(capacity=100)
        assert bucket.try_acquire()
        assert bucket.tokens == 99.0

    def test_acquire_fails_when_empty(self) -> None:
        bucket = _Bucket(capacity=1)
        assert bucket.try_acquire()
        assert not bucket.try_acquire()

    def test_wait_time_zero_when_available(self) -> None:
        bucket = _Bucket(capacity=100)
        assert bucket.wait_time() == 0.0

    def test_wait_time_positive_when_empty(self) -> None:
        bucket = _Bucket(capacity=1)
        bucket.try_acquire()
        wt = bucket.wait_time()
        assert wt > 0.0
        assert wt <= 10.0

    def test_refill_restores_tokens(self) -> None:
        bucket = _Bucket(capacity=100)
        bucket.tokens = 0.0
        bucket.last_refill = time.monotonic() - 15.0  # 15s ago
        bucket._refill()
        assert bucket.tokens == 100.0


class TestRateLimiter:
    def test_all_groups_initialised(self) -> None:
        limiter = RateLimiter()
        for group in ENDPOINT_LIMITS:
            assert group in limiter._buckets

    def test_stats_returns_all_groups(self) -> None:
        limiter = RateLimiter()
        stats = limiter.stats()
        assert "clob_general" in stats
        assert "gamma_discovery" in stats
        assert stats["clob_general"]["capacity"] == 9000

    @pytest.mark.asyncio
    async def test_acquire_unknown_group_passes(self) -> None:
        limiter = RateLimiter()
        await limiter.acquire("nonexistent_group")  # Should not raise

    @pytest.mark.asyncio
    async def test_acquire_consumes_token(self) -> None:
        limiter = RateLimiter()
        initial = limiter._buckets["clob_general"].tokens
        await limiter.acquire("clob_general")
        assert limiter._buckets["clob_general"].tokens < initial
