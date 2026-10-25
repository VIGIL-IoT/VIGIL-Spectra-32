"""ESP32 DevKit-style board metadata and interactive SVG renderer."""

from __future__ import annotations

import json
from html import escape
from typing import Any


LEFT_HEADER = (
    ("3V3", "3V3", "Power"),
    ("EN", "EN", "Enable / reset"),
    ("GPIO36", "VP / 36", "Analog input"),
    ("GPIO39", "VN / 39", "Analog input"),
    ("GPIO34", "GPIO34", "Digital input"),
    ("GPIO35", "GPIO35", "Digital input"),
    ("GPIO32", "GPIO32", "Digital I/O"),
    ("GPIO33", "GPIO33", "Digital I/O"),
    ("GPIO25", "GPIO25", "Digital I/O"),
    ("GPIO26", "GPIO26", "Digital I/O"),
    ("GPIO27", "GPIO27", "Digital I/O"),
    ("GPIO14", "GPIO14", "Digital I/O"),
    ("GPIO12", "GPIO12", "Digital I/O"),
    ("GND_LEFT", "GND", "Ground"),
    ("GPIO13", "GPIO13", "Digital I/O"),
)

RIGHT_HEADER = (
    ("VIN", "VIN / 5V", "Power"),
    ("GND_RIGHT_1", "GND", "Ground"),
    ("GPIO23", "GPIO23", "Digital I/O"),
    ("GPIO22", "GPIO22", "Digital I/O · I²C SCL"),
    ("TX0", "TX0 / 1", "UART transmit"),
    ("RX0", "RX0 / 3", "UART receive"),
    ("GPIO21", "GPIO21", "Digital I/O · I²C SDA"),
    ("GND_RIGHT_2", "GND", "Ground"),
    ("GPIO19", "GPIO19", "Digital I/O"),
    ("GPIO18", "GPIO18", "Digital I/O"),
    ("GPIO5", "GPIO5", "Digital I/O"),
    ("GPIO17", "GPIO17", "Digital I/O"),
    ("GPIO16", "GPIO16", "Digital I/O"),
    ("GPIO4", "GPIO4", "Digital output · on-board LED"),
    ("GPIO2", "GPIO2", "Digital I/O"),
)


def pin_metadata() -> dict[str, dict[str, Any]]:
    """Return board pin definitions independent of the SVG layout."""
    pins: dict[str, dict[str, Any]] = {}
    for side, rows in (("left", LEFT_HEADER), ("right", RIGHT_HEADER)):
        for position, (component_id, label, pin_type) in enumerate(rows, start=1):
            pins[component_id] = {
                "id": component_id,
                "label": label,
                "side": side,
                "position": position,
                "type": pin_type,
            }
    return pins


ESP32_PINS = pin_metadata()


def _field(label: str, value: object) -> dict[str, str]:
    return {"label": label, "value": str(value)}


