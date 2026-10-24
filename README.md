# SPECTRA-32

A low-cost ESP32 security testbed for evaluating IoT vulnerabilities, attack-defense mechanisms, secure communication, and cyber-physical resilience.

## Project status

**Research planning.** No firmware, attacks, or measurements have been run in this repository yet. The first planned milestone is an independent reproduction of the T800 ESP32 packet-filtering study, followed by a clearly separated SPECTRA-32 extension.

## Start here

- [Research analysis and paper selection](docs/RESEARCH_ANALYSIS.md)
- [T800 reproduction plan](docs/T800_REPRODUCTION_PLAN.md)
- [Testbed architecture](docs/ARCHITECTURE.md)
- [Experiment protocol](docs/EXPERIMENT_PROTOCOL.md)
- [Safety and data handling](docs/SAFETY_AND_DATA.md)
- [Roadmap](docs/ROADMAP.md)

## First research target

**T800: Design and implementation of intelligent packet filtering in IoT microcontroller-based devices.** The paper evaluates an ESP32 packet filter at the lwIP ingress path, focusing on TCP port-scan traffic and system overhead. The authors publish the implementation and a reproduction manual. This is a bounded, reproducible starting point; it does not cover every attack family discussed in the initial project brainstorm.

- [Published article](https://doi.org/10.5753/jisa.2024.3835)
- [Authors' source repository](https://github.com/c2dc/T800)
- [Authors' reproduction manual](https://github.com/c2dc/T800/blob/main/manual/manual_en.md)

All experiments are planned for devices and networks we own or have permission to test. See the safety document before running any traffic-generation scripts.
