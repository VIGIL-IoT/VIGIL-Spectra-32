"""Streamlit console for the loopback-only SPECTRA-32 behavior model."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st


API_BASE = "http://127.0.0.1:8080"
API_TIMEOUT_SECONDS = 1.5


def read_state() -> tuple[dict[str, object] | None, str | None]:
    """Read state from the local behavioral-model HTTP API."""
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


def set_led(state: str) -> tuple[dict[str, object] | None, str | None]:
    """Send one UI command to the local REST API."""
    body = urlencode({"state": state}).encode("ascii")
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
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(ellipse at 78% 0%, #163449 0%, transparent 38%),
                #0d1b2a;
        }
        [data-testid="stHeader"] { background: transparent; }
        .block-container { max-width: 1320px; padding-top: 2.3rem; padding-bottom: 3rem; }
        .brand-line { color: #55c2bd; font-size: .73rem; font-weight: 750;
            letter-spacing: .17em; text-transform: uppercase; }
        .hero-row { display: flex; align-items: flex-end; justify-content: space-between;
            gap: 1.5rem; margin: .55rem 0 1.25rem; }
        .hero-title { margin: 0; color: #eef3f4; font-size: clamp(2.3rem, 6vw, 4rem);
            font-weight: 760; letter-spacing: -.055em; line-height: 1; }
        .hero-subtitle { margin: .65rem 0 0; color: #a8bac4; font-size: 1rem; }
        .mode-tag { border: 1px solid #456071; border-radius: 999px; color: #c8d6dc;
            display: inline-flex; align-items: center; gap: .55rem; padding: .55rem .8rem;
            font-size: .76rem; font-weight: 700; letter-spacing: .08em; white-space: nowrap; }
        .mode-dot { width: .48rem; height: .48rem; border-radius: 50%; background: #e4ae58;
            box-shadow: 0 0 12px #e4ae5877; }
        .scope-band { border: 1px solid #705d3a; border-left: 3px solid #e4ae58;
            border-radius: 10px; background: #1d2931; color: #c7d0d3; padding: .9rem 1rem;
            margin: .4rem 0 1.2rem; font-size: .88rem; }
        .scope-band strong { color: #f0c875; }
        .panel-heading { color: #a8bac4; font-size: .7rem; font-weight: 750;
            letter-spacing: .13em; text-transform: uppercase; margin-bottom: .45rem; }
        .led-state { display: flex; align-items: center; gap: 1rem; min-height: 112px; }
        .led-orb { flex: 0 0 auto; width: 54px; height: 54px; border-radius: 50%;
            border: 1px solid #516776; background: #52616a; }
        .led-orb.on { border-color: #72d7cf; background: #55c2bd;
            box-shadow: 0 0 14px #55c2bd99, 0 0 42px #55c2bd55; }
        .led-orb.unknown { border-color: #e4ae58; background: #4f493e; }
        .led-kicker { display: block; color: #a8bac4; font-size: .73rem;
            letter-spacing: .12em; text-transform: uppercase; }
        .led-value { display: block; color: #eef3f4; font-size: 2.1rem;
            font-weight: 750; letter-spacing: -.04em; line-height: 1.2; }
        .link-state { display: inline-flex; align-items: center; gap: .55rem;
            color: #eef3f4; font-weight: 650; }
        .link-dot { width: .56rem; height: .56rem; border-radius: 50%; background: #788791; }
        .link-dot.connected { background: #55c2bd; box-shadow: 0 0 10px #55c2bd88; }
        .detail-label { color: #a8bac4; font-size: .76rem; margin-bottom: .3rem; }
        .detail-value { color: #eef3f4; font-size: .92rem; font-weight: 600; }
        .stButton button { min-height: 2.85rem; border-radius: 9px; font-weight: 650; }
        [data-testid="stMetric"] { background: #14283a; border: 1px solid #2a4052;
            border-radius: 12px; padding: .9rem 1rem; }
        [data-testid="stMetricLabel"] { color: #a8bac4; }
        hr { border-color: #2a4052; }
        @media (max-width: 680px) {
            .hero-row { align-items: flex-start; flex-direction: column; }
            .block-container { padding-left: 1rem; padding-right: 1rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_output(state: dict[str, object] | None) -> None:
    if state is None:
        label, class_name = "NO DATA", "unknown"
    else:
        led_on = state.get("led") == "ON"
        label, class_name = ("ON", "on") if led_on else ("OFF", "off")

    st.markdown(
        f"""
        <div class="led-state">
            <span class="led-orb {class_name}" aria-hidden="true"></span>
            <span>
                <span class="led-kicker">Virtual LED output</span>
                <strong class="led-value">{label}</strong>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard() -> None:
    state, error = read_state()
    last_sync = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")

    mqtt_connected = bool(state and state.get("mqtt_connected"))
    connection_label = "Connected" if mqtt_connected else "Disconnected"
    connection_class = "connected" if mqtt_connected else ""

    output_column, links_column = st.columns([1.35, 1], gap="large")
    with output_column:
        st.markdown('<div class="panel-heading">Device output</div>', unsafe_allow_html=True)
        with st.container(border=True):
            output_slot = st.empty()
            button_on, button_off = st.columns(2)
            with button_on:
                on_clicked = st.button(
                    "Set output ON",
                    type="primary",
                    width="stretch",
                    disabled=state is None,
                    key="virtual_led_on",
                )
            with button_off:
                off_clicked = st.button(
                    "Set output OFF",
                    width="stretch",
                    disabled=state is None,
                    key="virtual_led_off",
                )

            if on_clicked or off_clicked:
                state, action_error = set_led("on" if on_clicked else "off")
                if action_error:
                    st.error(action_error)
                else:
                    st.toast(f"Virtual output set to {state.get('led', 'updated')}.")

            with output_slot.container():
                render_output(state)

    with links_column:
        st.markdown('<div class="panel-heading">Local links</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="link-state">
                    <span class="link-dot {connection_class}" aria-hidden="true"></span>
                    <span>MQTT {connection_label}</span>
                </div>
                <div style="height:1rem"></div>
                <div class="detail-label">Broker</div>
                <div class="detail-value">127.0.0.1:1883 · loopback</div>
                <div style="height:.8rem"></div>
                <div class="detail-label">Model API</div>
                <div class="detail-value">127.0.0.1:8080 · HTTP</div>
                """,
                unsafe_allow_html=True,
            )

    if error:
        st.warning(
            "Behavior model unavailable. Start Mosquitto and the Python node model "
            "in separate terminals; this dashboard connects to 127.0.0.1:8080."
        )

    st.markdown("### Model telemetry")
    metrics = st.columns(3)
    with metrics[0]:
        st.metric("Commands applied", state.get("commands_applied", "—") if state else "—")
    with metrics[1]:
        st.metric("Runtime", "Host model" if state else "Unavailable")
    with metrics[2]:
        st.metric("Last state poll", last_sync)


def main() -> None:
    st.set_page_config(
        page_title="SPECTRA-32 · VIGIL-IoT",
        page_icon="◈",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_theme()

    st.markdown('<div class="brand-line">A VIGIL-IoT Project · Embedded Security Research</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero-row">
            <div>
                <h1 class="hero-title">SPECTRA-32</h1>
                <p class="hero-subtitle">Virtual ESP32 device console</p>
            </div>
            <div class="mode-tag"><span class="mode-dot"></span>SOFTWARE MODEL · V0.1</div>
        </div>
        <div class="scope-band"><strong>Simulation boundary.</strong>
            This dashboard controls a host-side behavior model. No ESP32 firmware,
            Wi-Fi radio, GPIO, or physical output is running here.</div>
        """,
        unsafe_allow_html=True,
    )

    @st.fragment(run_every=2.0, key="device_dashboard")
    def live_device_panel() -> None:
        render_dashboard()

    live_device_panel()
    st.divider()
    st.caption(
        "Build → Attack → Observe → Defend → Measure  ·  Vulnerable baseline  ·  "
        "Commands use the loopback API and update the virtual LED state."
    )


if __name__ == "__main__":
    main()
