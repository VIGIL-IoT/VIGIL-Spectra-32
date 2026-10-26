# SPECTRA-32 Streamlit Scenario Catalog

**A VIGIL-IoT Project**  
Research note · 2026-10-26

This catalog maps common IoT security problem areas to experiments the SPECTRA-32 Streamlit console can represent safely. The console changes a session-local Python model. It does not connect to a broker, send packets, exercise a Wi-Fi or BLE radio, flash firmware, or drive an ESP32 pin.

## Evidence and scope

The threat categories use the **OWASP IoT Top 10 2018** as a taxonomy, not as a claim about the most prevalent threats in 2026. NISTIR 8259A supplies a device-capability lens: device identification, configuration, data protection, logical access to interfaces, software update, cybersecurity state awareness, and device security. These references help select experiment questions; they do not certify this simulator or prove a vulnerability in a commercial product.

The Streamlit model can demonstrate deterministic decisions and observable state changes: accepted or rejected commands, virtual GPIO state, counters, event records, selected security profile, and a highlighted device path. It cannot produce real latency, radio behavior, CPU/RAM/flash usage, packet confidentiality, broker ACL enforcement, or physical power measurements.

## Scenario candidates

| Threat class | Reference mapping | Safe in-app stimulus | Vulnerable-profile observation | Hardened-profile observation | Streamlit status |
| --- | --- | --- | --- | --- | --- |
| Command replay / stale command | NISTIR 8259A: logical access and device security; freshness is an experiment-specific control | Re-submit one already-seen sample command once | Command accepted again; virtual output changes | Duplicate nonce rejected | Implemented |
| Invalid authentication attempt | OWASP I1; NISTIR 8259A: logical access | Submit one invalid lab credential | Record the failed attempt; do not imply a password was guessed | Record the failed attempt | Implemented |
| MQTT without transport security | OWASP I7; NISTIR 8259A: data protection | Select the vulnerable profile's no-TLS policy | Show `No TLS · simulated`; no packet is observed | Show that the profile requires TLS; do not claim a TLS handshake occurred | Implemented as profile state |
| Bounded request burst | OWASP I2: insecure network services and availability | Apply one fixed 40-request sample to counters; do not loop or emit requests | Show the modeled rate without throttling | Show the configured sample requests rate-limited | Implemented; not a DoS test |
| Unsigned firmware candidate | OWASP I4; NISTIR 8259A: software update | Present a metadata-only candidate with no valid signature | Record that the candidate *would* be accepted; never write firmware | Reject the candidate in the model | Implemented |
| Development UART exposure | OWASP I2 / I10; NISTIR 8259A: logical access to interfaces | Select the UART/debug event | Mark the modeled debug interface exposed | Mark it restricted | Implemented; a proxy for interface posture, not physical probing |
| Default credential accepted | OWASP I1; NISTIR 8259A: logical access | Use one fixed lab-only default credential, with no guessing loop | Model one accepted command and output change | Reject the default credential | Recommended next addition |
| Unauthorized MQTT topic / control command | OWASP I3; NISTIR 8259A: logical access to interfaces | Submit one fixed unauthorized command to the virtual relay topic | Model a command accepted without the required ACL | Reject it under the profile's simulated topic policy | Recommended next addition |
| Out-of-range sensor value | OWASP I3 / I7; NISTIR 8259A: data protection and state awareness | Inject one documented synthetic reading outside the configured range | Show the raw sample as accepted and flagged | Reject or quarantine it while retaining the last valid sample | Recommended after a sensor-value model is defined |
| Firmware downgrade / rollback | OWASP I4; NISTIR 8259A: software update | Offer a metadata-only older version identifier | Model downgrade if anti-rollback is absent | Reject the older version | Recommended after version and anti-rollback state are explicit |
| Insecure default configuration | OWASP I9; NISTIR 8259A: device configuration | Toggle one named configuration setting, such as open debug or missing TLS policy | Show the exposed configuration | Show the hardened setting | Partly represented by profile selection; make each setting explicit before treating it as a separate experiment |
| Outdated component / supply-chain issue | OWASP I5 | Requires a real dependency inventory and a pinned advisory snapshot | No defensible outcome without component/version data | No defensible outcome without a patch policy | Defer; do not invent CVEs or severity |
| Privacy/data-retention issue | OWASP I6 | Requires a defined sample data field, access policy, and retention rule | No current personal-data model exists | No current deletion/export control exists | Defer until a data-handling model exists |
| Device lifecycle / monitoring gap | OWASP I8; NISTIR 8259A: cybersecurity state awareness | Could model a missing heartbeat or unsupported node after adding lifecycle state | Show missing alert or stale record | Show the modeled alert/response | Future; current sample counters are not persistent monitoring |
| Wi-Fi deauthentication, evil twin, BLE spoofing, radio jamming, real packet flood, or physical tampering | OWASP I2 / I10 and wider radio/physical threat models | Not a Streamlit-only experiment | No radio or hardware effect can be measured in a browser session | No device defense can be validated in a browser session | Out of scope for the Streamlit simulator; move only to an isolated, authorized lab with owned equipment |

## Recommended sequence

1. Keep the current six security scenarios as deterministic, inspectable state transitions, and retain normal traffic as a baseline.
2. Add the default-credential and unauthorized-command cases. They add clear vulnerable-versus-hardened outcomes without introducing network traffic.
3. Add synthetic sensor integrity only after defining a typed reading, valid range, retained-last-good behavior, and a visible result in the dashboard.
4. Add downgrade behavior only after the model distinguishes firmware version, signature validity, and rollback policy.
5. Leave BLE, Wi-Fi radio attacks, packet floods, and physical attacks for a separately scoped hardware-lab experiment.

## Measurement rules

For each in-app scenario, record the scenario label, profile, model decision, virtual output before/after, event timestamp, and the counters directly changed by the transition. Call these **simulated outcomes**. Do not report simulated counts as attack success rates from a real device, or infer latency, network throughput, energy, or firmware resource overhead from Streamlit.

For a later hardware experiment, freeze the board revision, firmware commit, broker configuration, network boundary, command format, and repeat count in a separate protocol. Keep vulnerable and hardened firmware distinct and collect physical metrics with appropriate instrumentation.

## References

- [OWASP Internet of Things project — IoT Top 10 2018](https://owasp.org/projects/internet-of-things)
- [NISTIR 8259A — IoT Device Cybersecurity Capability Core Baseline (PDF)](https://nvlpubs.nist.gov/nistpubs/ir/2020/NIST.IR.8259A.pdf)
- [NIST IoT Cybersecurity Capabilities Catalog](https://pages.nist.gov/IoT-Device-Cybersecurity-Requirement-Catalogs/)
- [NISTIR 8259 Series, including the 2026 Revision 1 manufacturer guidance](https://www.nist.gov/itl/applied-cybersecurity/nist-cybersecurity-iot-program/nistir-8259-series)
