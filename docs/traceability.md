# Requirements Traceability

Status is limited to the evidence named in the row. A unit test verifies a code path, not a device-level security property.

| Requirement ID | Requirement | Objective | Design decision | Implementation | Verification | Evidence | Status |
|---|---|---|---|---|---|---|---|
| FR-01 | Dashboard scenarios remain session-local and emit no attack traffic | O-1, O-3 | [ADR-002](decisions/ADR-002-session-local-scenarios.md) | `services/simulator.py`, `simulator/dashboard/app.py` | AppTest scenarios across both profiles; source path inspection | `tests/test_dashboard_app.py`, `tests/test_scenarios.py` | Partially Verified |
| FR-02 | Board pins/components can be selected and explained | O-1, O-3 | Existing interactive SVG component | `data/board_definition.py`, `components/board.py`, `components/board_component/index.html` | Streamlit AppTest selection paths | `tests/test_dashboard_app.py` | Verified (UI behavior only) |
| FR-03 | One bounded, inspectable event is applied per selected scenario | O-1 | Deterministic session transition | `data/scenarios.py`, `services/simulator.py` | Both profiles, replay difference, bounded event history | `tests/test_scenarios.py` | Verified (simulation semantics only) |
| FR-04 | Chip identification is explicit and does not write flash | O-3 | [ADR-003](decisions/ADR-003-host-chip-identification.md) | `services/hardware.py`, hardware view in `app.py` | Mocked esptool command and failure-output tests | `tests/test_scenarios.py` | Partially Verified; physical probe untested |
| FR-05 | Standalone HTTP model validates LED controls and exposes state | O-2 | Local-only behavior model | `simulator/vulnerable/basic_node.py` | Loopback test server exercises valid, malformed, duplicate, and unknown routes | `tests/test_node_http.py` | Verified (HTTP routes) |
| FR-06 | MQTT model accepts fixed commands and publishes status | O-2 | Separate broker-backed service | `simulator/vulnerable/basic_node.py`, `lab/simulation/mosquitto.conf` | Source review only; Mosquitto not installed | `services/simulator.py` and node source | Partially Verified |
| FR-07 | Default desktop interfaces remain loopback-only | O-3 | Loopback-only defaults | `lab/simulation/mosquitto.conf`, node server startup, `.streamlit/config.toml` | Configuration review; no remote-bind test | Config files and code | Partially Verified |
| FR-08 | Classic ESP32 firmware builds and matches software behavior | O-6 | [ADR-001](decisions/ADR-001-software-model-boundary.md) | `firmware/vulnerable/basic-node/` | No ESP-IDF toolchain or board available | No build/run evidence | Untested |
| FR-09 | Python setup and deterministic tests are repeatable | O-5 | Pinned direct dependencies and CI | `requirements.txt`, `simulator/requirements.txt`, `.github/workflows/python-quality.yml` | Python 3.14 local suite; CI matrix defined for 3.12/3.14 | `docs/REPOSITORY_AUDIT.md`; CI run pending | Partially Verified |
| FR-10 | EXP-01 run records identify commit, setup, outcomes, deviations, and hashes | O-4 | Experiment protocol and ledger | `experiments/EXP-01-replay/README.md`, `docs/EXPERIMENT_PROTOCOL.md` | Documentation review; no experiment run | Run ledger says no runs | Partially Verified (protocol exists; experiment not run) |
| NFR-01 | Raw captures and local credentials are excluded by default | O-3 | Ignore raw captures and secret config | `.gitignore`, `docs/SAFETY_AND_DATA.md` | `git check-ignore` spot checks and secret-pattern scan | Audit record | Partially Verified |
| NFR-02 | Claims distinguish simulation from measured hardware behavior | O-3, O-4 | Scope labels in UI and documentation | README, architecture, limitations, experiment docs | Cross-document and source review | `docs/limitations.md`, scenario labels | Verified (documentation/source wording) |

No row is marked as hardware-verified. MQTT integration, ESP-IDF build, physical chip identification, and experimental results remain open.
