# EXP-02: Embedded resilience under modeled faults

**Status:** protocol and behavioral simulator implemented; no physical run or empirical result exists.

## Objective

Evaluate whether an interactive, deterministic behavioral model can make embedded/IoT failure propagation and recovery policy differences inspectable without requiring physical hardware. The protocol does not claim to measure ESP32 resilience.

## Research questions

- **RQ1:** Under the same bounded modeled fault, how do the declared Vulnerable and Hardened transition plans differ in service availability, operation success, detection, retries, restart behavior, and modeled recovery?
- **RQ2:** Does explicit dependency modeling show the intended propagation rules (Wi-Fi loss affects MQTT; an MQTT broker outage does not imply Wi-Fi loss)?
- **RQ3:** Can fixed logical time and deterministic formulas make the scenario outcomes reproducible in automated tests?

## Hypotheses represented by the model

- **H1:** The Hardened profile reaches modeled recovery sooner or with better operation handling for scenarios where bounded retry, fallback, validation, task supervision, or workload shedding is defined.
- **H2:** MQTT-only failure leaves modeled Wi-Fi online, while Wi-Fi failure propagates to MQTT.
- **H3:** Identical scenario, profile, and parameter inputs produce identical milestones and metrics.

These are code-level hypotheses. Test results can confirm that the implementation follows its declared model; they cannot establish that a physical device behaves this way.

## Failure model and scope

The target is `ESP32 IoT node — Behavioral Model` in Streamlit session state. The only variable is a selected catalogued fault, plus an optional integer packet-loss parameter from 0 to 50%. The experiment horizon is 10 simulated seconds, including the one-second baseline. Fault windows, dependency state, and recovery timing are encoded in `data/chaos_scenarios.py`.

Vulnerable and Hardened are policy profiles for this model. They are not separate verified firmware binaries. In-scope scenarios:

1. MQTT broker outage
2. Wi-Fi connectivity loss
3. Device / firmware crash
4. Sensor failure
5. Network latency
6. Packet loss
7. Memory pressure
8. Watchdog / task stall

Out of scope: physical sensor readings, real Wi-Fi/MQTT traffic, process termination, load or flood generation, host resource pressure, radio disruption, serial interaction, flashing/erasing firmware, and actuator control.

## Variables and controls

| Variable | Levels / control | Source |
|---|---|---|
| Scenario | One of eight fixed catalog entries | `data/chaos_scenarios.py` |
| Security profile | Vulnerable, Hardened, or Compare both | Streamlit widget and per-profile plan |
| Modeled packet loss | 0–50%, integer, packet-loss scenario only | Session slider |
| Elapsed time | 0–10 logical seconds | UI monotonic clock; tests set it directly |
| Fixed workload | Scenario-specific operation count; packet-loss scenario uses ten unique operations | Declarative plan |
| Network/hardware | None | Explicitly excluded |

No random number generator is used. For packet loss, first-attempt losses are `round(10 × loss_pct / 100)` using a fixed integer rounding rule (`floor(x + 0.5)`). Hardened retries are capped at `min(losses, 3)`, and modeled retry successes are `floor(retries × (100 − loss_pct) / 100 + 0.5)`. The plan records unique operation results separately from retry count.

## Outcomes and metrics

- Stage transitions and event sequence.
- Logical Device, Wi-Fi, MQTT, HTTP, sensor, and recovery status.
- Modeled service availability over elapsed experiment seconds.
- Unique operation attempts, successes, failures, retries, and restart count.
- Detection delay and recovery duration when their timestamps exist.
- Degraded duration and recovery outcome.
- Model-specific resilience score.

The score is `round(0.45 × availability% + 0.35 × operation-success% + 0.20 × recovery-outcome%)`. Recovery outcome is 100 if a plan reaches `RECOVERED` in the 10-second window, otherwise 0. See [`docs/CHAOS_LAB.md`](../../docs/CHAOS_LAB.md) for full definitions, denominator rules, interpretation, and limitations.

## Procedure

### Deterministic automated procedure

1. Create a clean Chaos session state.
2. Select one scenario, one profile or both, and the scenario parameter where applicable.
3. Start at a fixed monotonic origin, then pass integer elapsed seconds to the transition function.
4. Check baseline → fault → degraded → recovery → terminal stage; inspect status, timeline, and metrics.
5. Repeat with the same inputs and compare results exactly.
6. Repeat across profile plans and verify dependency behavior where applicable.
7. Run the Streamlit AppTest to verify navigation, controls, completion, and reset.

### Physical follow-up (not authorized or performed by this protocol)

A future study must be specified separately before testing a physical target. It must define an owned classic ESP32 revision, firmware hash, isolated access point and broker, the exact safe fault mechanism, power/reset behavior, independent observation and time source, authorization, blast-radius controls, stop conditions, repeat count, raw-data handling, and deviations. No command in the public Streamlit page should be repurposed as a hardware control without a reviewed protocol and separate backend.

## Reproducibility and evidence

From the repository root:

```powershell
uv run --locked --group dev python -m unittest discover -s tests -p "test_chaos_simulator.py" -v
uv run --locked --group dev python -m unittest discover -s tests -p "test_dashboard_app.py" -v
```

The tests validate model semantics and UI wiring. They are not experimental runs and do not supply empirical effect sizes or physical measurements. No run ledger or measurement dataset is included because no physical experiment has been conducted.

## Interpretation and falsifiability

H1–H3 are falsifiable against the code model: a counterexample in a deterministic run indicates that implementation and declared plan disagree. They are **not** hypotheses tested on physical ESP32 hardware. To test a physical extension, define primary endpoints, profile artifacts, identical fault conditions, independent repetitions, failure/exclusion handling, and analysis before collection. Preserve negative results and report deviations.

## Limitations

- The plans are authored expectations, not calibrated models.
- The 10-second horizon and score weights are project choices.
- The availability metric integrates declared profile states, not observed server responses.
- Operation success reflects the model's semantic outcomes, not network delivery or application correctness measured on hardware.
- Sensor and memory faults are qualitative and generic; no electrical range, heap value, CPU load, or board behavior is asserted.
- Streamlit fragment updates are non-blocking UI refreshes, not real-time scheduling.
- No physical result, reproduced paper result, or validated defense is reported.

## Conceptual references

- Netflix, [Chaos Monkey](https://github.com/Netflix/chaosmonkey) — conceptual failure-exposure inspiration only; no code reused.
- [Principles of Chaos Engineering](https://principlesofchaos.org/) — steady-state/hypothesis/variable/observation framing.
- [SPECTRA-32 Chaos Lab definition and limitations](../../docs/CHAOS_LAB.md).
