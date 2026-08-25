"""Tests for Cremalink entity translation coverage."""

import json
from pathlib import Path

from custom_components.cremalink_ha.button import (
    COMMAND_TRANSLATION_KEYS,
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
