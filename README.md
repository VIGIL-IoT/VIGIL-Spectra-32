# SPECTRA-32

**A VIGIL-IoT Project**  
**Security Platform for Embedded Cyber Threat Research & Analysis**

SPECTRA-32 is the experimental attack-and-defense testbed of **VIGIL-IoT — Vulnerability Intelligence & Guarding for IoT Layers**.

> A low-cost ESP32 security testbed for evaluating IoT vulnerabilities, attack-defense mechanisms, secure communication, and cyber-physical resilience.

The research loop is **Build → Attack → Observe → Defend → Measure**. Experiments stay inside owned or explicitly authorized lab systems and networks.

## What exists now

The repository contains the project identity and architecture, an incremental roadmap, research and safety notes, a local Python behavior model, an interactive Streamlit device console, and an ESP-IDF reference port for later hardware validation.

The first milestone is a computer-run behavior model of an ESP32-style node. Its Streamlit console includes an interactive DevKit-style board illustration and session-local security scenarios for comparing vulnerable and hardened outcomes. Those scenarios are UI-only: they do not send attack traffic, alter the MQTT broker, or change the behavior model. The local node model still has no application authentication, command freshness checks, HTTPS, MQTT authentication, or MQTT TLS. The Streamlit console and example broker bind to loopback only. The ESP-IDF port has not been built or flashed, and no ESP32 hardware measurements have been collected.

## First milestone: v0.1 software simulation

The local model in `simulator/` exposes a web page and REST API, accepts `ON`/`OFF` MQTT messages, and tracks a virtual LED. The branded Streamlit console controls that loopback model and shows API/MQTT state, a clickable ESP32-style board, pin details, security telemetry, simulated attack paths, and an event log. The in-app vulnerable/hardened profiles are scenario visualizations, not firmware defenses.

This is software behavior simulation, not ESP32 emulation. It does not run ESP-IDF firmware or model ESP32 Wi-Fi, lwIP, GPIO timing, CPU, RAM, flash, or power. Board pins and components are illustrative rather than a wiring diagram. The later ESP-IDF port lives in `firmware/vulnerable/basic-node` and needs a real board plus ESP-IDF to validate.

### Run the simulation

Use Python 3.10+, Mosquitto, and the pinned packages in `simulator/requirements.txt`. Start a loopback-only broker in one terminal:

```powershell
mosquitto -c lab/simulation/mosquitto.conf
```

In a second terminal, create the environment, install the pinned packages, and start the model:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r simulator/requirements.txt
python simulator/vulnerable/basic_node.py
```

In a third terminal, start the Streamlit console:

```powershell
streamlit run simulator/dashboard/app.py
```

Open `http://127.0.0.1:8501`. The minimal built-in web page remains at `http://127.0.0.1:8080`. The MQTT command topic is `spectra/device01/cmd`; the status topic is `spectra/device01/status`. The [simulator guide](simulator/README.md) has setup details and explains the limits of the in-app scenarios.

The local model counts every valid command it applies, including repeats. This is observation instrumentation and does not prevent replay. Use the [hardware lab configuration](lab/mosquitto.conf.example) only later, on a dedicated network with no upstream connection.

## Research tracks

- [Project architecture](docs/ARCHITECTURE.md)
- [Brand and interface guidance](docs/BRAND.md)
- [Roadmap](docs/ROADMAP.md)
- [Experiment protocol](docs/EXPERIMENT_PROTOCOL.md)
- [Safety and data handling](docs/SAFETY_AND_DATA.md)
- [Research and paper selection](docs/research/RESEARCH_ANALYSIS.md)
- [T800 reproduction plan](docs/research/T800_REPRODUCTION_PLAN.md)
- [T800 experiment protocol](docs/research/T800_EXPERIMENT_PROTOCOL.md)
- [Experiment 01: MQTT command replay](experiments/EXP-01-replay/README.md)
- [Software simulator guide](simulator/README.md)
- [Streamlit device console](simulator/dashboard/app.py)

The T800 paper is a separate, strong candidate for a faithful reproduction because its authors publish code and a hardware reproduction manual. It studies TCP port-scan filtering, not MQTT replay. ReplIoT is the closer research reference for replay-test methodology; SPECTRA-32 will clearly label any ESP32-specific adaptation rather than call it an exact reproduction.

## Repository map

```text
simulator/                  v0.1 local software-in-the-loop model and dashboard
firmware/
  vulnerable/basic-node/   ESP-IDF reference port for later hardware runs
  hardened/                reserved for separate hardened implementations
experiments/
  EXP-01-replay/           replay experiment design; not yet run
lab/                       loopback simulation and isolated hardware broker configs
docs/                      architecture, brand, safety, and roadmap
docs/research/              paper analysis and T800 reproduction materials
```

Each future experiment should keep the vulnerable and hardened implementations distinct and record its threat model, exact configuration, run provenance, failures, and measurements. Useful outcomes include accepted/rejected commands, latency, RAM/flash, bandwidth, recovery time, false positives/negatives, and power when measured with suitable instrumentation.
