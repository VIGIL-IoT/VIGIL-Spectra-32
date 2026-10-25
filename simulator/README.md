# SPECTRA-32 Virtual Node Console

**A VIGIL-IoT Project** · an interactive, session-local security console for the SPECTRA-32 sample node.

The Streamlit app presents a clickable ESP32 DevKit-style board, 32-pin/component inspection, vulnerable and hardened profiles, bounded security scenarios, telemetry, an affected-path view, and a searchable event log. The interface uses the dark, mint-accented visual system documented in [`docs/BRAND.md`](../docs/BRAND.md).

## Simulation boundary

The console updates only the current Streamlit session's sample state. Replay, authentication, plaintext MQTT, high request-rate, unsigned OTA, and debug-exposure scenarios do not publish MQTT messages, call the REST API, send packets, write firmware, or touch hardware. The GPIO23 relay is simulated. Vulnerable and Hardened profiles are comparison scenarios; they do not alter the separate Python node model or provide evidence of ESP32 protection.

The Python node model in `simulator/vulnerable/` remains a separate software-in-the-loop service. It exposes a loopback web page and REST API and can use the MQTT broker; the Streamlit dashboard does not connect to that API. The board illustration is not a wiring diagram. This project does not emulate ESP32 CPU, radio, GPIO timing, memory, flash, or power.

## Run the console

Use Python 3.10 or newer. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r simulator/requirements.txt
streamlit run simulator/dashboard/app.py
```

Open `http://127.0.0.1:8501`. No MQTT broker or node-model process is required for the console.

## Run the optional local node model

For the separate behavior model, start a loopback-only Mosquitto broker with `mosquitto -c lab/simulation/mosquitto.conf`, then run `python simulator/vulnerable/basic_node.py` in another terminal. Its HTTP endpoints are `GET /api/state` and `POST /api/led` on `127.0.0.1:8080`; the minimal model page is also served there. MQTT topics are `spectra/device01/cmd` and `spectra/device01/status`.

The vulnerable node model accepts repeated valid ON/OFF commands without authentication or freshness checks. Its accepted-command counter observes commands; it does not prevent replay. Keep the model and broker on loopback or an isolated lab network.
