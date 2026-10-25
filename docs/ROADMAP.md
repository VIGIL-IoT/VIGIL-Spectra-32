# VIGIL-IoT / SPECTRA-32 Roadmap

SPECTRA-32 grows through small, measurable modules. The first node is simulated on a computer so the command and state model can be exercised before a physical board is required. A roadmap item is complete only when its code, setup, and evidence are present; planned work is not a result.

## v0.0 — Repository foundation

- [x] Establish VIGIL-IoT and SPECTRA-32 naming and purpose.
- [x] Document architecture, safety boundaries, brand direction, and research tracks.
- [x] Create separate paths for the virtual model, vulnerable firmware, and future hardened variants.

## v0.1 — Computer-run basic node

- [ ] Run the local Python model with the loopback-only Mosquitto broker.
- [ ] Verify web/REST control and state reporting.
- [ ] Verify MQTT ON/OFF commands and status publication.
- [ ] Record the environment, commands, and observed functional behavior.

**Boundary:** application authentication, HTTPS, MQTT authentication/TLS, anti-replay defense, and sensor telemetry are absent. The model is loopback-only and has a virtual LED. It does not provide Wi-Fi, GPIO, memory, timing, or power measurements for an ESP32.

## v0.2 — Replay attack lab

- [ ] Freeze the threat model and application-level command replay procedure.
- [ ] Re-submit a previously valid MQTT command to the software model and record its state effect.
- [ ] Keep the unprotected model and hardened model in separate paths.
- [ ] Add authenticated commands and a freshness mechanism after selecting and documenting the command envelope and reset behavior.
- [ ] Measure legitimate-command acceptance, stale replay acceptance/rejection, end-to-end latency, payload overhead, and model memory/resource costs only where those costs are clearly labeled as host-side.
- [ ] Compare the method with REPLIOT and label the ESP32/MQTT model as an adaptation.

**Exit:** repeatable run records show the vulnerable model accepts the defined stale command and the hardened model rejects it while continuing to accept fresh commands. These are software-model results, not ESP32 hardware results.

Host process CPU and memory are properties of this computer-run simulator and must not be presented as ESP32 costs. Device RAM, flash, radio/network timing, GPIO timing, and power measurements belong to the hardware milestone and require suitable instrumentation.

## v0.3 — ESP32 hardware port

- [ ] Build and flash the ESP-IDF baseline on the selected classic ESP32 board.
- [ ] Connect to a dedicated isolated WPA2 Wi-Fi network and local broker.
- [ ] Replace the virtual output with a board-verified low-voltage LED GPIO.
- [ ] Repeat the baseline command sequences and compare state behavior with the software model.
- [ ] Record board revision, wiring, toolchain versions, firmware hash, and deviations.

No relay, motor, mains circuit, or hazardous actuator belongs in this milestone.

## v0.4 — MQTT and REST/API security

- Compare plain and authenticated/encrypted communication. Document broker/client identity, key provisioning, and failure behavior. Keep replay protection separate from transport encryption.

## v0.5 — BLE security

- Add one BLE experiment only after selecting hardware, pairing behavior, authorized scope, and a measurable baseline.

## v0.6 — Firmware and OTA security

- Add signed-update verification and controlled cases for unsigned, altered, and stale packages.

## v0.7 — Monitoring and attack detection

- Record device, broker, and host events with synchronized timestamps and a run manifest. Evaluate detection only after defining a dataset split and error metrics.

## v0.8 — Cyber-physical extension

- Add a sensor and safe actuator only when the experiment requires them. Record electrical limits, reset behavior, and recovery. The earlier LED baseline remains the first output.

## v0.9 — TinyML, if supported by evidence

- Consider anomaly detection only after the project has enough labeled, repeatable traces to justify it. Compare against simple rules and report resource costs and detection errors.

## v1.0 — Research platform

- Package stable vulnerable/hardened experiments, simulator and hardware setup, run manifests, reproducible analysis, sanitized data, license provenance, and paper-ready evidence.

## Independent paper reproduction

T800 remains a separate candidate because it has public ESP32 code and a reproduction manual. It evaluates TCP port-scan filtering, which is outside the replay experiment. Pin and audit its upstream source and dedicated ESP-IDF environment before attempting a faithful run; do not mix T800 results with simulator or replay results.
