# SPECTRA-32

**A VIGIL-IoT Project**  
**Security Platform for Embedded Cyber Threat Research & Analysis**

SPECTRA-32 is the experimental attack-and-defense testbed of **VIGIL-IoT — Vulnerability Intelligence & Guarding for IoT Layers**.

> A low-cost ESP32 security testbed for evaluating IoT vulnerabilities, attack-defense mechanisms, secure communication, and cyber-physical resilience.

The research loop is **Build → Attack → Observe → Defend → Measure**. Experiments stay inside owned or explicitly authorized lab systems and networks.

## What exists now

The repository contains the project identity and architecture, an incremental roadmap, research and safety notes, a local software model, and an ESP-IDF reference port for later hardware validation.

The selected first milestone is a computer-run simulation of the ESP32 node. It has no application authentication, command freshness checks, HTTPS, MQTT authentication, or MQTT TLS. The model and example broker bind to loopback only. The simulator has not been run, and the ESP-IDF port has not been built or flashed; no measurements have been collected.

## First milestone: v0.1 software simulation

The local model in `simulator/` exposes a web page and REST API, accepts `ON`/`OFF` MQTT messages, and tracks a virtual LED. A branded Streamlit console controls the model and shows its MQTT state and command count. It preserves the command and status interface planned for the ESP32 node while avoiding hardware setup.

This is software-in-the-loop behavior simulation. It does not run ESP-IDF firmware or emulate ESP32 Wi-Fi, lwIP, GPIO timing, CPU, RAM, flash, or power. The later ESP-IDF port lives in `firmware/vulnerable/basic-node` and needs a real board plus ESP-IDF to validate.

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

Open `http://127.0.0.1:8501`. The minimal built-in web page remains at `http://127.0.0.1:8080`. The MQTT command topic is `spectra/device01/cmd`; the status topic is `spectra/device01/status`. The [simulator guide](simulator/README.md) has command-line examples.

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
