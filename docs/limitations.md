# Limitations

## Current implementation

- Streamlit scenarios operate on one browser session's in-memory state. State is not persisted across restarts or shared across users.
- The Streamlit console does not connect to the standalone Python node, its REST API, an MQTT broker, or the physical firmware. The dashboard chart is session-model counters, not live device telemetry.
- The virtual board is a representative ESP32 DevKit-style illustration. Pin labeling and board revisions can differ; it is not a schematic or wiring guide.
- USB discovery runs on the host that runs Python. Streamlit Cloud cannot enumerate USB hardware attached to a user's computer. Chip identification needs an explicit click, may reset the board, and has only mocked-output unit tests in this repo.
- The session's Hardened profile changes modeled flags and outcomes. It is not a real implementation of authentication, TLS, ACLs, replay protection, secure boot, flash encryption, OTA signature checks, rate limiting, or UART lockdown.
- Sample initial counters and events are illustrative. They are not generated from a real run.
- Chaos Lab contains eight fixed 10-second behavioral scenarios. A Streamlit fragment refreshes the session view once per second; no execution timing guarantee applies to a physical device.
- Chaos service availability, operation success, detection/recovery duration, retry/restart counts, and resilience score are scenario-plan outputs. They are not measured ESP32 performance, network statistics, or evidence that a real defense is effective.
- The Chaos score is a SPECTRA-32 educational metric with a documented formula, not an industry standard, certification, or security rating. Its assumptions and scenario workload are model-specific.
- Packet-loss behavior is a fixed deterministic formula. Memory pressure, sensor failure, latency, reboot, and watchdog behavior use qualitative model state and generic assumptions, not measured hardware ranges.
- Chaos sessions are not persisted or shared. The timer advances only while the Streamlit session is active, and there is no hardware-in-loop execution backend.

## Standalone Python model

- The HTTP and MQTT interfaces are unauthenticated by design; the software configuration binds to loopback. Do not expose it on a LAN or public interface.
- The node's state is volatile and reset on process restart.
- HTTP route tests use a fake MQTT publisher. A separate integration test verifies MQTT commands and status with a local Mosquitto process in CI; a local developer broker run was not performed in the audit.
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
- Mosquitto is not installed locally. The Python node's broker-backed behavior is verified in hosted loopback CI, while physical firmware behavior is not verified. The firmware CI build uses ESP-IDF 6.1.0 and the checked-in `dependencies.lock` pins `espressif/mqtt` 1.1.0.
- No package build is defined because the project is an application repository, not a distributable Python library.
- GitHub Actions audits the locked runtime and development environment with `pip-audit`; the Python 3.14 job generates and uploads a CycloneDX 1.5 runtime SBOM. GitHub Releases also attach the exact ESP-IDF Component Manager lock from the firmware build. That lock does not enumerate ESP-IDF built-in components or compiler/toolchain binaries, so it is not a complete firmware SBOM.

## Scope and safety

No testing against third-party devices, networks, applications, or services is supported or claimed. Real radio tests, scanning, availability stress, firmware modification, and physical interaction require their own protocol, owned equipment, isolated network, and authorization. See `docs/SAFETY_AND_DATA.md` and `SECURITY.md`.
