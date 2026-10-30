# ADR-002: Keep dashboard security scenarios session-local

## Status

Accepted (retrospective interpretation based on current repository evidence).

## Context

The Streamlit UI demonstrates several attack/defense concepts. It is hosted locally or on Streamlit Community Cloud and may not have access to a user's hardware. Scenario actions currently update only Streamlit session state.

## Decision

Keep dashboard scenario stimuli deterministic and local to the current session. Do not emit packets, send broker commands, flash firmware, or actuate hardware from these controls. Label the outcomes as modeled/simulated.

## Alternatives

- Send scenario traffic to the standalone node or broker.
- Use a browser/host action to write or flash the board.
- Present modeled outcomes without a simulation boundary.

## Rationale

Session-only behavior is suitable for interface exploration and regression testing without exposing users' networks or devices. It keeps the Cloud UI useful while making its capability limit visible.

## Consequences and tradeoffs

- The dashboard cannot validate network controls or defenses.
- Counts and events are not persistent across sessions or deployments.
- Hardware behavior requires a separately authorized integration and a dedicated evidence path.

## Evidence

`services/simulator.py`, `simulator/dashboard/app.py`, `tests/test_scenarios.py`, and `tests/test_dashboard_app.py`.
