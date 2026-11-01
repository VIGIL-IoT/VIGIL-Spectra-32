# Changelog

This file records versioned project changes and verification scope. It is not a research-results log. Released source snapshots and assets are available from [GitHub Releases](https://github.com/VIGIL-IoT/VIGIL-Spectra-32/releases).

## [0.2.0] - 2026-11-01

### Added

- Loopback Mosquitto integration coverage for the standalone Python node's MQTT command and status flow, including rejection of invalid commands.
- A release process that pairs each release tag with a verified runtime SBOM, checksum, and source manifest.

### Improved

- Readable zero-based session-counter chart with visible latest samples and distinct time labels.
- VIGIL-IoT dashboard colors and locally bundled, licensed typefaces.

### Verification

- Exact-tag Python quality and MQTT integration passed in [run 41323154657](https://github.com/VIGIL-IoT/VIGIL-Spectra-32/actions/runs/41323154657); the ESP-IDF build passed in [run 41323154363](https://github.com/VIGIL-IoT/VIGIL-Spectra-32/actions/runs/41323154363). The release includes a version-matched SBOM and provenance manifest.

### Limitations

- No physical-board validation, hardware-in-loop test, or security experiment is included. The Streamlit scenarios remain a session-local software model.

## [0.1.0] - 2026-11-01

### Added

- Initial VIGIL-IoT / SPECTRA-32 research prototype: Streamlit behavior model, representative ESP32 DevKit board, scenario controls, host-side chip identification, separate loopback HTTP/MQTT node, and classic ESP32 reference firmware.
- Research protocols, safety and limitations guidance, architecture and traceability documentation, and CI for Python quality and ESP-IDF builds.
- CycloneDX 1.5 runtime SBOM artifact generation and validation in Python 3.14 CI.

### Verification

- Exact-tag Python quality run [41323154451](https://github.com/VIGIL-IoT/VIGIL-Spectra-32/actions/runs/41323154451) and ESP-IDF firmware build [41323154494](https://github.com/VIGIL-IoT/VIGIL-Spectra-32/actions/runs/41323154494) passed before publication. The release includes a version-matched runtime SBOM and provenance manifest.

### Limitations

- The dashboard does not drive the separate node or physical firmware. No physical-board test, attack/defense experiment, or measured result is included.
