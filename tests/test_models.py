"""Tests for models: config, gates, scrubbing."""

from __future__ import annotations

import pytest

from polymarket_mcp.models import (
    APIError,
    PolymarketError,
    RateLimitError,
    check_confirm_gate,
    check_write_gate,
    is_write_enabled,
    resolve_config,
    scrub_credentials,
)


class TestResolveConfig:
    def test_defaults(self) -> None:
        config = resolve_config()
        assert config.gamma_host == "https://gamma-api.polymarket.com"
        assert config.clob_host == "https://clob.polymarket.com"
        assert config.data_host == "https://data-api.polymarket.com"

    def test_custom_hosts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("POLYMARKET_GAMMA_HOST", "http://localhost:8001")
        monkeypatch.setenv("POLYMARKET_CLOB_HOST", "http://localhost:8002")
        monkeypatch.setenv("POLYMARKET_DATA_HOST", "http://localhost:8003")
        config = resolve_config()
        assert config.gamma_host == "http://localhost:8001"
        assert config.clob_host == "http://localhost:8002"
        assert config.data_host == "http://localhost:8003"

    def test_empty_env_uses_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("POLYMARKET_GAMMA_HOST", "   ")
        config = resolve_config()
        assert config.gamma_host == "https://gamma-api.polymarket.com"

    def test_config_is_frozen(self) -> None:
        config = resolve_config()
        with pytest.raises(AttributeError):
            config.gamma_host = "nope"  # type: ignore[misc]


class TestWriteGate:
    def test_disabled_by_default(self) -> None:
        assert not is_write_enabled()

    def test_enabled_when_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("POLYMARKET_WRITE_ENABLED", "true")
        assert is_write_enabled()

    def test_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("POLYMARKET_WRITE_ENABLED", "TRUE")
        assert is_write_enabled()

    def test_check_gate_blocks(self) -> None:
        result = check_write_gate()
        assert result is not None
        assert "disabled" in result.lower()

    def test_check_gate_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("POLYMARKET_WRITE_ENABLED", "true")
        assert check_write_gate() is None


class TestConfirmGate:
    def test_blocks_without_confirm(self) -> None:
        result = check_confirm_gate(False, "Place order")
        assert result is not None
        assert "Place order" in result

    def test_passes_with_confirm(self) -> None:
        assert check_confirm_gate(True, "Place order") is None


class TestScrubCredentials:
    def test_scrubs_bearer_token(self) -> None:
        text = "Authorization: Bearer sk-secret123"
        assert "sk-secret123" not in scrub_credentials(text)
        assert "****" in scrub_credentials(text)

    def test_scrubs_api_key(self) -> None:
        text = "api_key=my-secret-key"
        assert "my-secret-key" not in scrub_credentials(text)

    def test_preserves_clean_text(self) -> None:
        text = "Normal error message"
        assert scrub_credentials(text) == text


class TestExceptions:
    def test_polymarket_error(self) -> None:
        e = PolymarketError("fail", details="detail")
        assert str(e) == "fail"
        assert e.details == "detail"

    def test_api_error_status(self) -> None:
        e = APIError("not found", status_code=404)
        assert e.status_code == 404

    def test_rate_limit_error(self) -> None:
        e = RateLimitError("slow down")
        assert str(e) == "slow down"
