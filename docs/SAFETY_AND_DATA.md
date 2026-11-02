# Safety and Data Handling

SPECTRA-32 is an embedded-security research platform. All testing is limited to software, hardware, and networks the project owns or is explicitly authorized to test.

## Computer-run simulator

1. The standalone v0.1 node and Mosquitto example bind to 127.0.0.1. The Streamlit server config also binds its local development server to 127.0.0.1. Run Streamlit from the repository root so `.streamlit/config.toml` is applied.
2. The broker has anonymous access and no TLS by design. Do not change it to listen on a LAN interface for the software-only milestone.
3. The model changes only a virtual LED state. It does not send traffic to other hosts or control a physical output.
4. The Streamlit security-event controls update only the current dashboard session's in-memory model. Replay, authentication, high request-rate, OTA, and debug scenarios do not call the node API, publish MQTT messages, or send network traffic. The dashboard is not connected to the standalone node process. No scanning, flooding, brute force, OTA write, physical GPIO control, or interaction with unrelated devices is part of this software milestone.
5. Chaos Lab runs a separate deterministic behavioral model in the current Streamlit session. It does not kill or pause processes, change Wi-Fi, manipulate routes or packets, stop a broker, open a serial port, restart firmware, flash hardware, or drive GPIO.
6. USB serial discovery runs on the machine hosting the Streamlit Python process. Port listing does not open the port. The user-triggered esptool chip-ID probe may reset a board but does not write or erase flash.

## Later hardware runs

1. Use a dedicated access point with no internet or other network uplink.
2. Keep only the experiment host, broker, and owned ESP32 devices on the lab segment.
3. Bind the hardware-stage broker only to the broker host's lab-network address. Never run the unauthenticated example on a home, office, campus, hotel, conference, public, or internet-facing interface.
4. Keep hardware commands bounded to the documented LED topics. The baseline has no application-level authorization.

## Hardware boundary

- Start with one low-voltage LED and a series resistor on a board-verified GPIO.
- Do not attach mains voltage, a relay, motor, door lock, heater, or other hazardous output in the first hardware port.
- Keep USB power disconnect and reset available. Verify the exact board pinout before wiring.
- Add sensors or actuators only for a named experiment with electrical limits, reset behavior, and safety measures documented.

## Qualitative failure-mode screen

This is a qualitative design screen for the current prototype, not a numerical risk assessment. Severity and likelihood are not assigned scores because the board, lab conditions, and physical tests are not yet characterized.

| Failure mode | Possible effect | Current controls | Detection or evidence | Remaining action |
|---|---|---|---|---|
| Board revision or pin map is assumed incorrectly | Miswiring, unexpected boot behavior, or board damage | Illustration is labeled as a generic reference; strap and flash pins carry warnings; no wiring is claimed | `tests/test_board_definition.py`, [hardware reference](hardware-references.md) | Record exact board model and revision before physical wiring |
| External circuitry changes a strap pin during reset | Board selects a different boot or supply configuration | GPIO0, GPIO2, GPIO5, GPIO12, and GPIO15 are flagged for review | Source-backed pin metadata and the Espressif references | Reassess strap levels against the exact board and circuit |
| Chip-ID probe interrupts a connected board | Device resets or an in-progress interaction is interrupted | Probe is a user-triggered action with a bounded timeout and no flash write or erase | `services/hardware.py` and mocked command tests | Warn before probing and test the selected physical board before lab use |
| Anonymous example broker is exposed beyond loopback | Unauthorized clients can issue commands to the vulnerable model | Desktop defaults bind to loopback; lab guidance requires an isolated segment | Configuration review and loopback tests | Keep the broker off public, shared, and general LANs |
| Session model output is mistaken for device telemetry | Incorrect conclusions about hardware or security effectiveness | UI, architecture, protocols, and results label output as simulated | Scenario and dashboard tests; docs review | Validate against measured data before making effectiveness claims |
| Malformed HTTP body is parsed ambiguously or incompletely | Unintended virtual state transition or request-handler error | Duplicate framing, transfer encoding, content type, body size, field count, and exact length are validated | `tests/test_node_http.py` includes malformed raw requests | Keep the endpoint loopback-only and rerun verification after parser changes |

## Data handling

- sdkconfig, local credentials, and local .env files are gitignored. Do not commit them.
- Keep raw PCAPs, unredacted serial logs, MAC/IP identifiers, device serial numbers, and local machine identifiers out of Git by default.
- Commit only sanitized, necessary results with a documented transformation and output hash.
- Verify software, paper artifact, model, and dataset licenses before redistributing them. A code license does not license third-party datasets.
- Quarantine traces that include non-lab traffic; do not include them in results or releases.
- Retain failed runs and explain exclusions so the results remain auditable.

## Scope boundary

The first model is intentionally unprotected. It does not implement authentication, replay defenses, HTTPS, MQTT authentication, MQTT TLS, BLE security, secure OTA, or attack detection. Future tests need their own threat model, protocol, and authorized lab scope. Do not describe baseline behavior as a vulnerability in third-party products; it is a controlled project target.
