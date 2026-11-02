"""Pin and component metadata for the ESP32 DevKit-style board illustration."""

from __future__ import annotations

from typing import TypedDict

BOARD_DEFINITION_VERSION = 3


class PinDefinition(TypedDict):
    id: str
    label: str
    side: str
    position: int
    kind: str
    mode: str
    state: str
    connected_to: str
    security_state: str
    description: str


_LEFT_PINS = [
    ("3V3", "3V3", "Power", "POWER", "3.3 V", "Sensor rail", "Normal", "3.3 V regulated output."),
    ("EN", "EN", "Control", "INPUT", "HIGH", "Reset line", "Normal", "Chip enable and reset input."),
    ("GPIO36", "GPIO36 / VP", "Analog input", "INPUT", "N/A", "ADC1 sensor", "Normal", "Input-only ADC1 pin."),
    ("GPIO39", "GPIO39 / VN", "Analog input", "INPUT", "N/A", "ADC1 sensor", "Normal", "Input-only ADC1 pin."),
    ("GPIO34", "GPIO34", "Digital input", "INPUT", "LOW", "Spare input", "Normal", "Input-only digital pin."),
    ("GPIO35", "GPIO35", "Digital input", "INPUT", "LOW", "Spare input", "Normal", "Input-only digital pin."),
    ("GPIO32", "GPIO32", "Digital I/O", "INPUT", "LOW", "Spare input", "Normal", "Digital I/O and touch-capable pin."),
    ("GPIO33", "GPIO33", "Digital I/O", "INPUT", "LOW", "Spare input", "Normal", "Digital I/O and touch-capable pin."),
    ("GPIO25", "GPIO25", "Digital I/O", "OUTPUT", "LOW", "DAC channel", "Normal", "Digital I/O and DAC-capable pin."),
    ("GPIO26", "GPIO26", "Digital I/O", "OUTPUT", "LOW", "DAC channel", "Normal", "Digital I/O and DAC-capable pin."),
    ("GPIO27", "GPIO27", "Digital I/O", "INPUT", "LOW", "Spare input", "Normal", "Digital I/O and touch-capable pin."),
    ("GPIO14", "GPIO14", "Digital I/O", "OUTPUT", "LOW", "SPI clock", "Normal", "Common SPI clock pin."),
    ("GPIO12", "GPIO12", "Digital I/O", "INPUT", "LOW", "Strap pin", "Review", "Strapping pin MTDI. Its reset level affects flash supply selection; verify the exact module and board before wiring."),
    ("GND_L", "GND", "Ground", "GROUND", "0 V", "Common ground", "Normal", "Ground reference."),
    ("GPIO13", "GPIO13", "Digital I/O", "OUTPUT", "LOW", "SPI MOSI", "Normal", "Common SPI data pin."),
    ("GPIO9", "GPIO9 / SD2", "Flash bus", "RESERVED", "N/A", "On-module SPI flash", "Reserved", "GPIO9 is normally connected to SPI0/1 flash on the module; do not treat it as a general output."),
]

