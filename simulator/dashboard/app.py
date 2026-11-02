"""VIGIL-IoT / SPECTRA-32 local device console and security simulation."""

from __future__ import annotations

import html
import importlib
import math
from datetime import datetime
from pathlib import Path
import sys
import time
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
CSS = (ROOT / "assets" / "app.css").read_text(encoding="utf-8")


def _current_module(name: str, required_symbols: tuple[str, ...]):
    """Refresh a project module when a hot deployment left an older API cached."""
    module = importlib.import_module(name)
    if all(hasattr(module, symbol) for symbol in required_symbols):
        return module, False
    importlib.invalidate_caches()
    return importlib.reload(module), True


board_definition_module, _ = _current_module(
    "data.board_definition",
    ("BOARD_DEFINITION_VERSION", "BOARD_COMPONENTS", "PIN_DEFINITIONS", "VIRTUAL_COMPONENTS"),
)
if getattr(board_definition_module, "BOARD_DEFINITION_VERSION", 0) < 3:
    board_definition_module = importlib.reload(board_definition_module)
device_state_module, state_module_refreshed = _current_module(
    "data.device_state",
    ("STATE_SCHEMA_VERSION", "DeviceState", "create_initial_state"),
)
scenario_module, scenario_module_refreshed = _current_module(
    "data.scenarios",
    ("SCENARIO_GUIDANCE", "SCENARIOS", "normalize_scenario"),
)
chaos_state_module, _ = _current_module(
    "data.chaos_state",
    ("CHAOS_STATE_SCHEMA_VERSION", "ChaosState", "create_initial_chaos_state"),
)
chaos_scenario_module, chaos_scenario_module_refreshed = _current_module(
    "data.chaos_scenarios",
    ("CHAOS_SCENARIOS", "CHAOS_SCENARIO_IDS", "normalize_chaos_scenario"),
)
if (
    getattr(device_state_module, "STATE_SCHEMA_VERSION", 0) < 4
    or "chaos" not in getattr(device_state_module.DeviceState, "__annotations__", {})
):
    device_state_module = importlib.reload(device_state_module)
simulator_module, simulator_module_refreshed = _current_module(
    "services.simulator",
    ("SCENARIOS", "log_profile_change", "set_security_mode", "set_simulation_mode", "simulate_event"),
)
if (
    state_module_refreshed
    or scenario_module_refreshed
    or chaos_scenario_module_refreshed
    or simulator_module_refreshed
    or simulator_module.SCENARIOS != scenario_module.SCENARIOS
):
    simulator_module = importlib.reload(simulator_module)
chaos_service_module, chaos_service_refreshed = _current_module(
    "services.chaos_simulator",
    ("PROFILE_SELECTIONS", "advance_experiment", "reset_experiment", "service_availability_series", "start_experiment"),
)
if chaos_scenario_module_refreshed or chaos_service_refreshed:
    chaos_service_module = importlib.reload(chaos_service_module)
hardware_module, _ = _current_module(
    "services.hardware",
    ("identify_esp_chip", "list_serial_ports"),
)
board_module, _ = _current_module("components.board", ("render_board",))

BOARD_COMPONENTS = board_definition_module.BOARD_COMPONENTS
PIN_DEFINITIONS = board_definition_module.PIN_DEFINITIONS
VIRTUAL_COMPONENTS = board_definition_module.VIRTUAL_COMPONENTS
STATE_SCHEMA_VERSION = device_state_module.STATE_SCHEMA_VERSION
DeviceState = device_state_module.DeviceState
create_initial_state = device_state_module.create_initial_state
CHAOS_STATE_SCHEMA_VERSION = chaos_state_module.CHAOS_STATE_SCHEMA_VERSION
create_initial_chaos_state = chaos_state_module.create_initial_chaos_state
SCENARIO_GUIDANCE = scenario_module.SCENARIO_GUIDANCE
SCENARIOS = scenario_module.SCENARIOS
normalize_scenario = scenario_module.normalize_scenario
CHAOS_SCENARIOS = chaos_scenario_module.CHAOS_SCENARIOS
CHAOS_SCENARIO_IDS = chaos_scenario_module.CHAOS_SCENARIO_IDS
normalize_chaos_scenario = chaos_scenario_module.normalize_chaos_scenario
PROFILE_SELECTIONS = chaos_service_module.PROFILE_SELECTIONS
advance_experiment = chaos_service_module.advance_experiment
reset_experiment = chaos_service_module.reset_experiment
service_availability_series = chaos_service_module.service_availability_series
start_experiment = chaos_service_module.start_experiment
log_profile_change = simulator_module.log_profile_change
set_security_mode = simulator_module.set_security_mode
set_simulation_mode = simulator_module.set_simulation_mode
simulate_event = simulator_module.simulate_event
identify_esp_chip = hardware_module.identify_esp_chip
list_serial_ports = hardware_module.list_serial_ports
render_board = board_module.render_board


