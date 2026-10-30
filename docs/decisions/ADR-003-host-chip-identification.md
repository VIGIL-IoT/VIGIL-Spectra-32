# ADR-003: Identify chips through an explicit host-side esptool probe

## Status

Accepted (retrospective interpretation based on current repository evidence).

## Context

The app needs to distinguish a serial adapter from an Espressif chip. USB serial access belongs to the host process, not the browser. An esptool ROM probe can reset a board even when it does not write flash.

## Decision

Enumerate ports on the Python host, show the port choice, and run a bounded esptool `chip-id` operation only after a user clicks **Identify chip**. Use `--no-stub`, report classic ESP32 as supported, and report other Espressif targets as unsupported for the current milestone. Do not run chip identification automatically during refresh.

## Alternatives

- Infer board type from USB VID/PID alone.
- Run esptool continuously on every refresh.
- Use Web Serial from the browser.

## Rationale

Port descriptors identify USB bridges but do not reliably establish the connected SoC. An explicit ROM probe provides stronger chip evidence while keeping the reset operation visible to the user. Host-side discovery works locally but cannot see a user's attached board when the app runs in the cloud.

## Consequences and tradeoffs

- The board may reset when the user asks for identification.
- Some boards require BOOT/reset assistance, and the feature can fail if another serial tool holds the port.
- Unit tests cover classification and command construction only; physical identification remains unverified.
- The probe contains no flash erase/write command.

## Evidence

`services/hardware.py`, `simulator/dashboard/app.py`, `simulator/README.md`, and the hardware-related tests in `tests/test_scenarios.py`.