def component_details(state: dict[str, Any], mode: str) -> dict[str, dict[str, Any]]:
    """Build details for every selectable pin and major board component."""
    security = state["security"]
    gpio_state = state["gpio"]
    active = set(state.get("active_components", []))
    details: dict[str, dict[str, Any]] = {}

    for component_id, pin in ESP32_PINS.items():
        gpio = gpio_state.get(component_id, {})
        details[component_id] = {
            "name": pin["label"],
            "category": "Header pin",
            "fields": [
                _field("Type", pin["type"]),
                _field("Header", f"{pin['side'].title()} · position {pin['position']}"),
                _field("Mode", gpio.get("mode", "Not configured")),
                _field("State", gpio.get("state", "—")),
                _field("Connected device", gpio.get("connected_to", "None assigned")),
                _field(
                    "Security state",
                    "Highlighted by the last simulated event"
                    if component_id in active
                    else "Normal",
                ),
            ],
        }

    findings = sum(
        not bool(security[field])
        for field in ("secure_boot", "flash_encryption", "ota_signing", "replay_protection")
    ) + int(bool(security["debug_interface_enabled"]))
    details.update(
        {
            "ESP32_MODULE": {
                "name": "ESP32-WROOM-32 Module",
                "category": "Compute module",
                "fields": [
                    _field("Firmware profile", state["firmware"]),
                    _field("Secure Boot", _enabled(security["secure_boot"])),
                    _field("Flash encryption", _enabled(security["flash_encryption"])),
                    _field("OTA signing", _enabled(security["ota_signing"])),
                    _field("Replay protection", _enabled(security["replay_protection"])),
                    _field("Security findings", f"{findings} in {mode.lower()} profile (simulated)"),
                ],
            },
            "WIFI": {
                "name": "Wi-Fi / BLE antenna",
                "category": "Radio interface",
                "fields": [
                    _field("State", "Simulated connected" if state["wifi"]["connected"] else "Offline"),
                    _field("SSID", state["wifi"]["ssid"]),
                    _field("RSSI", f"{state['wifi']['rssi']} dBm (simulated)"),
                    _field("Security state", "In-app state only; no radio is active"),
                ],
            },
            "USB": {
                "name": "USB connector",
                "category": "Power / serial",
                "fields": [
                    _field("Function", "USB power and UART bridge"),
                    _field("Host link", "Illustrative only"),
                    _field("Security state", "No physical USB device is attached"),
                ],
            },
            "UART_BRIDGE": {
                "name": "USB-to-UART bridge",
                "category": "Serial interface",
                "fields": [
                    _field("Function", "USB serial link to ESP32 UART"),
                    _field("TX / RX", "TX0 / GPIO1 · RX0 / GPIO3"),
                    _field("Debug access", "Enabled" if security["debug_interface_enabled"] else "Restricted"),
                ],
            },
            "UART": {
                "name": "UART debug interface",
                "category": "Serial interface",
                "fields": [
                    _field("Status", "Enabled" if security["debug_interface_enabled"] else "Restricted"),
                    _field("Exposure", "Development profile" if security["debug_interface_enabled"] else "Hardened profile"),
                    _field("Risk", "Debug data may be exposed" if security["debug_interface_enabled"] else "Reduced by simulated profile"),
                ],
            },
            "FLASH": {
                "name": "Flash memory / OTA",
                "category": "Firmware storage",
                "fields": [
                    _field("Flash encryption", _enabled(security["flash_encryption"])),
                    _field("OTA signing", _enabled(security["ota_signing"])),
                    _field("Last candidate", security["ota_candidate"]),
                    _field("Firmware state", state["firmware_status"]),
                ],
            },
            "BOOT": {
                "name": "BOOT button",
                "category": "Boot control",
                "fields": [
                    _field("Function", "Selects bootloader mode during reset"),
                    _field("State", "Idle · simulated"),
                    _field("Security note", "Physical boot behavior is not modeled"),
                ],
            },
            "EN": {
                "name": "EN / reset button",
                "category": "Reset control",
                "fields": [
                    _field("Function", "Enable or reset the module"),
                    _field("State", "Online" if state["online"] else "Model API offline"),
                    _field("Security note", "Physical reset behavior is not modeled"),
                ],
            },
            "REGULATOR": {
                "name": "3.3 V regulator",
                "category": "Power",
                "fields": [
                    _field("Input", "USB / VIN · illustrative"),
                    _field("Output", "3.3 V · illustrative"),
                    _field("Security state", "Power behavior is not simulated"),
                ],
            },
            "ONBOARD_LED": {
                "name": "On-board LED",
                "category": "GPIO output",
                "fields": [
                    _field("Pin", "GPIO4"),
                    _field("Mode", gpio_state["GPIO4"]["mode"]),
                    _field("State", gpio_state["GPIO4"]["state"]),
                    _field("Source", "Loopback node API" if state["api"]["available"] else "Model API unavailable"),
                ],
            },
        }
    )
    return details


