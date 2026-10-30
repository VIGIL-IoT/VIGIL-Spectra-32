# Project Requirements and Scope

**Status:** current requirements baseline for the SPECTRA-32 software prototype. The requirements describe checked-in behavior separately from planned hardware work.

## Identity and problem statement

**SPECTRA-32 — Security Platform for Embedded Cyber Threat Research & Analysis** is the experimental attack-and-defense testbed of VIGIL-IoT. It is a hybrid embedded-security research project: a Python software behavior model and Streamlit console exist today; the ESP-IDF reference compiles in CI, while physical hardware experiments remain unverified.

The engineering problem is to make selected IoT security behaviors inspectable and repeatable on a low-cost development path without confusing a host-side model with physical-device evidence. The current software model makes command/state behavior available before a board is required. The repository does not claim that a browser simulator replaces hardware testing, or that its profile labels implement actual security controls.

The current gap is project-specific: dashboard scenarios, a standalone node model, and future firmware need a traceable boundary and repeatable verification path. The current console scenarios are not connected to the standalone node or firmware, and only the Python HTTP routes have deterministic local route tests. No experiment has been run.

## Users and use cases

- **Embedded-security learners and researchers:** inspect modeled attack and defense decisions before planning lab work.
- **ESP32 engineers:** review pin metadata and a future classic ESP32 reference port.
- **Maintainers and reviewers:** inspect scope, evidence, safety constraints, and experiment plans.
- **Current use cases:** run the Streamlit session model locally; run the separate loopback Python node with a local broker; identify a connected Espressif chip from the local Streamlit host after an explicit click; review the planned replay and T800 protocols.

## Objectives and success criteria

| Objective | Success criterion | Evidence source |
|---|---|---|
| O-1: Keep modeled events deterministic and inspectable | Each catalogued scenario produces a bounded state/event transition and is smoke-tested in both profiles | `tests/test_scenarios.py`, `tests/test_dashboard_app.py` |
| O-2: Make the standalone software node's HTTP behavior reproducible | Valid LED forms update one virtual state; invalid/duplicate values and unknown routes are rejected | `tests/test_node_http.py` |
| O-3: Distinguish software model, host USB discovery, and hardware | UI/docs label sample values; chip probe is explicit; no attack scenario is represented as physical telemetry | architecture docs, `services/hardware.py`, scenario tests |
| O-4: Define a defensible replay experiment | Threat model, controls, outcomes, repetition plan, run ledger, and reproduction label are written before data collection | `experiments/EXP-01-replay/README.md` |
| O-5: Enable another contributor to verify the Python prototype | A cross-platform dependency lock, setup instructions, CI checks, and test commands are available | README, `pyproject.toml`, `uv.lock`, Python quality workflow |
| O-6: Validate the ESP32 implementation | Build, flash, and compare a declared firmware commit on a documented board and isolated lab | Future evidence; not met today |

The objectives do not imply measured effectiveness. O-6 is a future validation goal.

## Scope

### Implemented

- An in-memory Streamlit session model with vulnerable/hardened comparison profiles, sample security events, board visualization, counters, event log, and session chart.
- Local host USB serial-port enumeration and an explicit, no-flash-write esptool chip-identification probe.
- A separate Python node with loopback HTTP routes, virtual LED state, and optional MQTT command/status handling.
- Loopback Mosquitto configuration for the computer-run node.
- A classic ESP32 ESP-IDF reference implementation in source form.
- Written replay and T800 experimental protocols; these protocols have no associated run results.
- GitHub Pages publication of a static Archify research workflow diagram.

### Partly implemented or not yet verified

- The standalone Python node's MQTT code exists, but a broker-backed integration run is not verified.
- The ESP-IDF source builds for classic `esp32` in CI, but no flash, board test, or parity run is recorded.
- Physical chip classification is unit-tested with mocked esptool output; no physical probe is recorded in the repository.
- The current Python app and tests were run on Python 3.14.7. The declared support range is Python 3.12 through 3.14; CI covers all three minor versions.

### Out of scope for the current release

- Sending attack traffic from the Streamlit dashboard or controlling physical GPIO from browser scenarios.
- General-purpose scanning, flooding, brute-force, firmware-write, radio attack, or public-network testing tools.
- Exact reproduction of REPLIOT or T800 without their documented artifacts, environments, hardware, and run evidence.
- Production security, safety certification, multi-user persistent storage, cloud device management, or real-time device telemetry.
- Claims about commercial products or security improvement based only on the UI model.

## Functional requirements

