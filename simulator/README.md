# v0.1 computer-run model of ESP32 node behavior

This local software-in-the-loop model represents the v0.1 device behavior without an ESP32 board: a web page and REST API control a virtual LED, and MQTT accepts ON/OFF commands and publishes state.

It is a **behavioral model**, not an ESP32 hardware emulator. It does not run ESP-IDF firmware and does not model Wi-Fi radio behavior, lwIP, GPIO timing, processor performance, RAM, flash, or power. Use it to develop and repeat command-level behavior before doing a later ESP32 port.

The simulator and example broker bind to loopback addresses only. No service is exposed to the local network.

## Requirements and run

Use Python 3.10 or newer, install Mosquitto, and run these commands from the repository root in PowerShell.

1. Start the loopback-only broker in one terminal: mosquitto -c lab/simulation/mosquitto.conf
2. Create and activate a virtual environment: python -m venv .venv; .venv\Scripts\Activate.ps1
3. Install the pinned Python client: python -m pip install -r simulator/requirements.txt
4. Start the model in a second terminal: python simulator/vulnerable/basic_node.py
5. Open http://127.0.0.1:8080 in a browser.

The web API is GET /api/state and POST /api/led with form value state=on or state=off. The MQTT command topic is spectra/device01/cmd; the status topic is spectra/device01/status.

For command-line interaction, run mosquitto_sub against 127.0.0.1 on spectra/device01/status, then publish ON or OFF to spectra/device01/cmd with mosquitto_pub.

The baseline intentionally accepts repeated ON/OFF commands without authentication or freshness checks. The simulator counts every accepted command, including duplicates. That counter is for observing the model; it does not prevent replays.
