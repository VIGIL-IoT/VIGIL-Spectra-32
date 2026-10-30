"""Regression checks for scenario labels and in-memory event execution."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from data.device_state import STATE_SCHEMA_VERSION, create_initial_state
from data.scenarios import SCENARIOS, SCENARIO_GUIDANCE, normalize_scenario
from services.hardware import classify_esptool_output, identify_esp_chip
from services.simulator import set_security_mode, set_simulation_mode, simulate_event


class ScenarioCatalogTests(unittest.TestCase):
    def test_scenario_options_match_guidance(self) -> None:
        self.assertEqual(SCENARIOS, tuple(SCENARIO_GUIDANCE))

    def test_legacy_mqtt_label_is_migrated(self) -> None:
        self.assertEqual(normalize_scenario("MQTT plaintext warning"), "MQTT without TLS")

    def test_unknown_label_uses_safe_default(self) -> None:
        self.assertEqual(normalize_scenario("removed scenario"), SCENARIOS[0])

    def test_initial_state_has_a_schema_version(self) -> None:
        self.assertEqual(create_initial_state()["schema_version"], STATE_SCHEMA_VERSION)

    def test_chip_classification_supports_only_classic_esp32(self) -> None:
        self.assertEqual(classify_esptool_output("Detecting chip type... ESP32"), ("supported", "ESP32"))
        self.assertEqual(classify_esptool_output("Detecting chip type... ESP32-S3"), ("other_esp", "ESP32-S3"))
        self.assertEqual(classify_esptool_output("Chip is ESP32-D0WD-V3 (revision v3.1)"), ("supported", "ESP32-D0WD-V3"))
        self.assertEqual(classify_esptool_output("no bootloader response"), ("unidentified", "A serial port responded, but esptool could not confirm an Espressif chip."))

    @patch("services.hardware.list_serial_ports", return_value=([{"device": "COM3", "description": "USB serial", "vendor_id": 1, "product_id": 2}], None))
    @patch("services.hardware.subprocess.run", return_value=SimpleNamespace(stdout="Detecting chip type... ESP32", stderr="", returncode=0))
    def test_chip_identification_uses_read_only_esptool_command(self, run_command, _list_ports) -> None:
        result = identify_esp_chip("COM3")
        self.assertEqual(result["status"], "supported")
        self.assertIn("chip-id", run_command.call_args.args[0])
        self.assertIn("--no-stub", run_command.call_args.args[0])
        self.assertNotIn("write-flash", run_command.call_args.args[0])

    @patch("services.hardware.list_serial_ports", return_value=([{"device": "COM3", "description": "USB serial", "vendor_id": 1, "product_id": 2}], None))
    @patch("services.hardware.subprocess.run", return_value=SimpleNamespace(stdout="Detecting chip type... ESP32", stderr="probe failed", returncode=2))
    def test_failed_esptool_command_is_not_reported_as_a_detected_chip(self, _run_command, _list_ports) -> None:
        result = identify_esp_chip("COM3")
        self.assertEqual(result["status"], "unidentified")
        self.assertEqual(result["chip"], "Unknown")

    def test_all_scenarios_run_in_both_profiles(self) -> None:
        for profile in ("Vulnerable", "Hardened"):
            for scenario in SCENARIOS:
                with self.subTest(profile=profile, scenario=scenario):
                    state = create_initial_state()
                    set_security_mode(state, profile)
                    set_simulation_mode(state, True)

                    event = simulate_event(state, scenario)

                    self.assertEqual(event["event_type"], state["events"][0]["event_type"])
                    self.assertEqual(event["target"], state["events"][0]["target"])

    def test_replay_outcome_differs_between_session_profiles(self) -> None:
        outcomes = {}
        for profile in ("Vulnerable", "Hardened"):
            state = create_initial_state()
            set_security_mode(state, profile)
            set_simulation_mode(state, True)
            event = simulate_event(state, "Replay attempt")
            outcomes[profile] = event["decision"]

        self.assertEqual(outcomes, {"Vulnerable": "Accepted", "Hardened": "Rejected"})

    def test_event_history_is_capped_at_sixty_records(self) -> None:
        state = create_initial_state()
        set_simulation_mode(state, True)
        for _ in range(65):
            simulate_event(state, "Normal traffic")
        self.assertEqual(len(state["events"]), 60)


if __name__ == "__main__":
    unittest.main()
