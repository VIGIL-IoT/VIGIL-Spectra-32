"""Typed, serializable SPECTRA-32 node state and its clearly labeled demo baseline."""

from __future__ import annotations

from datetime import datetime
from typing import TypedDict
from zoneinfo import ZoneInfo

from data.board_definition import PIN_DEFINITIONS


class PinState(TypedDict):
    mode: str
    state: str
    connected_to: str
    security_state: str


class EventRecord(TypedDict):
    timestamp: str
    event_type: str
    component: str
    severity: str
    decision: str
    reason: str
    target: str


class DeviceState(TypedDict):
    node_id: str
    online: bool
    mode: str
    firmware: str
    wifi: dict[str, object]
    mqtt: dict[str, object]
    security: dict[str, object]
    gpio: dict[str, PinState]
    simulation_mode: bool
    selected_component: str
    active_path: list[str]
    events: list[EventRecord]


def local_timestamp() -> str:
    return datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%H:%M:%S")


def create_initial_state() -> DeviceState:
    """Create an offline-only sample model using the values in the project brief."""
    gpio = {
        pin_id: {
            "mode": pin["mode"],
            "state": pin["state"],
            "connected_to": pin["connected_to"],
            "security_state": pin["security_state"],
        }
        for pin_id, pin in PIN_DEFINITIONS.items()
        if pin["kind"] not in {"Power", "Ground", "Control", "Boot control", "Flash bus"}
    }
    return {
        "node_id": "SPECTRA-NODE-01",
        "online": True,
        "mode": "Vulnerable",
        "firmware": "vulnerable-v0.2",
        "wifi": {"connected": True, "ssid": "SPECTRA-LAB", "rssi": -52},
        "mqtt": {"connected": True, "tls": False, "broker": "broker.spectra.local"},
        "security": {
            "threat_level": "MEDIUM",
            "replay_attempts": 3,
            "auth_failures": 7,
            "blocked_requests": 4,
            "accepted_commands": 0,
            "current_request_rate": 0,
            "rate_limited_requests": 0,
            "accepted_replays": 0,
            "accepted_ota_attempts": 0,
            "secure_boot": False,
            "flash_encryption": False,
            "ota_signing": False,
            "debug_enabled": True,
        },
        "gpio": gpio,
        "simulation_mode": False,
        "selected_component": "GPIO23",
        "active_path": [],
        "events": [
            {
                "timestamp": local_timestamp(),
                "event_type": "Sample baseline loaded",
                "component": "SPECTRA-NODE-01",
                "severity": "INFO",
                "decision": "Simulated",
                "reason": "3 replay attempts, 7 authentication failures, and 4 blocked requests are example values from the brief.",
                "target": "SPECTRA-NODE-01",
            }
        ],
    }
