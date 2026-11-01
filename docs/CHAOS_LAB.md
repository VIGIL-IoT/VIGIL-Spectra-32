# SPECTRA-32 Chaos Lab

**Status:** behavioral simulation implemented; no physical fault injection or resilience measurement has been performed.

## Purpose

Chaos Lab is an educational, session-local model for exploring how an ESP32-style IoT node might behave during a bounded fault. It makes the sequence **steady state → failure → impact → detection → recovery → result** visible without requiring an ESP32, broker, lab network, sensor, or test instrument.

It is a separate subsystem from the existing security-event simulator. Security scenarios remain in `services/simulator.py`; Chaos Lab definitions and transitions live in `data/chaos_scenarios.py` and `services/chaos_simulator.py`. Both are owned by the versioned `DeviceState`, but a Chaos run does not modify the security scenario counters, Python node, broker, firmware, pin state, or physical board.

## Research grounding

[Netflix Chaos Monkey](https://github.com/Netflix/chaosmonkey) is a resiliency tool that intentionally exposes applications to instance failures. Its implementation is designed for cloud infrastructure and is integrated with Spinnaker; SPECTRA-32 uses only the high-level concept of deliberately studying failure behavior. It does not copy Netflix source code, cloud architecture, random selection, production execution, or instance-termination mechanism. This project is not affiliated with or endorsed by Netflix.

The [Principles of Chaos Engineering](https://principlesofchaos.org/) describe experiments that define measurable steady state, form a hypothesis, introduce a real-world variable, and look for a change in steady state. That is a useful experimental structure. SPECTRA-32's current Chaos Lab is an **interactive behavioral simulation**, not an empirical Chaos Engineering experiment on production or a physical embedded system. Physical testing requires a separately reviewed, authorized protocol and an isolated lab.

## Architecture and execution boundary

```text
Streamlit Chaos Lab view
  └── st.fragment(run_every=1) display clock
      └── services/chaos_simulator.py
          ├── data/chaos_scenarios.py (declarative plans)
          └── DeviceState.chaos (versioned, per-session state)
```

The fragment reads elapsed monotonic time and passes integer elapsed seconds to a deterministic transition function. It does not call `sleep()`. Tests supply elapsed seconds directly, which makes state transitions independent of wall-clock timing. The session state contains the selected scenario, profile, active/terminal stage, logical node statuses, timeline, metrics, and result.

There is no physical execution mode. Chaos actions never:

- stop or pause an operating-system process;
- change Wi-Fi, routes, sockets, packet delivery, or host resources;
- connect to or stop an MQTT broker or node API;
- open a serial port, reboot a board, write firmware, or erase flash;
- control a GPIO or actuator.

The board illustration highlights logical affected components. Its pin metadata and simulated electrical states are not changed by Chaos runs.

## Scenario catalog

Each scenario has a fixed ten-simulated-second plan for Vulnerable and Hardened profiles. The plans include assumptions, affected components, fault behavior, recovery policy, primary metric, educational explanation, and explicit limitations.

| Scenario | Failure model | Vulnerable behavior | Hardened behavior |
|---|---|---|---|
| MQTT broker outage | Broker unavailable; Wi-Fi remains online | Command path stays offline after broker restoration; manual reconnect is required | Detects disconnect, uses bounded retry/backoff, and reconnects after restoration |
| Wi-Fi connectivity loss | Wi-Fi drops and MQTT follows its dependency | Access link can return while MQTT stays disconnected | Retries Wi-Fi, then reconnects MQTT in dependency order |
| Device / firmware crash | Application, HTTP, and MQTT become unavailable; reboot resets modeled volatile state | Remains down until manual restart | One supervised restart, then Wi-Fi and services restore in order |
| Sensor failure | Abstract sensor input becomes stale/invalid | Trusts invalid input and records integrity failures | Rejects invalid input, retains last-known-valid state, validates fresh input |
| Network latency | Modeled delay rises to 1,200 ms against an illustrative 800 ms timeout | Delayed operations exceed the timeout without bounded fallback | Contains timeout, bounds retry, then returns to nominal model latency |
| Packet loss | Fixed ten-operation batch and selected 0–50% deterministic loss | No retries for operations lost on first attempt | Retries at most three modeled losses once, using a deterministic success formula |
| Memory pressure | Qualitative NORMAL → ELEVATED → CRITICAL resource state | Optional work remains enabled and model enters an unstable restart state | Sheds nonessential work and restores it gradually after pressure clears |
| Watchdog / task stall | Logical task heartbeat stops; watchdog threshold is modeled at T+03 | No watchdog response; task remains stalled | One bounded watchdog restart and service restoration |

No physical sensor is assumed, no hardware memory amount is asserted, and no particular board timing or timeout is claimed. Values such as latency and threshold are explicit example parameters for the model.

## Lifecycle and timeline

The user can run Vulnerable, Hardened, or Compare both. Both profiles receive the same scenario and bounded inputs. Each plan follows the lifecycle:

```text
IDLE → BASELINE → FAULT_INJECTED → DEGRADED → RECOVERING
                                  ├── RECOVERED → COMPLETE
                                  └── FAILED_TO_RECOVER → COMPLETE
```

The fixed plan can include additional same-stage events. The UI reports simulated time as `T+00:SS`. Timeline entries identify experiment ID, scenario, profile, stage, affected component, severity, transition, explanation, and recovery action. The display is chronological and bounded to the latest 60 events.

For dependency propagation, Wi-Fi loss marks both Wi-Fi and MQTT unavailable. An MQTT broker outage changes MQTT only and leaves Wi-Fi online. The modeled HTTP service remains available during broker outage where the scenario defines it so.

## Metrics and score

Every displayed value belongs to a deterministic session model and is labeled **modeled**, **simulated**, or **session model**. The 10-second horizon includes the one-second steady-state baseline.

- **Modeled service availability:** available seconds ÷ elapsed simulated seconds × 100. For a completed run, denominator is 10 seconds.
- **Operation success:** unique modeled operations that succeed ÷ unique modeled operations attempted × 100. Packet-loss retries are reported separately and do not increase the unique-operation denominator.
- **Operations failed:** unique operations not correctly handled by the end of the plan. For sensor scenarios, rejecting an invalid sample in Hardened is a successful safe handling outcome; trusting an invalid sample in Vulnerable counts as an operation failure and an integrity failure.
- **Detection delay:** first modeled detection time minus fault-injection time. A profile that does not detect the fault reports no detection delay.
- **Recovery duration:** first modeled `RECOVERED` time minus fault-injection time. A profile that fails to recover within the window reports no recovery duration.
- **Degraded duration:** seconds marked degraded or unavailable by the profile plan.
- **Retries and restarts:** explicit bounded events in the plan. These do not execute on a device or network.

The model-specific resilience score is:

```text
score = round(0.45 × modeled_service_availability_pct
            + 0.35 × operation_success_pct
            + 0.20 × recovery_outcome_pct)
```

`recovery_outcome_pct` is 100 if the model reaches `RECOVERED` inside the horizon and 0 otherwise. The score is an educational, SPECTRA-32-specific comparison metric. It is not a security rating, certification, industry-standard metric, or physical ESP32 result. Its weights and fixed workload encode project assumptions; changing those assumptions changes the score.

## Vulnerable / Hardened comparison

The profiles differ in the actual modeled transition plan: detection, reconnect behavior, operation failures, fallback, retry count, restarts, and recovery outcome. The score is calculated after those transitions; it is not directly assigned by profile name. The comparison table and accompanying explanation identify the modeled policy responsible for the difference.

The Hardened label describes only this model's policy. It does not imply that the repository contains or verifies corresponding hardened ESP-IDF firmware or that the policy would work on a physical board.

## Reproduction and checks

Run the deterministic unit and dashboard checks from the repository root:

```powershell
uv run --locked --group dev python -m unittest discover -s tests -p "test_chaos_simulator.py" -v
uv run --locked --group dev python -m unittest discover -s tests -p "test_dashboard_app.py" -v
```

`tests/test_chaos_simulator.py` validates catalog metadata, lifecycle transitions, profile differences, dependency propagation, deterministic packet loss, metric calculations, sensor handling, invalid input, and reset. The dashboard AppTest verifies the Chaos Lab navigation, controls, comparison, completion, and reset path.

## Limitations and planned physical validation

This version has no hardware-in-loop adapter, no empirical model calibration, no persistence, and no measured outcomes. It does not represent real ESP32 CPU, heap, flash, radio, Wi-Fi, MQTT, HTTP server, watchdog, sensor, power, or GPIO timing. Streamlit fragment timing is a view clock, not a real-time guarantee. Model values must not be published as device measurements.

A future physical study must define an owned classic ESP32 target, board revision and firmware hash, isolated Wi-Fi/broker setup, safe failure mechanism, external observation method, stop conditions, repeat count, and run record before executing. It must report physical readings separately from the behavioral model and must not silently route public Streamlit interactions to a device.

## References

- Netflix, [Chaos Monkey repository](https://github.com/Netflix/chaosmonkey) (conceptual inspiration; no source reuse or affiliation).
- [Principles of Chaos Engineering](https://principlesofchaos.org/) (steady-state hypothesis and controlled experiment framing).
- Streamlit, [`st.fragment` API](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment) (non-blocking fragment reruns; this repository pins Streamlit 1.66.1).
- [EXP-02 behavioral resilience protocol](../experiments/EXP-02-chaos-resilience/README.md).
