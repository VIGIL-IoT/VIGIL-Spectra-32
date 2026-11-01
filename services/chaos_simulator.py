"""Deterministic, session-only lifecycle engine for embedded failure scenarios."""

from __future__ import annotations

from math import floor
from uuid import uuid4

from data.chaos_scenarios import CHAOS_SCENARIOS, ChaosMilestone, ChaosScenario, normalize_chaos_scenario
from data.chaos_state import ChaosProfileState, ChaosState, create_initial_chaos_state


PROFILES = ("Vulnerable", "Hardened")
PROFILE_SELECTIONS = (*PROFILES, "Compare both")
_METRIC_KEYS = (
    "operations_attempted",
    "operations_succeeded",
    "operations_failed",
    "retry_count",
    "restart_count",
    "integrity_failures",
    "invalid_samples_rejected",
)
_BASELINE_STATUS = {
    "device": "RUNNING",
    "wifi": "ONLINE",
    "mqtt": "ONLINE",
    "http": "ONLINE",
    "sensor": "HEALTHY",
    "recovery": "READY",
}


def start_experiment(
    state: ChaosState,
    scenario_id: str,
    profile_selection: str,
    *,
    now_monotonic: float,
    packet_loss_pct: int = 30,
) -> None:
    """Start or replace a deterministic experiment in the current session."""
    normalized_scenario = normalize_chaos_scenario(scenario_id)
    if profile_selection not in PROFILE_SELECTIONS:
        raise ValueError(f"Unknown Chaos Lab profile: {profile_selection}")
    if not isinstance(packet_loss_pct, int) or not 0 <= packet_loss_pct <= 50:
        raise ValueError("packet loss must be an integer from 0 to 50 percent")

    scenario = CHAOS_SCENARIOS[normalized_scenario]
    profiles = PROFILES if profile_selection == "Compare both" else (profile_selection,)
    state.update(
        {
            "schema_version": state.get("schema_version", 1),
            "is_simulated": True,
            "active": True,
            "experiment_id": f"CHAOS-{uuid4().hex[:8].upper()}",
            "scenario_id": scenario.id,
            "scenario_name": scenario.name,
            "profile_selection": profile_selection,
            "stage": "BASELINE",
            "elapsed_seconds": 0,
            "started_at_monotonic": float(now_monotonic),
            "packet_loss_pct": packet_loss_pct,
            "baseline_snapshot": dict(_BASELINE_STATUS),
            "board_path": list(scenario.board_path),
            "profiles": {
                profile: ChaosProfileState(
                    stage="IDLE",
                    statuses=dict(_BASELINE_STATUS),
                    metrics={key: 0 for key in _METRIC_KEYS},
                    processed_milestones=[],
                    detected_at_seconds=None,
                    recovered_at_seconds=None,
                    result=None,
                )
                for profile in profiles
            },
            "timeline": [],
            "result": None,
        }
    )
    advance_experiment(state, 0)


def reset_experiment(state: ChaosState) -> None:
    """Return the Chaos Lab to idle while retaining its selected profile."""
    profile_selection = state.get("profile_selection", "Vulnerable")
    state.clear()
    state.update(create_initial_chaos_state(profile_selection))


def advance_experiment(state: ChaosState, elapsed_seconds: int) -> None:
    """Advance to a logical time without sleeping or affecting external systems."""
    if not state.get("scenario_id"):
        return
    scenario = CHAOS_SCENARIOS.get(state["scenario_id"])
    if scenario is None:
        reset_experiment(state)
        return

    duration = max(milestone.at_seconds for plan in scenario.plans.values() for milestone in plan)
    elapsed = max(0, min(int(elapsed_seconds), duration))
    state["elapsed_seconds"] = elapsed
    for profile, profile_state in state["profiles"].items():
        plan = scenario.plans[profile]
        _advance_profile(state, scenario, profile, profile_state, plan, elapsed)
    profile_order = {profile: index for index, profile in enumerate(PROFILES)}
    state["timeline"].sort(
        key=lambda event: (event["elapsed_seconds"], profile_order.get(event["profile"], 99))
    )

    if elapsed >= duration:
        state["active"] = False
        state["stage"] = "COMPLETE"
        result_profiles = {}
        for profile, profile_state in state["profiles"].items():
            profile_state["result"] = _calculate_metrics(
                scenario.plans[profile],
                profile_state,
                elapsed,
                completed=True,
            )
            result_profiles[profile] = {
                "stage": profile_state["stage"],
                "statuses": dict(profile_state["statuses"]),
                "metrics": dict(profile_state["result"]),
            }
        state["result"] = {
            "experiment_id": state["experiment_id"],
            "scenario_id": scenario.id,
            "scenario_name": scenario.name,
            "completed": True,
            "is_simulated": True,
            "profiles": result_profiles,
        }
    else:
        primary_profile = "Vulnerable" if "Vulnerable" in state["profiles"] else next(iter(state["profiles"]))
        state["stage"] = state["profiles"][primary_profile]["stage"]


