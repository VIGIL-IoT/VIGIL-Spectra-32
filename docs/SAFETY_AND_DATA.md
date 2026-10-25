# Safety and Data Handling

SPECTRA-32 is an embedded-security research platform. All testing is limited to software, hardware, and networks the project owns or is explicitly authorized to test.

## Computer-run simulator

1. The v0.1 model, Streamlit dashboard, and Mosquitto example bind to 127.0.0.1. Run Streamlit from the repository root so `.streamlit/config.toml` is applied; keep all three services loopback-only.
2. The broker has anonymous access and no TLS by design. Do not change it to listen on a LAN interface for the software-only milestone.
3. The model changes only a virtual LED state. It does not send traffic to other hosts or control a physical output.
4. The Streamlit security-event controls update only the current dashboard session's in-memory model. Replay, authentication, high request-rate, OTA, and debug scenarios do not send MQTT messages or network traffic. The separate node API is used only by the virtual GPIO4 ON/OFF control. No scanning, flooding, brute force, OTA write, or interaction with unrelated devices is part of this software milestone.

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

## Data handling

- sdkconfig, local credentials, and local .env files are gitignored. Do not commit them.
- Keep raw PCAPs, unredacted serial logs, MAC/IP identifiers, device serial numbers, and local machine identifiers out of Git by default.
- Commit only sanitized, necessary results with a documented transformation and output hash.
- Verify software, paper artifact, model, and dataset licenses before redistributing them. A code license does not license third-party datasets.
- Quarantine traces that include non-lab traffic; do not include them in results or releases.
- Retain failed runs and explain exclusions so the results remain auditable.

## Scope boundary

The first model is intentionally unprotected. It does not implement authentication, replay defenses, HTTPS, MQTT authentication, MQTT TLS, BLE security, secure OTA, or attack detection. Future tests need their own threat model, protocol, and authorized lab scope. Do not describe baseline behavior as a vulnerability in third-party products; it is a controlled project target.
