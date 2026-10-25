# T800 Reproduction Plan

**Status:** planned; no build or experiment has been run.  
**Primary target:** Gustavo de Carvalho Bertoli et al., “Design and implementation of intelligent packet filtering in IoT microcontroller-based devices,” *Journal of Internet Services and Applications*, 15(1), 289–301, 2024, [doi:10.5753/jisa.2024.3835](https://doi.org/10.5753/jisa.2024.3835).

The authors point to their [T800 implementation](https://github.com/c2dc/T800) and [English reproduction manual](https://github.com/c2dc/T800/blob/main/manual/manual_en.md). The project repository is marked MIT licensed. Keep upstream files separate from SPECTRA-32 code and preserve their license notices if any code is later reused.

## Reproduction levels

Use the word **reproduction** only for re-running the authors' artifact or method and reporting what happened. Keep these levels distinct:

1. **Artifact check:** inspect and pin the authors' repository commit; verify the existing data, model files, and analysis steps; rerun analysis where feasible.
2. **Firmware reproduction:** build and flash the documented filter on a classic ESP32, then verify that the selected packets are allowed/dropped as expected.
3. **Hardware experiment:** repeat the authors' traffic and system-metric conditions on our hardware and compare outcomes with the paper, documenting all deviations.
4. **SPECTRA-32 extension:** only after the baseline is complete, test one new workload or board and label it as an extension.

If an early stage fails, record it as a partial/failed reproduction with logs. Do not silently replace the paper's method with a new implementation and call it reproduced.

## Minimum setup

### Required for a faithful first pass

- ESP32-WROOM-32 / ESP32 DevKit V1 class board, USB cable, and host computer.
- Linux host for the upstream tools and traffic scripts; a dedicated isolated Wi-Fi access point with no bridge to a public, campus, office, or household network.
- The versions documented by the authors where obtainable: Python 3.8, ESP-IDF, iperf v2.0.13, and Nmap 7.80. Record exact versions and hashes instead of assuming current versions are equivalent.
- One dedicated ESP-IDF checkout for this experiment. Do not share it with other projects.

### Optional for matching every reported metric

- INA219 current/voltage sensor and a separate microcontroller/reader as documented in the upstream manual.
- A second measurement computer or interface if the chosen setup would otherwise distort the traffic path.

If the exact ESP32 variant or power meter is unavailable, document that as a deviation. Do not silently transfer classic ESP32 timing or memory values to ESP32-S3 or another chip.

## Stage 0 — artifact and environment audit

Before running upstream code:

1. Record the T800 repository URL, branch, exact commit SHA, and SHA-256 of any downloaded artifact. Do not cite a moving `main` branch as the experiment version.
2. Read the English manual, `install.sh`, component configuration, model files, data-preparation scripts, and benchmark controller. Inspect every command that can generate traffic.
3. Verify dataset provenance and terms before redistributing it. The upstream code's MIT license does not automatically license third-party datasets.
4. Create an isolated ESP-IDF clone/environment. The upstream installer copies files into `$IDF_PATH`, including modified lwIP files. Preserve the unmodified upstream baseline and record a patch/diff for every change.
5. Resolve exact ESP-IDF version, target board, model feature schema, dataset split/seed, and output fields. If the repository does not specify a value, record it as an unresolved reproduction detail rather than inventing it.

**Gate to proceed:** a clean, dedicated toolchain exists; install changes are understood; target IP and lab subnet are fixed; and the source tree has no credentials or private data.

## Stage 1 — artifact-level reproduction

Re-run the authors' stored-data analysis before long hardware campaigns. Trace the notebook/scripts and identify:

- Which artifacts are raw measurements, preprocessed measurements, training data, and serialized models.
- The complete feature list and label construction.
- How training/validation/test sets are created, including seeds and any sampling or salting.
- The metrics used for each reported score and whether a score is measured on held-out data.
- The source of each figure/table and the exact command that regenerates it.

Save a SPECTRA-32 analysis script and environment manifest separately from upstream. Compare regenerated values with the paper, listing any mismatch and its likely cause. Do not modify test data or tune to match a published number.

## Stage 2 — firmware smoke check

1. Build the unfiltered baseline in the isolated environment and confirm ordinary TCP communication with the ESP32.
2. Build the T800 variant and confirm the lwIP hook is invoked; record serial output and a small, sanitized CSV.
3. Use one manually verified, low-rate scan from the attacker host to the single configured ESP32 lab address. Confirm that the target and controller logs agree on packet counts and decisions.
4. Confirm normal benign traffic still reaches the target. Reboot and repeat once to catch stale configuration/state.

These are engineering smoke checks, not evidence that the paper's accuracy or performance claims have been reproduced.

## Stage 3 — faithful workload matrix

The paper describes four workload cells and five filter settings. Recreate this matrix only after the smoke check:

| Benign TCP traffic | Port scan present | Scan absent |
|---|---|---|
| 8 Mbps | I0M1 | I0M0 |
| 16 Mbps | I1M1 | I1M0 |

Run each cell with the no-T800 baseline and the four paper model policies: DT-12, Logistic Regression, linear SVM, and MLP. The paper reports 30 replications of 360 seconds per experiment. If all 20 combinations are run, the nominal measurement time is about **60 device-hours**, before setup, recovery, and validation time.

Start with a short pilot to catch configuration errors. Label it **pilot only** and do not use it to support paper-level conclusions. If time or hardware limits prevent all 20 combinations, prioritize a preregistered subset (for example, no filter versus DT-12 across all four workload cells) and call the result a **partial reproduction**.

The original setup uses an attacker computer on the same Wi-Fi network, benign TCP traffic generated with iperf, and Nmap port-scan traffic. Only use a fixed, owned lab target address. Exact scan command, rate, interface, RF channel, and traffic timing must come from the pinned upstream scripts/manual and be recorded.

## Outcomes to record

### Security behavior

- True positives, false positives, false negatives, and true negatives at packet/run level.
- Scan packets dropped and benign packets preserved.
- Confusion matrix, precision, recall, F1, and false-positive rate, with the exact denominator and aggregation level stated.

### System behavior

- CPU utilization per core if available.
- Wi-Fi/TCP goodput and packet delivery or loss.
- Stack and heap measurements, each clearly named; do not equate task stack high-water mark with total RAM use.
- Power/current only with calibrated instrumentation matching the chosen setup.
- Firmware build size, static memory, model size, and crash/reboot count.

### Experimental record

For each run capture: run ID, timestamp, SPECTRA-32 commit, T800 commit, ESP-IDF commit, board/chip revision, host OS, tool versions, AP/channel, model, workload cell, random seed where applicable, start/end times, raw output hash, and any deviation or failure.

## Analysis rules

- The unit of replication is the **independent run**, not each one-second sample in a run. Treat time samples as repeated measurements, not as hundreds of independent experiments.
- Report per-run summaries and condition-level median, IQR, and confidence intervals. Include effect sizes and the exact sample count. Report failures and exclusions with reasons.
- Reproduce the authors' analysis first. Any alternative statistical test or metric is an explicitly labeled SPECTRA-32 analysis.
- Freeze the test split and primary metric before hardware runs. Never tune a model on the held-out test set.
- Keep raw local logs out of Git by default. Commit sanitized aggregates, scripts, environment manifests, run metadata, and figure-generating code only after checking privacy and data licenses.

## Completion labels

- **Artifact reproduced:** stored-data analysis or author artifact reruns with recorded versions and explained differences.
- **Firmware reproduced:** documented T800 code builds and its filter behavior is verified on the target board.
- **Experiment reproduced:** the selected published conditions, repeats, and metrics are completed and compared with the paper.
- **Partial reproduction:** a declared subset ran, with all deviations visible.
- **Failed reproduction:** the method/artifact could not be run as documented; preserve logs and explain the blocker.

No status above should be checked until supported by committed logs and outputs.