def _advance_profile(
    state: ChaosState,
    scenario: ChaosScenario,
    profile: str,
    profile_state: ChaosProfileState,
    plan: tuple[ChaosMilestone, ...],
    elapsed: int,
) -> None:
    processed = set(profile_state["processed_milestones"])
    previous_stage = profile_state["stage"]
    for index, milestone in enumerate(plan):
        event_id = f"{profile.lower()}-{index}-{milestone.at_seconds}"
        if milestone.at_seconds > elapsed or event_id in processed:
            continue
        profile_state["statuses"].update(milestone.status)
        for key, value in _metric_delta(state, scenario, profile, milestone).items():
            profile_state["metrics"][key] = int(profile_state["metrics"].get(key, 0) or 0) + value
        if milestone.detected and profile_state["detected_at_seconds"] is None:
            profile_state["detected_at_seconds"] = milestone.at_seconds
        if milestone.recovered and profile_state["recovered_at_seconds"] is None:
            profile_state["recovered_at_seconds"] = milestone.at_seconds
        profile_state["stage"] = milestone.stage
        _record_milestone(
            state,
            scenario,
            profile,
            milestone,
            event_id,
            previous_stage,
        )
        previous_stage = milestone.stage
        processed.add(event_id)
    profile_state["processed_milestones"] = sorted(processed)
    profile_state["metrics"].update(
        _calculate_metrics(plan, profile_state, elapsed, completed=False)
    )


def _metric_delta(
    state: ChaosState,
    scenario: ChaosScenario,
    profile: str,
    milestone: ChaosMilestone,
) -> dict[str, int]:
    if scenario.parameter_kind != "packet_loss_pct" or milestone.at_seconds != 2:
        return milestone.metric_delta

    loss_pct = state["packet_loss_pct"]
    first_attempt_losses = min(10, floor(10 * loss_pct / 100 + 0.5))
    first_attempt_successes = 10 - first_attempt_losses
    if profile == "Vulnerable":
        return {
            "operations_attempted": 10,
            "operations_succeeded": first_attempt_successes,
            "operations_failed": first_attempt_losses,
        }

    retries = min(first_attempt_losses, 3)
    retry_successes = floor(retries * (100 - loss_pct) / 100 + 0.5)
    total_successes = first_attempt_successes + retry_successes
    return {
        "operations_attempted": 10,
        "operations_succeeded": total_successes,
        "operations_failed": 10 - total_successes,
        "retry_count": retries,
    }


def _record_milestone(
    state: ChaosState,
    scenario: ChaosScenario,
    profile: str,
    milestone: ChaosMilestone,
    event_id: str,
    previous_stage: str,
) -> None:
    time_label = f"T+00:{milestone.at_seconds:02d}"
    state["timeline"].append(
        {
            "id": f"{state['experiment_id']}:{event_id}",
            "simulated_time": time_label,
            "elapsed_seconds": milestone.at_seconds,
            "experiment_id": state["experiment_id"],
            "fault": scenario.name,
            "event_type": milestone.event_type,
            "profile": profile,
            "stage": milestone.stage,
            "component": milestone.component,
            "severity": milestone.severity,
            "transition": f"{previous_stage} → {milestone.stage}",
            "decision": milestone.decision,
            "explanation": milestone.reason,
            "recovery_action": milestone.recovery_action,
        }
    )
    del state["timeline"][:-60]


