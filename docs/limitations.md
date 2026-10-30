# Limitations

## Current implementation

- Streamlit scenarios operate on one browser session's in-memory state. State is not persisted across restarts or shared across users.
- The Streamlit console does not connect to the standalone Python node, its REST API, an MQTT broker, or the physical firmware. The dashboard chart is session-model counters, not live device telemetry.
- The virtual board is a representative ESP32 DevKit-style illustration. Pin labeling and board revisions can differ; it is not a schematic or wiring guide.
- USB discovery runs on the host that runs Python. Streamlit Cloud cannot enumerate USB hardware attached to a user's computer. Chip identification needs an explicit click, may reset the board, and has only mocked-output unit tests in this repo.
- The session's Hardened profile changes modeled flags and outcomes. It is not a real implementation of authentication, TLS, ACLs, replay protection, secure boot, flash encryption, OTA signature checks, rate limiting, or UART lockdown.
- Sample initial counters and events are illustrative. They are not generated from a real run.

## Standalone Python model

- The HTTP and MQTT interfaces are unauthenticated by design; the software configuration binds to loopback. Do not expose it on a LAN or public interface.
- The node's state is volatile and reset on process restart.
- HTTP route tests use a fake MQTT publisher. A real Mosquitto integration run has not been verified.
- The model accepts repeated valid `ON`/`OFF` messages. Its command counter observes repeats; it does not prevent replay.
- The node is an application-level behavior model. It does not emulate ESP32 radio, lwIP, GPIO timing, CPU, RAM, flash, or power.

## Firmware and hardware

- ESP-IDF 6.1 compiles the classic ESP32 target in CI, but the image has not been flashed or verified on a physical board. No sensor or calibrated measurement device was used in the audit.
- The vulnerable firmware and lab broker lack application authentication and transport encryption. They are unsafe outside an isolated, owned lab.
- The firmware's HTTP/MQTT output path is separate from dashboard controls. There is no browser-to-board attack command channel or physical event log view.
- The board/pin mapping requires validation against the exact physical board before wiring. Only a low-voltage LED with suitable current limiting is in the first hardware plan; no hazardous actuator is supported.
- There is no separate hardened firmware implementation or validated comparison yet.

## Research and statistics

- EXP-01 and T800 documents are plans; the run ledgers contain no experiment results.
- The replay workflow adapts a methodological idea and is not an exact reproduction of REPLIOT.
- T800 is a separate TCP port-scan study and has no SPECTRA-32 reproduction evidence.
- No attack success rates, confidence intervals, device resource costs, power values, false-positive rates, or SDG outcomes are measured.

## Reproducibility and operations

- Python dependencies are pinned in `pyproject.toml` and resolved in the cross-platform `uv.lock`; the lock is generated with uv 0.13.6 and checked in CI with `--locked`.
- Python 3.14.7 was tested locally. CI covers Python 3.12, 3.13, and 3.14; the other matrix interpreters are not installed in this local environment.
- Mosquitto is not installed locally. The firmware CI build uses ESP-IDF 6.1.0 and the checked-in `dependencies.lock` pins `espressif/mqtt` 1.1.0; neither broker-backed behavior nor physical firmware behavior is verified.
- No package build is defined because the project is an application repository, not a distributable Python library.
- GitHub Actions audits the locked runtime and development environment with `pip-audit`. No SBOM is generated yet.

## Scope and safety

No testing against third-party devices, networks, applications, or services is supported or claimed. Real radio tests, scanning, availability stress, firmware modification, and physical interaction require their own protocol, owned equipment, isolated network, and authorization. See `docs/SAFETY_AND_DATA.md` and `SECURITY.md`.
