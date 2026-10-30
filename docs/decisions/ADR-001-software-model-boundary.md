# ADR-001: Keep the software behavior model separate from firmware

## Status

Accepted (retrospective interpretation based on current repository evidence).

## Context

The repository contains a Python virtual node, a Streamlit session model, and an ESP-IDF reference implementation. They currently have different state owners and interfaces. The Streamlit security scenarios do not call the node API or firmware.

## Decision

Keep the host-side behavior model, dashboard scenarios, and ESP-IDF firmware as separate implementation paths. Label results by their source and validation level. Do not describe host simulation as ESP32 emulation or a hardware result.

## Alternatives

- Connect the dashboard directly to the local node and call the integrated view a device console.
- Make Streamlit controls directly operate physical GPIO.
- Keep all behavior in a single shared state service.

## Rationale

The current split preserves the useful software model while avoiding an implicit control channel. It also makes later parity experiments explicit and prevents the dashboard's illustrative profile from being mistaken for a device defense.

## Consequences and tradeoffs

- The dashboard and local node can show different states; users must start the optional node separately.
- Hardware parity requires an explicit protocol and run record.
- The separate paths add some duplicated state/behavior that may be reconciled later if an authenticated, testable interface is designed.

## Evidence

`simulator/dashboard/app.py`, `services/simulator.py`, `simulator/vulnerable/basic_node.py`, and `firmware/vulnerable/basic-node/main/app_main.c`.
