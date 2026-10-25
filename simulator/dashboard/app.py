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


def make_board_svg(led_state: object) -> str:
    """Draw a schematic DevKit-style board with the modeled GPIO4 output."""
    left_pins = (
        "3V3", "EN", "VP / 36", "VN / 39", "GPIO34", "GPIO35", "GPIO32",
        "GPIO33", "GPIO25", "GPIO26", "GPIO27", "GPIO14", "GPIO12", "GND", "GPIO13",
    )
    right_pins = (
        "VIN / 5V", "GND", "GPIO23", "GPIO22", "TX0 / 1", "RX0 / 3", "GPIO21",
        "GND", "GPIO19", "GPIO18", "GPIO5", "GPIO17", "GPIO16", "GPIO4", "GPIO2",
    )
    led_on = led_state == "ON"
    led_unknown = led_state != "ON" and led_state != "OFF"
    led_color = "#55c2bd" if led_on else "#e4ae58" if led_unknown else "#53616b"
    led_halo = (
        '<circle cx="574" cy="390" r="18" fill="#55c2bd" opacity=".18"/>'
        '<circle cx="574" cy="390" r="11" fill="#55c2bd" opacity=".3"/>'
        if led_on
        else ""
    )
    led_label = "ON" if led_on else "NO LINK" if led_unknown else "OFF"
    pin_markup: list[str] = []

    for index, (left_label, right_label) in enumerate(zip(left_pins, right_pins)):
        y = 110 + index * 24
        gpio4 = right_label == "GPIO4"
        pad_color = "#55c2bd" if gpio4 else "#c28d45"
        text_color = "#75d8d0" if gpio4 else "#a8bac4"
        pin_markup.append(
            f'<g><text x="244" y="{y + 4}" text-anchor="end" class="pin">{left_label}</text>'
            f'<rect x="266" y="{y - 4}" width="22" height="8" rx="2" class="pad"/>'
            f'<g><rect x="652" y="{y - 4}" width="22" height="8" rx="2" '
            f'fill="{pad_color}" class="pad"/><text x="697" y="{y + 4}" '
            f'fill="{text_color}" class="pin">{right_label}</text></g></g>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 600"
        role="img" aria-label="ESP32 DevKit-style virtual board with GPIO4 LED state {led_label}"
        style="display:block;width:100%;height:auto;font-family:system-ui,sans-serif">
        <defs>
            <linearGradient id="pcb" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stop-color="#1a4743"/><stop offset="1" stop-color="#12302f"/>
            </linearGradient>
            <linearGradient id="shield" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stop-color="#48555d"/><stop offset="1" stop-color="#29343b"/>
            </linearGradient>
            <style>
                .pin {{ fill:#a8bac4;font-size:10px;font-weight:600;letter-spacing:.2px }}
                .pad {{ stroke:#e0b46c;stroke-width:1 }}
                .board-label {{ fill:#d5e0e2;font-size:10px;font-weight:700;letter-spacing:1.3px }}
                .micro {{ fill:#91a5ad;font-size:8px;font-weight:600;letter-spacing:.7px }}
            </style>
        </defs>
        <rect x="281" y="31" width="378" height="482" rx="24" fill="#06121b" opacity=".56"/>
        <rect x="274" y="24" width="378" height="482" rx="24" fill="url(#pcb)"
            stroke="#39716a" stroke-width="2"/>
        <rect x="285" y="35" width="356" height="460" rx="17" fill="none"
            stroke="#68a198" stroke-opacity=".25"/>
        {''.join(pin_markup)}

        <text x="463" y="68" text-anchor="middle" class="micro">2.4 GHz ANTENNA</text>
        <path d="M420 77h86m-79 8h72m-65 8h58" stroke="#7ba89f" stroke-width="2" opacity=".8"/>
        <rect x="348" y="103" width="230" height="167" rx="13" fill="#101b22"
            stroke="#61717a" stroke-width="2"/>
        <rect x="362" y="127" width="202" height="125" rx="7" fill="url(#shield)"
            stroke="#7d898e" stroke-width="1.5"/>
        <path d="M375 139h176M375 244h176" stroke="#92a0a4" stroke-opacity=".55"/>
        <text x="463" y="185" text-anchor="middle" fill="#edf1ef" font-size="19"
            font-weight="750" letter-spacing="1">ESP32</text>
        <text x="463" y="207" text-anchor="middle" fill="#c0c9c8" font-size="11"
            font-weight="650" letter-spacing="1.1">WROOM-32</text>
        <text x="463" y="232" text-anchor="middle" fill="#91a5ad" font-size="8"
            letter-spacing="1.6">DUAL-CORE · WI-FI · BLE</text>

        <rect x="344" y="296" width="90" height="44" rx="5" fill="#253138" stroke="#60727a"/>
        <text x="389" y="315" text-anchor="middle" class="micro">USB</text>
        <text x="389" y="328" text-anchor="middle" fill="#b8c4c7" font-size="8">UART BRIDGE</text>
        <rect x="453" y="296" width="66" height="44" rx="5" fill="#26333a" stroke="#60727a"/>
        <text x="486" y="316" text-anchor="middle" class="micro">3V3</text>
        <text x="486" y="329" text-anchor="middle" fill="#b8c4c7" font-size="8">REGULATOR</text>
        <rect x="535" y="296" width="66" height="44" rx="5" fill="#26333a" stroke="#60727a"/>
        <text x="568" y="316" text-anchor="middle" class="micro">FLASH</text>
        <text x="568" y="329" text-anchor="middle" fill="#b8c4c7" font-size="8">MEMORY</text>

        <rect x="354" y="363" width="54" height="30" rx="6" fill="#152229" stroke="#62727a"/>
        <rect x="367" y="371" width="28" height="14" rx="3" fill="#46545b"/>
        <text x="381" y="408" text-anchor="middle" class="micro">EN</text>
        <rect x="421" y="363" width="54" height="30" rx="6" fill="#152229" stroke="#62727a"/>
        <rect x="434" y="371" width="28" height="14" rx="3" fill="#46545b"/>
        <text x="448" y="408" text-anchor="middle" class="micro">BOOT</text>

        <path d="M652 422h-42v-29h-25" fill="none" stroke="#55c2bd" stroke-width="2"
            stroke-opacity=".8"/>
        <circle cx="574" cy="390" r="8" fill="{led_color}" stroke="#b7d6cf" stroke-width="1.5"/>
        {led_halo}
        <text x="574" y="420" text-anchor="middle" fill="#d5e0e2" font-size="8"
            font-weight="700" letter-spacing=".6">GPIO4 · {led_label}</text>
        <text x="463" y="469" text-anchor="middle" class="board-label">SPECTRA-32 · NODE 01</text>
        <text x="463" y="485" text-anchor="middle" class="micro">VIGIL-IoT RESEARCH MODEL</text>

        <rect x="390" y="493" width="146" height="57" rx="13" fill="#16232a"
            stroke="#87969a" stroke-width="2"/>
        <rect x="423" y="507" width="80" height="29" rx="9" fill="#080f13"
            stroke="#43525a"/>
        <path d="M438 514h50v15h-50z" fill="#18252b"/>
        <text x="463" y="562" text-anchor="middle" class="micro">USB POWER / DATA</text>

        <text x="460" y="20" text-anchor="middle" class="board-label">ESP32 DEVKIT-STYLE VIRTUAL BOARD</text>
        <text x="460" y="586" text-anchor="middle" fill="#8ea2aa" font-size="8">
            Illustrative drawing · pin layout varies by board revision
        </text>
    </svg>"""


def render_output(state: dict[str, object] | None) -> None:
    led_state = state.get("led") if state else None
    if led_state != "ON" and led_state != "OFF":
        label, class_name = "NO DATA", "unknown"
    else:
        label, class_name = ("ON", "on") if led_state == "ON" else ("OFF", "off")

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

    board_column, control_column = st.columns([1.55, 1], gap="large")
    with control_column:
        st.markdown('<div class="panel-heading">Device controls</div>', unsafe_allow_html=True)
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

    with board_column:
        st.markdown('<div class="panel-heading">Virtual board view</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.html(make_board_svg(state.get("led") if state else None))
        st.caption(
            "DevKit-style illustration. GPIO4 follows the model output; pin placement is "
            "representative and varies by board revision."
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
