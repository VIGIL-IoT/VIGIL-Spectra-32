# v0.1 computer-run model of ESP32 node behavior

This local software-in-the-loop model represents the v0.1 device behavior without an ESP32 board: a web page and REST API control a virtual LED, and MQTT accepts ON/OFF commands and publishes state.

It is a **behavioral model**, not an ESP32 hardware emulator. It does not run ESP-IDF firmware and does not model Wi-Fi radio behavior, lwIP, GPIO timing, processor performance, RAM, flash, or power. Use it to develop and repeat command-level behavior before doing a later ESP32 port.

The simulator and example broker bind to loopback addresses only. No service is exposed to the local network.

## Requirements and run

Use Python 3.10 or newer, install Mosquitto, and run these commands from the repository root in PowerShell. The Streamlit console is the primary UI; the node model remains a separate local service.

1. Start the loopback-only broker in one terminal: mosquitto -c lab/simulation/mosquitto.conf
2. Create and activate a virtual environment: python -m venv .venv; .venv\Scripts\Activate.ps1
3. Install the pinned Python packages: python -m pip install -r simulator/requirements.txt
4. Start the behavior model in a second terminal: python simulator/vulnerable/basic_node.py
5. Start the Streamlit console in a third terminal: streamlit run simulator/dashboard/app.py
6. Open http://127.0.0.1:8501. The model's minimal built-in page remains at http://127.0.0.1:8080.

The web API is GET /api/state and POST /api/led with form value state=on or state=off. The MQTT command topic is spectra/device01/cmd; the status topic is spectra/device01/status.

For command-line interaction, run mosquitto_sub against 127.0.0.1 on spectra/device01/status, then publish ON or OFF to spectra/device01/cmd with mosquitto_pub.

The baseline intentionally accepts repeated ON/OFF commands without authentication or freshness checks. The simulator counts every accepted command, including duplicates. That counter is for observing the model; it does not prevent replays.

The Streamlit console polls the local model API every two seconds and sends its ON/OFF controls through that API. Its default project config binds the dashboard to loopback. It is not a public Streamlit deployment: the model has no authentication, and the dashboard expects the behavior service at 127.0.0.1:8080.

The console includes an illustrative ESP32 DevKit-style board view. Its GPIO4 LED indicator follows the model's virtual output state. The drawing is a UI aid, not a wiring diagram or hardware emulator; pin placement varies across ESP32 development-board revisions.

The dashboard uses the documented [`st.fragment` periodic rerun API](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment). Project configuration follows Streamlit's [configuration options](https://docs.streamlit.io/develop/concepts/configuration/options).