def _calculate_metrics(
    plan: tuple[ChaosMilestone, ...],
    profile_state: ChaosProfileState,
    elapsed: int,
    *,
    completed: bool,
) -> dict[str, float | int | str | None]:
    available_seconds, degraded_seconds = _elapsed_service_state(plan, elapsed)
    attempted = int(profile_state["metrics"].get("operations_attempted", 0) or 0)
    succeeded = int(profile_state["metrics"].get("operations_succeeded", 0) or 0)
    failed = int(profile_state["metrics"].get("operations_failed", 0) or 0)
    operation_success_pct = round(100 * succeeded / attempted, 1) if attempted else 100.0
    availability_pct = round(100 * available_seconds / elapsed, 1) if elapsed else 100.0
    fault_at = next((item.at_seconds for item in plan if item.stage == "FAULT_INJECTED"), None)
    detected_at = profile_state["detected_at_seconds"]
    recovered_at = profile_state["recovered_at_seconds"]
    detection_delay = detected_at - fault_at if detected_at is not None and fault_at is not None else None
    recovery_duration = recovered_at - fault_at if recovered_at is not None and fault_at is not None else None
    recovery_status = "Recovered" if recovered_at is not None else "Failed to recover" if completed else "In progress"
    resilience_score: int | None = None
    if completed:
        recovery_component = 100 if recovered_at is not None else 0
        resilience_score = round(
            0.45 * availability_pct + 0.35 * operation_success_pct + 0.20 * recovery_component
        )

    return {
        "modeled_availability_pct": availability_pct,
        "operation_success_pct": operation_success_pct,
        "operations_attempted": attempted,
        "operations_succeeded": succeeded,
        "operations_failed": failed,
        "retry_count": int(profile_state["metrics"].get("retry_count", 0) or 0),
        "restart_count": int(profile_state["metrics"].get("restart_count", 0) or 0),
        "integrity_failures": int(profile_state["metrics"].get("integrity_failures", 0) or 0),
        "invalid_samples_rejected": int(profile_state["metrics"].get("invalid_samples_rejected", 0) or 0),
        "degraded_duration_seconds": degraded_seconds,
        "detection_delay_seconds": detection_delay,
        "recovery_duration_seconds": recovery_duration,
        "recovery_status": recovery_status,
        "resilience_score": resilience_score,
    }


def _elapsed_service_state(plan: tuple[ChaosMilestone, ...], elapsed: int) -> tuple[int, int]:
    available_seconds = 0
    degraded_seconds = 0
    cursor = 0
    available = True
    degraded = False
    for milestone in plan:
        if milestone.at_seconds > elapsed:
            break
        end = min(milestone.at_seconds, elapsed)
        interval = max(0, end - cursor)
        if available:
            available_seconds += interval
        if degraded or not available:
            degraded_seconds += interval
        cursor = end
        available = milestone.service_available
        degraded = milestone.degraded
    if cursor < elapsed:
        interval = elapsed - cursor
        if available:
            available_seconds += interval
        if degraded or not available:
            degraded_seconds += interval
    return available_seconds, degraded_seconds


def scenario_for(value: object) -> ChaosScenario:
    """Return catalog metadata for a persisted ID or user-facing label."""
    return CHAOS_SCENARIOS[normalize_chaos_scenario(value)]


def service_availability_series(state: ChaosState) -> list[dict[str, object]]:
    """Return cumulative model availability samples for the current experiment."""
    if not state.get("scenario_id"):
        return []
    scenario = CHAOS_SCENARIOS.get(state["scenario_id"])
    if scenario is None:
        return []

    rows: list[dict[str, object]] = []
    for profile in state["profiles"]:
        plan = scenario.plans[profile]
        for elapsed in range(state["elapsed_seconds"] + 1):
            available_seconds, _ = _elapsed_service_state(plan, elapsed)
            availability = round(100 * available_seconds / elapsed, 1) if elapsed else 100.0
            rows.append(
                {
                    "Elapsed": elapsed,
                    "Profile": profile,
                    "Availability": availability,
                }
            )
    return rows
