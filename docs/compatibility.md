# Compatibility Matrix

This matrix distinguishes checked environments from the project's declared range. A CI build or mocked test is not a claim of physical-device compatibility.

| Area | Declared or configured target | Verified evidence | Not verified |
|---|---|---|---|
| Python runtime | CPython 3.12, 3.13, and 3.14; `pyproject.toml` excludes 3.15 and later | Locked install, tests, lint, compile, documentation checks, and dependency audit run in the Python quality CI matrix. Local audit used Python 3.14.7. | Other interpreters, Python 3.11 and earlier, and Python 3.15 and later |
| Local operating system | Windows development host and Ubuntu 24.04 CI | Local Python suite and browser checks ran on the Windows host. CI configuration targets Ubuntu 24.04. | macOS and other Linux distributions are not part of the recorded matrix. The exact Windows release is not recorded. |
| Streamlit dashboard | Local Streamlit session and hosted Python deployment | Local UI was inspected at desktop, tablet, and phone viewports. The app's model tests use Streamlit AppTest. | Browser USB access is not possible through the hosted app. This audit does not claim a current hosted deployment or Cloud-log review. |
| Python HTTP node | Loopback HTTP server, form-encoded LED state route | Unit tests exercise valid values, duplicate and invalid fields, request framing, content type, incomplete bodies, and unknown routes. | LAN or public deployment is intentionally unsupported and untested. |
| MQTT software model | Mosquitto local broker on loopback | Dedicated CI integration job installs Mosquitto and exercises command/status flow. | Local broker run is unavailable in the current development environment. No hardware MQTT path is claimed. |
| ESP-IDF firmware | ESP-IDF 6.1, target `esp32` | GitHub Actions compiles the vulnerable reference firmware for classic ESP32. | No firmware flash, serial monitor session, physical behavior, board-specific pinout, or model parity run is recorded. |
| Board illustration | Generic classic ESP32-WROOM-32 style reference | Source-backed metadata tests check strap warnings, module flash, reserved GPIO9, and model-only paths. | Exact board model, revision, USB bridge, onboard LED, and header routing remain unknown. It is not a wiring guide. |
| Browser layout and basic accessibility | Streamlit console in Chromium-based local browser | Local inspection at 1280 desktop plus Taste review at 768 and 390 CSS pixels found no horizontal overflow. Keyboard Tab reached the skip link and a visible heading focus ring. Dashboard navigation, board pins, and chart data expose accessible names or text. | Focus and names received a spot check only. This is not a WCAG conformance evaluation or cross-browser certification. |

The supported Python range is defined in `pyproject.toml` and fixed by `uv.lock`. The automated local entry point is:

```powershell
python -m uv run --locked --group dev python tools/verify.py
```

Firmware build verification is separate from the Python verification command. See [the firmware workflow](../.github/workflows/esp32-firmware.yml) and [limitations](limitations.md).
