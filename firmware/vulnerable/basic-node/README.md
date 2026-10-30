# Future ESP32 hardware port: vulnerable basic node

This ESP-IDF implementation is a future hardware port of the computer-run node model. It is not the current v0.1 milestone. It compiles in the pinned ESP-IDF 6.1 GitHub Actions workflow, but has not been flashed or verified on a physical board. It is the intentionally unprotected SPECTRA-32 baseline for later hardware work. It connects as a station to the configured isolated WPA2 lab network, serves a local web control page and REST endpoints, controls one LED GPIO, and uses a local MQTT broker.

## Endpoints and topics

| Interface | Path/topic | Behavior |
|---|---|---|
| HTTP | / | Minimal device control page |
| HTTP GET | /api/state | Returns LED and MQTT connection state |
| HTTP POST | /api/led | Accepts form value state=on or state=off |
| MQTT subscribe | spectra/device01/cmd | Accepts ON or OFF |
| MQTT publish | spectra/device01/status | Publishes current LED state |

The firmware does not implement application authentication, command freshness, HTTPS, MQTT credentials, or MQTT TLS. Use it only on an isolated lab network. The GPIO default is 4; confirm the exact board pinout before wiring an external LED and series resistor.

## Build

For a future hardware run, use ESP-IDF 6.1 with the classic ESP32 target. From an ESP-IDF terminal, enter this directory, run `idf.py set-target esp32`, then `idf.py menuconfig`. Configure the lab Wi-Fi credentials, local broker URI, and LED GPIO under SPECTRA-32 future ESP32 port. The checked-in `dependencies.lock` pins ESP-IDF 6.1.0 and `espressif/mqtt` 1.1.0. Build and flash only on the documented isolated lab setup. The [ESP32 firmware workflow](../../../.github/workflows/esp32-firmware.yml) performs a compile-only CI check; it does not flash hardware.

The MQTT component constraint is declared in `main/idf_component.yml`; the exact component resolution is recorded in `dependencies.lock`. Local `sdkconfig` and generated build files are ignored by Git.

Source/API references: [ESP-IDF Wi-Fi](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/network/esp_wifi.html), [ESP-IDF HTTP Server](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/protocols/esp_http_server.html), [GPIO](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html), and [ESP-MQTT](https://docs.espressif.com/projects/esp-mqtt/en/latest/esp32/).
