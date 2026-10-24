# SPECTRA-32 Roadmap

The roadmap separates reproducing one paper from later extensions. A phase is complete only when its deliverables are recorded; planned items are not results.

## Phase 0 — Research and artifact freeze

- [x] Select T800 as the initial paper based on direct ESP32 fit and public author artifacts.
- [x] Document the claim, boundaries, and first experiment design.
- [ ] Record the exact upstream T800 commit SHA and license state.
- [ ] Resolve the ESP32 board variant and access to an isolated access point.
- [ ] Audit the upstream installer, firmware components, traffic scripts, models, datasets, and analysis split.

**Exit:** pinned source, understood toolchain changes, safe target configuration, and documented unresolved details.

## Phase 1 — Reproduction environment

- [ ] Create a dedicated ESP-IDF checkout/container/VM for T800.
- [ ] Record host OS and exact Python, ESP-IDF, iperf, Nmap, compiler, and component versions.
- [ ] Generate an environment manifest and patch diff; keep the default ESP-IDF checkout untouched.
- [ ] Re-run the stored-data analysis and compare it with the paper.

**Exit:** a clean environment can rebuild the artifact and regenerate analysis outputs, or a failure is documented with logs.

## Phase 2 — Board smoke check

- [ ] Build and flash the no-filter baseline.
- [ ] Build and flash T800 with the selected model.
- [ ] Verify hook invocation, allow/drop behavior, benign traffic, logging, and recovery after reboot.
- [ ] Use a short, authorized pilot and label it as engineering-only.

**Exit:** stable end-to-end operation on the documented board; no pilot results presented as paper reproduction.

## Phase 3 — Faithful reproduction

- [ ] Freeze conditions, run count, metrics, split, and analysis command.
- [ ] Run baseline vs DT-12 across the four workload cells.
- [ ] If feasible, complete the LR, SVM, and MLP conditions.
- [ ] Measure power only with the documented measurement chain; otherwise report partial coverage.
- [ ] Publish sanitized data, run manifest, analysis code, figures, deviations, and failures.

**Exit:** completed run records and a reproduction status of reproduced, partial, or failed, supported by evidence.

## Phase 4 — SPECTRA-32 research extension

Choose one extension after the reproduction, for example:

- A held-out scanner implementation to test generalization beyond the training workload.
- A simple explicit allowlist baseline to compare machine-learning filtering with a transparent rule.
- A second ESP32 variant to measure portability and resource trade-offs.
- An MQTT replay-defense experiment with a separate protocol, threat model, and baseline.

Do not bundle several extensions into one claim. Freeze baseline results before selecting and tuning an extension.

## Phase 5 — Expanded cyber-physical testbed

Only after the first study is stable, consider adding a sensor, safe LED output, MQTT dashboard, BLE, signed OTA, or TinyML monitoring. Each module needs its own experiment specification, authorized lab scope, baseline, and metrics. Do not describe these future modules as covered by the T800 reproduction.
