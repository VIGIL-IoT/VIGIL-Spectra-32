"""Apply safe, in-memory security scenarios to a SPECTRA-32 sample state."""

from __future__ import annotations

from data.device_state import DeviceState, EventRecord, local_timestamp


SCENARIOS = (
    "Normal traffic",
    "Replay attempt",
    "Authentication failure",
    "MQTT plaintext warning",
    "Flood / high request-rate event",
    "Unsigned OTA attempt",
    "Debug interface exposure",
)


def _record(
    state: DeviceState,
    *,
    event_type: str,
    component: str,
    severity: str,
    decision: str,
    reason: str,
    target: str,
) -> None:
    event: EventRecord = {
        "timestamp": local_timestamp(),
        "event_type": event_type,
        "component": component,
        "severity": severity,
        "decision": decision,
        "reason": reason,
        "target": target,
    }
    state["events"].insert(0, event)
    del state["events"][60:]


def _set_threat_level(state: DeviceState) -> None:
    security = state["security"]
    if state["mode"] == "Hardened":
        security["threat_level"] = "LOW"
    elif security["accepted_replays"] or security["accepted_ota_attempts"]:
        security["threat_level"] = "HIGH"
    elif security["current_request_rate"] >= 40 or security["auth_failures"] >= 10:
        security["threat_level"] = "HIGH"
    else:
        security["threat_level"] = "MEDIUM"


def set_security_mode(state: DeviceState, mode: str) -> None:
    """Set the simulated protection profile without changing real hardware."""
    if mode not in {"Vulnerable", "Hardened"}:
        raise ValueError(f"Unknown security profile: {mode}")

    state["mode"] = mode
    hardened = mode == "Hardened"
    state["firmware"] = "hardened-v0.2" if hardened else "vulnerable-v0.2"
    state["mqtt"]["tls"] = hardened
    state["security"].update(
        {
            "secure_boot": hardened,
            "flash_encryption": hardened,
            "ota_signing": hardened,
            "debug_enabled": not hardened,
        }
    )
    _set_threat_level(state)


def set_simulation_mode(state: DeviceState, enabled: bool) -> None:
    state["simulation_mode"] = enabled


def simulate_event(state: DeviceState, scenario: str) -> EventRecord:
    """Run one non-networked scenario and update only the in-memory session model."""
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown simulation scenario: {scenario}")
    if not state["simulation_mode"]:
        raise RuntimeError("Enable Simulation Mode before running a scenario.")

    security = state["security"]
    state["active_path"] = []
    if scenario == "Normal traffic":
        security["accepted_commands"] += 1
        security["current_request_rate"] = 8
        state["selected_component"] = "GPIO22"
        state["active_path"] = ["Wi-Fi", "ESP32", "MQTT", "GPIO22", "Sensor"]
        _record(
            state,
            event_type="Normal MQTT command",
            component="GPIO22 / Sensor",
            severity="INFO",
            decision="Accepted",
            reason="A sample sensor update passed through the local simulation.",
            target="GPIO22",
        )
    elif scenario == "Replay attempt":
        security["replay_attempts"] += 1
        state["selected_component"] = "GPIO23"
        state["active_path"] = ["Wi-Fi", "ESP32", "MQTT", "GPIO23", "Relay"]
        if state["mode"] == "Vulnerable":
            security["accepted_commands"] += 1
            security["accepted_replays"] += 1
            state["gpio"]["GPIO23"]["state"] = "HIGH"
            state["gpio"]["GPIO23"]["security_state"] = "Replay accepted"
            decision = "Accepted"
            reason = "The vulnerable profile has no nonce check; the relay command was repeated."
        else:
            security["blocked_requests"] += 1
            state["gpio"]["GPIO23"]["security_state"] = "Replay rejected"
            decision = "Rejected"
            reason = "The hardened profile rejected a nonce that had already been used."
        _record(
            state,
            event_type="Replay attempt detected",
            component="GPIO23 / Relay",
            severity="HIGH",
            decision=decision,
            reason=reason,
            target="GPIO23",
        )
    elif scenario == "Authentication failure":
        security["auth_failures"] += 1
        security["blocked_requests"] += 1
        state["selected_component"] = "MQTT"
        state["active_path"] = ["Wi-Fi", "MQTT", "ESP32"]
        _record(
            state,
            event_type="Authentication failure",
            component="MQTT broker",
            severity="MEDIUM",
            decision="Rejected",
            reason="The simulated client credential did not match the lab profile.",
            target="MQTT",
        )
    elif scenario == "MQTT plaintext warning":
        state["selected_component"] = "MQTT"
        state["active_path"] = ["Wi-Fi", "MQTT", "ESP32"]
        if state["mode"] == "Hardened":
            security["blocked_requests"] += 1
            decision = "Rejected"
            reason = "The hardened profile requires TLS before a broker session is accepted."
        else:
            decision = "Observed"
            reason = "MQTT is connected without TLS; payload confidentiality is not protected."
        _record(
            state,
            event_type="MQTT plaintext warning",
            component="Wi-Fi → MQTT",
            severity="MEDIUM",
            decision=decision,
            reason=reason,
            target="MQTT",
        )
    elif scenario == "Flood / high request-rate event":
        security["current_request_rate"] = 40
        state["selected_component"] = "MQTT"
        state["active_path"] = ["Wi-Fi", "MQTT", "ESP32"]
        if state["mode"] == "Hardened":
            security["rate_limited_requests"] += 38
            security["blocked_requests"] += 38
            decision = "38 of 40 rate-limited"
            reason = "A 40-request sample burst exceeded the hardened token-bucket limit."
        else:
            decision = "Not rate-limited"
            reason = "The vulnerable profile has no request-rate limit for this simulated burst."
        _record(
            state,
            event_type="High request-rate event",
            component="Wi-Fi → MQTT",
            severity="HIGH",
            decision=decision,
            reason=reason,
            target="MQTT",
        )
    elif scenario == "Unsigned OTA attempt":
        state["selected_component"] = "FLASH"
        state["active_path"] = ["Network", "ESP32", "Firmware / Flash"]
        if state["mode"] == "Hardened":
            security["blocked_requests"] += 1
            decision = "Rejected"
            reason = "The hardened profile rejected a firmware image without a valid signature."
        else:
            security["accepted_ota_attempts"] += 1
            decision = "Would be accepted"
            reason = "OTA signing is disabled in this profile; no firmware is actually written."
        _record(
            state,
            event_type="Unsigned OTA attempt",
            component="Firmware / Flash",
            severity="HIGH",
            decision=decision,
            reason=reason,
            target="FLASH",
        )
    else:  # Debug interface exposure
        state["selected_component"] = "TX"
        state["active_path"] = ["USB", "TX", "ESP32", "Debug console"]
        if state["mode"] == "Hardened":
            decision = "Restricted"
            reason = "The hardened profile disables the development UART console."
        else:
            decision = "Exposed"
            reason = "UART debug output is enabled in development mode."
        _record(
            state,
            event_type="Debug interface exposure",
            component="UART / USB",
            severity="MEDIUM",
            decision=decision,
            reason=reason,
            target="TX",
        )

    _set_threat_level(state)
    return state["events"][0]


def log_profile_change(state: DeviceState, previous_mode: str) -> None:
    if previous_mode == state["mode"]:
        return
    _record(
        state,
        event_type="Security profile changed",
        component="SPECTRA-32 node",
        severity="INFO",
        decision=state["mode"],
        reason="Protection settings changed in the local simulation model only.",
        target="ESP32_MODULE",
    )
