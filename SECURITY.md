# Security policy

## Supported scope

There are no tagged releases or formal support branches. Security fixes should target the current `main` branch.

SPECTRA-32 is an embedded-security research project. Its desktop broker, Python node, and future firmware baseline intentionally lack some security controls. The dashboard's simulated Hardened profile is not a deployed defense. Do not use the unauthenticated node or firmware on an untrusted network.

## Reporting a vulnerability

Do not publish credentials, device identifiers, exploit details, or non-lab traffic in a public issue. If GitHub private vulnerability reporting is enabled for this repository, use the repository's **Security → Advisories → Report a vulnerability** flow. Otherwise contact the VIGIL-IoT maintainers through the contact method listed on the [organization profile](https://github.com/VIGIL-IoT) and include only the minimum detail needed to reproduce the issue safely.

Reports should identify the affected commit/path, configuration, impact, and a bounded reproduction on software or equipment you own or are authorized to test. Do not scan, stress, or exploit third-party devices or networks as part of a report.

## Current security boundaries

- Streamlit scenario controls update only per-session sample state.
- The optional desktop node and Mosquitto configuration are unauthenticated and loopback-only by default.
- The ESP-IDF source is an intentionally vulnerable reference implementation and has not been built or validated.
- USB chip identification is a user-triggered host-side ROM probe; it may reset a connected board but has no flash-write or erase step.
- No production security claim, certification, or hardware protection guarantee is made.

See [`docs/SAFETY_AND_DATA.md`](docs/SAFETY_AND_DATA.md) before running a lab experiment.
