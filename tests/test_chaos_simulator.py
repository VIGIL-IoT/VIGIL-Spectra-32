"""Deterministic state, dependency, and metric checks for Chaos Lab."""

from __future__ import annotations

import unittest

from data.chaos_scenarios import CHAOS_SCENARIOS, CHAOS_SCENARIO_IDS
from data.chaos_state import create_initial_chaos_state
from data.device_state import STATE_SCHEMA_VERSION, create_initial_state
from services.chaos_simulator import advance_experiment, reset_experiment, start_experiment


class ChaosScenarioCatalogTests(unittest.TestCase):
    def test_catalog_metadata_and_profile_plans_are_complete(self) -> None:
        self.assertEqual(len(CHAOS_SCENARIOS), 8)
        self.assertEqual(len(set(CHAOS_SCENARIO_IDS)), len(CHAOS_SCENARIO_IDS))
        for scenario in CHAOS_SCENARIOS.values():
            with self.subTest(scenario=scenario.id):
                self.assertTrue(scenario.name)
                self.assertTrue(scenario.category)
                self.assertTrue(scenario.summary)
                self.assertTrue(scenario.affected_components)
                self.assertTrue(scenario.assumptions)
                self.assertTrue(scenario.fault_behavior)
                self.assertTrue(scenario.vulnerable_behavior)
                self.assertTrue(scenario.hardened_behavior)
                self.assertTrue(scenario.recovery_policy)
                self.assertTrue(scenario.primary_metric)
                self.assertTrue(scenario.educational_explanation)
                self.assertTrue(scenario.limitations)
                self.assertEqual(set(scenario.plans), {"Vulnerable", "Hardened"})
                for plan in scenario.plans.values():
                    moments = [milestone.at_seconds for milestone in plan]
                    self.assertEqual(moments, sorted(moments))
                    self.assertEqual(moments[0], 0)
                    self.assertEqual(moments[-1], 10)

    def test_state_schema_has_separate_chaos_state(self) -> None:
        state = create_initial_state()
        self.assertEqual(state["schema_version"], STATE_SCHEMA_VERSION)
        self.assertIn("chaos", state)
        self.assertTrue(state["chaos"]["is_simulated"])
        self.assertEqual(state["chaos"]["stage"], "IDLE")


