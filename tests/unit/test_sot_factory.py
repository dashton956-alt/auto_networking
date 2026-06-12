"""Tests for the SoT adapter factory."""

import pytest

from anif_platform.exceptions import SoTAdapterError


def test_factory_raises_on_unknown_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOT_BACKEND", "unknown")
    from anif_platform.sot import get_sot_adapter

    with pytest.raises(SoTAdapterError, match="Unknown SOT_BACKEND"):
        get_sot_adapter()


def test_factory_raises_on_missing_nautobot_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOT_BACKEND", "nautobot")
    monkeypatch.delenv("NAUTOBOT_URL", raising=False)
    monkeypatch.delenv("NAUTOBOT_TOKEN", raising=False)
    from anif_platform.sot import get_sot_adapter

    with pytest.raises(SoTAdapterError, match="NAUTOBOT_URL"):
        get_sot_adapter()


def test_factory_returns_nautobot_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOT_BACKEND", "nautobot")
    monkeypatch.setenv("NAUTOBOT_URL", "http://nautobot.test")
    monkeypatch.setenv("NAUTOBOT_TOKEN", "test-token")
    from anif_platform.sot import get_sot_adapter
    from anif_platform.sot.nautobot import NautobotAdapter

    adapter = get_sot_adapter()
    assert isinstance(adapter, NautobotAdapter)
