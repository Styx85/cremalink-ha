"""Tests for the temporary monitor diagnostics sensor."""

from datetime import datetime, timedelta
from types import SimpleNamespace

from custom_components.cremalink_ha.sensor import (
    CremalinkMonitorDiagnosticsSensor,
)


ENTRY = SimpleNamespace(
    title="Test Coffee Machine",
    entry_id="test-ecam610",
)


class FakeCoordinator:
    """Minimal coordinator carrying one monitor view."""

    def __init__(self, data):
        self.data = data
        self.last_update_success = True
        self.update_interval = timedelta(seconds=30)
        self.monitor_consecutive_failures = 1


def make_monitor_view():
    """Build one internally consistent fake MonitorView."""
    received_at = datetime.now()

    snapshot = SimpleNamespace(
        source="local",
        device_id="dsn-test",
        warnings=[],
        errors=[],
    )

    return SimpleNamespace(
        snapshot=snapshot,
        received_at=received_at,
        raw_b64="AAECAwQ=",
        raw=b"\x00\x01\x02\x03\x04",
        parsed={
            "status": 0,
            "action": 2,
            "progress": 100,
            "accessory": 4,
            "alarms": [1, 0, 0, 0],
            "switches": [64, 2],
        },
        status_name="in_standby",
        action_name="2",
        accessory_name="latte_crema_hot_clean",
        available_fields=[
            "is_busy",
            "is_idle",
            "is_watertank_empty",
            "is_watertank_open",
            "is_waste_container_full",
            "is_waste_container_missing",
        ],
        is_busy=True,
        is_idle=False,
        is_watertank_empty=True,
        is_watertank_open=False,
        is_waste_container_full=False,
        is_waste_container_missing=False,
    )


def test_monitor_diagnostics_exposes_same_snapshot_raw_and_derived():
    view = make_monitor_view()
    sensor = CremalinkMonitorDiagnosticsSensor(
        FakeCoordinator(view),
        ENTRY,
    )

    assert sensor.available is True
    assert sensor.native_value == view.received_at.isoformat()

    attrs = sensor.extra_state_attributes

    assert attrs["raw_b64"] == "AAECAwQ="
    assert attrs["raw_hex"] == "0001020304"
    assert attrs["status"] == 0
    assert attrs["status_name"] == "in_standby"
    assert attrs["action"] == 2
    assert attrs["accessory"] == 4
    assert attrs["alarms"] == [1, 0, 0, 0]
    assert attrs["switches"] == [64, 2]
    assert attrs["is_busy"] is True
    assert attrs["is_idle"] is False
    assert attrs["is_watertank_empty"] is True
    assert attrs["is_watertank_open"] is False
    assert attrs["coordinator_last_update_success"] is True
    assert attrs["coordinator_update_interval_seconds"] == 30.0
    assert attrs["monitor_consecutive_failures"] == 1
    assert attrs["frame_age_seconds"] is not None


def test_monitor_diagnostics_is_disabled_by_default():
    sensor = CremalinkMonitorDiagnosticsSensor(
        FakeCoordinator(make_monitor_view()),
        ENTRY,
    )

    assert sensor._attr_entity_registry_enabled_default is False


def test_monitor_diagnostics_preserves_parser_warnings_and_errors():
    view = make_monitor_view()
    view.snapshot.warnings = ["synthetic warning"]
    view.snapshot.errors = ["synthetic error"]

    sensor = CremalinkMonitorDiagnosticsSensor(
        FakeCoordinator(view),
        ENTRY,
    )

    attrs = sensor.extra_state_attributes

    assert attrs["warnings"] == ["synthetic warning"]
    assert attrs["errors"] == ["synthetic error"]