_RIGHT_PINS = [
    ("VIN", "VIN / 5V", "Power", "POWER", "5 V", "USB power rail", "Normal", "Board input rail; observe the board's supply limits."),
    ("GND_R", "GND", "Ground", "GROUND", "0 V", "Common ground", "Normal", "Ground reference."),
    ("GPIO23", "GPIO23", "Digital I/O", "OUTPUT", "HIGH", "Sample relay path (model only)", "Normal", "Relay-control path in the session model only. No physical relay is attached or driven."),
    ("GPIO22", "GPIO22", "Digital I/O", "INPUT", "LOW", "Sample sensor path (model only)", "Normal", "Sensor path in the session model only. No physical sensor is attached or read."),
    ("TX", "TX0 / GPIO1", "UART", "UART TX", "115200 baud", "UART monitor", "Exposed", "UART0 transmit line; debug output can disclose device state."),
    ("RX", "RX0 / GPIO3", "UART", "UART RX", "115200 baud", "UART monitor", "Exposed", "UART0 receive line; development interface is enabled in vulnerable mode."),
    ("GPIO21", "GPIO21", "I²C", "I²C SDA", "N/A", "I²C sensor bus", "Normal", "Common I²C data pin."),
    ("GPIO19", "GPIO19", "Digital I/O", "OUTPUT", "LOW", "SPI MISO", "Normal", "Common SPI data pin."),
    ("GPIO18", "GPIO18", "Digital I/O", "OUTPUT", "LOW", "SPI clock", "Normal", "Common SPI clock pin."),
    ("GPIO5", "GPIO5", "Digital I/O", "OUTPUT", "LOW", "SPI chip select", "Review", "Strapping pin. The reset-level requirement takes precedence over a peripheral role; verify the exact board before wiring."),
    ("GPIO17", "GPIO17", "Digital I/O", "OUTPUT", "LOW", "UART2 TX", "Normal", "Secondary UART transmit pin."),
    ("GPIO16", "GPIO16", "Digital I/O", "INPUT", "LOW", "UART2 RX", "Normal", "Secondary UART receive pin."),
    ("GPIO4", "GPIO4", "Digital I/O", "INPUT", "LOW", "Spare input", "Normal", "Digital I/O and touch-capable pin."),
    ("BOOT", "GPIO0 / BOOT", "Boot control", "INPUT", "HIGH", "Boot selector", "Review", "Strapping pin. Holding GPIO0 low while resetting selects serial download boot mode."),
    ("GPIO2", "GPIO2", "Digital I/O", "OUTPUT", "LOW", "Example output (model)", "Review", "Strapping pin and simulated output. A physical LED may be absent or connected to another GPIO; the dashboard does not drive it."),
    ("GPIO15", "GPIO15", "Digital I/O", "OUTPUT", "LOW", "SPI chip select", "Review", "Strapping pin MTDO. Verify the required reset level for the exact target and board before wiring."),
]


def _make_pins(rows: list[tuple[str, str, str, str, str, str, str, str]], side: str) -> list[PinDefinition]:
    return [
        {
            "id": pin_id,
            "label": label,
            "side": side,
            "position": position,
            "kind": kind,
            "mode": mode,
            "state": state,
            "connected_to": connected_to,
            "security_state": security_state,
            "description": description,
        }
        for position, (pin_id, label, kind, mode, state, connected_to, security_state, description) in enumerate(rows)
    ]


PIN_DEFINITIONS: dict[str, PinDefinition] = {
    pin["id"]: pin for pin in _make_pins(_LEFT_PINS, "left") + _make_pins(_RIGHT_PINS, "right")
}

BOARD_COMPONENTS = {
    "ESP32_MODULE": {
        "id": "ESP32_MODULE",
        "label": "ESP32-WROOM-32",
        "kind": "Microcontroller module",
        "description": "Classic ESP32 module with Wi-Fi, Bluetooth, and on-module SPI flash. The selected firmware posture is simulated.",
    },
    "USB": {
        "id": "USB",
        "label": "USB / UART",
        "kind": "Power and serial interface",
        "description": "Representative USB power and serial interface. Connector and bridge details vary by board revision; this visual does not enumerate a connected host.",
    },
    "FLASH": {
        "id": "FLASH",
        "label": "SPI flash (on module)",
        "kind": "Module storage",
        "description": "WROOM module flash storage. Capacity varies by module variant; encryption and OTA status follow the selected session profile only.",
    },
    "BOOT": {
        "id": "BOOT",
        "label": "BOOT",
        "kind": "Boot control",
        "description": "Boot selector. Unsigned OTA behavior is simulated in the event controls.",
    },
    "EN": {
        "id": "EN",
        "label": "EN / RESET",
        "kind": "Reset control",
        "description": "Chip enable and reset path for the ESP32 module.",
    },
    "LED": {
        "id": "LED",
        "label": "GPIO2 example output",
        "kind": "Illustrative output",
        "description": "GPIO2 is an example output in the session model. The physical board may not have an LED on this pin, and the dashboard never drives it.",
    },
}

VIRTUAL_COMPONENTS = {
    "MQTT": {
        "id": "MQTT",
        "label": "MQTT broker",
        "kind": "Network service",
        "description": "Local broker status follows the selected simulated security profile; no broker connection is made.",
    },
}


def board_pins() -> list[PinDefinition]:
    """Return pin definitions in board order for the SVG component."""
    return list(PIN_DEFINITIONS.values())
