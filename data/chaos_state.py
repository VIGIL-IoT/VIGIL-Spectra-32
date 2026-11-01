"""Typed session-only state for the separate SPECTRA-32 Chaos Lab."""

from __future__ import annotations

from typing import TypedDict


class ChaosProfileState(TypedDict):
    stage: str
    statuses: dict[str, str]
    metrics: dict[str, float | int | str | None]
    processed_milestones: list[str]
    detected_at_seconds: int | None
    recovered_at_seconds: int | None
    result: dict[str, float | int | str | None] | None


class ChaosEvent(TypedDict):
    id: str
    simulated_time: str
    elapsed_seconds: int
    experiment_id: str
    fault: str
    event_type: str
    profile: str
    stage: str
    component: str
    severity: str
    transition: str
    decision: str
    explanation: str
    recovery_action: str


class ChaosState(TypedDict):
    schema_version: int
    is_simulated: bool
    active: bool
    experiment_id: str
    scenario_id: str
    scenario_name: str
    profile_selection: str
    stage: str
    elapsed_seconds: int
    started_at_monotonic: float | None
    packet_loss_pct: int
    baseline_snapshot: dict[str, str]
    board_path: list[str]
    profiles: dict[str, ChaosProfileState]
    timeline: list[ChaosEvent]
    result: dict[str, object] | None


CHAOS_STATE_SCHEMA_VERSION = 1


def create_initial_chaos_state(default_profile: str = "Vulnerable") -> ChaosState:
    """Return an idle behavioral model; it owns no hardware or network state."""
    return {
        "schema_version": CHAOS_STATE_SCHEMA_VERSION,
        "is_simulated": True,
        "active": False,
        "experiment_id": "",
        "scenario_id": "",
        "scenario_name": "",
        "profile_selection": default_profile,
        "stage": "IDLE",
        "elapsed_seconds": 0,
        "started_at_monotonic": None,
        "packet_loss_pct": 30,
        "baseline_snapshot": {
            "device": "RUNNING",
            "wifi": "ONLINE",
            "mqtt": "ONLINE",
            "http": "ONLINE",
            "sensor": "HEALTHY",
            "recovery": "READY",
        },
        "board_path": [],
        "profiles": {},
        "timeline": [],
        "result": None,
    }