class ChaosLifecycleTests(unittest.TestCase):
    def start(self, scenario_id: str, profile: str = "Vulnerable", packet_loss_pct: int = 30):
        chaos = create_initial_chaos_state()
        start_experiment(
            chaos,
            scenario_id,
            profile,
            now_monotonic=100.0,
            packet_loss_pct=packet_loss_pct,
        )
        return chaos

    def test_state_machine_and_timeline_advance_without_sleeping(self) -> None:
        chaos = self.start("mqtt-broker-outage")
        self.assertEqual(chaos["stage"], "BASELINE")
        self.assertEqual(chaos["timeline"][0]["simulated_time"], "T+00:00")

        advance_experiment(chaos, 1)
        self.assertEqual(chaos["stage"], "FAULT_INJECTED")
        advance_experiment(chaos, 2)
        self.assertEqual(chaos["stage"], "DEGRADED")
        advance_experiment(chaos, 4)
        self.assertEqual(chaos["stage"], "RECOVERING")
        advance_experiment(chaos, 10)
        self.assertFalse(chaos["active"])
        self.assertEqual(chaos["stage"], "COMPLETE")
        self.assertTrue(chaos["result"]["completed"])
        self.assertEqual(chaos["timeline"][-1]["simulated_time"], "T+00:10")
        self.assertEqual(chaos["profiles"]["Vulnerable"]["stage"], "FAILED_TO_RECOVER")

    def test_compare_profiles_produces_distinct_recovery_behavior(self) -> None:
        chaos = self.start("mqtt-broker-outage", "Compare both")
        advance_experiment(chaos, 10)
        vulnerable = chaos["result"]["profiles"]["Vulnerable"]["metrics"]
        hardened = chaos["result"]["profiles"]["Hardened"]["metrics"]

        self.assertEqual(vulnerable["recovery_status"], "Failed to recover")
        self.assertEqual(hardened["recovery_status"], "Recovered")
        self.assertIsNone(vulnerable["recovery_duration_seconds"])
        self.assertEqual(hardened["recovery_duration_seconds"], 7)
        self.assertGreater(hardened["modeled_availability_pct"], vulnerable["modeled_availability_pct"])
        self.assertGreater(hardened["resilience_score"], vulnerable["resilience_score"])

    def test_every_catalog_scenario_completes_for_both_profiles(self) -> None:
        for scenario_id in CHAOS_SCENARIO_IDS:
            with self.subTest(scenario=scenario_id):
                chaos = self.start(scenario_id, "Compare both")
                advance_experiment(chaos, 10)

                self.assertFalse(chaos["active"])
                self.assertTrue(chaos["result"]["completed"])
                self.assertEqual(
                    set(chaos["result"]["profiles"]),
                    {"Vulnerable", "Hardened"},
                )
                self.assertLessEqual(len(chaos["timeline"]), 60)
                for profile_result in chaos["result"]["profiles"].values():
                    metrics = profile_result["metrics"]
                    self.assertGreaterEqual(metrics["modeled_availability_pct"], 0)
                    self.assertLessEqual(metrics["modeled_availability_pct"], 100)
                    self.assertGreaterEqual(metrics["operation_success_pct"], 0)
                    self.assertLessEqual(metrics["operation_success_pct"], 100)

    def test_wifi_loss_propagates_to_mqtt_but_mqtt_outage_does_not_drop_wifi(self) -> None:
        wifi = self.start("wifi-connectivity-loss")
        advance_experiment(wifi, 2)
        wifi_status = wifi["profiles"]["Vulnerable"]["statuses"]
        self.assertEqual(wifi_status["wifi"], "OFFLINE")
        self.assertEqual(wifi_status["mqtt"], "OFFLINE")

        mqtt = self.start("mqtt-broker-outage")
        advance_experiment(mqtt, 2)
        mqtt_status = mqtt["profiles"]["Vulnerable"]["statuses"]
        self.assertEqual(mqtt_status["mqtt"], "OFFLINE")
        self.assertEqual(mqtt_status["wifi"], "ONLINE")

    def test_packet_loss_is_deterministic_and_retries_are_bounded(self) -> None:
        first = self.start("packet-loss", "Compare both", packet_loss_pct=30)
        second = self.start("packet-loss", "Compare both", packet_loss_pct=30)
        advance_experiment(first, 10)
        advance_experiment(second, 10)
        first_results = first["result"]["profiles"]
        second_results = second["result"]["profiles"]
        self.assertEqual(first_results, second_results)

        vulnerable = first_results["Vulnerable"]["metrics"]
        hardened = first_results["Hardened"]["metrics"]
        self.assertEqual(vulnerable["operations_attempted"], 10)
        self.assertEqual(vulnerable["operations_failed"], 3)
        self.assertEqual(hardened["retry_count"], 3)
        self.assertLessEqual(hardened["retry_count"], 3)
        self.assertGreater(hardened["operations_succeeded"], vulnerable["operations_succeeded"])

    def test_packet_loss_zero_has_no_loss_or_retry(self) -> None:
        chaos = self.start("packet-loss", "Compare both", packet_loss_pct=0)
        advance_experiment(chaos, 10)
        for profile in ("Vulnerable", "Hardened"):
            metrics = chaos["result"]["profiles"][profile]["metrics"]
            self.assertEqual(metrics["operations_failed"], 0)
            self.assertEqual(metrics["retry_count"], 0)

    def test_sensor_profiles_treat_invalid_samples_differently(self) -> None:
        chaos = self.start("sensor-failure", "Compare both")
        advance_experiment(chaos, 10)
        vulnerable = chaos["result"]["profiles"]["Vulnerable"]["metrics"]
        hardened = chaos["result"]["profiles"]["Hardened"]["metrics"]
        self.assertEqual(vulnerable["integrity_failures"], 4)
        self.assertEqual(hardened["invalid_samples_rejected"], 2)
        self.assertGreater(hardened["operation_success_pct"], vulnerable["operation_success_pct"])

    def test_reset_returns_to_idle_and_invalid_inputs_are_rejected(self) -> None:
        chaos = self.start("watchdog-task-stall")
        reset_experiment(chaos)
        self.assertEqual(chaos["stage"], "IDLE")
        self.assertFalse(chaos["active"])
        with self.assertRaises(ValueError):
            start_experiment(chaos, "watchdog-task-stall", "unknown", now_monotonic=100)
        with self.assertRaises(ValueError):
            start_experiment(chaos, "packet-loss", "Vulnerable", now_monotonic=100, packet_loss_pct=51)


if __name__ == "__main__":
    unittest.main()
