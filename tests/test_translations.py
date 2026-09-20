"""Tests for Cremalink entity translation coverage."""

import json
from pathlib import Path

from custom_components.cremalink_ha.button import (
    COMMAND_TRANSLATION_KEYS,
)
from custom_components.cremalink_ha.sensor import (
    SENSORS,
    STATISTICS_SENSORS,
)


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "cremalink_ha"


ECAM610_EXPOSED_COMMANDS = {
    "americano",
    "caffe_latte",
    "cappuccino",
    "cappuccino_mix",
    "cappuccino_plus",
    "coffee",
    "cortado",
    "doppio_plus",
    "double_espresso",
    "espresso",
    "espresso_macchiato",
    "espresso_soul",
    "flat_white",
    "hot_milk",
    "hot_water",
    "latte_macchiato",
    "long_coffee",
    "stop",
}


def _load_json(path):
    return json.loads(path.read_text())


def test_ecam610_commands_have_translation_keys():
    """Every currently exposed ECAM610 command should be translated."""

    assert ECAM610_EXPOSED_COMMANDS <= set(
        COMMAND_TRANSLATION_KEYS
    )


def test_sensor_translation_keys_exist_in_all_languages():
    """Every exposed sensor should have English and German translations."""

    strings = _load_json(INTEGRATION / "strings.json")
    english = _load_json(INTEGRATION / "translations" / "en.json")
    german = _load_json(INTEGRATION / "translations" / "de.json")

    expected = {key for key, _name, _icon, _unit in SENSORS}
    expected |= {
        key for key, _name, _icon, _unit in STATISTICS_SENSORS
    }
    expected.add("a2_statistics_diagnostics")

    strings_sensors = strings["entity"]["sensor"]
    english_sensors = english["entity"]["sensor"]
    german_sensors = german["entity"]["sensor"]

    for translation_key in sorted(expected):
        assert translation_key in strings_sensors
        assert strings_sensors[translation_key]["name"]

        assert translation_key in english_sensors
        assert english_sensors[translation_key]["name"]

        assert translation_key in german_sensors
        assert german_sensors[translation_key]["name"]


def test_strings_and_english_entity_translations_match():
    """strings.json and en.json should expose identical sensor strings."""

    strings = _load_json(INTEGRATION / "strings.json")
    english = _load_json(INTEGRATION / "translations" / "en.json")

    assert strings["entity"]["sensor"] == english["entity"]["sensor"]


def test_command_translation_keys_exist_in_english_and_german():
    """Every known command translation key should exist in both languages."""

    strings = _load_json(INTEGRATION / "strings.json")
    german = _load_json(
        INTEGRATION / "translations" / "de.json"
    )

    english_buttons = strings["entity"]["button"]
    german_buttons = german["entity"]["button"]

    for translation_key in COMMAND_TRANSLATION_KEYS.values():
        assert translation_key in english_buttons
        assert english_buttons[translation_key]["name"]

        assert translation_key in german_buttons
        assert german_buttons[translation_key]["name"]



def _translation_key_shape(value):
    if isinstance(value, dict):
        return {
            key: _translation_key_shape(child)
            for key, child in value.items()
        }

    if isinstance(value, list):
        return [_translation_key_shape(child) for child in value]

    return None


def test_german_entity_translation_structure_is_complete():
    # German should contain every entity translation key from strings.json.
    strings = _load_json(INTEGRATION / "strings.json")
    german = _load_json(
        INTEGRATION / "translations" / "de.json"
    )

    assert _translation_key_shape(
        german["entity"]
    ) == _translation_key_shape(
        strings["entity"]
    )
