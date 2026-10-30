# Changelog

This project has no published version tags or release notes in the current repository history. Until the first tagged release, changes are grouped under **Unreleased**. This file records repository capabilities and project changes; it is not a run-results log.

## Unreleased

### Added

- Streamlit session model with selectable ESP32 DevKit-style board, scenario controls, counters, event log, and bounded session chart.
- Host-side USB serial discovery with explicit classic ESP32 chip identification.
- Separate Python virtual node with loopback HTTP and optional MQTT behavior.
- ESP-IDF classic ESP32 vulnerable reference implementation; its ESP-IDF 6.1 CI build passes, but it has not been flashed or verified on hardware.
- Replay and T800 research plans, safety boundaries, and an interactive Archify workflow page.
- MIT project license, third-party notices, tests, CI, contribution guidance, and repository traceability documentation.
- Cross-platform Python dependency lock, pinned ESP-IDF component lock, and a validated CycloneDX runtime SBOM artifact from Python 3.14 CI (30-day retention).

### Improved

- Made the session counter chart readable from a zero baseline, added latest-sample markers, and kept time labels distinct at short intervals.

### Limitations

- No security experiment, MQTT integration run, or physical-board validation is recorded. The CI SBOM artifact is retained for 30 days; no release-specific SBOM archive is configured.
- Dashboard scenario outcomes remain in-memory illustrations and are not device telemetry.
