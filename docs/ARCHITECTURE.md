# SPECTRA-32 Architecture

SPECTRA-32 is the experimental attack-and-defense testbed of **VIGIL-IoT — Vulnerability Intelligence & Guarding for IoT Layers**. Development starts with a local software model, then moves the same behavior to an ESP32 board.

## v0.1 computer-run node model

| Link | Data flow |
|---|---|
| Browser ↔ Streamlit console | Loopback dashboard polling the model API and sending REST controls |
| Browser ↔ simulator fallback | Loopback HTTP page, REST control, and virtual LED state |
| Simulator ↔ Mosquitto broker | MQTT LED commands and status, both on loopback |
| Virtual output | A process state variable displayed as an LED; no GPIO is accessed |
| ESP32 hardware | Future port under firmware/vulnerable/basic-node |

The simulator, Streamlit console, and example broker run on the experimenter's computer and bind to 127.0.0.1. No Wi-Fi access point, internet connection, physical ESP32, or external host is needed for v0.1.

The modeled node includes:

- A branded Streamlit dashboard plus a minimal local page, with REST endpoints for LED state and control.
- An MQTT command topic, spectra/device01/cmd, accepting plain ON and OFF payloads.
- An MQTT status topic, spectra/device01/status, publishing the current virtual LED state.
- A count of valid commands applied, including duplicates, to make behavior observable.

No sensor is selected yet, so the model does not generate synthetic temperature telemetry.

## Simulation boundary

The Python process models application behavior; it does not execute ESP-IDF firmware and is not cycle-accurate. It does not model Wi-Fi radio behavior, lwIP, GPIO timing, processor performance, memory limits, flash usage, or power. Use the simulator to develop and repeat functional command scenarios. Do not use its results as hardware performance or security measurements.

## Trust boundary and v0.1 limitations

The model deliberately lacks application-level authentication, per-command freshness, HTTPS, and MQTT authentication/TLS. It accepts repeated valid ON/OFF commands. Its HTTP and MQTT services are loopback-only, so the current simulator does not expose a remote network attack surface.

## Separate implementation paths

- simulator/: computer-run behavioral model and local web UI.
- firmware/vulnerable/basic-node/: unprotected ESP-IDF port for later hardware comparison.
- firmware/hardened/<experiment>/: future defense implementation, kept separate from the vulnerable baseline.
- experiments/EXP-01-replay/: controlled replay methods and run records.

The ESP-IDF port is not built or hardware-verified. A later parity check should compare the same command sequences and state changes in the software model and on the selected ESP32 board.

## Research paper track

The replay experiment is the first security module. REPLIOT is the closest methodological reference for controlled command replay. T800 remains a separate paper-reproduction candidate for ESP32 TCP port-scan filtering; it does not validate the replay experiment.
