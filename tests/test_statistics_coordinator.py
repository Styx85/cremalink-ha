"""Tests for the Cremalink statistics coordinator."""

import asyncio
from datetime import timedelta

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.cremalink_ha import statistics_coordinator as module
from custom_components.cremalink_ha.statistics_coordinator import (
    CremalinkStatisticsCoordinator,
    STATISTICS_UPDATE_INTERVAL,
)


class FakeHass:
    """Minimal Home Assistant executor stub."""

    async def async_add_executor_job(self, func, *args):
        return func(*args)


def test_statistics_poll_interval_is_slow():
    """Statistics must not use the fast monitor polling interval."""
    assert STATISTICS_UPDATE_INTERVAL == timedelta(minutes=10)


def test_statistics_coordinator_fetches_snapshot(monkeypatch):
    """Coordinator should expose the snapshot returned by the core library."""

    snapshot = {
        "known": {
            "total_beverages": 123,
            "descale_count": 4,
        },
        "unknown": {
            43000: 17,
        },
        "raw": {
            105: 4,
            43000: 17,
            43010: 123,
        },
    }

    calls = {}

    class FakeClient:
        def __init__(self, token_file):
            calls["token_file"] = token_file

        def get_ecam610_statistics(self, dsn):
            calls["dsn"] = dsn
            return snapshot

    monkeypatch.setattr(module, "Client", FakeClient)

    coordinator = CremalinkStatisticsCoordinator(
        FakeHass(),
        dsn="test-dsn",
        token_file="/tmp/test-token.json",
    )

    result = asyncio.run(coordinator._async_update_data())

    assert result == snapshot
    assert calls == {
        "token_file": "/tmp/test-token.json",
        "dsn": "test-dsn",
    }


def test_statistics_coordinator_wraps_client_failure(monkeypatch):
    """Core/cloud errors should become Home Assistant UpdateFailed errors."""

    class FakeClient:
        def __init__(self, _token_file):
            pass

        def get_ecam610_statistics(self, _dsn):
            raise RuntimeError("synthetic cloud failure")

    monkeypatch.setattr(module, "Client", FakeClient)

    coordinator = CremalinkStatisticsCoordinator(
        FakeHass(),
        dsn="test-dsn",
        token_file="/tmp/test-token.json",
    )

    with pytest.raises(
        UpdateFailed,
        match="synthetic cloud failure",
    ):
        asyncio.run(coordinator._async_update_data())


def test_statistics_coordinator_retains_snapshot_on_a2_timeout(monkeypatch):
    """A transient A2 timeout must keep the last successful snapshot."""

    previous = {
        "known": {
            "total_beverages": 123,
        },
        "unknown": {},
        "raw": {
            43010: 123,
        },
    }

    class FakeClient:
        def __init__(self, _token_file):
            pass

        def get_ecam610_statistics(self, _dsn):
            raise TimeoutError(
                "No A2 statistics response for start_id=3001 within 20s"
            )

    monkeypatch.setattr(module, "Client", FakeClient)

    coordinator = CremalinkStatisticsCoordinator(
        FakeHass(),
        dsn="test-dsn",
        token_file="/tmp/test-token.json",
    )
    coordinator.data = previous

    result = asyncio.run(coordinator._async_update_data())

    assert result is previous
def test_statistics_snapshot_timestamp_changes_only_on_success(monkeypatch):
    """Only a successful A2 read may advance the snapshot timestamp."""

    snapshots = [
        {
            "known": {"total_beverages": 123},
            "unknown": {},
            "raw": {43010: 123},
        },
    ]

    class FakeClient:
        def __init__(self, _token_file):
            pass

        def get_ecam610_statistics(self, _dsn):
            if snapshots:
                return snapshots.pop(0)

            raise TimeoutError("synthetic transient A2 timeout")

    times = iter(
        [
            "2026-08-25T07:00:00+00:00",
            "2026-08-25T07:01:00+00:00",
        ]
    )

    monkeypatch.setattr(module, "Client", FakeClient)
    monkeypatch.setattr(
        module,
        "_snapshot_timestamp",
        lambda: next(times),
        raising=False,
    )

    coordinator = CremalinkStatisticsCoordinator(
        FakeHass(),
        dsn="test-dsn",
        token_file="/tmp/test-token.json",
    )

    first = asyncio.run(coordinator._async_update_data())
    coordinator.data = first

    assert first["snapshot_fetched_at"] == "2026-08-25T07:00:00+00:00"

    second = asyncio.run(coordinator._async_update_data())

    assert second is first
    assert second["snapshot_fetched_at"] == "2026-08-25T07:00:00+00:00"
