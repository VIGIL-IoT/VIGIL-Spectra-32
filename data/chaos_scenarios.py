"""Declarative, simulation-only failure scenarios for the SPECTRA-32 Chaos Lab."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChaosMilestone:
    """One deterministic change in a profile's behavioral experiment."""

    at_seconds: int
    stage: str
    event_type: str
    component: str
    severity: str
    decision: str
    reason: str
    status: dict[str, str]
    metric_delta: dict[str, int]
    service_available: bool
    degraded: bool
    detected: bool = False
    recovered: bool = False
    recovery_action: str = "—"


@dataclass(frozen=True)
class ChaosScenario:
    """Scenario description and per-profile transition plans."""

    id: str
    name: str
    category: str
    summary: str
    affected_components: tuple[str, ...]
    board_path: tuple[str, ...]
    assumptions: tuple[str, ...]
    fault_behavior: str
    vulnerable_behavior: str
    hardened_behavior: str
    recovery_policy: str
    primary_metric: str
    educational_explanation: str
    limitations: str
    plans: dict[str, tuple[ChaosMilestone, ...]]
    parameter_kind: str = "none"
    default_packet_loss_pct: int = 30


def _m(
    at: int,
    stage: str,
    event: str,
    component: str,
    reason: str,
    *,
    status: dict[str, str] | None = None,
    metrics: dict[str, int] | None = None,
    available: bool = True,
    degraded: bool = False,
    detected: bool = False,
    recovered: bool = False,
    action: str = "—",
    severity: str = "INFO",
    decision: str = "Observed",
) -> ChaosMilestone:
    return ChaosMilestone(
        at_seconds=at,
        stage=stage,
        event_type=event,
        component=component,
        severity=severity,
        decision=decision,
        reason=reason,
        status=status or {},
        metric_delta=metrics or {},
        service_available=available,
        degraded=degraded,
        detected=detected,
        recovered=recovered,
        recovery_action=action,
    )


def _plan(*milestones: ChaosMilestone) -> tuple[ChaosMilestone, ...]:
    return milestones


_baseline = _m(
    0,
    "BASELINE",
    "Steady-state baseline recorded",
    "ESP32 IoT node model",
    "The modeled device starts with Wi-Fi, MQTT, and HTTP available; no physical device is sampled.",
    status={"device": "RUNNING", "wifi": "ONLINE", "mqtt": "ONLINE", "http": "ONLINE", "sensor": "HEALTHY", "recovery": "READY"},
)

