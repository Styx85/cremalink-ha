"""Tests for ECAM610 statistics sensors."""

from types import SimpleNamespace

from custom_components.cremalink_ha.sensor import (
    CremalinkStatisticsDiagnosticsSensor,
    CremalinkStatisticsSensor,
)


class FakeCoordinator:
    """Minimal coordinator carrying a statistics snapshot."""

    def __init__(self, data):
        self.data = data
        self.last_update_success = True
        self.refresh_in_progress = False


ENTRY = SimpleNamespace(
    title="Test Coffee Machine",
    entry_id="test-ecam610",
)


SNAPSHOT = {
    "known": {
        "total_beverages": 1234,
        "total_black_beverages": 234,
        "total_milk_beverages": 1000,
        "total_water_l": 321.5,
        "descale_count": 7,
        "filter_replacements": 4,
        "grounds_container_clean_count": 456,
    },
    "unknown": {
        43000: 111,
        43005: 222,
        43014: 333,
    },
    "raw": {
        105: 7,
        106: 643000,
        108: 4,
        115: 456,
        3000: 234,
        43000: 111,
        43005: 222,
        43010: 1234,
        43014: 333,
    },
    "snapshot_fetched_at": "2026-08-25T07:00:00+00:00",
}


def make_sensor(key, name="Test", unit=None):
    return CremalinkStatisticsSensor(
        FakeCoordinator(SNAPSHOT),
        ENTRY,
        key,
        name,
        "mdi:counter",
        unit,
    )


def test_total_beverages():
    sensor = make_sensor("total_beverages")

    assert sensor.available is True
    assert sensor.native_value == 1234
    assert sensor._attr_unique_id == (
        "test-ecam610_statistics_total_beverages"
    )


def test_total_milk_beverages():
    sensor = make_sensor("total_milk_beverages")

    assert sensor.available is True
    assert sensor.native_value == 1000


def test_total_water():
    sensor = make_sensor(
        "total_water_l",
        name="Total water",
        unit="L",
    )

    assert sensor.available is True
    assert sensor.native_value == 321.5
    assert sensor._attr_native_unit_of_measurement == "L"
    assert sensor._attr_suggested_display_precision == 1


def test_maintenance_statistics():
    assert make_sensor("descale_count").native_value == 7
    assert make_sensor("filter_replacements").native_value == 4
    assert make_sensor("grounds_container_clean_count").native_value == 456


def test_missing_statistic_is_unavailable():
    sensor = make_sensor("does_not_exist")

    assert sensor.available is False
    assert sensor.native_value is None


def test_statistics_retains_last_value_after_failed_update():
    coordinator = FakeCoordinator(SNAPSHOT)
    coordinator.last_update_success = False

    sensor = CremalinkStatisticsSensor(
        coordinator,
        ENTRY,
        "total_beverages",
        "Total beverages",
        "mdi:counter",
        None,
    )

    assert sensor.available is True
    assert sensor.native_value == 1234


def test_diagnostics_sensor_preserves_unknown_and_raw_values():
    sensor = CremalinkStatisticsDiagnosticsSensor(
        FakeCoordinator(SNAPSHOT),
        ENTRY,
    )

    assert sensor.available is True
    assert sensor.native_value == 3

    attrs = sensor.extra_state_attributes

    assert attrs["unknown_statistics"] == {
        "43000": 111,
        "43005": 222,
        "43014": 333,
    }
    assert attrs["raw_statistics"]["43010"] == 1234
    assert attrs["raw_statistics"]["106"] == 643000
    assert attrs["raw_count"] == 9
    assert (
        attrs["snapshot_fetched_at"]
        == "2026-08-25T07:00:00+00:00"
    )
    assert attrs["refresh_in_progress"] is False


def test_diagnostics_entity_disabled_by_default():
    sensor = CremalinkStatisticsDiagnosticsSensor(
        FakeCoordinator(SNAPSHOT),
        ENTRY,
    )

    assert sensor._attr_entity_registry_enabled_default is False
