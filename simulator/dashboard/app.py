"""VIGIL-IoT / SPECTRA-32 local device console and security simulation."""

from __future__ import annotations

import html
from pathlib import Path
import sys
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
CSS = (ROOT / "assets" / "app.css").read_text(encoding="utf-8")

from components.board import render_board  # noqa: E402
from data.board_definition import BOARD_COMPONENTS, PIN_DEFINITIONS, VIRTUAL_COMPONENTS  # noqa: E402
from data.device_state import DeviceState, create_initial_state  # noqa: E402
from data.scenarios import SCENARIO_GUIDANCE  # noqa: E402
from services.simulator import (  # noqa: E402
    SCENARIOS,
    log_profile_change,
    set_security_mode,
    set_simulation_mode,
    simulate_event,
)


st.set_page_config(
    page_title="SPECTRA-32 Node Console · VIGIL-IoT",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

if (
    "device_state" not in st.session_state
    or not isinstance(st.session_state.device_state, dict)
    or "mode" not in st.session_state.device_state
):
    # Reset legacy session data when Streamlit reloads from the earlier console schema.
    st.session_state.device_state = create_initial_state()
if "active_view" not in st.session_state:
    st.session_state.active_view = "Console"
state: DeviceState = st.session_state.device_state
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
        st.radio(
            "Primary view",
            ("Console", "Events", "Hardware"),
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
              <span class="sample-stamp">NO LIVE DEVICE</span>
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
            "Inspect the board map, pin metadata, and simulated component posture.",
            "ESP32 · DevKit-style map",
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
        st.session_state.setdefault("security_profile", state["mode"])
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
        enabled = st.toggle(
            "Simulation Mode",
            key="simulation_mode_toggle",
            value=state["simulation_mode"],
            help="Applies one bounded event to this session's model. No network traffic is generated.",
        )
    set_simulation_mode(state, enabled)

    with scenario_col:
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
          <div class="network-cell"><span>Wi-Fi · {'Sample connected' if wifi['connected'] else 'Sample offline'}</span><strong>{esc(wifi_value)}</strong></div>
          <div class="network-cell"><span>MQTT · {'Sample connected' if mqtt['connected'] else 'Sample offline'}</span><strong><span class="state-chip {mqtt_class}">{esc(mqtt_value)}</span></strong></div>
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
    st.session_state.setdefault("component_picker", state["selected_component"])
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
        <p class="data-boundary">Initial counters use the sample values in the brief. Controls update this session only; no traffic reaches a device or broker.</p>
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
    caption = "Highlighted route from the latest simulated event." if active else "Example command route; run a scenario to highlight its affected path."
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


def render_overview() -> None:
    board_col, detail_col = st.columns([1.4, 1], gap="large", vertical_alignment="top")
    with board_col:
        with st.container(border=True, key="board_panel"):
            st.markdown(
                '<div class="panel-title"><h2>Interactive ESP32 DevKit</h2><span>Select a pin · swipe to pan</span></div>',
                unsafe_allow_html=True,
            )
            render_board_selection()
    with detail_col:
        with st.container(border=True, key="node_panel"):
            render_component_details()
            st.markdown('<div class="subsection-heading">Node state</div>', unsafe_allow_html=True)
            render_network_status()
            st.markdown('<div class="subsection-heading">Security posture</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="security-list">{security_rows()}</div>', unsafe_allow_html=True)

    render_metrics()
    path_col, event_col = st.columns([0.9, 1.6], gap="large", vertical_alignment="top")
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
    board_col, detail_col = st.columns([1.4, 1], gap="large", vertical_alignment="top")
    with board_col:
        with st.container(border=True, key="hardware_board_panel"):
            st.markdown('<div class="panel-title"><h2>ESP32 DevKit-style board</h2><span>32 pins · swipe to pan</span></div>', unsafe_allow_html=True)
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


render_topbar()
view = st.session_state.active_view
render_title(view)
render_controls()

if view == "Console":
    render_overview()
elif view == "Events":
    render_metrics()
    render_events_page()
else:
    render_hardware_page()
