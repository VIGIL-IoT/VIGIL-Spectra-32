# Safety and Data Handling

This project includes controlled security tests. Run them only on devices and networks that we own or have explicit permission to test.

## Lab safety rules

1. Use a dedicated access point with no internet or other network uplink.
2. Configure one fixed ESP32 target IP and make traffic scripts fail closed if that target is missing or differs from the lab configuration.
3. Use bounded, low-rate scan traffic against the target only. The first reproduction does not require a denial-of-service flood.
4. Do not scan campus, conference, hotel, office, household, public Wi-Fi, or internet hosts.
5. Before using upstream scripts, inspect their target selection, rate settings, and subprocess calls. Never run an unreviewed command with elevated privileges.
6. Keep a physical reset/power-disconnect available during experiments. Start without relays or actuators; add an LED/sensor only after the packet-filter benchmark is stable.

## Data handling

- Keep Wi-Fi SSIDs/passwords, private IP/MAC addresses, serial numbers, and local machine identifiers in ignored local configuration files.
- Raw PCAPs and device logs remain local until reviewed for identifiers and checked against applicable dataset licenses.
- The MIT license in the T800 repository covers that repository's code; it does not automatically grant rights to redistribute AB-TRAP, MAWILab, or other third-party datasets.
- Prefer sanitized aggregate metrics and reproducible scripts in Git. Record each anonymization or filtering step.
- Do not commit raw data from unrelated networks. If non-lab traffic appears in a capture, quarantine it locally and remove it from any release bundle.
- Verify all third-party software and model licenses before copying files into SPECTRA-32.

## Scope boundary

The initial experiment is limited to controlled TCP port-scan traffic directed at the ESP32 test device. Replay, brute-force, Wi-Fi impersonation, BLE spoofing, OTA tampering, and flooding are separate future experiments and are not authorized by this protocol unless independently scoped to owned lab devices and documented here first.
