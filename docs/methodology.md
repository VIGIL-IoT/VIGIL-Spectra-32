# Implementation and Experiment Methodology

## Engineering approach

SPECTRA-32 uses staged implementation so the model can be inspected before hardware is required. The code keeps three paths distinct:

1. **Streamlit session model:** deterministic scenario transitions mutate in-memory `DeviceState`, append an event, update a virtual pin/counter, and render the result. No broker, node API, radio, or physical GPIO call is made by a scenario.
2. **Standalone software node:** `VirtualNode` owns volatile virtual-LED state. A loopback HTTP server and optional Paho MQTT link call the same state object. The dashboard does not consume this service.
3. **ESP-IDF reference firmware:** a separate, intentionally vulnerable classic ESP32 implementation models HTTP/MQTT control and a configurable low-voltage output. ESP-IDF 6.1 compiles it in CI; it has not been flashed or compared with the software model.

This separation avoids silently turning a teaching UI into hardware-control software and makes the scope of future parity tests explicit.

## Software processing pipeline

```mermaid
flowchart LR
  Inputs[Selected profile and scenario] --> Validate[Catalog and simulation-mode checks]
  Validate --> Transition[Deterministic state transition]
  Transition --> State[Session state and bounded event list]
  State --> Output[Board, counters, chart, path, and event UI]
  Output --> Evidence[AppTest assertions and saved run record]
```

For the standalone node, HTTP form input is parsed and validated before the `VirtualNode` is updated. MQTT accepts only exact `ON` or `OFF` payloads on the fixed command topic. State is volatile and reset on process restart. The MQTT lifecycle still requires a broker-backed integration run.

## Security scenario method

The console is a deterministic state illustration. For each scenario, the code selects a fixed stimulus from `data/scenarios.py` and applies one model transition in `services/simulator.py`. The current model does not build an actual packet, credential-guessing loop, OTA image, or nonce-bearing command. Report its output only as **simulated**.

## Chaos Lab behavioral method

The Chaos Lab applies the same experimental discipline to a deliberately bounded embedded-system behavior model. Its conceptual framing follows the controlled fault exposure and observation loop described by [Netflix Chaos Monkey](https://github.com/Netflix/chaosmonkey) and the [Principles of Chaos Engineering](https://principlesofchaos.org/); those projects supply concepts only. SPECTRA-32 does not reuse their source, architecture, production infrastructure, or fault-execution mechanisms.

For each EXP-02 run:

1. Record the modeled steady-state baseline in the session.
2. Select one catalogued fault and either Vulnerable, Hardened, or both profiles.
3. Advance the profile's declarative milestones against logical elapsed seconds. Vulnerable/Hardened plans have explicit status, operation, detection, and recovery outcomes.
4. Compare service availability, operation success, detection delay, recovery duration, degradation, retries, restarts, and the model-specific score where defined.
5. Interpret the timeline and the defense named by the scenario plan. Do not generalize model outputs to physical ESP32 behavior.

Tests pass logical elapsed seconds directly, so no timer or waiting is needed for deterministic verification. The Streamlit view uses `st.fragment(run_every=1)` as a non-blocking display clock; it never sleeps. The browser timer does not control an external system. EXP-02 is a behavioral simulation protocol; there are no measured run records.

## Experiment method before physical validation

For EXP-01 MQTT command replay:

1. Freeze source commit, model/broker versions, topic, command format, initial output, and run identifier.
2. Send one valid command, record its outcome, transition state, then replay the exact same command once.
3. Compare an unchanged vulnerable implementation with a separate hardened implementation using the same command semantics.
4. Repeat independent runs and retain failures. The candidate protocol, key provisioning, freshness/reset behavior, and repeat count must be fixed before confirmatory collection.
5. Report stale replay success and legitimate command acceptance separately. Keep host latency/resource metrics distinct from device RAM, flash, radio timing, GPIO timing, and power.

For T800, follow the separate pinned-artifact plan. Do not mix its TCP port-scan study with the MQTT replay experiment. Follow `docs/SAFETY_AND_DATA.md`; scan traffic is only ever directed at the single owned lab target described in the run record.

## Evidence and validation levels

- **Static inspection:** source/configuration reviewed; does not prove runtime behavior.
- **Unit/smoke test:** deterministic functions and local loopback HTTP routes checked; does not prove physical-device behavior.
- **Integration test:** multiple local processes run together. The standalone Python node's MQTT command/status path is verified against Mosquitto on loopback in [Python quality CI run 41105134754](https://github.com/VIGIL-IoT/VIGIL-Spectra-32/actions/runs/41105134754); this does not verify physical firmware behavior.
- **Hardware validation:** firmware build/flash and device observation on a documented board; not yet available.
- **Experiment:** frozen procedure with run records, repetitions, outputs, hashes, and analysis; no SPECTRA-32 security experiment has been run.

Every report must state the highest level actually completed and any deviations.
