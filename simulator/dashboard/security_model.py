"""Session-local device and security state for the SPECTRA-32 console.

Simulation events only update this Python model. They do not send attack traffic,
publish MQTT messages, or modify the separate loopback node process.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


VULNERABLE_MODE = "Vulnerable"
HARDENED_MODE = "Hardened"
SIMULATION_EVENTS = (
    "Normal traffic",
    "Replay attempt",
    "Authentication failure",
    "MQTT plaintext warning",
    "Flood / high request-rate",
    "Unsigned OTA attempt",
    "Debug interface exposure",
)


def create_device_state() -> dict[str, Any]:
    """Return a fresh, JSON-like device model for one Streamlit session."""
    return {
        "node_id": "SPECTRA-NODE-01",
        "online": False,
        "firmware": "vulnerable-v0.2",
        "firmware_status": "Baseline image",
        "wifi": {
            "connected": True,
            "ssid": "SPECTRA-LAB (simulated)",
            "rssi": -52,
            "source": "dashboard simulation",
        },
        "mqtt": {
            "connected": False,
            "tls_actual": False,
            "tls_required_by_profile": False,
        },
        "api": {
            "available": False,
            "error": "Behavior model has not been checked yet.",
            "commands_applied": 0,
        },
        "gpio": {
            "GPIO23": {
                "mode": "OUTPUT",
                "state": "LOW",
                "connected_to": "Relay (simulated)",
            },
            "GPIO22": {
                "mode": "INPUT",
                "state": "LOW",
                "connected_to": "Sensor (simulated)",
            },
            "GPIO4": {
                "mode": "OUTPUT",
                "state": "OFF",
                "connected_to": "On-board LED (model API)",
            },
        },
        "security": {
            "threat_level": "LOW",
            "replay_attempts": 0,
            "auth_failures": 0,
            "blocked_commands": 0,
            "simulated_accepted_commands": 0,
            "request_rate": 0,
            "mqtt_plaintext_warnings": 0,
            "ota_attempts": 0,
            "debug_exposures": 0,
            "ota_candidate": "None",
            "debug_interface_enabled": True,
            "secure_boot": False,
            "flash_encryption": False,
            "ota_signing": False,
            "replay_protection": False,
        },
        "active_path": [],
        "active_path_status": "neutral",
        "active_components": [],
        "events": [],
    }


def apply_profile(state: dict[str, Any], mode: str) -> dict[str, Any]:
    """Apply a UI-only security profile without changing the local node process."""
    hardened = mode == HARDENED_MODE
    state["firmware"] = "hardened-v0.2" if hardened else "vulnerable-v0.2"
    candidate = state["security"].get("ota_candidate", "None")
    if candidate == "None":
        state["firmware_status"] = "Signed baseline profile" if hardened else "Unsigned baseline profile"
    else:
        state["firmware_status"] = str(candidate)
    state["security"].update(
        {
            "secure_boot": hardened,
            "flash_encryption": hardened,
            "ota_signing": hardened,
            "replay_protection": hardened,
            "debug_interface_enabled": not hardened,
        }
    )
    state["mqtt"]["tls_required_by_profile"] = hardened
    return state


def sync_backend(
    state: dict[str, Any],
    backend: dict[str, Any] | None,
    error: str | None,
) -> dict[str, Any]:
    """Merge truthful loopback API observations into the simulated device state."""
    state["online"] = backend is not None
    state["api"]["available"] = backend is not None
    state["api"]["error"] = error

    if backend is None:
        state["mqtt"]["connected"] = False
        return state

    state["mqtt"]["connected"] = bool(backend.get("mqtt_connected", False))
    state["api"]["commands_applied"] = _safe_nonnegative_int(
        backend.get("commands_applied", 0)
    )
    led_state = backend.get("led")
    if led_state in {"ON", "OFF"}:
        state["gpio"]["GPIO4"]["state"] = led_state
    return state


def apply_simulated_event(
    current_state: dict[str, Any],
    event_type: str,
    mode: str,
) -> dict[str, Any]:
    """Apply one bounded, in-dashboard event and return a new state snapshot."""
    state = deepcopy(current_state)
    state = apply_profile(state, mode)
    security = state["security"]
    hardened = mode == HARDENED_MODE

    event: dict[str, Any] = {
        "time": datetime.now().astimezone().strftime("%H:%M:%S"),
        "event_type": event_type,
        "component": "SPECTRA-NODE-01",
        "severity": "INFO",
        "decision": "OBSERVED",
        "explanation": "In-app state simulation only; no network traffic was sent.",
        "path": [],
        "highlighted_components": [],
    }

    if event_type == "Normal traffic":
        security["simulated_accepted_commands"] += 1
        security["request_rate"] = 2
        state["gpio"]["GPIO23"]["state"] = "HIGH"
        event.update(
            {
                "component": "GPIO23 / Relay",
                "decision": "ACCEPTED",
                "explanation": "Simulated command followed the configured device path.",
                "path": ["Wi-Fi", "ESP32 module", "MQTT", "GPIO23", "Relay"],
                "highlighted_components": ["WIFI", "ESP32_MODULE", "GPIO23"],
            }
        )
        state["active_path_status"] = "normal"
        security["threat_level"] = "LOW"

    elif event_type == "Replay attempt":
        security["replay_attempts"] += 1
        security["request_rate"] = 1
        if hardened:
            security["blocked_commands"] += 1
            event.update(
                {
                    "component": "MQTT → GPIO23 / Relay",
                    "severity": "MEDIUM",
                    "decision": "REJECTED",
                    "explanation": "Hardened profile rejected a reused command nonce.",
                    "path": ["Wi-Fi", "ESP32 module", "MQTT", "GPIO23", "Relay"],
                    "highlighted_components": ["WIFI", "ESP32_MODULE", "GPIO23"],
                }
            )
            state["active_path_status"] = "defended"
            security["threat_level"] = "MEDIUM"
        else:
            security["simulated_accepted_commands"] += 1
            state["gpio"]["GPIO23"]["state"] = "HIGH"
            event.update(
                {
                    "component": "MQTT → GPIO23 / Relay",
                    "severity": "HIGH",
                    "decision": "ACCEPTED",
                    "explanation": "Vulnerable profile has no command freshness check.",
                    "path": ["Wi-Fi", "ESP32 module", "MQTT", "GPIO23", "Relay"],
                    "highlighted_components": ["WIFI", "ESP32_MODULE", "GPIO23"],
                }
            )
            state["active_path_status"] = "warning"
            security["threat_level"] = "HIGH"

    elif event_type == "Authentication failure":
        security["auth_failures"] += 1
        security["request_rate"] = 1
        if hardened:
            security["blocked_commands"] += 1
            event.update(
                {
                    "component": "MQTT authentication",
                    "severity": "MEDIUM",
                    "decision": "REJECTED",
                    "explanation": "Hardened profile rejected the simulated invalid credential.",
                    "path": ["Wi-Fi", "MQTT broker"],
                    "highlighted_components": ["WIFI"],
                }
            )
            state["active_path_status"] = "defended"
            security["threat_level"] = "MEDIUM"
        else:
            security["simulated_accepted_commands"] += 1
            state["gpio"]["GPIO23"]["state"] = "HIGH"
            event.update(
                {
                    "component": "MQTT authentication → GPIO23 / Relay",
                    "severity": "HIGH",
                    "decision": "ACCEPTED (WEAK AUTH)",
                    "explanation": "Vulnerable profile lacks a robust authentication gate in this scenario.",
                    "path": ["Wi-Fi", "MQTT broker", "ESP32 module", "GPIO23", "Relay"],
                    "highlighted_components": ["WIFI", "ESP32_MODULE", "GPIO23"],
                }
            )
            state["active_path_status"] = "warning"
            security["threat_level"] = "HIGH"

    elif event_type == "MQTT plaintext warning":
        security["mqtt_plaintext_warnings"] += 1
        security["request_rate"] = 1
        if hardened:
            security["blocked_commands"] += 1
            event.update(
                {
                    "component": "MQTT transport",
                    "severity": "INFO",
                    "decision": "BLOCKED",
                    "explanation": "Hardened profile requires TLS; the local broker transport is unchanged.",
                    "path": ["Wi-Fi", "MQTT broker"],
                    "highlighted_components": ["WIFI"],
                }
            )
            state["active_path_status"] = "defended"
            security["threat_level"] = "LOW"
        else:
            event.update(
                {
                    "component": "MQTT transport",
                    "severity": "MEDIUM",
                    "decision": "PLAINTEXT WARNING",
                    "explanation": "Vulnerable profile allows plaintext MQTT in this simulated scenario.",
                    "path": ["Wi-Fi", "MQTT broker"],
                    "highlighted_components": ["WIFI"],
                }
            )
            state["active_path_status"] = "warning"
            security["threat_level"] = "MEDIUM"

    elif event_type == "Flood / high request-rate":
        if hardened:
            security["blocked_commands"] += 1
            security["request_rate"] = 8
            event.update(
                {
                    "component": "HTTP / MQTT request path",
                    "severity": "MEDIUM",
                    "decision": "THROTTLED",
                    "explanation": "Hardened profile caps the simulated request rate; no requests were generated.",
                    "path": ["Wi-Fi", "ESP32 module", "MQTT"],
                    "highlighted_components": ["WIFI", "ESP32_MODULE"],
                }
            )
            state["active_path_status"] = "defended"
            security["threat_level"] = "MEDIUM"
        else:
            security["simulated_accepted_commands"] += 10
            security["request_rate"] = 120
            event.update(
                {
                    "component": "HTTP / MQTT request path",
                    "severity": "CRITICAL",
                    "decision": "UNTHROTTLED (SIMULATED)",
                    "explanation": "Request-rate metric was raised in memory only; no traffic was generated.",
                    "path": ["Wi-Fi", "ESP32 module", "MQTT"],
                    "highlighted_components": ["WIFI", "ESP32_MODULE"],
                }
            )
            state["active_path_status"] = "warning"
            security["threat_level"] = "CRITICAL"

    elif event_type == "Unsigned OTA attempt":
        security["ota_attempts"] += 1
        security["request_rate"] = 1
        if hardened:
            security["blocked_commands"] += 1
            security["ota_candidate"] = "Rejected by signature policy (simulated)"
            event.update(
                {
                    "component": "Firmware / flash",
                    "severity": "MEDIUM",
                    "decision": "REJECTED",
                    "explanation": "Hardened profile requires a valid firmware signature.",
                    "path": ["Network", "ESP32 module", "Firmware / flash"],
                    "highlighted_components": ["WIFI", "ESP32_MODULE", "FLASH"],
                }
            )
            state["active_path_status"] = "defended"
            security["threat_level"] = "MEDIUM"
        else:
            security["ota_candidate"] = "Unsigned image staged (simulated only)"
            state["firmware_status"] = "Unsigned image staged (simulated)"
            event.update(
                {
                    "component": "Firmware / flash",
                    "severity": "CRITICAL",
                    "decision": "ACCEPTED (SIMULATED)",
                    "explanation": "Vulnerable profile has no OTA signature check; no image was written.",
                    "path": ["Network", "ESP32 module", "Firmware / flash"],
                    "highlighted_components": ["WIFI", "ESP32_MODULE", "FLASH"],
                }
            )
            state["active_path_status"] = "warning"
            security["threat_level"] = "CRITICAL"

    elif event_type == "Debug interface exposure":
        security["debug_exposures"] += 1
        security["request_rate"] = 1
        if hardened:
            event.update(
                {
                    "component": "UART debug interface",
                    "severity": "INFO",
                    "decision": "RESTRICTED",
                    "explanation": "Hardened profile disables the simulated development debug interface.",
                    "path": ["USB / UART", "ESP32 module"],
                    "highlighted_components": ["USB", "UART", "ESP32_MODULE"],
                }
            )
            state["active_path_status"] = "defended"
            security["threat_level"] = "LOW"
        else:
            event.update(
                {
                    "component": "UART debug interface",
                    "severity": "HIGH",
                    "decision": "EXPOSED (SIMULATED)",
                    "explanation": "Vulnerable profile leaves development UART access enabled in the model.",
                    "path": ["USB / UART", "ESP32 module"],
                    "highlighted_components": ["USB", "UART", "ESP32_MODULE"],
                }
            )
            state["active_path_status"] = "warning"
            security["threat_level"] = "HIGH"

    else:
        raise ValueError(f"Unsupported simulation event: {event_type}")

    state["active_path"] = event["path"]
    state["active_components"] = event["highlighted_components"]
    state["events"] = [event, *state["events"]][:50]
    return state


def _safe_nonnegative_int(value: object) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return 0