def render_board_component(state: dict[str, Any], mode: str) -> str:
    """Return a self-contained, clickable HTML/SVG board for a Streamlit iframe."""
    details = component_details(state, mode)
    details_json = json.dumps(details, ensure_ascii=False).replace("<", "\\u003c")
    active_components = set(state.get("active_components", []))
    active_status = state.get("active_path_status", "neutral")

    def active_class(component_id: str) -> str:
        if component_id not in active_components:
            return ""
        return f" impact-{escape(str(active_status), quote=True)}"

    left_pins = "".join(_render_pin(pin, row, active_class) for row, pin in enumerate(LEFT_HEADER))
    right_pins = "".join(_render_pin(pin, row, active_class) for row, pin in enumerate(RIGHT_HEADER))
    svg = f"""<svg class="board-svg" viewBox="0 0 760 650" role="img" aria-label="Interactive ESP32 DevKit-style board">
      <text x="380" y="24" text-anchor="middle" class="svg-title">ESP32 DEVKIT-STYLE · NODE 01</text>
      <rect x="231" y="48" width="298" height="526" rx="22" class="pcb"/>
      <rect x="241" y="58" width="278" height="506" rx="16" class="pcb-inset"/>
      <g data-component="WIFI" class="board-item{active_class('WIFI')}" tabindex="0" role="button" aria-label="Wi-Fi and BLE antenna">
        <text x="380" y="84" text-anchor="middle" class="micro">2.4 GHz ANTENNA</text>
        <path d="M333 94h94m-85 9h76m-66 9h56" class="trace"/>
      </g>
      <g data-component="ESP32_MODULE" class="board-item module{active_class('ESP32_MODULE')}" tabindex="0" role="button" aria-label="ESP32 module">
        <rect x="291" y="126" width="178" height="151" rx="12" class="module-shell"/>
        <rect x="302" y="145" width="156" height="112" rx="7" class="module-shield"/>
        <path d="M312 158h136M312 244h136" class="metal-line"/>
        <text x="380" y="194" text-anchor="middle" class="module-name">ESP32</text>
        <text x="380" y="216" text-anchor="middle" class="module-sub">WROOM-32</text>
        <text x="380" y="239" text-anchor="middle" class="micro">WI-FI · BLE · DUAL CORE</text>
      </g>
      <g data-component="UART_BRIDGE" class="board-item{active_class('UART_BRIDGE')}" tabindex="0" role="button" aria-label="USB to UART bridge">
        <rect x="262" y="316" width="86" height="50" rx="6" class="component-shell"/>
        <text x="305" y="338" text-anchor="middle" class="micro">USB</text>
        <text x="305" y="353" text-anchor="middle" class="tiny">UART BRIDGE</text>
      </g>
      <g data-component="REGULATOR" class="board-item{active_class('REGULATOR')}" tabindex="0" role="button" aria-label="3.3 volt regulator">
        <rect x="356" y="316" width="68" height="50" rx="6" class="component-shell"/>
        <text x="390" y="338" text-anchor="middle" class="micro">3V3</text>
        <text x="390" y="353" text-anchor="middle" class="tiny">REGULATOR</text>
      </g>
      <g data-component="FLASH" class="board-item{active_class('FLASH')}" tabindex="0" role="button" aria-label="Flash memory and OTA">
        <rect x="432" y="316" width="68" height="50" rx="6" class="component-shell"/>
        <text x="466" y="338" text-anchor="middle" class="micro">FLASH</text>
        <text x="466" y="353" text-anchor="middle" class="tiny">MEMORY</text>
      </g>
      <g data-component="EN" class="board-item{active_class('EN')}" tabindex="0" role="button" aria-label="Enable and reset button">
        <rect x="277" y="397" width="58" height="38" rx="7" class="button-shell"/>
        <rect x="293" y="406" width="26" height="18" rx="5" class="button-cap"/>
        <text x="306" y="451" text-anchor="middle" class="micro">EN</text>
      </g>
      <g data-component="BOOT" class="board-item{active_class('BOOT')}" tabindex="0" role="button" aria-label="Boot button">
        <rect x="346" y="397" width="58" height="38" rx="7" class="button-shell"/>
        <rect x="362" y="406" width="26" height="18" rx="5" class="button-cap"/>
        <text x="375" y="451" text-anchor="middle" class="micro">BOOT</text>
      </g>
      <g data-component="UART" class="board-item{active_class('UART')}" tabindex="0" role="button" aria-label="UART debug interface">
        <path d="M262 481h45v-26h34" class="uart-trace"/>
        <circle cx="341" cy="455" r="5" class="uart-node"/>
        <text x="281" y="499" class="tiny">TX0 / RX0</text>
      </g>
      <g data-component="ONBOARD_LED" class="board-item{active_class('GPIO4')}" tabindex="0" role="button" aria-label="On-board LED on GPIO4">
        <circle cx="464" cy="455" r="13" class="led-halo"/>
        <circle cx="464" cy="455" r="7" class="led-core{' on' if state['gpio']['GPIO4']['state'] == 'ON' else ''}"/>
        <path d="M464 468v14h-29" class="led-trace"/>
        <text x="464" y="499" text-anchor="middle" class="tiny">GPIO4 · {escape(str(state['gpio']['GPIO4']['state']))}</text>
      </g>
      <g data-component="USB" class="board-item{active_class('USB')}" tabindex="0" role="button" aria-label="USB power connector">
        <rect x="323" y="506" width="114" height="56" rx="11" class="usb-shell"/>
        <rect x="349" y="519" width="62" height="27" rx="7" class="usb-port"/>
        <text x="380" y="558" text-anchor="middle" class="tiny">USB POWER / DATA</text>
      </g>
      <text x="380" y="591" text-anchor="middle" class="board-label">SPECTRA-32 · VIGIL-IoT</text>
      {left_pins}{right_pins}
      <text x="380" y="629" text-anchor="middle" class="micro">ILLUSTRATIVE MODEL · PIN LAYOUT VARIES BY BOARD</text>
    </svg>"""

    default_details = details["ESP32_MODULE"]
    default_fields = "".join(
        f'<div class="detail-row"><span>{escape(field["label"])}</span><strong>{escape(field["value"])}</strong></div>'
        for field in default_details["fields"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#091720;color:#eaf0f2;font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}}
.console{{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(245px,.75fr);gap:14px;align-items:start}}
.board-wrap,.inspector{{border:1px solid #2a4052;border-radius:16px;background:#0d1b2a}}
.board-wrap{{padding:10px 6px 5px}} .inspector{{padding:16px;min-height:220px}}
.board-svg{{display:block;width:100%;height:auto;max-height:670px}}
.svg-title{{fill:#a8bac4;font-size:12px;font-weight:700;letter-spacing:1.3px}}
.pcb{{fill:#16413e;stroke:#4f8b83;stroke-width:2}} .pcb-inset{{fill:none;stroke:#86b5aa;stroke-opacity:.25}}
.trace{{fill:none;stroke:#7ba89f;stroke-width:2}} .module-shell{{fill:#101b22;stroke:#6c7d84;stroke-width:2}}
.module-shield{{fill:#344147;stroke:#89979b;stroke-width:1.5}} .metal-line{{stroke:#a4b0b2;stroke-opacity:.45}}
.module-name{{fill:#eef3f4;font-size:22px;font-weight:750;letter-spacing:1px}} .module-sub{{fill:#c0c9c8;font-size:12px;font-weight:650;letter-spacing:1.1px}}
.micro{{fill:#b6c7cc;font-size:11px;font-weight:650;letter-spacing:.5px}} .tiny{{fill:#91a5ad;font-size:9px;font-weight:600}}
.board-label{{fill:#d5e0e2;font-size:12px;font-weight:700;letter-spacing:1px}}
.component-shell,.button-shell{{fill:#26353b;stroke:#74858a;stroke-width:1.2}} .button-cap{{fill:#4c5d62;stroke:#9cabad}}
.usb-shell{{fill:#17272d;stroke:#8a999c;stroke-width:2}} .usb-port{{fill:#080f13;stroke:#59676b;stroke-width:1.4}}
.uart-trace,.led-trace{{fill:none;stroke:#55c2bd;stroke-width:2}} .uart-node{{fill:#55c2bd}}
.led-core{{fill:#596a70;stroke:#b7d6cf;stroke-width:1.3}} .led-core.on{{fill:#55c2bd}} .led-halo{{fill:#55c2bd;opacity:.1}}
.header-pad{{fill:#bd8b4d;stroke:#f0c47d;stroke-width:1}} .header-pad.active{{fill:#55c2bd;stroke:#9be4dc}}
.pin-label{{fill:#bdcbd0;font-size:11px;font-weight:600}} .board-item{{cursor:pointer;outline:none}}
.board-item:hover .header-pad,.board-item:focus .header-pad{{fill:#75d8d0;stroke:#e3fffc}}
.board-item:hover .module-shell,.board-item:focus .module-shell,.board-item.selected .module-shell{{stroke:#75d8d0;stroke-width:3}}
.board-item.impact-warning .header-pad,.board-item.impact-warning .module-shell{{stroke:#e4ae58;stroke-width:3}}
.board-item.impact-defended .header-pad,.board-item.impact-defended .module-shell{{stroke:#55c2bd;stroke-width:3}}
.inspector-kicker{{color:#55c2bd;font-size:11px;font-weight:700;letter-spacing:.08em}} h2{{font-size:20px;line-height:1.2;margin:5px 0 14px}}
.detail-row{{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-top:1px solid #263d4b}}
.detail-row span{{color:#9eb1bb}} .detail-row strong{{text-align:right;color:#eaf0f2;font-weight:600}}
.hint{{color:#8599a4;font-size:12px;margin:14px 0 0}}
@media(max-width:720px){{.console{{grid-template-columns:1fr}} .board-svg{{max-height:none}} .inspector{{min-height:unset}}}}
</style></head><body>
<div class="console"><div class="board-wrap">{svg}</div>
<section class="inspector" aria-live="polite"><div class="inspector-kicker" id="category">{escape(default_details['category'])}</div>
<h2 id="name">{escape(default_details['name'])}</h2><div id="fields">{default_fields}</div>
<p class="hint">Select a highlighted pin or component on the board to inspect it.</p></section></div>
<script>
const details={details_json};
const panel={{category:document.getElementById('category'),name:document.getElementById('name'),fields:document.getElementById('fields')}};
function selectComponent(id){{const item=details[id];if(!item)return;document.querySelectorAll('[data-component]').forEach(el=>el.classList.toggle('selected',el.dataset.component===id));panel.category.textContent=item.category;panel.name.textContent=item.name;panel.fields.replaceChildren();item.fields.forEach(field=>{{const row=document.createElement('div');row.className='detail-row';const label=document.createElement('span');label.textContent=field.label;const value=document.createElement('strong');value.textContent=field.value;row.append(label,value);panel.fields.append(row);}});try{{localStorage.setItem('spectra32-selected-component',id);}}catch{{}}}}
document.addEventListener('click',event=>{{const target=event.target.closest('[data-component]');if(target)selectComponent(target.dataset.component);}});
document.addEventListener('keydown',event=>{{if((event.key==='Enter'||event.key===' ')&&event.target.matches('[data-component]')){{event.preventDefault();selectComponent(event.target.dataset.component);}}}});
let initial='ESP32_MODULE';try{{initial=localStorage.getItem('spectra32-selected-component')||initial;}}catch{{}}selectComponent(initial);
</script></body></html>"""


def _render_pin(
    pin: tuple[str, str, str],
    row: int,
    active_class: Any,
) -> str:
    component_id, label, _pin_type = pin
    y = 126 + row * 25
    # Side is derived from the pin table rather than label spelling (e.g. GND).
    is_left = component_id in {item[0] for item in LEFT_HEADER}
    if is_left:
        pad_x, label_x, anchor = 216, 204, "end"
    else:
        pad_x, label_x, anchor = 530, 560, "start"
    label_html = escape(label)
    component_html = escape(component_id, quote=True)
    return (
        f'<g id="pin-{component_html}" data-component="{component_html}" '
        f'class="board-item{active_class(component_id)}" tabindex="0" role="button" '
        f'aria-label="Inspect {label_html}"><rect x="{pad_x}" y="{y - 5}" width="14" height="10" '
        f'rx="2" class="header-pad"/><text x="{label_x}" y="{y + 4}" text-anchor="{anchor}" '
        f'class="pin-label">{label_html}</text></g>'
    )


def _enabled(value: object) -> str:
    return "Enabled (simulated)" if bool(value) else "Disabled (simulated)"
