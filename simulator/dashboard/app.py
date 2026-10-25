"""VIGIL-IoT / SPECTRA-32 Streamlit node and security console."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from typing import Any

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.dashboard.board import render_board_component  # noqa: E402
from simulator.dashboard.security_model import (  # noqa: E402
    HARDENED_MODE,
    SIMULATION_EVENTS,
    VULNERABLE_MODE,
    apply_profile,
    apply_simulated_event,
    create_device_state,
    sync_backend,
)


API_BASE = "http://127.0.0.1:8080"
API_TIMEOUT_SECONDS = 1.5


def read_state() -> tuple[dict[str, Any] | None, str | None]:
    """Read the loopback-only node model's current state."""
    request = Request(f"{API_BASE}/api/state", headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=API_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return None, f"Model API returned HTTP {exc.code}."
    except (URLError, TimeoutError, OSError) as exc:
        return None, f"Cannot reach the local behavior model ({exc})."
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "The behavior model returned an invalid state response."

    if not isinstance(payload, dict):
        return None, "The behavior model returned an invalid state response."
    return payload, None


def set_led(output_state: str) -> tuple[dict[str, Any] | None, str | None]:
    """Send the selected virtual LED command to the loopback node model."""
    body = urlencode({"state": output_state}).encode("ascii")
    request = Request(
        f"{API_BASE}/api/led",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=API_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return None, f"Model API rejected the command (HTTP {exc.code})."
    except (URLError, TimeoutError, OSError) as exc:
        return None, f"Could not send the command to the local behavior model ({exc})."
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "The behavior model returned an invalid command response."

    if not isinstance(payload, dict):
        return None, "The behavior model returned an invalid command response."
    return payload, None


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] { background: #0d1b2a; }
        [data-testid="stHeader"] { background: transparent; }
        .block-container { max-width: 1580px; padding-top: 1.25rem; padding-bottom: 2.5rem; }
        section[data-testid="stSidebar"] { background: #102333; border-right: 1px solid #2a4052; }
        section[data-testid="stSidebar"] .block-container { padding-top: 1.1rem; }
        .brand { color: #55c2bd; font-size: .78rem; font-weight: 700; letter-spacing: .07em; }
        .brand strong { color: #eef3f4; font-size: 1.15rem; letter-spacing: -.025em; margin-right: .55rem; }
        .app-title { color: #eef3f4; font-size: 1.9rem; font-weight: 740; letter-spacing: -.045em; margin: .25rem 0 .1rem; }
        .app-subtitle { color: #a8bac4; font-size: .95rem; margin: 0 0 .9rem; }
        .status-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: .65rem; margin: .7rem 0 1rem; }
        .status-card { min-height: 82px; background: #14283a; border: 1px solid #2a4052; border-radius: 12px; padding: .7rem .8rem; }
        .status-label { color: #9eb2bc; display: block; font-size: .72rem; margin-bottom: .28rem; }
        .status-value { color: #eef3f4; display: block; font-size: .95rem; font-weight: 700; overflow-wrap: anywhere; }
        .status-detail { color: #91a5ad; display: block; font-size: .7rem; margin-top: .2rem; }
        .status-online { color: #70d1c8; } .status-offline { color: #e4ae58; }
        .panel-title { color: #55c2bd; font-size: .82rem; font-weight: 700; letter-spacing: .04em; margin: .15rem 0 .55rem; }
        .surface { background: #14283a; border: 1px solid #2a4052; border-radius: 14px; padding: 1rem; }
        .surface + .surface { margin-top: .8rem; }
        .posture-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .45rem; }
        .posture-item { display: flex; align-items: center; justify-content: space-between; gap: .5rem; padding: .55rem .65rem; border: 1px solid #2a4052; border-radius: 9px; background: #102333; }
        .posture-name { color: #c5d2d6; font-size: .8rem; }
        .posture-state { font-size: .73rem; font-weight: 700; }
        .posture-state.enabled { color: #70d1c8; } .posture-state.disabled { color: #e4ae58; }
        .path-row { display: flex; flex-wrap: wrap; align-items: center; gap: .35rem; }
        .path-node { color: #bdcbd0; border: 1px solid #304854; border-radius: 999px; background: #102333; padding: .35rem .55rem; font-size: .76rem; }
        .path-node.active-normal, .path-node.active-defended { color: #a8f0e8; border-color: #438981; background: #133633; }
        .path-node.active-warning { color: #ffdb9b; border-color: #a77934; background: #382d1d; }
        .path-arrow { color: #718792; font-size: .82rem; }
        .event-log { max-height: 350px; overflow-y: auto; padding-right: .2rem; }
        .event-row { display: grid; grid-template-columns: 70px 78px minmax(0, 1fr); gap: .55rem; padding: .65rem 0; border-top: 1px solid #2a4052; }
        .event-time { color: #95aab4; font-size: .75rem; font-variant-numeric: tabular-nums; }
        .event-severity { font-size: .7rem; font-weight: 750; letter-spacing: .025em; }
        .severity-info { color: #70d1c8; } .severity-medium { color: #e4ae58; }
        .severity-high, .severity-critical { color: #ff8b7a; }
        .event-name { color: #eef3f4; font-size: .82rem; font-weight: 700; }
        .event-detail { color: #a8bac4; font-size: .75rem; line-height: 1.45; margin-top: .15rem; }
        .simulation-note { color: #cbd7dc; background: #1d2931; border-left: 3px solid #e4ae58; border-radius: 0 8px 8px 0; padding: .7rem .8rem; font-size: .8rem; line-height: 1.5; }
        [data-testid="stMetric"] { background: #14283a; border: 1px solid #2a4052; border-radius: 12px; padding: .7rem .8rem; }
        [data-testid="stMetricLabel"] { color: #a8bac4; font-size: .73rem; }
        [data-testid="stMetricValue"] { color: #eef3f4; font-size: 1.2rem !important; font-variant-numeric: tabular-nums; }
        .stButton button { min-height: 2.55rem; border-radius: 9px; font-weight: 650; }
        button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primary"] p { color: #082129 !important; }
        @media(max-width: 1000px) { .status-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
        @media(max-width: 640px) { .status-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .posture-list { grid-template-columns: 1fr; } .event-row { grid-template-columns: 62px 68px minmax(0,1fr); gap: .35rem; } .app-title { font-size: 1.55rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session() -> None:
    if "device_state" not in st.session_state:
        st.session_state.device_state = create_device_state()
    if "security_mode" not in st.session_state:
        st.session_state.security_mode = VULNERABLE_MODE
    if "simulation_enabled" not in st.session_state:
        st.session_state.simulation_enabled = True


def render_sidebar(state: dict[str, Any]) -> tuple[str, bool, str, bool, str | None]:
    with st.sidebar:
        st.markdown(
            '<div class="brand"><strong>◈ SPECTRA-32</strong><br>A VIGIL-IoT Project</div>',
            unsafe_allow_html=True,
        )
        st.divider()
        mode = st.radio(
            "Security profile",
            (VULNERABLE_MODE, HARDENED_MODE),
            key="security_mode",
            help="This selector changes the dashboard's simulated security profile only.",
        )
        simulation_enabled = st.toggle(
            "Simulation mode",
            key="simulation_enabled",
            help="Events update in-app state only. They do not send packets or issue MQTT attacks.",
        )
        with st.form("security_event_form", clear_on_submit=False):
            event_type = st.selectbox("Simulated event", SIMULATION_EVENTS)
            event_submitted = st.form_submit_button(
                "Run in-app simulation",
                type="primary",
                width="stretch",
                disabled=not simulation_enabled,
            )
        st.caption("Local state simulation only · no attack traffic is generated.")
        st.divider()
        st.markdown('<div class="panel-title">Virtual GPIO4 LED</div>', unsafe_allow_html=True)
        led_on, led_off = st.columns(2, gap="small")
        with led_on:
            on_clicked = st.button(
                "Set ON",
                type="primary",
                width="stretch",
                disabled=not state["online"],
                key="set_led_on",
            )
        with led_off:
            off_clicked = st.button(
                "Set OFF",
                width="stretch",
                disabled=not state["online"],
                key="set_led_off",
            )
        if not state["online"]:
            st.caption("Start the loopback Python node model to enable physical-model API controls.")
        st.divider()
        st.caption("This is a host-side model. It does not run ESP32 firmware or control physical hardware.")

    led_action = "on" if on_clicked else "off" if off_clicked else None
    return mode, simulation_enabled, event_type, event_submitted, led_action


def status_card(label: str, value: object, detail: object = "", value_class: str = "") -> str:
    return (
        '<div class="status-card">'
        f'<span class="status-label">{escape(label)}</span>'
        f'<span class="status-value {escape(value_class)}">{escape(str(value))}</span>'
        f'<span class="status-detail">{escape(str(detail))}</span>'
        "</div>"
    )


def render_status_row(state: dict[str, Any], mode: str) -> None:
    online = bool(state["online"])
    wifi = state["wifi"]
    mqtt = state["mqtt"]
    security = state["security"]
    status_cards = [
        status_card("Node ID", state["node_id"], "Virtual SPECTRA-32 node"),
        status_card("Node state", "ONLINE" if online else "OFFLINE", "Loopback model API", "status-online" if online else "status-offline"),
        status_card("Firmware profile", state["firmware"], f"{mode} · simulated"),
        status_card("Wi-Fi", "Connected" if wifi["connected"] else "Offline", f"{wifi['ssid']} · simulated"),
        status_card(
            "MQTT",
            "Connected" if mqtt["connected"] else "Disconnected",
            "TLS required in hardened profile (simulated)" if mqtt["tls_required_by_profile"] else "Local model uses plaintext MQTT",
            "status-online" if mqtt["connected"] else "status-offline",
        ),
    ]
    st.markdown('<div class="status-grid">' + "".join(status_cards) + "</div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="simulation-note"><strong>Simulation boundary.</strong> The profile and security events below are in-memory scenarios. '
        'Only the GPIO4 ON/OFF control talks to the loopback behavior model; no attack packets are sent and no physical output is controlled.</div>',
        unsafe_allow_html=True,
    )


def render_metrics(state: dict[str, Any]) -> None:
    security = state["security"]
    accepted = state["api"]["commands_applied"] + security["simulated_accepted_commands"]
    columns = st.columns(6, gap="small")
    metrics = (
        ("Replay attempts", security["replay_attempts"]),
        ("Auth failures", security["auth_failures"]),
        ("Blocked commands", security["blocked_commands"]),
        ("Accepted commands", accepted),
        ("Current request rate", f"{security['request_rate']} req/s"),
        ("Threat level", security["threat_level"]),
    )
    for column, (label, value) in zip(columns, metrics):
        with column:
            st.metric(label, value)


def render_attack_path(state: dict[str, Any]) -> None:
    event = state["events"][0] if state["events"] else None
    path = event["path"] if event else ["Wi-Fi", "ESP32 module", "MQTT", "GPIO23", "Relay"]
    status = state["active_path_status"] if event else "neutral"
    nodes: list[str] = []
    for index, node in enumerate(path):
        class_suffix = f" active-{status}" if status in {"normal", "warning", "defended"} else ""
        nodes.append(f'<span class="path-node{class_suffix}">{escape(str(node))}</span>')
        if index < len(path) - 1:
            nodes.append('<span class="path-arrow" aria-hidden="true">→</span>')
    if event:
        explanation = f"{event['decision']} · {event['component']} · {event['explanation']}"
    else:
        explanation = "Default node-to-actuator route · waiting for a simulated event."
    st.markdown(
        '<div class="surface"><div class="panel-title">Attack path · cyber-physical route</div>'
        f'<div class="path-row">{"".join(nodes)}</div>'
        f'<p class="event-detail">{escape(explanation)}</p></div>',
        unsafe_allow_html=True,
    )


def render_posture(state: dict[str, Any]) -> None:
    security = state["security"]
    controls = (
        ("Replay protection", security["replay_protection"]),
        ("Secure Boot", security["secure_boot"]),
        ("Flash encryption", security["flash_encryption"]),
        ("OTA signing", security["ota_signing"]),
        ("UART debug restricted", not security["debug_interface_enabled"]),
        ("MQTT TLS profile", state["mqtt"]["tls_required_by_profile"]),
    )
    rows = []
    for label, enabled in controls:
        state_label = "Enabled" if enabled else "Disabled"
        rows.append(
            f'<div class="posture-item"><span class="posture-name">{escape(label)}</span>'
            f'<span class="posture-state {"enabled" if enabled else "disabled"}">{state_label}</span></div>'
        )
    st.markdown(
        '<div class="surface"><div class="panel-title">Security posture · profile simulation</div>'
        f'<div class="posture-list">{"".join(rows)}</div>'
        '<p class="event-detail">Changing these values does not reconfigure the loopback MQTT broker or the separate node process.</p></div>',
        unsafe_allow_html=True,
    )


def render_event_log(state: dict[str, Any]) -> None:
    events = state["events"]
    if not events:
        body = '<div class="event-detail">No events yet. Enable Simulation mode and run a local scenario.</div>'
    else:
        rows = []
        for event in events[:20]:
            severity = str(event["severity"]).lower()
            rows.append(
                '<div class="event-row">'
                f'<span class="event-time">{escape(str(event["time"]))}</span>'
                f'<span class="event-severity severity-{escape(severity)}">{escape(str(event["severity"]))}</span>'
                '<div>'
                f'<div class="event-name">{escape(str(event["event_type"]))} · {escape(str(event["decision"]))}</div>'
                f'<div class="event-detail">{escape(str(event["component"]))} — {escape(str(event["explanation"]))}</div>'
                '</div></div>'
            )
        body = '<div class="event-log">' + "".join(rows) + "</div>"
    st.markdown(
        '<div class="surface"><div class="panel-title">Security event log</div>' + body + '</div>',
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="SPECTRA-32 Node Console · VIGIL-IoT",
        page_icon="◈",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_theme()
    initialize_session()

    state = st.session_state.device_state
    backend_state, api_error = read_state()
    state = sync_backend(state, backend_state, api_error)
    mode, simulation_enabled, event_type, event_submitted, led_action = render_sidebar(state)
    state = apply_profile(state, mode)

    action_error = None
    if event_submitted and simulation_enabled:
        state = apply_simulated_event(state, event_type, mode)
        st.toast(f"Simulated: {event_type}")

    if led_action:
        updated_state, action_error = set_led(led_action)
        if updated_state is not None:
            state = sync_backend(state, updated_state, None)
            st.toast(f"Virtual GPIO4 LED set to {updated_state.get('led', led_action.upper())}.")

    st.session_state.device_state = state
    st.markdown(
        '<div class="brand"><strong>VIGIL-IoT</strong> Vulnerability Intelligence &amp; Guarding for IoT Layers</div>'
        '<h1 class="app-title">SPECTRA-32 Node Console</h1>'
        '<p class="app-subtitle">Visual device console and security monitor · <strong>A VIGIL-IoT Project</strong></p>',
        unsafe_allow_html=True,
    )

    render_status_row(state, mode)
    if api_error:
        st.warning("The local node API is unavailable. In-app security simulations still work; GPIO4 controls are disabled.")
    if action_error:
        st.error(action_error)

    st.markdown('<div class="panel-title">Security telemetry</div>', unsafe_allow_html=True)
    render_metrics(state)

    st.markdown('<div class="panel-title">Interactive ESP32 board · select any pin or component</div>', unsafe_allow_html=True)
    st.iframe(
        render_board_component(state, mode),
        height=790,
    )

    left, right = st.columns([1.05, .95], gap="medium")
    with left:
        render_attack_path(state)
    with right:
        render_posture(state)

    render_event_log(state)
    st.divider()
    st.caption(
        "Vulnerable/Hardened profiles and security events are dashboard simulations. "
        "Only the virtual GPIO4 command uses the loopback node API. No real attack traffic is generated."
    )


if __name__ == "__main__":
    main()
