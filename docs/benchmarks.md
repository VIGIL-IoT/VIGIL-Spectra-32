# Benchmarks and Measurement Plan

**Current result:** no performance benchmark or security experiment has been run. The values shown in the Streamlit UI are sample counters or deterministic in-memory outcomes; they are not measurements.

## Available evidence today

| Evidence | Result | What it does not establish |
|---|---|---|
| Python unit and UI tests | Test outcomes are in the repository audit and CI logs | Performance, hardware security, MQTT broker behavior, or ESP32 resource cost |
| Dashboard session chart | Displays bounded accepted/blocked session counters | Sensor telemetry, real-time device telemetry, network rate, or device performance |
| HTTP route tests | Exercise the standalone node over a local loopback test server | MQTT integration or firmware parity |
| Paper reference values | Clearly marked in research notes | SPECTRA-32 results or guaranteed reproduction targets |

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

## Benchmark protocol requirements

- Pin source revisions, broker/client versions, OS, board revision, firmware configuration, network topology, and workload.
- Separate independent runs from repeated samples within a run. Keep failures and exclusions.
- Define the primary outcome and repeat count before confirmatory runs.
- Report per-run values, sample counts, missing data, and analysis method. Use effect sizes and intervals where justified.
- Do not compare Streamlit session values with hardware values or use paper-reported values as local results.

## Why no results table is published

The Python model and dashboard tests check correctness paths, not throughput or latency. The Mosquitto executable, ESP-IDF toolchain, physical board, and measurement instruments were unavailable for this audit. Reporting numerical performance here would fabricate evidence.
