# SPECTRA-32

**A VIGIL-IoT Project**  
**Security Platform for Embedded Cyber Threat Research & Analysis**

SPECTRA-32 is the experimental attack-and-defense testbed of **VIGIL-IoT — Vulnerability Intelligence & Guarding for IoT Layers**.

> A low-cost ESP32 security testbed for evaluating IoT vulnerabilities, attack-defense mechanisms, secure communication, and cyber-physical resilience.

The research loop is **Build → Attack → Observe → Defend → Measure**. Experiments stay inside owned or explicitly authorized lab systems and networks.

## What exists now

The repository contains the project identity and architecture, an incremental roadmap, research and safety notes, a local Python behavior model, the VIGIL-IoT Streamlit console, and an ESP-IDF reference port for later hardware validation.

The Streamlit console now uses the dark, mint-accented SPECTRA-32 interface with an interactive DevKit board, pin and component details, vulnerable/hardened profiles, session-local security scenarios, telemetry, attack-path highlights, and an event log. The console is an in-memory visualization and does not call the local node-model API, publish MQTT messages, send attack traffic, write firmware, or control hardware.

## First milestone: v0.1 software simulation

The local Python model in `simulator/` exposes a web page and REST API, accepts `ON`/`OFF` MQTT messages, and tracks a virtual LED. It runs separately from the Streamlit console. The console uses its own session-local sample state; its vulnerable/hardened profile and event outcomes are illustrative comparisons, not defenses in the Python model or firmware.

This is software behavior simulation, not ESP32 emulation. It does not run ESP-IDF firmware or model ESP32 Wi-Fi, lwIP, GPIO timing, CPU, RAM, flash, or power. Board pins and components are illustrative rather than a wiring diagram. The later ESP-IDF port lives in `firmware/vulnerable/basic-node` and needs a real board plus ESP-IDF to validate.

### Run the Streamlit console

Use Python 3.10+ and the pinned packages in `simulator/requirements.txt`. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r simulator/requirements.txt
streamlit run simulator/dashboard/app.py
```

Open `http://127.0.0.1:8501`. The console does not require the MQTT broker or the separate Python node model. Its sample counters and scenario results live only in the current Streamlit session.

### Run the optional local node model

The node model and broker remain separate tools for the software-in-the-loop milestone. Start a loopback-only broker in one terminal with `mosquitto -c lab/simulation/mosquitto.conf`. In another terminal, run `python simulator/vulnerable/basic_node.py`. The model's minimal web page and REST API are available on `127.0.0.1:8080`; MQTT topics are `spectra/device01/cmd` and `spectra/device01/status`.

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
