# Dashboard Typography Assets

The Streamlit dashboard uses locally bundled fonts so the hosted app and local app render consistently without requesting fonts from a third-party service.

| Use | Bundled file | Official source at pinned revision | SHA-256 | License |
|---|---|---|---|---|
| Interface text | `simulator/dashboard/static/fonts/DM-Sans-Variable.ttf` | [`ofl/dmsans/DMSans[opsz,wght].ttf`](https://github.com/google/fonts/blob/6c1dbe27dcf7d817d4b62cec033ba77fa8e2a5ec/ofl/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf) | `8cd08d97e89c24d0aa92edd2f0f4c8ee6195eee9b7c9f154865a58b02f0c1c0d` | [`DM-Sans-OFL.txt`](../licenses/third-party/DM-Sans-OFL.txt) |
| Headings | `simulator/dashboard/static/fonts/Manrope-Variable.ttf` | [`ofl/manrope/Manrope[wght].ttf`](https://github.com/google/fonts/blob/6c1dbe27dcf7d817d4b62cec033ba77fa8e2a5ec/ofl/manrope/Manrope%5Bwght%5D.ttf) | `3ae11c49db0455a3cc33e37d380f20fdb8c7f8b41dc07625c177e3d87a9d6ae6` | [`Manrope-OFL.txt`](../licenses/third-party/Manrope-OFL.txt) |
| Compact telemetry | `simulator/dashboard/static/fonts/DM-Mono-Regular.ttf` | [`ofl/dmmono/DMMono-Regular.ttf`](https://github.com/google/fonts/blob/6c1dbe27dcf7d817d4b62cec033ba77fa8e2a5ec/ofl/dmmono/DMMono-Regular.ttf) | `55b4c98f123daebb3ed27947ba47b2af00554fc6284d639a540bcef5e6258ad2` | [`DM-Mono-OFL.txt`](../licenses/third-party/DM-Mono-OFL.txt) |

All three source files are from [`google/fonts`](https://github.com/google/fonts) revision `6c1dbe27dcf7d817d4b62cec033ba77fa8e2a5ec`. The dashboard references them through Streamlit static serving and `theme.fontFaces`; the board iframe loads its interface font from the same local static path. `THIRD_PARTY_NOTICES.md` records the redistribution and license relationship.
