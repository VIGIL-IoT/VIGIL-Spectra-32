# Experiment Protocol

**Status:** planned protocol; no experiments have been run.  
**Primary comparison:** no T800 filter versus T800 Decision Tree (DT-12), followed by the remaining upstream models if the first subset is stable.

## Hypotheses

- **H1, security behavior:** with the scan workload enabled, the T800 filter drops a greater fraction of scan packets than the unfiltered baseline.
- **H2, legitimate traffic:** with benign traffic only, the filter preserves legitimate packet delivery within the tolerance fixed before the run.
- **H3, resource trade-off:** T800 changes CPU, throughput, memory, and power measurements relative to the baseline; the direction and size are measured rather than assumed.

These are testable hypotheses, not findings. Define numerical acceptance tolerances after checking the pinned paper version and upstream code, then freeze them in the run manifest before collecting confirmatory data.

## Conditions

| Factor | Levels |
|---|---|
| Benign TCP traffic intensity | 8 Mbps, 16 Mbps |
| Port-scan traffic | Absent, present |
| Filter policy | None, DT-12, Logistic Regression, linear SVM, MLP |
| Duration/repeats for full replication | 360 seconds per run, 30 replications per cell as reported by the paper |

This is 4 workload cells × 5 filter settings = 20 condition cells (about 60 measurement hours at the paper's duration/repeat count). A first engineering pilot should use only a few short runs and be clearly labeled as a pilot. A feasible first scientific subset is no filter vs DT-12 over the four workload cells; report it as partial until all selected conditions and repeats are complete.

## Procedure

1. Confirm the AP has no upstream connection and the ESP32 is the only configured target.
2. Record repository commits, software versions, board ID/revision, AP/channel, target IP, and all runtime configuration. Do not commit credentials.
3. Flash the no-filter baseline and confirm benign TCP traffic and measurement logging.
4. Flash the chosen T800 model, verify the ingress hook, and confirm that the host and board logs align.
5. For each frozen condition, start logging, run the authorized workload for the specified duration, stop traffic, and validate that the output is complete.
6. Randomize or block the order of conditions to reduce time/RF confounding. Record this order. If following the upstream script requires a fixed sequence, record that as a deviation.
7. Repeat until the declared number of independent runs is reached. Retain failed runs with failure status; do not silently discard them.
8. Compute metrics using a version-controlled analysis script. Store figures with their source data and generating command.

Before running any scanner command, audit the pinned upstream script and replace implicit/wildcard targets with a single configured lab target. Keep the scan rate and exact command in the run manifest.

## Metrics

### Detection and availability

- Confusion matrix, precision, recall, F1, and false-positive rate.
- Fraction of scan packets dropped and benign packets delivered.
- TCP goodput, retransmissions, and loss where the harness can measure them reliably.
- Crashes, resets, watchdog events, and time to recover.

### Resource cost

- CPU utilization, per-core if available.
- Stack high-water mark and heap separately.
- Network throughput/goodput.
- Current and power only if the INA219 measurement chain is available and calibrated.

### Validity and provenance

- Every run has a unique ID and includes source commits, board, software versions, condition, seed if applicable, timestamps, output hashes, exclusions, and deviations.
- Label paper-reported numbers as reference values; never place them in SPECTRA-32 results tables as measured values.
- Record the exact dataset files, transformations, split policy, and license used for any model training.

## Analysis plan

- Treat each complete run as the experimental unit. One-second samples within one run are repeated observations and are not independent replicates.
- First reproduce the authors' analysis. Separately report run-level summaries with median, IQR, effect size, and confidence intervals.
- Compare the same conditions between the unfiltered and filtered setup. Keep the held-out dataset split unchanged and do not tune on test data.
- Report all conditions and failed runs. If the observed data violate assumptions of a planned test, document and justify a robust alternative before interpreting results.
- Distinguish statistical evidence from practical importance. A small p-value alone is not evidence that a filter is useful.

## Run log template

Copy one row per run into the eventual run ledger; use one row per run rather than one row per second-level sample.

| Run ID | Timestamp | SPECTRA commit | T800 commit | ESP-IDF commit | Board | Filter/model | Mbps | Scan | Duration | Seed | Output hash | Status/deviation |
|---|---|---|---|---|---|---|---:|---|---:|---|---|---|
| — | — | — | — | — | — | — | — | — | — | — | — | No runs yet |
