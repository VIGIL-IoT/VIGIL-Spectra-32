"""Source-backed checks for the representative classic ESP32 board map."""

from __future__ import annotations

import unittest
from pathlib import Path

from data.board_definition import BOARD_COMPONENTS, PIN_DEFINITIONS

ROOT = Path(__file__).resolve().parents[1]


class BoardDefinitionTests(unittest.TestCase):
    def test_classic_esp32_strapping_pins_are_flagged_for_review(self) -> None:
        for pin_id in ("BOOT", "GPIO2", "GPIO5", "GPIO12", "GPIO15"):
            with self.subTest(pin_id=pin_id):
                self.assertEqual(PIN_DEFINITIONS[pin_id]["security_state"], "Review")

    def test_module_flash_pin_is_reserved(self) -> None:
        gpio9 = PIN_DEFINITIONS["GPIO9"]
        self.assertEqual(gpio9["kind"], "Flash bus")
        self.assertEqual(gpio9["mode"], "RESERVED")
        self.assertIn("not treat it as a general output", gpio9["description"])

    def test_wroom_flash_is_described_as_module_storage(self) -> None:
        flash = BOARD_COMPONENTS["FLASH"]
        self.assertIn("on module", flash["label"])
        self.assertIn("module", flash["kind"].lower())
        self.assertIn("varies by module variant", flash["description"])

    def test_sample_sensor_and_relay_paths_are_not_described_as_physical_wiring(self) -> None:
        self.assertIn("model only", PIN_DEFINITIONS["GPIO22"]["connected_to"])
        self.assertIn("model only", PIN_DEFINITIONS["GPIO23"]["connected_to"])
        self.assertIn("never drives it", BOARD_COMPONENTS["LED"]["description"])

    def test_board_svg_labels_the_map_and_gpio2_as_references(self) -> None:
        source = (ROOT / "components" / "board_component" / "index.html").read_text(encoding="utf-8")
        self.assertIn("ESP32 DEVKIT-STYLE REFERENCE", source)
        self.assertIn("GPIO2 MODEL", source)
        self.assertNotIn("GPIO2 LED", source)


if __name__ == "__main__":
    unittest.main()
