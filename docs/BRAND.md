# VIGIL-IoT / SPECTRA-32 Brand and Interface Direction

## Project identity

- **Umbrella:** VIGIL-IoT — Vulnerability Intelligence & Guarding for IoT Layers
- **Project:** SPECTRA-32 — Security Platform for Embedded Cyber Threat Research & Analysis
- **Relationship:** SPECTRA-32 is the experimental attack-and-defense testbed of VIGIL-IoT.
- **Required project marker:** “A VIGIL-IoT Project”.
- **Research loop:** Build → Attack → Observe → Defend → Measure.

Keep claims specific to implemented and measured behavior. The Streamlit console is a session-local visualization; its Hardened profile is not firmware or hardware evidence.

## Visual direction

Use the existing SPECTRA-32 console direction: a restrained dark data terminal, crisp outlined panels, quiet dividers, a branded top bar, compact navigation, an interactive board schematic, and readable telemetry. Avoid skulls, weapon imagery, Matrix code, neon-green-on-black, glitch styling, and generic “hacker terminal” visuals.

### UI color tokens

| Token | Hex | Use |
|---|---|---|
| Ground | #0D1111 | Page background |
| Surface | #151A1A | Panels and device surfaces |
| Border | #2B3531 | Dividers and outlines |
| Primary text | #F2F4F1 | Main text and strong controls |
| Muted text | #A0AAA5 | Supporting text |
| Signal mint | #74DFC3 | Active state and positive status |
| Caution amber | #E8BD85 | Warnings and medium risk |
| Alert rose | #E98488 | High-risk state |

Use DM Sans for interface text, Manrope for titles, and DM Mono for compact telemetry. Status values must include text labels so color is never the only indicator.

## Voice

Be calm, direct, and research-oriented. Distinguish planned work, source code, hardware-verified behavior, and measured findings. Label the vulnerable baseline and lab-only setup plainly without turning the interface into an attack console.
