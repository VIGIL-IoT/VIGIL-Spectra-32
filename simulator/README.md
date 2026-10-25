# SPECTRA-32 Virtual Node Console

**A VIGIL-IoT Project** · a local, computer-run model of an ESP32-style IoT node.

The Streamlit console provides an interactive DevKit-style board illustration, a pin and component inspector, virtual GPIO4 LED controls, device status, security metrics, attack-path highlights, and an event log. Vulnerable and Hardened profiles drive bounded, in-app security scenarios.

## What this is

This is a software behavior model. It does not emulate ESP32 CPU instructions, run ESP-IDF firmware, model Wi-Fi radio behavior, or provide physical GPIO, RAM, flash, timing, or power measurements. The board drawing is illustrative; it is not a wiring diagram and pin placement varies by board revision.

The event selector changes only the current Streamlit session's in-memory state. Replay, authentication, plaintext MQTT, high request-rate, unsigned OTA, and debug-exposure scenarios do not publish MQTT messages, send packets, write firmware, or touch hardware. Only the GPIO4 ON/OFF controls call the separate loopback node-model API. The relay on GPIO23 is simulated.

The dashboard's Hardened profile is a comparison model; it does not harden the separate Python node or broker. A Hardened event outcome is not evidence of protection on ESP32 hardware.

## Run locally

Use Python 3.10 or newer and the pinned dependencies in `requirements.txt`. From the repository root, open separate PowerShell terminals:

1. Start the optional local MQTT broker: `mosquitto -c lab/simulation/mosquitto.conf`
2. Create a virtual environment, activate it, and install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r simulator/requirements.txt
   ```

3. Start the local behavior model: `python simulator/vulnerable/basic_node.py`
4. Start the console: `streamlit run simulator/dashboard/app.py`
5. Open `http://127.0.0.1:8501`.

The MQTT broker is optional for the dashboard and HTTP model API. If it is not running, MQTT is shown as disconnected. The behavior model serves `GET /api/state` and `POST /api/led` on `127.0.0.1:8080`. The model's minimal built-in page also remains available at `http://127.0.0.1:8080`.

The MQTT command topic is `spectra/device01/cmd`; the status topic is `spectra/device01/status`. The intentionally vulnerable command model accepts repeated valid ON/OFF commands without authentication or freshness checks. Its accepted-command counter observes commands; it does not prevent replay.

## Deployment boundary

The repository has no Vercel deployment. The Streamlit dashboard expects a model API at the user's own `127.0.0.1:8080`, which is only reachable from that same machine. Putting this dashboard on Vercel would require a separate browser frontend and a hosted, authenticated API; this local dashboard and its model should not be exposed publicly as configured.
