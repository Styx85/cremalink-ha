"""Tests for the normal Cremalink monitor coordinator."""

import asyncio
from types import SimpleNamespace

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.cremalink_ha import coordinator as module


class FakeHass:
    """Minimal executor stub."""

    async def async_add_executor_job(self, func, *args):
        return func(*args)


class FakeDevice:
    """Return queued monitor results or exceptions."""

    def __init__(self, results):
        self.results = iter(results)

    def get_monitor(self):
        result = next(self.results)

        if isinstance(result, Exception):
            raise result

        return result


def monitor(status):
    """Build a synthetic monitor result."""
    return SimpleNamespace(
        parsed={"status": status},
    )


def test_monitor_single_transient_failure_retains_last_snapshot():
    """One failed poll must not make normal entities unavailable."""

    good = monitor(1)

    coordinator = module.CremalinkCoordinator(
        FakeHass(),
        FakeDevice(
            [
                good,
                ValueError("synthetic malformed monitor frame"),
            ]
        ),
    )

    first = asyncio.run(coordinator._async_update_data())
    coordinator.data = first

    second = asyncio.run(coordinator._async_update_data())

    assert second is good
    assert coordinator.monitor_consecutive_failures == 1


def test_monitor_success_resets_failure_counter():
    """A successful monitor poll must end the transient-failure streak."""

    first_good = monitor(1)
    second_good = monitor(1)

    coordinator = module.CremalinkCoordinator(
        FakeHass(),
        FakeDevice(
            [
                first_good,
                ValueError("synthetic transient failure"),
                second_good,
            ]
        ),
    )

    coordinator.data = asyncio.run(
        coordinator._async_update_data()
    )

    coordinator.data = asyncio.run(
        coordinator._async_update_data()
    )
    assert coordinator.monitor_consecutive_failures == 1

    result = asyncio.run(coordinator._async_update_data())

    assert result is second_good
    assert coordinator.monitor_consecutive_failures == 0


def test_monitor_becomes_unavailable_after_sustained_failures():
    """A real sustained disconnect must eventually raise UpdateFailed."""

    good = monitor(1)

    coordinator = module.CremalinkCoordinator(
        FakeHass(),
        FakeDevice(
            [
                good,
                RuntimeError("synthetic failure 1"),
                RuntimeError("synthetic failure 2"),
                RuntimeError("synthetic failure 3"),
            ]
        ),
    )

    coordinator.data = asyncio.run(
        coordinator._async_update_data()
    )

    # Two transient failures are retained.
    coordinator.data = asyncio.run(
        coordinator._async_update_data()
    )
    coordinator.data = asyncio.run(
        coordinator._async_update_data()
    )

    with pytest.raises(
        UpdateFailed,
        match="synthetic failure 3",
    ):
        asyncio.run(coordinator._async_update_data())

    assert coordinator.monitor_consecutive_failures == 3


def test_monitor_initial_failure_is_not_hidden():
    """Without any known-good snapshot an error must fail immediately."""

    coordinator = module.CremalinkCoordinator(
        FakeHass(),
        FakeDevice(
            [RuntimeError("synthetic initial failure")]
        ),
    )

    with pytest.raises(
        UpdateFailed,
        match="synthetic initial failure",
    ):
        asyncio.run(coordinator._async_update_data())
