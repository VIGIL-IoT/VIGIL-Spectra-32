# Benchmarks and Measurement Plan

**Current result:** no performance benchmark or physical security experiment has been run. Chaos Lab now produces deterministic in-memory behavioral outcomes; those outcomes are model checks, not measurements.

## Available evidence today

| Evidence | Result | What it does not establish |
|---|---|---|
| Python unit and UI tests | Test outcomes are in the repository audit and CI logs | Performance, hardware security, MQTT broker behavior, or ESP32 resource cost |
| Dashboard session chart | Displays bounded accepted/blocked session counters | Sensor telemetry, real-time device telemetry, network rate, or device performance |
| HTTP route tests | Exercise the standalone node over a local loopback test server | MQTT integration or firmware parity |
| Paper reference values | Clearly marked in research notes | SPECTRA-32 results or guaranteed reproduction targets |
| EXP-02 Chaos Lab | Deterministic scenarios and score formulas exercised by unit/UI tests | Physical-device resilience, measured latency, firmware recovery, or evidence that a hardening policy works |

## Metrics for EXP-01 replay

| Metric | Definition | Measurement source | Status |
|---|---|---|---|
| Stale replay success | Replays that change output / replay attempts delivered | Model event/state log, then firmware log | Planned |
| Legitimate command acceptance | Fresh valid commands applied / fresh commands sent | Model event/state log, then firmware log | Planned |
| Host end-to-end latency | Timestamp difference between local publish and observed state | Synchronized host clocks; report clock method | Planned |
| MQTT payload and message count | Bytes and messages sent per run | Publisher/broker logs | Planned |
| Host process resource use | CPU and memory of the Python process | Host monitor; label host-only | Planned |
| Device heap/stack/flash | ESP32-specific resource costs | ESP-IDF and firmware instrumentation | Not measurable in current software model |
| Device power | Current/energy under stated workload | Calibrated meter and recorded sampling method | Not measurable; no meter setup in repo |

## Metrics for EXP-02 Chaos resilience

EXP-02's current implementation returns model outputs only. The model has a fixed 10-second horizon and calculates:

| Metric | Model definition | Status and limit |
|---|---|---|
| Modeled service availability | Seconds where the scenario's primary modeled service is available ÷ elapsed modeled seconds × 100; the initial baseline second is included | Deterministic simulation output, not measured uptime |
| Operation success | Unique modeled operations that succeed ÷ unique operations in the fixed workload × 100 | Deterministic simulation output; packet-loss retries do not increase the unique-operation denominator |
| Detection delay | First modeled detection time minus modeled fault-injection time | `Pending` if the profile does not detect the fault before completion |
| Recovery duration | First modeled recovered time minus modeled fault-injection time | `Pending` if the profile does not recover within the scenario window |
| Degraded duration | Elapsed seconds marked degraded or unavailable in the profile plan | Behavioral-model value, not device downtime |
| Retry / restart counts | Bounded retry or restart events defined in the profile plan | Model counts only; no retry packet or reset occurs |
| Resilience score | `0.45 × availability% + 0.35 × operation-success% + 0.20 × recovery-outcome%`, rounded to an integer; recovery outcome is 100 when recovered within the horizon and 0 otherwise | SPECTRA-32 educational comparison metric; not a standard or certification |

The profile plans and formula are in [`docs/CHAOS_LAB.md`](CHAOS_LAB.md). Do not include the model score in a results table as an ESP32 measurement. Physical validation requires an independent experiment with a board, documented fault mechanism, synchronized observation, and a separate run record.

## Benchmark protocol requirements

- Pin source revisions, broker/client versions, OS, board revision, firmware configuration, network topology, and workload.
- Separate independent runs from repeated samples within a run. Keep failures and exclusions.
- Define the primary outcome and repeat count before confirmatory runs.
- Report per-run values, sample counts, missing data, and analysis method. Use effect sizes and intervals where justified.
- Do not compare Streamlit session values with hardware values or use paper-reported values as local results.

## Why no results table is published

The Python model and dashboard tests check correctness paths, not throughput or latency. The Mosquitto executable, local ESP-IDF toolchain, physical board, and measurement instruments were unavailable for this audit. A pinned ESP-IDF 6.1 CI build verifies compilation only. Reporting numerical performance here would fabricate evidence.
