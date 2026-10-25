# Experiment Protocol

Every SPECTRA-32 experiment follows **Build → Attack → Observe → Defend → Measure** inside an owned or explicitly authorized lab. The planned replay experiment is described in EXP-01-replay. No security experiment has been run yet.

## Before a run

1. State the research question, threat model, attacker capability, target, and out-of-scope behavior.
2. Identify the vulnerable baseline and the hardened variant. Freeze code commits, board, firmware settings, network, broker, and command format.
3. Define the primary outcome, repeat count, failure conditions, and analysis before collecting confirmatory data.
4. Confirm the access point has no upstream bridge and only owned lab devices are connected.
5. Record toolchain/library versions, device revision, GPIO wiring, broker configuration, and time synchronization.
6. Keep secrets in local ignored configuration and store raw traces locally until checked for sensitive identifiers and license constraints.

## Run record

Create one record per independent run. Keep failed and interrupted runs; mark them with a reason instead of silently dropping them.

| Field | Value |
|---|---|
| Run ID and UTC timestamp | — |
| Experiment and hypothesis | — |
| SPECTRA-32 commit | — |
| Vulnerable/hardened variant and firmware hash | — |
| Board/chip revision and GPIO | — |
| ESP-IDF, component, broker, host OS versions | — |
| Network topology and sanitized configuration ID | — |
| Test command, duration, repetitions, seed | — |
| Metrics and measurement method | — |
| Output paths and hashes | — |
| Status, deviations, failures, exclusions | — |

## Measurement and analysis

- Report per-run outcomes before aggregating. Samples inside one continuous run are not independent runs.
- Use a credible baseline and preserve the same hardware and traffic conditions across variants.
- Include effect sizes and confidence intervals where the design supports them; distinguish statistical evidence from practical engineering impact.
- Keep resource metrics separate: CPU, free/minimum heap, stack high-water mark, flash size, bandwidth, latency, reset/recovery time, and power have different meanings.
- Record all deviations, missing data, and negative results. Paper-reported values are reference values, never SPECTRA measurements.
- Save sanitized summaries and the generating command with every figure. Keep raw PCAPs, serial logs, and machine identifiers local until reviewed.

## Reproduction labels

- **Artifact reproduced:** the original data/code analysis runs with pinned versions and explained differences.
- **Firmware reproduced:** the paper's implementation builds and its behavior is verified on the documented hardware.
- **Experiment reproduced:** the declared paper conditions, repeats, and measurements are completed and compared.
- **Partial reproduction:** an explicitly declared subset ran, with deviations and failed runs recorded.
- **Adaptation/extension:** the paper's method or idea is changed for SPECTRA-32; do not call it an exact reproduction.
- **Not run:** no run-level evidence exists. This is the current status for all experiments.