st.set_page_config(
    page_title="SPECTRA-32 Node Console · VIGIL-IoT",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

if (
    "device_state" not in st.session_state
    or not isinstance(st.session_state.device_state, dict)
    or st.session_state.device_state.get("schema_version") != STATE_SCHEMA_VERSION
    or not isinstance(st.session_state.device_state.get("chaos"), dict)
    or st.session_state.device_state["chaos"].get("schema_version") != CHAOS_STATE_SCHEMA_VERSION
):
    # The session contains sample data only. Refresh it when the schema or
    # sample baseline changes so stale values do not survive a deployment.
    st.session_state.device_state = create_initial_state()
if "active_view" not in st.session_state:
    st.session_state.active_view = "Console"
state: DeviceState = st.session_state.device_state
if "chaos" not in state:
    state["chaos"] = create_initial_chaos_state()
if "component_picker" in st.session_state:
    state["selected_component"] = st.session_state.component_picker


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def status_class(value: str) -> str:
    normalized = value.lower()
    if any(term in normalized for term in ("accepted", "exposed", "high", "disabled", "plaintext")):
        return "bad"
    if any(term in normalized for term in ("review", "medium", "rejected", "restricted")):
        return "warn"
    return "good"


def normalize_widget_choice(key: str, options: tuple[str, ...] | list[str], default: str) -> None:
    """Replace stale persisted widget values before Streamlit builds the widget."""
    if st.session_state.get(key, default) not in options:
        st.session_state[key] = default


def render_topbar() -> None:
    brand, nav, status = st.columns([1.25, 1.55, 1.2], vertical_alignment="center")
    with brand:
        st.markdown(
            """
            <div class="brand-lockup">
              <span class="brand-mark" aria-hidden="true"></span>
              <div><div class="brand-word">VIGIL-IoT</div><div class="brand-caption">A VIGIL-IoT Project</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with nav:
        normalize_widget_choice("active_view", ("Console", "Events", "Hardware", "Chaos Lab"), "Console")
        st.radio(
            "Primary view",
            ("Console", "Events", "Hardware", "Chaos Lab"),
            horizontal=True,
            label_visibility="collapsed",
            key="active_view",
        )
    with status:
        threat = str(state["security"]["threat_level"])
        st.markdown(
            f"""
            <div class="status-cluster">
              <span class="status-chip"><i class="status-dot"></i>SESSION MODEL</span>
              <span class="threat-chip {esc(threat.lower())}">THREAT {esc(threat)}</span>
              <span class="sample-stamp">LIVE CONTROL OFF</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('<div class="topbar-rule"></div>', unsafe_allow_html=True)


def render_title(view: str) -> None:
    titles = {
        "Console": (
            "SPECTRA-32 Node Console",
            "Security Platform for Embedded Cyber Threat Research &amp; Analysis.",
            state["node_id"],
        ),
        "Events": (
            "Security event log",
            "Review simulated security events, affected interfaces, and policy decisions.",
            "Local session",
        ),
        "Hardware": (
            "ESP32 DevKit board",
            "Inspect the board map, detect a locally attached chip, and review simulated posture.",
            "ESP32 · local USB scan",
        ),
        "Chaos Lab": (
            "SPECTRA-32 Chaos Lab",
            "Inject a bounded modeled fault, observe service impact, and compare recovery policies over simulated time.",
            "BEHAVIORAL MODEL · SESSION ONLY",
        ),
    }
    title, description, scope = titles[view]
    st.markdown(
        f"""
        <div class="page-heading">
          <div><h1>{title}</h1><p>{description}</p></div>
          <div class="scope">{esc(scope)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_controls() -> None:
    mode_col, simulation_col, scenario_col, action_col = st.columns([1.22, 1.05, 1.7, 0.85], vertical_alignment="bottom")
    with mode_col:
        st.markdown('<div class="control-heading">Security profile</div>', unsafe_allow_html=True)
        normalize_widget_choice("security_profile", ("Vulnerable", "Hardened"), state["mode"])
        selected_mode = st.radio(
            "Security profile",
            ("Vulnerable", "Hardened"),
            horizontal=True,
            label_visibility="collapsed",
            key="security_profile",
        )
    if selected_mode != state["mode"]:
        previous_mode = state["mode"]
        set_security_mode(state, selected_mode)
        log_profile_change(state, previous_mode)

    with simulation_col:
        st.markdown('<div class="control-heading">Simulation</div>', unsafe_allow_html=True)
        if not isinstance(st.session_state.get("simulation_mode_toggle", state["simulation_mode"]), bool):
            st.session_state["simulation_mode_toggle"] = bool(state["simulation_mode"])
        enabled = st.toggle(
            "Simulation Mode",
            key="simulation_mode_toggle",
            value=state["simulation_mode"],
            help="Applies one bounded event to this session's model. No network traffic is generated.",
        )
    set_simulation_mode(state, enabled)

    with scenario_col:
        # A deployed session can outlive a release and still hold an old option
        # label. Normalize it before constructing the keyed widget.
        st.session_state["simulation_scenario"] = normalize_scenario(
            st.session_state.get("simulation_scenario")
        )
        scenario = st.selectbox(
            "Simulated event",
            SCENARIOS,
            label_visibility="visible",
            disabled=not enabled,
            key="simulation_scenario",
        )

    with action_col:
        if st.button(
            "Run simulation",
            type="primary",
            use_container_width=True,
            disabled=not enabled,
            key="simulate_button",
        ):
            simulate_event(state, scenario)
            st.session_state["component_picker"] = state["selected_component"]

    guidance = SCENARIO_GUIDANCE[scenario]
    outcome = guidance["vulnerable" if selected_mode == "Vulnerable" else "hardened"]
    st.markdown(
        f"""
        <div class="scenario-readout">
          <div class="scenario-copy">
            <span>Selected scenario</span>
            <strong>{esc(scenario)}</strong>
            <p>{esc(guidance['summary'])}</p>
          </div>
          <div class="scenario-result">
            <span>{esc(selected_mode)} profile outcome</span>
            <strong>{esc(outcome)}</strong>
            <small>{esc(guidance['mapping'])}</small>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_network_status() -> None:
    wifi = state["wifi"]
    mqtt = state["mqtt"]
    wifi_value = f"{wifi['ssid']} · {wifi['rssi']} dBm (sample)" if wifi["connected"] else "Sample offline"
    mqtt_value = "TLS required · profile" if mqtt["tls"] else "No TLS · simulated"
    mqtt_class = "good" if mqtt["tls"] else "bad"
    threat = str(state["security"]["threat_level"])
    st.markdown(
        f"""
        <div class="node-status-line">
          <strong>Node 01</strong>
          <span class="mode-chip">{esc(state['firmware'])}</span>
          <span class="threat-chip {threat.lower()}">THREAT {esc(threat)}</span>
        </div>
        <div class="network-grid">
          <div class="network-cell">
            <span class="network-label">Wi-Fi · {'Sample connected' if wifi['connected'] else 'Sample offline'}</span>
            <strong class="network-value network-value--telemetry">{esc(wifi_value)}</strong>
          </div>
          <div class="network-cell">
            <span class="network-label">MQTT · {'Sample connected' if mqtt['connected'] else 'Sample offline'}</span>
            <strong class="network-value"><span class="state-chip {mqtt_class}">{esc(mqtt_value)}</span></strong>
          </div>
        </div>
        <p class="network-footnote">Illustrative link state only. This dashboard sends no Wi-Fi or MQTT traffic.</p>
        """,
        unsafe_allow_html=True,
    )


def security_rows() -> str:
    security = state["security"]
    rows = [
        ("MQTT authentication", bool(security["mqtt_auth_required"])),
        ("MQTT topic ACL", bool(security["mqtt_topic_acl_enabled"])),
        ("Secure Boot", bool(security["secure_boot"])),
        ("Flash encryption", bool(security["flash_encryption"])),
        ("OTA signing", bool(security["ota_signing"])),
    ]
    rendered = []
    for label, enabled in rows:
        rendered.append(
            f'<div class="security-row"><span>{label}</span><span class="state-chip {"good" if enabled else "warn"}">{"Enabled" if enabled else "Disabled"}</span></div>'
        )
    debug_enabled = bool(security["debug_enabled"])
    rendered.append(
        f'<div class="security-row"><span>UART debug</span><span class="state-chip {"warn" if debug_enabled else "good"}">{"Enabled" if debug_enabled else "Restricted"}</span></div>'
    )
    return "".join(rendered)


def component_details(component_id: str) -> tuple[str, str, list[tuple[str, str]], str]:
    security = state["security"]
    if component_id == "MQTT":
        mqtt = state["mqtt"]
        return (
            "MQTT broker",
            "Network service",
            [
                ("Modelled link", "Sample connected" if mqtt["connected"] else "Sample offline"),
                ("TLS policy", "Required by profile" if mqtt["tls"] else "Not required by profile"),
                ("Authentication", "Required by profile" if security["mqtt_auth_required"] else "Not required by profile"),
                ("Topic ACL", "Enabled by profile" if security["mqtt_topic_acl_enabled"] else "Open in profile"),
                ("Live broker", "No connection"),
                ("Authentication failures", str(security["auth_failures"])),
            ],
            VIRTUAL_COMPONENTS["MQTT"]["description"],
        )
    if component_id == "ESP32_MODULE":
        findings = sum(not bool(security[key]) for key in ("secure_boot", "flash_encryption", "ota_signing"))
        fields = [
            ("Firmware", state["firmware"]),
            ("Secure Boot", "Enabled" if security["secure_boot"] else "Disabled"),
            ("Flash encryption", "Enabled" if security["flash_encryption"] else "Disabled"),
            ("OTA signing", "Enabled" if security["ota_signing"] else "Disabled"),
            ("Security findings", str(findings)),
        ]
        return "ESP32 Module", "Microcontroller module", fields, "Firmware posture follows the selected local simulation profile."

    if component_id in BOARD_COMPONENTS:
        component = BOARD_COMPONENTS[component_id]
        if component_id == "LED":
            led_state = state["gpio"].get("GPIO2", {}).get("state", "LOW")
            return component["label"], component["kind"], [("GPIO2 state", led_state), ("Profile", state["mode"])], component["description"]
        if component_id == "USB":
            debug = bool(security["debug_enabled"])
            return component["label"], component["kind"], [("UART bridge", "Enabled"), ("Debug exposure", "Development mode" if debug else "Restricted")], component["description"]
        if component_id == "FLASH":
            encrypted = bool(security["flash_encryption"])
            signed = bool(security["ota_signing"])
            return component["label"], component["kind"], [("Flash encryption", "Enabled" if encrypted else "Disabled"), ("OTA signing", "Enabled" if signed else "Disabled")], component["description"]
        if component_id in {"EN", "BOOT"}:
            pin = PIN_DEFINITIONS[component_id]
            return component["label"], component["kind"], [("Type", pin["kind"]), ("Signal", pin["state"])], component["description"]
        return component["label"], component["kind"], [("Node", state["node_id"]), ("Profile", state["mode"])], component["description"]

    pin = PIN_DEFINITIONS[component_id]
    live = state["gpio"].get(component_id, {})
    mode = str(live.get("mode", pin["mode"]))
    signal_state = str(live.get("state", pin["state"]))
    connected_to = str(live.get("connected_to", pin["connected_to"]))
    security_state = str(live.get("security_state", pin["security_state"]))
    fields = [("Type", pin["kind"]), ("Mode", mode), ("State", signal_state), ("Connected device", connected_to), ("Security state", security_state)]
    if component_id in {"TX", "RX"}:
        debug = bool(security["debug_enabled"])
        fields = [
            ("Status", "Enabled" if debug else "Restricted"),
            ("Exposure", "Development mode" if debug else "Reduced"),
            ("Risk", "Debug data may be exposed" if debug else "Console disabled by profile"),
        ]
    return component_id, pin["kind"], fields, pin["description"]


def render_component_details() -> None:
    component_options = list(dict.fromkeys([*PIN_DEFINITIONS.keys(), *BOARD_COMPONENTS.keys(), *VIRTUAL_COMPONENTS.keys()]))
    default_component = state["selected_component"] if state["selected_component"] in component_options else "GPIO23"
    state["selected_component"] = default_component
    normalize_widget_choice("component_picker", component_options, default_component)
    selected = st.selectbox(
        "Selected pin or component",
        component_options,
        key="component_picker",
        label_visibility="visible",
    )
    state["selected_component"] = selected
    title, kind, fields, description = component_details(selected)
    chip_value = next((value for key, value in fields if key == "Security state"), "Normal")
    st.markdown(
        f"""
        <div class="component-heading"><div><h3>{esc(title)}</h3><small>{esc(kind)}</small></div>
          <span class="state-chip {status_class(str(chip_value))}">{esc(chip_value)}</span></div>
        <div class="detail-grid">{''.join(f'<span>{esc(label)}</span><strong>{esc(value)}</strong>' for label, value in fields)}</div>
        <p class="detail-description">{esc(description)}</p>
        """,
        unsafe_allow_html=True,
    )


def render_board_selection() -> None:
    """Render the clickable SVG and carry a new pin choice into this rerun."""
    component_options = set(PIN_DEFINITIONS) | set(BOARD_COMPONENTS)
    clicked = render_board(
        selected=state["selected_component"],
        active_path=state["active_path"],
        pin_states=state["gpio"],
        height=424,
    )
    if clicked in component_options and clicked != st.session_state.get("last_board_click"):
        state["selected_component"] = clicked
        st.session_state["last_board_click"] = clicked
        st.session_state["component_picker"] = clicked


def render_metrics() -> None:
    security = state["security"]
    metrics = [
        ("Replay attempts", security["replay_attempts"], "", "warn"),
        ("Authentication failures", security["auth_failures"], "", "warn"),
        ("Blocked requests", security["blocked_requests"], "", ""),
        ("Accepted commands", security["accepted_commands"], "", ""),
        ("Current request rate", security["current_request_rate"], "req/min", "alert" if security["current_request_rate"] >= 40 else ""),
    ]
    cells = "".join(
        f'<div class="metric"><div class="metric-label">{esc(label)}</div><div class="metric-value {tone}">{esc(value)}<small>{esc(unit)}</small></div></div>'
        for label, value, unit, tone in metrics
    )
    st.markdown(
        f"""
        <div class="metrics-head"><h2>Security metrics</h2><span>Sample session · local simulation</span></div>
        <div class="metric-strip" role="group" aria-label="SPECTRA-32 security metrics">{cells}</div>
        <p class="data-boundary metrics-note">Sample values are from the brief. Controls affect only this session; no device or broker receives traffic.</p>
        """,
        unsafe_allow_html=True,
    )


def path_labels() -> list[str]:
    if state["active_path"]:
        return state["active_path"]
    return ["Wi-Fi", "ESP32", "MQTT", "GPIO23", "Relay"]


def render_attack_path() -> None:
    labels = path_labels()
    active = bool(state["active_path"])
    items = []
    for index, label in enumerate(labels):
        cls = "path-node active" if active else "path-node"
        items.append(f'<span class="{cls}">{esc(label)}</span>')
        if index < len(labels) - 1:
            items.append('<span class="path-arrow" aria-hidden="true">→</span>')
    caption = "Highlighted by the latest simulated event." if active else "Example route · run a scenario to highlight the affected path."
    st.markdown(
        f"""
        <div class="panel-title"><h2>Attack path</h2><span>{'Active simulation' if active else 'Idle route'}</span></div>
        <p class="path-caption">{caption}</p>
        <div class="attack-path" role="img" aria-label="{' to '.join(labels)}">{''.join(items)}</div>
        """,
        unsafe_allow_html=True,
    )


def render_event_rows(events: list[dict[str, Any]]) -> None:
    if not events:
        st.markdown('<div class="empty-state">No events match this filter.</div>', unsafe_allow_html=True)
        return
    rows = []
    for event in events:
        severity = str(event["severity"]).lower()
        rows.append(
            f'<div class="event-row" role="listitem"><time class="event-time">{esc(event["timestamp"])}</time>'
            f'<span class="severity {esc(severity)}">{esc(event["severity"])}</span>'
            f'<div class="event-main"><strong>{esc(event["event_type"])}</strong><small>{esc(event["component"])}</small></div>'
            f'<div class="event-decision"><strong>{esc(event["decision"])}</strong><small>{esc(event["reason"])}</small></div></div>'
        )
    st.markdown(f'<div class="event-list" role="list">{"".join(rows)}</div>', unsafe_allow_html=True)


@st.fragment(run_every=2)
def render_command_activity() -> None:
    """Stream recent command counters from the local session model."""
    session_state: DeviceState = st.session_state.device_state
    security = session_state["security"]
    accepted = int(security["accepted_commands"])
    blocked = int(security["blocked_requests"])
    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    history = st.session_state.get("command_activity_history", [])
    if not isinstance(history, list):
        history = []
    last = history[-1] if history else None
    if last is not None and (accepted < last["accepted"] or blocked < last["blocked"]):
        history = []
        last = None
    changed = last is None or (last["accepted"], last["blocked"]) != (accepted, blocked)
    elapsed = last is None or (now - last["time"]).total_seconds() >= 2
    if changed or elapsed:
        history.append({"time": now, "accepted": accepted, "blocked": blocked})
        del history[:-60]
        st.session_state.command_activity_history = history

    chart_rows = []
    for index, sample in enumerate(history):
        timestamp = sample["time"].replace(tzinfo=None)
        chart_rows.extend(
            (
                {
                    "Time": timestamp,
                    "Counter": "Accepted commands",
                    "Value": int(sample["accepted"]),
                    "Latest": index == len(history) - 1,
                },
                {
                    "Time": timestamp,
                    "Counter": "Blocked requests",
                    "Value": int(sample["blocked"]),
                    "Latest": index == len(history) - 1,
                },
            )
        )
    chart_data = pd.DataFrame(chart_rows)
    time_start = chart_rows[0]["Time"]
    time_end = chart_rows[-1]["Time"]
    if time_start == time_end:
        time_start -= pd.Timedelta(seconds=2)
        time_end += pd.Timedelta(seconds=2)
    max_count = max((row["Value"] for row in chart_rows), default=0)
    tick_step = max(1, math.ceil(max_count / 5))
    chart_max = tick_step * 5
    chart_ticks = list(range(0, chart_max + 1, tick_step))
    chart_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
        "layer": [
            {"mark": {"type": "line", "strokeWidth": 2, "clip": True}},
            {
                "transform": [{"filter": {"field": "Latest", "equal": True}}],
                "mark": {"type": "point", "filled": True, "size": 36},
            },
        ],
        "encoding": {
            "x": {
                "field": "Time",
                "type": "temporal",
                "scale": {
                    "domain": [time_start.isoformat(), time_end.isoformat()],
                    "nice": False,
                },
                "axis": {
                    "title": "Time",
                    "format": "%H:%M:%S",
                    "tickCount": 4,
                    "grid": False,
                },
            },
            "y": {
                "field": "Value",
                "type": "quantitative",
                "scale": {"domain": [0, chart_max], "nice": False},
                "axis": {
                    "title": "Count",
                    "values": chart_ticks,
                    "format": "d",
                    "domain": False,
                    "grid": True,
                },
            },
            "color": {
                "field": "Counter",
                "type": "nominal",
                "scale": {
                    "domain": ["Accepted commands", "Blocked requests"],
                    "range": ["#74dfc3", "#e8bd85"],
                },
                "legend": {"title": None, "orient": "top", "direction": "horizontal"},
            },
            "tooltip": [
                {"field": "Time", "type": "temporal", "title": "Time", "format": "%H:%M:%S"},
                {"field": "Counter", "type": "nominal", "title": "Counter"},
                {"field": "Value", "type": "quantitative", "title": "Count", "format": "d"},
            ],
        },
        "config": {
            "background": "transparent",
            "view": {"stroke": None},
            "axis": {
                "labelColor": "#a9bcb3",
                "titleColor": "#a9bcb3",
                "labelFontSize": 11,
                "titleFontSize": 11,
                "gridColor": "#263631",
                "gridOpacity": 0.8,
            },
            "legend": {"labelColor": "#a9bcb3", "labelFontSize": 11, "symbolStrokeWidth": 2},
        },
        "padding": {"left": 0, "right": 8, "top": 2, "bottom": 0},
    }
    with st.container(border=True, key="telemetry_panel"):
        st.markdown(
            '<div class="panel-title"><h2>Security counters</h2><span>SESSION MODEL · LIVE</span></div>',
            unsafe_allow_html=True,
        )
        st.vega_lite_chart(
            chart_data,
            chart_spec,
            width="stretch",
            height=160,
            theme=None,
            key="command_activity_chart",
            alt="Accepted commands and blocked requests over time in the local simulation model.",
        )
        st.markdown(
            '<p class="telemetry-note">Sample baseline and simulated actions · no live hardware data.</p>',
            unsafe_allow_html=True,
        )


def render_overview() -> None:
    board_col, detail_col = st.columns([1.2, 1], gap="medium", vertical_alignment="top")
    with board_col:
        with st.container(border=True, key="board_panel"):
            st.markdown(
                '<div class="panel-title"><h2>Interactive ESP32 DevKit</h2></div>',
                unsafe_allow_html=True,
            )
            render_board_selection()
        render_command_activity()
    with detail_col:
        with st.container(border=True, key="node_panel"):
            render_component_details()
            st.markdown('<div class="subsection-heading">Node state</div>', unsafe_allow_html=True)
            render_network_status()
            st.markdown('<div class="subsection-heading">Security posture</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="security-list">{security_rows()}</div>', unsafe_allow_html=True)

    render_metrics()
    path_col, event_col = st.columns([1, 1.45], gap="medium", vertical_alignment="top")
    with path_col:
        with st.container(border=True, key="path_panel"):
            render_attack_path()
    with event_col:
        with st.container(border=True, key="recent_events_panel"):
            recent = state["events"][:5]
            heading = f"Recent events · {len(state['events'])} in session"
            st.markdown(f'<div class="panel-title"><h2>{esc(heading)}</h2><span>Newest first</span></div>', unsafe_allow_html=True)
            render_event_rows(recent)


def render_events_page() -> None:
    filter_col, search_col = st.columns([0.75, 1.25], vertical_alignment="bottom")
    with filter_col:
        normalize_widget_choice("event_severity_filter", ("All", "HIGH", "MEDIUM", "INFO"), "All")
        severity_filter = st.selectbox("Severity", ("All", "HIGH", "MEDIUM", "INFO"), key="event_severity_filter")
    with search_col:
        query = st.text_input("Find an event or component", key="event_search", placeholder="Replay, MQTT, GPIO23…")
    filtered = [
        event
        for event in state["events"]
        if (severity_filter == "All" or event["severity"] == severity_filter)
        and (not query or query.lower() in " ".join(str(value) for value in event.values()).lower())
    ]
    with st.container(border=True, key="full_event_panel"):
        st.markdown(f'<div class="panel-title"><h2>Events · {len(filtered)} shown</h2><span>Newest first</span></div>', unsafe_allow_html=True)
        render_event_rows(filtered)


def render_pin_table() -> None:
    rows = []
    for pin_id, pin in PIN_DEFINITIONS.items():
        live = state["gpio"].get(pin_id, {})
        fields = (
            pin_id,
            pin["kind"],
            str(live.get("mode", pin["mode"])),
            str(live.get("state", pin["state"])),
            str(live.get("connected_to", pin["connected_to"])),
            str(live.get("security_state", pin["security_state"])),
        )
        rows.append("<tr>" + "".join(f"<td>{esc(value)}</td>" for value in fields) + "</tr>")
    st.markdown(
        f"""
        <div style="overflow-x:auto"><table class="pin-table">
          <thead><tr><th>Pin</th><th>Type</th><th>Mode</th><th>State</th><th>Connected device</th><th>Security</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table></div>
        """,
        unsafe_allow_html=True,
    )


def render_hardware_page() -> None:
    render_hardware_connection()
    board_col, detail_col = st.columns([1.4, 1], gap="large", vertical_alignment="top")
    with board_col:
        with st.container(border=True, key="hardware_board_panel"):
            st.markdown('<div class="panel-title"><h2>ESP32 DevKit-style board</h2></div>', unsafe_allow_html=True)
            render_board_selection()
    with detail_col:
        with st.container(border=True, key="hardware_posture_panel"):
            render_component_details()
            st.markdown('<div class="subsection-heading">Firmware posture</div>', unsafe_allow_html=True)
            st.markdown('<div class="panel-title"><h2>Security posture</h2><span>{}</span></div>'.format(esc(state["firmware"])), unsafe_allow_html=True)
            st.markdown('<div class="security-list">{}</div>'.format(security_rows()), unsafe_allow_html=True)
            findings = sum(not bool(state["security"][key]) for key in ("secure_boot", "flash_encryption", "ota_signing"))
            st.markdown(f'<p class="data-boundary">{findings} firmware security finding(s) in the selected profile. Pin metadata is a board-map reference, not a live electrical measurement.</p>', unsafe_allow_html=True)
    with st.container(border=True, key="pin_table_panel"):
        st.markdown('<div class="panel-title"><h2>Pin definition</h2><span>ESP32 DevKit-style reference</span></div>', unsafe_allow_html=True)
        render_pin_table()


@st.fragment(run_every=2)
def render_hardware_connection() -> None:
    """Poll serial ports on the Python host and identify a selected chip on demand."""
    with st.container(border=True, key="physical_board_connection_panel"):
        st.markdown(
            '<div class="panel-title"><h2>Physical board connection</h2><span>Local USB scan · every 2 s</span></div>',
            unsafe_allow_html=True,
        )
        ports, scan_error = list_serial_ports()
        live_ports = {port["device"] for port in ports}
        previous_identification = st.session_state.get("physical_board_identification")
        if (
            isinstance(previous_identification, dict)
            and previous_identification.get("port") not in live_ports
        ):
            st.session_state.pop("physical_board_identification", None)

        if scan_error:
            st.warning(scan_error)
        elif not ports:
            st.markdown(
                '<div class="empty-state">No USB serial ports detected on the machine running this app.</div>',
                unsafe_allow_html=True,
            )
        else:
            port_names = [port["device"] for port in ports]
            descriptions = {port["device"]: port["description"] for port in ports}
            default_port = port_names[0]
            normalize_widget_choice("physical_serial_port", port_names, default_port)
            selected_port = st.selectbox(
                "USB serial port",
                port_names,
                format_func=lambda device: f"{device} · {descriptions[device]}",
                key="physical_serial_port",
            )
            st.caption(
                "A USB serial adapter alone does not prove the chip type. Identify chip uses esptool's ROM loader; the board may reset, but flash is never written or erased."
            )
            if st.button("Identify chip", key="identify_physical_chip", type="primary"):
                with st.spinner("Reading the chip identity over USB serial…"):
                    result = identify_esp_chip(selected_port)
                st.session_state["physical_board_identification"] = {
                    **result,
                    "port": selected_port,
                }

            identification = st.session_state.get("physical_board_identification")
            if isinstance(identification, dict) and identification.get("port") == selected_port:
                status = identification.get("status")
                if status == "supported":
                    st.success(f"ESP32 · supported · {identification.get('chip', 'ESP32')}")
                elif status == "other_esp":
                    st.info(f"Other ESP · {identification.get('chip', 'unknown')} · unsupported in v0.1")
                else:
                    st.warning(identification.get("message", "Chip not identified."))

        st.caption(
            "This scan runs on the Python host. Streamlit Cloud cannot see USB devices plugged into your PC; run the app locally for hardware detection. Current attack scenarios still update only the session model and send no commands to the board."
        )


def chaos_status_class(value: str) -> str:
    normalized = value.lower()
    if any(term in normalized for term in ("offline", "failed", "critical", "invalid", "stalled", "restart loop")):
        return "bad"
    if any(term in normalized for term in ("degraded", "connecting", "delayed", "stale", "booting", "detect", "retry", "manual", "pressure", "unavailable")):
        return "warn"
    return "good"


def chaos_duration(value: object) -> str:
    if value is None:
        return "Pending"
    return f"{int(value)} simulated s"


def render_chaos_status_card(profile: str, profile_state: dict[str, Any], elapsed: int) -> None:
    statuses = profile_state.get("statuses", {})
    service_labels = (
        ("Device", "device"),
        ("Wi-Fi", "wifi"),
        ("MQTT", "mqtt"),
        ("HTTP", "http"),
        ("Sensor model", "sensor"),
        ("Recovery", "recovery"),
    )
    cells = "".join(
        f'<div class="chaos-state-cell"><span>{label}</span><strong class="{chaos_status_class(str(statuses.get(key, "UNKNOWN")))}">{esc(statuses.get(key, "UNKNOWN"))}</strong></div>'
        for label, key in service_labels
    )
    stage = str(profile_state.get("stage", "BASELINE"))
    st.markdown(
        f"""
        <section class="chaos-profile-card">
          <div class="chaos-profile-head"><strong>{esc(profile)}</strong><span class="chaos-stage-chip {chaos_status_class(stage)}">{esc(stage.replace("_", " "))}</span></div>
          <div class="chaos-status-grid">{cells}</div>
          <div class="chaos-elapsed"><span>Experiment time</span><strong>T+00:{elapsed:02d} simulated s</strong></div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_chaos_metric_strip(profile: str, metrics: dict[str, Any], *, result_ready: bool) -> None:
    score = metrics.get("resilience_score")
    cells = (
        ("Modeled availability", f"{metrics.get('modeled_availability_pct', 100):.1f}%"),
        ("Operation success", f"{metrics.get('operation_success_pct', 100):.1f}%"),
        ("Operations failed", str(metrics.get("operations_failed", 0))),
        ("Retry attempts", str(metrics.get("retry_count", 0))),
        ("Unexpected restarts", str(metrics.get("restart_count", 0))),
        ("Resilience score", str(score) if result_ready and score is not None else "Pending"),
    )
    rendered = "".join(
        f'<div class="chaos-metric"><span>{esc(label)}</span><strong>{esc(value)}</strong></div>'
        for label, value in cells
    )
    st.markdown(
        f'<div class="chaos-metric-head"><h3>{esc(profile)} · modeled metrics</h3><span>SESSION MODEL</span></div><div class="chaos-metric-grid">{rendered}</div>',
        unsafe_allow_html=True,
    )


def render_chaos_comparison(scenario: Any, profiles: dict[str, Any], result_ready: bool) -> None:
    if set(profiles) != {"Vulnerable", "Hardened"}:
        return
    metric_rows = (
        ("Modeled service availability", "modeled_availability_pct", "%"),
        ("Operation success", "operation_success_pct", "%"),
        ("Operations attempted", "operations_attempted", ""),
        ("Operations succeeded", "operations_succeeded", ""),
        ("Operations failed", "operations_failed", ""),
        ("Retry attempts", "retry_count", ""),
        ("Unexpected restarts", "restart_count", ""),
        ("Detection delay", "detection_delay_seconds", " simulated s"),
        ("Recovery duration", "recovery_duration_seconds", " simulated s"),
        ("Recovery outcome", "recovery_status", ""),
        ("Resilience score", "resilience_score", " / 100"),
    )
    rows = []
    for label, key, suffix in metric_rows:
        values = []
        for profile in ("Vulnerable", "Hardened"):
            profile_data = profiles[profile]
            metrics = profile_data.get("result") if result_ready else profile_data.get("metrics", {})
            value = metrics.get(key) if isinstance(metrics, dict) else None
            if value is None:
                formatted = "Pending" if not result_ready and key in {"recovery_duration_seconds", "resilience_score"} else "N/A"
            elif key in {"modeled_availability_pct", "operation_success_pct"}:
                formatted = f"{float(value):.1f}{suffix}"
            else:
                formatted = f"{value}{suffix}"
            values.append(f"<td>{esc(formatted)}</td>")
        rows.append(f"<tr><th scope=\"row\">{esc(label)}</th>{''.join(values)}</tr>")
    st.markdown(
        f"""
        <div class="chaos-comparison-wrap"><table class="chaos-comparison">
          <thead><tr><th scope="col">Metric · simulated</th><th scope="col">Vulnerable</th><th scope="col">Hardened</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table></div>
        <div class="chaos-profile-explanations">
          <p><strong>Vulnerable.</strong> {esc(scenario.vulnerable_behavior)}</p>
          <p><strong>Hardened.</strong> {esc(scenario.hardened_behavior)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chaos_timeline(events: list[dict[str, Any]]) -> None:
    if not events:
        st.markdown('<div class="empty-state">Start an experiment to reveal its simulated event timeline.</div>', unsafe_allow_html=True)
        return
    rows = []
    for event in events:
        severity = str(event.get("severity", "INFO")).lower()
        rows.append(
            f'<div class="chaos-timeline-row">'
            f'<time>{esc(event.get("simulated_time", ""))}</time>'
            f'<span class="chaos-profile-label">{esc(event.get("profile", ""))}</span>'
            f'<span class="severity {esc(severity)}">{esc(event.get("stage", ""))}</span>'
            f'<div class="chaos-timeline-main"><strong>{esc(event.get("event_type", ""))}</strong>'
            f'<small>{esc(event.get("component", ""))} · {esc(event.get("decision", ""))}</small>'
            f'<p>{esc(event.get("explanation", ""))}</p></div>'
            f'<div class="chaos-timeline-action"><span>Recovery action</span><strong>{esc(event.get("recovery_action", "None"))}</strong></div>'
            f'</div>'
        )
    st.markdown(f'<div class="chaos-timeline" role="list">{"".join(rows)}</div>', unsafe_allow_html=True)


def render_chaos_availability_chart(chaos: dict[str, Any]) -> None:
    rows = service_availability_series(chaos)
    if not rows or chaos.get("elapsed_seconds", 0) < 1:
        st.markdown('<div class="empty-state">The modeled availability trace will appear after the fault is injected.</div>', unsafe_allow_html=True)
        return
    chart_data = pd.DataFrame(rows)
    elapsed = max(1, int(chaos["elapsed_seconds"]))
    profiles = list(chaos["profiles"])
    colors = ["#e8bd85" if profile == "Vulnerable" else "#74dfc3" for profile in profiles]
    chart_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
        "layer": [
            {"mark": {"type": "line", "strokeWidth": 2, "clip": True}},
            {
                "transform": [{"filter": {"field": "Elapsed", "equal": elapsed}}],
                "mark": {"type": "point", "filled": True, "size": 42},
            },
        ],
        "encoding": {
            "x": {
                "field": "Elapsed",
                "type": "quantitative",
                "scale": {"domain": [0, max(10, elapsed)], "nice": False},
                "axis": {"title": "Elapsed · simulated seconds", "values": list(range(0, max(10, elapsed) + 1, 2)), "grid": False},
            },
            "y": {
                "field": "Availability",
                "type": "quantitative",
                "scale": {"domain": [0, 100], "nice": False},
                "axis": {"title": "Modeled availability (%)", "values": [0, 25, 50, 75, 100], "format": ".0f", "grid": True},
            },
            "color": {
                "field": "Profile",
                "type": "nominal",
                "scale": {"domain": profiles, "range": colors},
                "legend": {"title": None, "orient": "top", "direction": "horizontal"} if len(profiles) > 1 else False,
            },
            "tooltip": [
                {"field": "Elapsed", "type": "quantitative", "title": "Elapsed · simulated seconds", "format": ".0f"},
                {"field": "Profile", "type": "nominal", "title": "Profile"},
                {"field": "Availability", "type": "quantitative", "title": "Modeled availability", "format": ".1f"},
            ],
        },
        "config": {
            "background": "transparent",
            "view": {"stroke": None},
            "axis": {"labelColor": "#a9bcb3", "titleColor": "#a9bcb3", "labelFontSize": 11, "titleFontSize": 11, "gridColor": "#263631", "gridOpacity": 0.8},
            "legend": {"labelColor": "#a9bcb3", "labelFontSize": 11},
        },
        "padding": {"left": 0, "right": 8, "top": 2, "bottom": 0},
    }
    st.vega_lite_chart(
        chart_data,
        chart_spec,
        width="stretch",
        height=220,
        theme=None,
        key="chaos_availability_chart",
        alt="Modeled service availability over simulated experiment time for each selected profile.",
    )


@st.fragment(run_every=1)
def render_chaos_lab() -> None:
    """Render controls and the non-blocking, session-local Chaos Lab run."""
    chaos = st.session_state.device_state["chaos"]
    active = bool(chaos.get("active"))

    with st.container(border=True, key="chaos_boundary_panel"):
        st.markdown(
            '<div class="chaos-boundary"><strong>Behavioral simulation · session only</strong>'
            '<span>Failures advance on a 1 second UI timer. No broker, network, process, firmware, serial port, or GPIO is touched.</span></div>',
            unsafe_allow_html=True,
        )

    normalize_widget_choice("chaos_scenario", CHAOS_SCENARIO_IDS, CHAOS_SCENARIO_IDS[0])
    scenario_id = normalize_chaos_scenario(st.session_state.get("chaos_scenario"))
    st.session_state["chaos_scenario"] = scenario_id
    scenario = CHAOS_SCENARIOS[scenario_id]
    normalize_widget_choice("chaos_profile", PROFILE_SELECTIONS, chaos.get("profile_selection", "Vulnerable"))
    profile_selection = st.session_state.get("chaos_profile", "Vulnerable")

    with st.container(border=True, key="chaos_config_panel"):
        st.markdown('<div class="panel-title"><h2>Experiment configuration</h2><span>10 simulated seconds · 1× playback</span></div>', unsafe_allow_html=True)
        scenario_col, profile_col, parameter_col, actions_col = st.columns([1.3, 1.2, 1.0, 0.85], vertical_alignment="bottom")
        with scenario_col:
            scenario_id = st.selectbox(
                "Fault scenario",
                CHAOS_SCENARIO_IDS,
                format_func=lambda item: CHAOS_SCENARIOS[item].name,
                key="chaos_scenario",
                disabled=active,
            )
        scenario = CHAOS_SCENARIOS[scenario_id]
        with profile_col:
            profile_selection = st.radio(
                "Security profile",
                PROFILE_SELECTIONS,
                horizontal=True,
                key="chaos_profile",
                disabled=active,
                help="Run one profile or both against the same deterministic scenario.",
            )
        with parameter_col:
            if scenario.parameter_kind == "packet_loss_pct":
                if not isinstance(st.session_state.get("chaos_packet_loss"), int):
                    st.session_state["chaos_packet_loss"] = scenario.default_packet_loss_pct
                packet_loss_pct = st.slider(
                    "Modeled packet loss",
                    min_value=0,
                    max_value=50,
                    step=1,
                    key="chaos_packet_loss",
                    disabled=active,
                    format="%d%%",
                )
            else:
                packet_loss_pct = 30
                st.markdown('<div class="chaos-parameter-note"><span>Fault scope</span><strong>Fixed scenario model</strong></div>', unsafe_allow_html=True)
        with actions_col:
            if st.button("Run experiment", key="chaos_start", type="primary", use_container_width=True, disabled=active):
                start_experiment(
                    chaos,
                    scenario_id,
                    profile_selection,
                    now_monotonic=time.monotonic(),
                    packet_loss_pct=packet_loss_pct,
                )
            if st.button("Reset", key="chaos_reset", use_container_width=True):
                reset_experiment(chaos)

        st.markdown(
            f'<p class="chaos-scenario-summary"><strong>{esc(scenario.category)}</strong> · {esc(scenario.summary)}</p>',
            unsafe_allow_html=True,
        )

    if chaos.get("active"):
        started_at = chaos.get("started_at_monotonic")
        if not isinstance(started_at, (float, int)):
            started_at = time.monotonic()
            chaos["started_at_monotonic"] = float(started_at)
        advance_experiment(chaos, int(max(0, time.monotonic() - started_at)))

    stage_order = ("BASELINE", "FAULT_INJECTED", "DEGRADED", "RECOVERING", "RECOVERED", "COMPLETE")
    stage_alias = {"FAILED_TO_RECOVER": "RECOVERED"}
    selected_stage = stage_alias.get(str(chaos.get("stage", "IDLE")), str(chaos.get("stage", "IDLE")))
    current_index = stage_order.index(selected_stage) if selected_stage in stage_order else -1
    step_markup = []
    for index, stage in enumerate(stage_order):
        css = "current" if index == current_index else "past" if index < current_index else ""
        if chaos.get("stage") == "FAILED_TO_RECOVER" and stage == "RECOVERED":
            css = "failed"
        step_markup.append(f'<span class="chaos-step {css}">{esc(stage.replace("_", " "))}</span>')
    st.markdown(f'<div class="chaos-lifecycle">{"".join(step_markup)}</div>', unsafe_allow_html=True)

    if chaos.get("scenario_id"):
        active_scenario = CHAOS_SCENARIOS.get(chaos["scenario_id"], scenario)
        profiles = chaos.get("profiles", {})
        selected_profiles = list(profiles)
        left_col, right_col = st.columns([1.1, 1], gap="medium", vertical_alignment="top")
        with left_col:
            with st.container(border=True, key="chaos_board_panel"):
                st.markdown('<div class="panel-title"><h2>Logical impact path</h2><span>ESP32 board illustration</span></div>', unsafe_allow_html=True)
                clicked = render_board(
                    selected=state["selected_component"],
                    active_path=chaos.get("board_path", []) if chaos.get("experiment_id") else [],
                    pin_states=state["gpio"],
                    height=424,
                )
                component_options = set(PIN_DEFINITIONS) | set(BOARD_COMPONENTS)
                if clicked in component_options:
                    state["selected_component"] = clicked
                    st.session_state["component_picker"] = clicked
                st.markdown(
                    f'<p class="chaos-board-note">Affected logical components: {esc(" → ".join(active_scenario.board_path))}. This highlights a representative board path; it does not alter pin metadata or show electrical measurements.</p>',
                    unsafe_allow_html=True,
                )
        with right_col:
            with st.container(border=True, key="chaos_live_panel"):
                st.markdown(
                    f'<div class="panel-title"><h2>Live node state</h2><span>{esc(chaos.get("stage", "IDLE").replace("_", " "))} · SESSION MODEL</span></div>',
                    unsafe_allow_html=True,
                )
                if not selected_profiles:
                    idle = {"stage": "BASELINE", "statuses": chaos.get("baseline_snapshot", {}), "metrics": {}}
                    render_chaos_status_card("Baseline", idle, int(chaos.get("elapsed_seconds", 0)))
                else:
                    for profile in selected_profiles:
                        render_chaos_status_card(profile, profiles[profile], int(chaos.get("elapsed_seconds", 0)))
                st.markdown(
                    f'<p class="chaos-explanation">{esc(active_scenario.educational_explanation)}</p>'
                    f'<p class="chaos-policy"><strong>Recovery policy.</strong> {esc(active_scenario.recovery_policy)}</p>',
                    unsafe_allow_html=True,
                )

        chart_col, detail_col = st.columns([1.3, 1], gap="medium", vertical_alignment="top")
        with chart_col:
            with st.container(border=True, key="chaos_chart_panel"):
                st.markdown('<div class="panel-title"><h2>Service availability</h2><span>MODELED · BY SIMULATED SECOND</span></div>', unsafe_allow_html=True)
                render_chaos_availability_chart(chaos)
                st.markdown('<p class="chaos-footnote">Availability is integrated over the experiment timeline. The initial baseline second is included.</p>', unsafe_allow_html=True)
        with detail_col:
            with st.container(border=True, key="chaos_metrics_panel"):
                st.markdown('<div class="panel-title"><h2>Resilience metrics</h2><span>MODEL OUTPUT</span></div>', unsafe_allow_html=True)
                if selected_profiles:
                    for profile in selected_profiles:
                        profile_state = profiles[profile]
                        metric_values = profile_state.get("result") or profile_state.get("metrics", {})
                        render_chaos_metric_strip(profile, metric_values, result_ready=bool(chaos.get("result")))
                else:
                    st.markdown('<div class="empty-state">Metrics begin when an experiment runs.</div>', unsafe_allow_html=True)

        with st.container(border=True, key="chaos_comparison_panel"):
            heading = "Vulnerable vs Hardened" if len(profiles) == 2 else "Profile outcome"
            st.markdown(f'<div class="panel-title"><h2>{heading}</h2><span>{"FINAL MODEL COMPARISON" if chaos.get("result") else "LIVE MODEL COMPARISON"}</span></div>', unsafe_allow_html=True)
            if len(profiles) == 2:
                render_chaos_comparison(active_scenario, profiles, bool(chaos.get("result")))
            elif selected_profiles:
                profile = selected_profiles[0]
                behavior = active_scenario.vulnerable_behavior if profile == "Vulnerable" else active_scenario.hardened_behavior
                st.markdown(f'<p class="chaos-profile-explanation"><strong>{esc(profile)} profile behavior.</strong> {esc(behavior)}</p>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty-state">Run both profiles to compare their recovery behavior.</div>', unsafe_allow_html=True)

        with st.container(border=True, key="chaos_timeline_panel"):
            timeline = chaos.get("timeline", [])
            st.markdown(
                f'<div class="panel-title"><h2>Experiment timeline · {len(timeline)} events</h2><span>OLDEST FIRST · SIMULATED TIME</span></div>',
                unsafe_allow_html=True,
            )
            render_chaos_timeline(timeline)

        st.markdown(
            '<p class="chaos-score-note">The model-specific score is 45% modeled service availability + 35% operation success + 20% recovery outcome (100 if recovered within the run, otherwise 0). It is an educational comparison metric, not a certification or measured device result.</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="chaos-ready"><div><strong>Fault catalog · {len(CHAOS_SCENARIOS)} scenarios</strong><span>{esc(scenario.educational_explanation)}</span></div>'
            f'<div><strong>Target · ESP32 IoT node behavioral model</strong><span>Vulnerable and Hardened are separate model policies. No physical execution mode is available in this release.</span></div></div>',
            unsafe_allow_html=True,
        )


render_topbar()
view = st.session_state.active_view
render_title(view)

if view == "Console":
    render_controls()
    render_overview()
elif view == "Events":
    render_metrics()
    render_events_page()
elif view == "Hardware":
    render_hardware_page()
else:
    render_chaos_lab()
