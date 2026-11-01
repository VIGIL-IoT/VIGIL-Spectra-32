# ADR-004: Keep Chaos Lab a deterministic behavioral simulation

## Status

Accepted for the v0.3.0 release.

## Context

SPECTRA-32 already separates Streamlit session scenarios, a loopback Python node, and future ESP-IDF firmware. The project wants an interactive resilience view that can be used without an ESP32, broker, or dedicated lab. Fault injection against real host processes, networks, brokers, or devices would add a new execution boundary and could be mistaken for a physical experiment.

Netflix Chaos Monkey provides conceptual inspiration for deliberate failure exposure, but its cloud/Spinnaker integration and production instance termination are not a suitable implementation for this embedded research simulator. The [Principles of Chaos Engineering](https://principlesofchaos.org/) provide a useful steady-state and observation framework; this release does not conduct a real-world experiment.

## Decision

- Implement a dedicated Chaos catalog and service, separate from `services/simulator.py`.
- Keep the eight scenarios deterministic, bounded, and session-local. Advance a ten-second logical lifecycle through a non-blocking Streamlit fragment.
- Make Vulnerable and Hardened behavior differ in their transition plans, not by assigning profile-based scores.
- Do not execute a scenario against the host, network, broker, serial interface, firmware, GPIO, or actuator.
- Label every timeline and metric as a behavioral model result. Keep physical validation as a separate future backend and protocol.
- Document the resilience score formula and identify it as a SPECTRA-32 educational metric.

## Alternatives

- Add fault cases to the existing security scenario function. Rejected because security policy events and availability/resilience failure experiments have different lifecycles and metrics.
- Execute failures on a local process or broker from Streamlit. Rejected for this release because it would introduce host-specific effects, require process/network authorization and cleanup semantics, and would not validate ESP32 behavior.
- Expose a browser-to-ESP32 fault API. Rejected because the current firmware has no authenticated Chaos protocol and Streamlit Cloud cannot reach the user's USB or lab network.
- Add physical hardware-in-loop tests now. Deferred until the lab target, safe fault mechanisms, ownership scope, measurements, and stop conditions are designed.

## Rationale

A deterministic behavioral model is available to hosted and local users without requiring hardware and is testable with fixed logical elapsed time. Separate services preserve the current security-model boundary. A declarative catalog keeps assumptions and per-profile behavior reviewable. The chosen boundary avoids implying that simulated timing or recovery proves hardware resilience.

## Consequences and tradeoffs

- The view demonstrates lifecycle concepts and exposes profile assumptions, but cannot discover actual hardware weaknesses or validate recovery on a device.
- Scenario timings, operation counts, and score weights are selected model parameters; they are not empirically calibrated.
- Browser fragment timing updates the visual session and has no real-time guarantee.
- A future physical backend must remain a separate, explicitly authorized path and report its observations separately from session-model outputs.

## Evidence

`data/chaos_scenarios.py`, `data/chaos_state.py`, `services/chaos_simulator.py`, the Chaos Lab view in `simulator/dashboard/app.py`, `tests/test_chaos_simulator.py`, and `tests/test_dashboard_app.py`.
