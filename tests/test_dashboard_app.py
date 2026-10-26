"""Streamlit UI smoke coverage for persisted state and interactive paths."""

from __future__ import annotations

from pathlib import Path
import importlib
import unittest

from streamlit.testing.v1 import AppTest

from data.device_state import STATE_SCHEMA_VERSION
from data.scenarios import SCENARIOS


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "simulator" / "dashboard" / "app.py"


class DashboardAppTests(unittest.TestCase):
    def assert_app_has_no_exceptions(self, app: AppTest) -> None:
        self.assertFalse([error.message for error in app.exception])

    def test_stale_session_and_all_primary_ui_paths(self) -> None:
        app = AppTest.from_file(str(APP_PATH), default_timeout=30)
        app.session_state["device_state"] = {"mode": "Vulnerable"}
        app.session_state["active_view"] = "Old view"
        app.session_state["security_profile"] = "Old profile"
        app.session_state["simulation_scenario"] = "MQTT plaintext warning"
        app.session_state["simulation_mode_toggle"] = "old toggle value"
        app.session_state["component_picker"] = "OLD_GPIO"
        app.run()

        self.assert_app_has_no_exceptions(app)
        self.assertEqual(app.session_state["device_state"]["schema_version"], STATE_SCHEMA_VERSION)
        self.assertEqual(app.session_state["active_view"], "Console")
        self.assertEqual(app.session_state["simulation_scenario"], "MQTT without TLS")

        for view in ("Events", "Hardware", "Console"):
            app.radio(key="active_view").set_value(view).run()
            self.assert_app_has_no_exceptions(app)

        component_options = list(app.selectbox(key="component_picker").options)
        for component in component_options:
            app.selectbox(key="component_picker").set_value(component).run()
            self.assert_app_has_no_exceptions(app)

        app.toggle(key="simulation_mode_toggle").set_value(True).run()
        for profile in ("Vulnerable", "Hardened"):
            app.radio(key="security_profile").set_value(profile).run()
            for scenario in SCENARIOS:
                app.selectbox(key="simulation_scenario").set_value(scenario).run()
                self.assert_app_has_no_exceptions(app)
                app.button(key="simulate_button").click().run()
                self.assert_app_has_no_exceptions(app)

        app.radio(key="active_view").set_value("Events").run()
        for severity in ("All", "HIGH", "MEDIUM", "INFO"):
            app.selectbox(key="event_severity_filter").set_value(severity).run()
            self.assert_app_has_no_exceptions(app)

    def test_hot_deploy_refreshes_stale_module_apis(self) -> None:
        import data.device_state as device_state_module
        import data.scenarios as scenario_module

        del device_state_module.STATE_SCHEMA_VERSION
        del scenario_module.normalize_scenario
        try:
            app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
            self.assert_app_has_no_exceptions(app)
            self.assertEqual(app.session_state["device_state"]["schema_version"], STATE_SCHEMA_VERSION)
        finally:
            importlib.reload(device_state_module)
            importlib.reload(scenario_module)


if __name__ == "__main__":
    unittest.main()