CHAOS_SCENARIOS: dict[str, ChaosScenario] = {
    "mqtt-broker-outage": ChaosScenario(
        id="mqtt-broker-outage",
        name="MQTT broker outage",
        category="Dependency outage",
        summary="Model the command broker going offline while local HTTP remains available.",
        affected_components=("MQTT", "ESP32", "Command path"),
        board_path=("Wi-Fi", "ESP32_MODULE", "MQTT"),
        assumptions=("The broker is a modeled dependency.", "The device and local HTTP service remain powered."),
        fault_behavior="MQTT becomes unavailable for the modeled fault window; Wi-Fi remains online.",
        vulnerable_behavior="The session model records failed commands and does not reconnect automatically.",
        hardened_behavior="The session model detects the disconnect, retries with bounded backoff, and reconnects after restoration.",
        recovery_policy="Broker restoration is modeled at T+06; profile policy determines whether the client reconnects.",
        primary_metric="Modeled MQTT recovery duration and operation delivery.",
        educational_explanation="A downstream broker outage should not be confused with a Wi-Fi outage. Recovery behavior depends on reconnect policy and bounded retry handling.",
        limitations="No broker process is stopped, no MQTT packet is sent, and HTTP availability is a logical model only.",
        plans={
            "Vulnerable": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Broker outage injected", "MQTT", "The modeled broker becomes unavailable; Wi-Fi stays online.", status={"mqtt": "OFFLINE", "recovery": "NOT DETECTED"}, degraded=True, severity="HIGH", decision="Injected"),
                _m(2, "DEGRADED", "Command delivery is interrupted", "MQTT → ESP32", "Three modeled operations fail while the broker is unavailable.", metrics={"operations_attempted": 3, "operations_failed": 3}, available=False, degraded=True, detected=True, severity="HIGH", decision="Failed"),
                _m(4, "RECOVERING", "Broker availability restored", "MQTT", "The dependency is available again, but the vulnerable profile has no automatic reconnect policy.", status={"mqtt": "AVAILABLE · CLIENT OFFLINE", "recovery": "MANUAL"}, available=False, degraded=True, action="Manual reconnect required", severity="MEDIUM"),
                _m(8, "FAILED_TO_RECOVER", "MQTT session remains disconnected", "MQTT", "The modeled client remains offline through the recovery window.", status={"mqtt": "OFFLINE", "recovery": "FAILED"}, available=False, degraded=True, action="Manual intervention required", severity="HIGH", decision="Failed to recover"),
                _m(10, "FAILED_TO_RECOVER", "Experiment window complete", "MQTT", "The primary command path did not recover within the modeled window.", available=False, degraded=True, action="Manual intervention required", severity="HIGH", decision="Failed to recover"),
            ),
            "Hardened": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Broker outage injected", "MQTT", "The modeled broker becomes unavailable; Wi-Fi stays online.", status={"mqtt": "OFFLINE", "recovery": "DETECTING"}, degraded=True, severity="HIGH", decision="Injected"),
                _m(2, "DEGRADED", "Disconnect detected", "MQTT", "The modeled client detects the missing broker session; local HTTP remains available.", status={"recovery": "BACKOFF"}, metrics={"operations_attempted": 3, "operations_failed": 3}, degraded=True, detected=True, action="Begin bounded reconnect backoff", severity="MEDIUM"),
                _m(4, "RECOVERING", "Reconnect retry scheduled", "MQTT", "A bounded retry is scheduled; no retry loop or packet is executed.", status={"recovery": "RETRYING"}, metrics={"retry_count": 2}, degraded=True, action="Retry with modeled backoff", severity="MEDIUM"),
                _m(6, "RECOVERING", "Modeled broker restored", "MQTT", "The dependency returns; the modeled client can establish a new session.", status={"mqtt": "CONNECTING", "recovery": "RECONNECTING"}, available=False, degraded=True, action="Reconnect after dependency restore", severity="INFO"),
                _m(8, "RECOVERED", "MQTT command path restored", "MQTT → ESP32", "The hardened reconnect policy restores the modeled command path.", status={"mqtt": "ONLINE", "recovery": "RECOVERED"}, metrics={"operations_attempted": 2, "operations_succeeded": 2}, recovered=True, action="Bounded reconnect and session restore", decision="Recovered"),
                _m(10, "COMPLETE", "Experiment window complete", "ESP32 IoT node model", "MQTT and local HTTP are modeled as available at the end of the run.", status={"mqtt": "ONLINE", "recovery": "STABLE"}, action="No further action", decision="Complete"),
            ),
        },
    ),
    "wifi-connectivity-loss": ChaosScenario(
        id="wifi-connectivity-loss",
        name="Wi-Fi connectivity loss",
        category="Network dependency",
        summary="Drop modeled Wi-Fi and propagate the dependency loss to MQTT.",
        affected_components=("Wi-Fi", "ESP32", "MQTT"),
        board_path=("Wi-Fi", "ESP32_MODULE", "MQTT"),
        assumptions=("Wi-Fi is an upstream dependency for MQTT.", "The ESP32 application remains powered."),
        fault_behavior="Wi-Fi disconnects; MQTT follows because it depends on the network link.",
        vulnerable_behavior="The model has no automatic Wi-Fi recovery, leaving MQTT unavailable after the access link returns.",
        hardened_behavior="The model retries Wi-Fi with bounded backoff, then reconnects MQTT after Wi-Fi returns.",
        recovery_policy="The modeled access link returns at T+06; MQTT is restored only after Wi-Fi.",
        primary_metric="Modeled dependency recovery and operation delivery.",
        educational_explanation="Dependency order matters: Wi-Fi loss propagates to MQTT, while an MQTT-only outage does not imply Wi-Fi loss.",
        limitations="No radio interface is disconnected and no access point or network is contacted.",
        plans={
            "Vulnerable": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Wi-Fi loss injected", "Wi-Fi", "The modeled station link drops.", status={"wifi": "OFFLINE", "mqtt": "OFFLINE", "recovery": "NOT DETECTED"}, available=False, degraded=True, severity="HIGH", decision="Injected"),
                _m(2, "DEGRADED", "MQTT dependency is unavailable", "Wi-Fi → MQTT", "Three modeled network operations fail because the upstream link is down.", metrics={"operations_attempted": 3, "operations_failed": 3}, available=False, degraded=True, detected=True, severity="HIGH", decision="Failed"),
                _m(4, "RECOVERING", "Modeled Wi-Fi restored", "Wi-Fi", "The access link returns, but the client is not configured to rejoin automatically.", status={"wifi": "ONLINE", "mqtt": "OFFLINE", "recovery": "MANUAL"}, available=False, degraded=True, action="Manual Wi-Fi reconnect required", severity="MEDIUM"),
                _m(8, "FAILED_TO_RECOVER", "MQTT remains disconnected", "MQTT", "The modeled command path remains down after Wi-Fi returns.", available=False, degraded=True, action="Manual reconnect required", severity="HIGH", decision="Failed to recover"),
                _m(10, "FAILED_TO_RECOVER", "Experiment window complete", "ESP32 IoT node model", "The dependent service did not recover within the modeled window.", available=False, degraded=True, decision="Failed to recover"),
            ),
            "Hardened": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Wi-Fi loss injected", "Wi-Fi", "The modeled station link drops.", status={"wifi": "OFFLINE", "mqtt": "OFFLINE", "recovery": "DETECTING"}, available=False, degraded=True, severity="HIGH", decision="Injected"),
                _m(2, "DEGRADED", "Dependency loss detected", "Wi-Fi → MQTT", "The client records that MQTT depends on Wi-Fi; HTTP availability remains locally modeled.", metrics={"operations_attempted": 3, "operations_failed": 3}, available=False, degraded=True, detected=True, action="Retry Wi-Fi with bounded backoff", severity="MEDIUM"),
                _m(4, "RECOVERING", "Wi-Fi retry scheduled", "Wi-Fi", "A bounded reconnection attempt is scheduled.", status={"recovery": "RETRYING WI-FI"}, metrics={"retry_count": 2}, available=False, degraded=True, action="Retry Wi-Fi", severity="MEDIUM"),
                _m(6, "RECOVERING", "Modeled Wi-Fi restored", "Wi-Fi", "The modeled station link returns; MQTT still needs its own reconnect.", status={"wifi": "ONLINE", "mqtt": "CONNECTING", "recovery": "RECONNECTING MQTT"}, available=False, degraded=True, action="Reconnect dependent MQTT session"),
                _m(8, "RECOVERED", "MQTT restored after Wi-Fi", "MQTT", "The hardened plan restores the dependency in order.", status={"mqtt": "ONLINE", "recovery": "RECOVERED"}, metrics={"operations_attempted": 2, "operations_succeeded": 2}, recovered=True, action="Restore Wi-Fi, then MQTT", decision="Recovered"),
                _m(10, "COMPLETE", "Experiment window complete", "ESP32 IoT node model", "Wi-Fi and MQTT are modeled as available at the end of the run.", status={"recovery": "STABLE"}, action="No further action", decision="Complete"),
            ),
        },
    ),
    "device-firmware-crash": ChaosScenario(
        id="device-firmware-crash",
        name="Device / firmware crash",
        category="Application availability",
        summary="Make the modeled device unavailable, then observe reboot and service restoration.",
        affected_components=("ESP32", "MQTT", "HTTP", "GPIO"),
        board_path=("ESP32_MODULE", "MQTT", "HTTP", "GPIO23"),
        assumptions=("The device process owns the modeled HTTP and MQTT services.", "Volatile application state is reset on reboot."),
        fault_behavior="Application stops; modeled HTTP and MQTT services go offline until restart.",
        vulnerable_behavior="Without a restart supervisor, service remains down until manual intervention.",
        hardened_behavior="A modeled supervisor restarts the application, then network services return in dependency order.",
        recovery_policy="The hardened model restarts at T+04, restores Wi-Fi at T+06, and MQTT/HTTP by T+08.",
        primary_metric="Modeled service availability and recovery duration.",
        educational_explanation="A process restart is different from a network reconnect: volatile application state can be lost, then dependencies must be re-established.",
        limitations="No process is crashed, no firmware is reset, and GPIO values are not read or changed.",
        plans={
            "Vulnerable": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Application crash injected", "ESP32 module", "The behavioral model marks the application as stopped.", status={"device": "OFFLINE", "http": "OFFLINE", "mqtt": "OFFLINE", "recovery": "NOT SUPERVISED"}, available=False, degraded=True, severity="HIGH", decision="Injected"),
                _m(2, "DEGRADED", "Node services unavailable", "ESP32 → HTTP / MQTT", "Three modeled operations cannot reach the stopped application.", metrics={"operations_attempted": 3, "operations_failed": 3}, available=False, degraded=True, detected=True, severity="HIGH", decision="Failed"),
                _m(4, "RECOVERING", "Manual restart needed", "ESP32 module", "The vulnerable profile has no automatic restart supervisor.", status={"recovery": "MANUAL RESTART"}, available=False, degraded=True, action="Manual restart required", severity="MEDIUM"),
                _m(8, "FAILED_TO_RECOVER", "Node remains unavailable", "ESP32 module", "The modeled application is still stopped at the end of the recovery window.", available=False, degraded=True, action="Manual restart required", severity="HIGH", decision="Failed to recover"),
                _m(10, "FAILED_TO_RECOVER", "Experiment window complete", "ESP32 module", "Service recovery did not occur within the modeled window.", available=False, degraded=True, decision="Failed to recover"),
            ),
            "Hardened": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Application crash injected", "ESP32 module", "The behavioral model marks the application as stopped.", status={"device": "OFFLINE", "http": "OFFLINE", "mqtt": "OFFLINE", "recovery": "SUPERVISOR DETECTING"}, available=False, degraded=True, severity="HIGH", decision="Injected"),
                _m(2, "DEGRADED", "Node services unavailable", "ESP32 → HTTP / MQTT", "The supervisor detects missed application progress.", metrics={"operations_attempted": 3, "operations_failed": 3}, available=False, degraded=True, detected=True, action="Schedule bounded application restart", severity="HIGH"),
                _m(4, "RECOVERING", "Modeled reboot begins", "ESP32 module", "A supervised reboot starts; volatile application state is reset in the model.", status={"device": "BOOTING", "recovery": "RESTARTING"}, metrics={"restart_count": 1}, available=False, degraded=True, action="Restart application", severity="MEDIUM"),
                _m(6, "RECOVERING", "Wi-Fi rejoined", "Wi-Fi", "The modeled application has booted and rejoined its network dependency.", status={"device": "RUNNING", "wifi": "ONLINE", "mqtt": "CONNECTING", "http": "ONLINE", "recovery": "RESTORING SERVICES"}, available=False, degraded=True, action="Reconnect MQTT after Wi-Fi"),
                _m(8, "RECOVERED", "Node services restored", "HTTP / MQTT", "The model restores local HTTP and MQTT after reboot.", status={"mqtt": "ONLINE", "recovery": "RECOVERED"}, metrics={"operations_attempted": 2, "operations_succeeded": 2}, recovered=True, action="Restore services in dependency order", decision="Recovered"),
                _m(10, "COMPLETE", "Experiment window complete", "ESP32 IoT node model", "The node is modeled as stable after one restart.", status={"recovery": "STABLE"}, action="No further action", decision="Complete"),
            ),
        },
    ),
    "sensor-failure": ChaosScenario(
        id="sensor-failure",
        name="Sensor failure",
        category="Input integrity",
        summary="Model stale or invalid sensor samples without assuming a specific sensor or board wiring.",
        affected_components=("Sensor model", "ESP32", "Application"),
        board_path=("ESP32_MODULE", "GPIO22", "Sensor model"),
        assumptions=("The sensor is an abstract input source, not a connected part.", "A last-known-valid sample is available to the hardened profile."),
        fault_behavior="The abstract sensor source emits stale/invalid samples for the fault window.",
        vulnerable_behavior="The model trusts invalid samples and records integrity failures.",
        hardened_behavior="The model rejects invalid samples, retains the last valid sample, and raises a fault state.",
        recovery_policy="The abstract sample source returns to normal at T+06.",
        primary_metric="Invalid samples accepted versus rejected.",
        educational_explanation="Input validation and fallback handling can preserve safe application behavior even when a sensor source is unreliable.",
        limitations="No physical sensor is present; no temperature, pressure, or other engineering range is asserted.",
        plans={
            "Vulnerable": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Sensor source fault injected", "Sensor model", "The abstract input changes from healthy to stale/invalid.", status={"sensor": "STALE / INVALID"}, degraded=True, severity="MEDIUM", decision="Injected"),
                _m(2, "DEGRADED", "Invalid samples trusted", "Sensor model → application", "Two invalid modeled samples are accepted without a plausibility check.", metrics={"operations_attempted": 2, "operations_failed": 2, "integrity_failures": 2}, degraded=True, detected=False, severity="HIGH", decision="Accepted invalid input"),
                _m(4, "DEGRADED", "Application remains exposed to stale input", "Sensor model", "The vulnerable profile continues consuming the stale sample.", metrics={"operations_attempted": 2, "operations_failed": 2, "integrity_failures": 2}, degraded=True, severity="MEDIUM"),
                _m(6, "RECOVERING", "Sensor source restored", "Sensor model", "The abstract source returns to healthy; the application has not validated prior samples.", status={"sensor": "HEALTHY", "recovery": "REVALIDATING"}, degraded=True, detected=True, action="Resume fresh sample processing", severity="MEDIUM"),
                _m(8, "RECOVERED", "Fresh input accepted", "Sensor model → application", "New samples are modeled as valid again.", metrics={"operations_attempted": 2, "operations_succeeded": 2}, recovered=True, action="Resume fresh samples", decision="Recovered"),
                _m(10, "COMPLETE", "Experiment window complete", "ESP32 IoT node model", "The abstract sensor source is healthy at the end of the run.", status={"recovery": "STABLE"}, decision="Complete"),
            ),
            "Hardened": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Sensor source fault injected", "Sensor model", "The abstract input changes from healthy to stale/invalid.", status={"sensor": "STALE / INVALID", "recovery": "VALIDATING"}, degraded=True, severity="MEDIUM", decision="Injected"),
                _m(2, "DEGRADED", "Invalid samples rejected", "Sensor model → application", "Two invalid samples are rejected; the model retains the last valid sample.", metrics={"operations_attempted": 2, "operations_failed": 2, "invalid_samples_rejected": 2}, degraded=True, detected=True, action="Use last-known-valid sample and flag sensor", severity="MEDIUM", decision="Rejected invalid input"),
                _m(4, "RECOVERING", "Fallback remains active", "Application", "Application service remains available on the last valid sample while the sensor is faulted.", status={"sensor": "UNAVAILABLE", "recovery": "FALLBACK ACTIVE"}, metrics={"operations_attempted": 2, "operations_succeeded": 2}, degraded=True, action="Keep last-known-valid sample", severity="INFO"),
                _m(6, "RECOVERING", "Sensor source restored", "Sensor model", "The abstract source returns; the model validates new samples before accepting them.", status={"sensor": "VALIDATING", "recovery": "REVALIDATING"}, action="Validate fresh sample"),
                _m(8, "RECOVERED", "Fresh input validated", "Sensor model → application", "A fresh sample passes the modeled plausibility gate.", status={"sensor": "HEALTHY", "recovery": "RECOVERED"}, metrics={"operations_attempted": 2, "operations_succeeded": 2}, recovered=True, action="Return to validated input", decision="Recovered"),
                _m(10, "COMPLETE", "Experiment window complete", "ESP32 IoT node model", "The abstract sensor source is healthy and the fallback is released.", status={"recovery": "STABLE"}, decision="Complete"),
            ),
        },
    ),
    "network-latency": ChaosScenario(
        id="network-latency",
        name="Network latency",
        category="Network quality",
        summary="Increase modeled request delay beyond a declared timeout budget.",
        affected_components=("Wi-Fi", "MQTT", "Command path"),
        board_path=("Wi-Fi", "ESP32_MODULE", "MQTT"),
        assumptions=("Nominal modeled latency is 80 ms.", "The example timeout budget is 800 ms; these are model parameters, not measurements."),
        fault_behavior="Modeled request latency rises to 1,200 ms and returns to 80 ms at T+06.",
        vulnerable_behavior="The model waits beyond its timeout budget and records delayed/failed work.",
        hardened_behavior="The model applies a bounded timeout and fallback, keeping the application responsive.",
        recovery_policy="Latency returns to nominal at T+06; recovery represents policy state, not network shaping.",
        primary_metric="Modeled timeout failures and recovery duration.",
        educational_explanation="Timeout budgets, bounded retries, and fallback behavior can prevent a slow dependency from consuming all application capacity.",
        limitations="No packets are delayed and the modeled millisecond values are not ESP32 or Wi-Fi measurements.",
        plans={
            "Vulnerable": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Latency raised to 1,200 ms", "Wi-Fi → MQTT", "Modeled latency exceeds the example 800 ms timeout budget.", status={"mqtt": "DELAYED · 1,200 ms"}, degraded=True, severity="MEDIUM", decision="Injected"),
                _m(2, "DEGRADED", "Requests exceed timeout budget", "MQTT command path", "Two modeled operations time out while the vulnerable profile waits without bounded fallback.", metrics={"operations_attempted": 2, "operations_failed": 2}, available=False, degraded=True, detected=True, severity="HIGH", decision="Timed out"),
                _m(4, "RECOVERING", "Latency remains above budget", "MQTT", "No bounded timeout recovery is applied in this profile.", metrics={"operations_attempted": 2, "operations_failed": 2}, available=False, degraded=True, action="No automatic fallback", severity="MEDIUM"),
                _m(6, "RECOVERING", "Modeled latency returns to 80 ms", "Wi-Fi → MQTT", "The network condition is restored in the model; queued operations still need resolution.", status={"mqtt": "RECONNECTING"}, available=False, degraded=True, action="Resolve delayed operations"),
                _m(8, "RECOVERED", "Command path responds within budget", "MQTT", "The modeled link is again within its example latency budget.", status={"mqtt": "ONLINE"}, metrics={"operations_attempted": 1, "operations_succeeded": 1}, recovered=True, action="Return to nominal latency", decision="Recovered"),
                _m(10, "COMPLETE", "Experiment window complete", "ESP32 IoT node model", "The command path is modeled as stable.", status={"recovery": "STABLE"}, decision="Complete"),
            ),
            "Hardened": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Latency raised to 1,200 ms", "Wi-Fi → MQTT", "Modeled latency exceeds the example 800 ms timeout budget.", status={"mqtt": "DELAYED · 1,200 ms", "recovery": "TIMEOUT GUARD"}, degraded=True, severity="MEDIUM", decision="Injected"),
                _m(2, "DEGRADED", "Timeout guard contains delay", "MQTT command path", "Two operations time out within the budget and the local application remains responsive.", metrics={"operations_attempted": 2, "operations_failed": 2}, degraded=True, detected=True, action="Apply bounded timeout and fallback", severity="MEDIUM", decision="Contained"),
                _m(4, "RECOVERING", "Retry remains bounded", "MQTT", "One modeled retry is scheduled; no network request is sent.", status={"recovery": "BOUNDED RETRY"}, metrics={"retry_count": 1}, degraded=True, action="Retry once within budget", severity="INFO"),
                _m(6, "RECOVERING", "Modeled latency returns to 80 ms", "Wi-Fi → MQTT", "The modeled link returns to the nominal latency assumption.", status={"mqtt": "RECONNECTING", "recovery": "RESTORING"}, degraded=True, action="Resume normal timeout budget"),
                _m(8, "RECOVERED", "Command path responds within budget", "MQTT", "The bounded policy restores normal modeled operation.", status={"mqtt": "ONLINE", "recovery": "RECOVERED"}, metrics={"operations_attempted": 2, "operations_succeeded": 2}, recovered=True, action="Return to nominal latency", decision="Recovered"),
                _m(10, "COMPLETE", "Experiment window complete", "ESP32 IoT node model", "The command path is modeled as stable and responsive.", status={"recovery": "STABLE"}, decision="Complete"),
            ),
        },
    ),
    "packet-loss": ChaosScenario(
        id="packet-loss",
        name="Packet loss",
        category="Network quality",
        summary="Apply a deterministic packet-loss model to a fixed operation batch.",
        affected_components=("Wi-Fi", "MQTT", "Command path"),
        board_path=("Wi-Fi", "ESP32_MODULE", "MQTT", "GPIO23"),
        assumptions=("The batch contains ten modeled operations.", "The loss pattern is a deterministic formula, not random traffic."),
        fault_behavior="The chosen 0–50% loss percentage marks a fixed subset of the ten-operation batch as lost.",
        vulnerable_behavior="The model does not retry operations marked lost on first delivery.",
        hardened_behavior="The model retries at most three lost operations once; retry delivery is calculated deterministically.",
        recovery_policy="The modeled link returns to nominal at T+06; retries are bounded by the fixed rule.",
        primary_metric="Modeled operation success and retry count.",
        educational_explanation="Retries improve delivery only when their count and behavior are bounded. Repeated retransmission can increase load, so this model caps retries at three.",
        limitations="No packet is transmitted or dropped; numbers describe a deterministic batch model only.",
        plans={
            "Vulnerable": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Packet-loss model enabled", "Wi-Fi → MQTT", "The selected fixed loss percentage is applied to a ten-operation batch.", status={"mqtt": "DEGRADED · LOSS MODEL"}, degraded=True, severity="MEDIUM", decision="Injected"),
                _m(2, "DEGRADED", "Fixed operation batch evaluated", "MQTT command path", "A deterministic loss formula evaluates the ten modeled operations.", degraded=True, detected=True, severity="MEDIUM", decision="Modeled"),
                _m(4, "RECOVERING", "No retry policy applied", "MQTT", "The vulnerable profile does not retry operations marked lost.", degraded=True, action="No retry", severity="INFO"),
                _m(6, "RECOVERING", "Modeled link restored", "Wi-Fi → MQTT", "The fault window ends; first-attempt delivery outcomes remain in the record.", status={"mqtt": "ONLINE"}, action="Restore nominal link"),
                _m(8, "RECOVERED", "Service returns to nominal", "MQTT", "The modeled transport condition is cleared.", recovered=True, action="Clear loss condition", decision="Recovered"),
                _m(10, "COMPLETE", "Experiment window complete", "ESP32 IoT node model", "The fixed operation batch and loss outcomes are recorded.", status={"recovery": "STABLE"}, decision="Complete"),
            ),
            "Hardened": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Packet-loss model enabled", "Wi-Fi → MQTT", "The selected fixed loss percentage is applied to a ten-operation batch.", status={"mqtt": "DEGRADED · LOSS MODEL", "recovery": "RETRY BUDGET 3"}, degraded=True, severity="MEDIUM", decision="Injected"),
                _m(2, "DEGRADED", "Fixed operation batch evaluated", "MQTT command path", "A deterministic loss formula evaluates the ten modeled operations.", degraded=True, detected=True, action="Retry up to three modeled losses", severity="MEDIUM", decision="Modeled"),
                _m(4, "RECOVERING", "Bounded retries evaluated", "MQTT", "At most three retry opportunities are applied by the deterministic model.", status={"recovery": "BOUNDED RETRY"}, degraded=True, action="Apply one bounded retry per selected loss"),
                _m(6, "RECOVERING", "Modeled link restored", "Wi-Fi → MQTT", "The fault window ends; deterministic retry outcomes are retained.", status={"mqtt": "ONLINE"}, action="Restore nominal link"),
                _m(8, "RECOVERED", "Service returns to nominal", "MQTT", "The modeled transport condition is cleared.", status={"recovery": "RECOVERED"}, recovered=True, action="Clear loss condition", decision="Recovered"),
                _m(10, "COMPLETE", "Experiment window complete", "ESP32 IoT node model", "The fixed operation batch and retry outcomes are recorded.", status={"recovery": "STABLE"}, decision="Complete"),
            ),
        },
        parameter_kind="packet_loss_pct",
        default_packet_loss_pct=30,
    ),
    "memory-pressure": ChaosScenario(
        id="memory-pressure",
        name="Memory pressure",
        category="Resource pressure",
        summary="Progress modeled resource pressure from elevated to critical without inventing heap measurements.",
        affected_components=("ESP32 application model", "MQTT", "Task queue"),
        board_path=("ESP32_MODULE", "MQTT", "GPIO23"),
        assumptions=("Pressure is qualitative: NORMAL, ELEVATED, or CRITICAL.", "No free-heap or RAM amount is asserted."),
        fault_behavior="Modeled application resource pressure progresses to critical during the fault window.",
        vulnerable_behavior="The model keeps optional work enabled and enters a repeated-restart failure state.",
        hardened_behavior="The model sheds optional work early and preserves essential service behavior.",
        recovery_policy="Pressure returns to nominal at T+06; hardened policy restores deferred work afterward.",
        primary_metric="Modeled service availability and restart count.",
        educational_explanation="Embedded systems have finite resources. Admission control and workload shedding can protect essential functions under pressure.",
        limitations="This is qualitative behavioral pressure; it is not ESP32 heap, stack, CPU, or flash telemetry.",
        plans={
            "Vulnerable": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Resource pressure raised", "ESP32 application model", "Modeled pressure rises from NORMAL to ELEVATED.", status={"device": "RUNNING · ELEVATED PRESSURE"}, degraded=True, severity="MEDIUM", decision="Injected"),
                _m(2, "DEGRADED", "Pressure reaches CRITICAL", "Task queue", "Optional and essential modeled work continue competing for capacity.", status={"device": "UNSTABLE · CRITICAL PRESSURE"}, metrics={"operations_attempted": 3, "operations_failed": 3}, available=False, degraded=True, detected=True, severity="HIGH", decision="Degraded"),
                _m(4, "RECOVERING", "Repeated restart state modeled", "ESP32 application model", "The vulnerable profile does not shed optional work; two modeled restarts occur.", status={"device": "RESTART LOOP", "recovery": "UNSTABLE"}, metrics={"restart_count": 2}, available=False, degraded=True, action="Manual workload reduction required", severity="HIGH"),
                _m(6, "RECOVERING", "Pressure fault cleared", "ESP32 application model", "Modeled pressure returns to NORMAL, but the application is not stable.", status={"recovery": "RESTARTING"}, available=False, degraded=True, action="Manual restart required"),
                _m(8, "FAILED_TO_RECOVER", "Service remains unstable", "Task queue", "The model does not exit the restart loop within the recovery window.", status={"recovery": "FAILED"}, available=False, degraded=True, action="Manual intervention required", severity="HIGH", decision="Failed to recover"),
                _m(10, "FAILED_TO_RECOVER", "Experiment window complete", "ESP32 IoT node model", "The modeled service did not stabilize within the run.", available=False, degraded=True, decision="Failed to recover"),
            ),
            "Hardened": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Resource pressure raised", "ESP32 application model", "Modeled pressure rises from NORMAL to ELEVATED.", status={"device": "RUNNING · ELEVATED PRESSURE"}, degraded=True, severity="MEDIUM", decision="Injected"),
                _m(2, "DEGRADED", "Optional work shed", "Task queue", "The modeled admission policy sheds nonessential work before pressure becomes critical.", status={"device": "RUNNING · ESSENTIAL WORK"}, metrics={"operations_attempted": 3, "operations_succeeded": 2, "operations_failed": 1}, degraded=True, detected=True, action="Defer nonessential tasks", severity="MEDIUM", decision="Contained"),
                _m(4, "RECOVERING", "Essential service remains available", "ESP32 application model", "Critical modeled work continues while optional work remains deferred.", status={"recovery": "PRESSURE CONTAINED"}, metrics={"operations_attempted": 2, "operations_succeeded": 2}, action="Keep optional work deferred"),
                _m(6, "RECOVERING", "Pressure returns to NORMAL", "ESP32 application model", "The modeled resource condition clears.", status={"device": "RUNNING · NORMAL PRESSURE", "recovery": "RESTORING"}, action="Restore deferred work gradually"),
                _m(8, "RECOVERED", "Deferred work restored", "Task queue", "The modeled node resumes its normal task mix without restarting.", status={"recovery": "RECOVERED"}, metrics={"operations_attempted": 2, "operations_succeeded": 2}, recovered=True, action="Restore workload gradually", decision="Recovered"),
                _m(10, "COMPLETE", "Experiment window complete", "ESP32 IoT node model", "Essential service remains stable with no modeled restart.", status={"recovery": "STABLE"}, decision="Complete"),
            ),
        },
    ),
    "watchdog-task-stall": ChaosScenario(
        id="watchdog-task-stall",
        name="Watchdog / task stall",
        category="Task liveness",
        summary="Stall a modeled application task and compare watchdog recovery behavior.",
        affected_components=("ESP32 task", "Watchdog model", "MQTT"),
        board_path=("ESP32_MODULE", "MQTT", "GPIO23"),
        assumptions=("Task progress is a logical heartbeat; no physical watchdog is read.", "Restart restores volatile app state."),
        fault_behavior="A modeled task stops advancing; a watchdog threshold is reached at T+03.",
        vulnerable_behavior="No watchdog response is modeled, so the task remains stalled through the run.",
        hardened_behavior="The watchdog model detects the missed heartbeat and initiates one bounded restart.",
        recovery_policy="Hardened restart at T+04; modeled service restoration completes at T+08.",
        primary_metric="Modeled detection delay, restart count, and recovery duration.",
        educational_explanation="A watchdog only helps when its threshold, ownership, and restart consequences are understood and bounded.",
        limitations="No FreeRTOS task, hardware watchdog, or ESP32 reset is triggered.",
        plans={
            "Vulnerable": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Application task stall injected", "ESP32 task model", "The modeled task heartbeat stops advancing.", status={"device": "RUNNING · TASK STALLED", "recovery": "WATCHDOG DISABLED"}, degraded=True, severity="MEDIUM", decision="Injected"),
                _m(2, "DEGRADED", "Task stops serving operations", "ESP32 task → MQTT", "Three modeled operations fail while the task is stalled.", metrics={"operations_attempted": 3, "operations_failed": 3}, available=False, degraded=True, detected=False, severity="HIGH", decision="Failed"),
                _m(4, "DEGRADED", "No watchdog action", "Watchdog model", "The vulnerable profile does not detect the missed heartbeat.", available=False, degraded=True, action="No watchdog configured", severity="HIGH"),
                _m(8, "FAILED_TO_RECOVER", "Task remains stalled", "ESP32 task model", "The modeled task is still unresponsive at the end of the recovery window.", status={"recovery": "FAILED"}, available=False, degraded=True, action="Manual restart required", severity="HIGH", decision="Failed to recover"),
                _m(10, "FAILED_TO_RECOVER", "Experiment window complete", "ESP32 task model", "No recovery was modeled within the run.", available=False, degraded=True, decision="Failed to recover"),
            ),
            "Hardened": _plan(
                _baseline,
                _m(1, "FAULT_INJECTED", "Application task stall injected", "ESP32 task model", "The modeled task heartbeat stops advancing.", status={"device": "RUNNING · TASK STALLED", "recovery": "WATCHDOG ARMED"}, degraded=True, severity="MEDIUM", decision="Injected"),
                _m(2, "DEGRADED", "Task progress missed", "ESP32 task model", "The modeled heartbeat is missing; the watchdog threshold is evaluated at T+03.", metrics={"operations_attempted": 3, "operations_failed": 3}, available=False, degraded=True, detected=True, action="Wait until bounded watchdog threshold", severity="MEDIUM"),
                _m(4, "RECOVERING", "Watchdog restart modeled", "ESP32 watchdog", "One restart is modeled after the missed-heartbeat threshold.", status={"device": "BOOTING", "recovery": "WATCHDOG RESTART"}, metrics={"restart_count": 1}, available=False, degraded=True, action="Restart stalled application", severity="MEDIUM"),
                _m(6, "RECOVERING", "Application task resumed", "ESP32 task model", "The modeled application restarts and reconnects its dependencies.", status={"device": "RUNNING", "mqtt": "CONNECTING", "recovery": "RESTORING"}, metrics={"operations_attempted": 1, "operations_succeeded": 1}, available=False, degraded=True, action="Restore service after reboot"),
                _m(8, "RECOVERED", "Task heartbeat restored", "ESP32 task model", "The model reports the task as responsive and its service path as available.", status={"mqtt": "ONLINE", "recovery": "RECOVERED"}, metrics={"operations_attempted": 2, "operations_succeeded": 2}, recovered=True, action="Resume monitored task", decision="Recovered"),
                _m(10, "COMPLETE", "Experiment window complete", "ESP32 IoT node model", "The modeled task remains stable after one restart.", status={"recovery": "STABLE"}, decision="Complete"),
            ),
        },
    ),
}

CHAOS_SCENARIO_IDS = tuple(CHAOS_SCENARIOS)
CHAOS_SCENARIO_NAMES = tuple(scenario.name for scenario in CHAOS_SCENARIOS.values())
CHAOS_SCENARIOS_BY_NAME = {scenario.name: scenario for scenario in CHAOS_SCENARIOS.values()}


def normalize_chaos_scenario(value: object) -> str:
    """Normalize a persisted scenario ID or label to a catalog ID."""
    text = str(value) if value is not None else ""
    if text in CHAOS_SCENARIOS:
        return text
    scenario = CHAOS_SCENARIOS_BY_NAME.get(text)
    return scenario.id if scenario else CHAOS_SCENARIO_IDS[0]
