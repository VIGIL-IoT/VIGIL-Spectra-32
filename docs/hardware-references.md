# ESP32 Board and Pin Reference

**Scope:** source notes for the representative board illustration and pin warnings. This document is not a wiring guide. The exact board model and revision owned by the project maintainer have not been recorded.

## Reference identity

The Streamlit illustration represents a classic ESP32-WROOM-32 style module on a generic development board. It is an explanatory reference, not a scale drawing, electrical schematic, or exact DevKitC pinout. Connector type, USB-to-UART bridge, header population, onboard LED, and flash variant depend on the board and module revision.

The SPI flash label belongs inside the ESP32 module boundary because the module contains its flash storage. Its drawn location is conceptual and does not specify package placement. GPIO6 through GPIO11 are normally used by the module flash interface. GPIO9 remains visible as a reserved reference pad in the drawing and must not be treated as a general output.

## Pin behavior relevant to the illustration

The classic ESP32 has strapping pins GPIO0, GPIO2, GPIO5, GPIO12/MTDI, and GPIO15/MTDO. Their reset levels can affect boot configuration. GPIO0 held low during reset selects the serial download boot mode. GPIO12/MTDI can affect the VDD_SDIO voltage selection. Confirm the target module and board documentation before attaching external circuitry.

GPIO34 through GPIO39 are input-only. The illustration includes GPIO36, GPIO39, GPIO34, and GPIO35. GPIO22 and GPIO23 are labels for the dashboard's sample sensor and relay paths only. No sensor or relay is connected, and the dashboard cannot drive either pin.

## Visual and implementation limits

- The board illustration is an interactive, code-authored SVG in `components/board_component/index.html`.
- Pin metadata and selection details come from `data/board_definition.py`.
- `BOOT`, GPIO2, GPIO5, GPIO12, and GPIO15 are marked for review because their strap behavior needs board-specific care.
- The map does not establish that GPIO2 has an onboard LED or that GPIO22/GPIO23 are routed to peripherals.
- USB / UART is deliberately generic. The illustration does not identify the user's connected board or enumerate its connector and bridge.
- No electrical limits, trace geometry, resistor values, or wiring claims are encoded by the drawing.

## Authoritative references

| Source | Revision / scope | Claim used |
|---|---|---|
| [Espressif ESP-IDF GPIO API reference](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html) | Classic ESP32 target documentation, accessed 2026-11-02 | Strapping pins, GPIO6-GPIO11 flash connection, and GPIO34-GPIO39 input-only behavior |
| [Espressif ESP32-DevKitC V4 user guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) | Specific DevKitC V4 board, accessed 2026-11-02 | Board revision and connector details belong to a specific hardware guide and cannot be generalized to this unidentified board |
| [Espressif esptool boot mode selection](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html) | Classic ESP32 serial boot behavior, accessed 2026-11-02 | GPIO0 reset behavior and the effect of strap levels during download-mode entry |
| [ESP32-WROOM-32E / ESP32-WROOM-32UE datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf) | Module variants, accessed 2026-11-02 | The WROOM module is the relevant packaging boundary; module capabilities and flash options vary by variant |

The references were inspected with Crawl4AI 0.9.5. The documentation describes multiple chips and board revisions. The illustration therefore marks the board family and reserved behaviors, while leaving exact connector, component placement, and wiring unclaimed.