| ID | Requirement |
|---|---|
| FR-01 | Provide a per-session model whose scenario actions do not call the broker, standalone node API, or physical GPIO. |
| FR-02 | Render the classic ESP32 DevKit-style reference pins/components and expose selected component details. |
| FR-03 | Provide bounded, inspectable events and counters for catalogued scenarios, with a readable session-local time series for accepted commands and blocked requests. |
| FR-04 | Enumerate host serial ports and run chip identification only after an explicit UI action. |
| FR-05 | Provide a separate loopback Python node API for virtual LED state and control. |
| FR-06 | Provide optional MQTT command/status behavior on the separate node, with lab-only broker guidance. |
| FR-07 | Keep the ESP-IDF vulnerable reference path separate from dashboard simulation and from any future hardened firmware. |
| FR-08 | Preserve run provenance, failure records, configuration, and evidence for any future experiment. |

## Nonfunctional requirements

| ID | Requirement |
|---|---|
| NFR-01 | Default desktop simulator services bind to loopback; the unauthenticated hardware example must remain on an isolated authorized lab network. |
| NFR-02 | Dashboard/profile/result wording must not imply hardware telemetry or measured security. |
| NFR-03 | Invalid HTTP form input is rejected; chip identification has a finite subprocess timeout and no write/erase command. |
| NFR-04 | Supported Python versions and runtime dependencies are explicit; a checked-in cross-platform lock fixes transitive Python dependency versions. |
| NFR-05 | UI and model state remain bounded: session event history is capped at 60 events and chart history at 60 samples; the counter chart uses a readable zero-based scale and shows the latest sample even when only one sample exists. |
| NFR-06 | Experiment files must separate measured, simulated, expected, and paper-reported outcomes. |
| NFR-07 | The Python 3.14 quality job exports and validates a CycloneDX 1.5 SBOM for the locked runtime dependency set, then uploads it as a short-lived artifact. |

## Technical stack

| Layer | Technology/version | Use/status |
|---|---|---|
| Language | Python >=3.12,<3.15; audited locally on 3.14.7 | Dashboard, model, and tests; CI covers 3.12, 3.13, and 3.14 |
| Environment lock | uv 0.13.6 | Cross-platform Python dependency lock; development tools are in a separate group |
| Dashboard | Streamlit 1.66.1 | Local or hosted session UI |
| Table/chart data | pandas 3.0.0 | In-memory counter chart |
| Image support | Pillow 13.0.0 | Streamlit transitive dependency; explicitly pinned to the patched compatible release |
| MQTT client | Paho MQTT 2.1.0 | Separate virtual node, MQTT 3.1.1 client protocol |
| USB serial | pySerial 3.5 | Host-side port discovery |
| Chip probe | esptool 5.6.0 | Explicit classic/other ESP identification |
| Broker | Mosquitto | Optional; version not recorded |
| Firmware | ESP-IDF 6.1.0, classic `esp32` target | CI compile passes; no physical board verification |
| Firmware MQTT | `espressif/mqtt` 1.1.0 | Exact version and component hash recorded in `firmware/vulnerable/basic-node/dependencies.lock` |
| Front end | HTML, CSS, JavaScript, SVG | Streamlit custom board component and standalone node page |
| CI and hosting | GitHub Actions, GitHub Pages | Python validation workflow and static workflow page |
| Dependency audit | pip-audit 2.10.1 | Locked runtime and development environment audit in CI |
| Runtime SBOM | CycloneDX 1.5 via uv 0.13.6 | Exported, validated, and uploaded as a 30-day artifact by the Python 3.14 quality job |
| Python lint | Ruff 0.17.3 | Correctness-focused E4/E7/E9/F checks in CI |
| Diagram renderer | Archify 3.2.0 at pinned commit `208acba8d412335185b2056fedf54b3405df43fb` | Workflow diagram generation |

There is no database, application persistence layer, ML framework, sensor, or physical measurement device in the current prototype.

## Assumptions and constraints

- The vulnerable node and Mosquitto example are for owned software and an authorized lab only.
- The classic ESP32 pin diagram represents one common DevKit-style layout; board revisions differ.
- The local Python model and Streamlit UI have separate state and execution paths.
- No device credentials, public broker, or Internet-connected hardware target is assumed.
- The current board detection feature is host-side; web hosting cannot see a developer's USB devices.

## Maturity

Current classification: **prototype / v0.1 software behavior model**. The dashboard has automated smoke coverage. The standalone HTTP API has local route tests. MQTT integration and ESP32 firmware have not been verified, and no security experiment has been run.
