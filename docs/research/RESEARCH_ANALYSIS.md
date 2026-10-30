# SPECTRA-32 Research Analysis

**Status:** desk research and implementation planning; the firmware compiles in ESP-IDF 6.1 CI but has not been flashed, and no security experiment has been run.
**Research checked:** 25 October 2026.

## Recommendation

Follow the intended sequence from the project brief:

1. Build the v0.1 computer-run behavioral model of the planned node: local web/REST control, MQTT, and a virtual LED. Do not add application security features yet; this is the controlled vulnerable baseline.
2. Use v0.2 for the MQTT command-replay experiment against the model, then add a separate hardened implementation and compare both.
3. Port the frozen behavior to an ESP32 in v0.3 and repeat only the checks that can be meaningfully compared on hardware. Treat paper reproduction as its own research track; do not describe an adaptation as a faithful reproduction.

For the replay track, **REPLIOT** is the closest peer-reviewed methodological reference we found. It is an IEEE PerCom 2024 paper with a public author artifact and data. Its testbed is designed around commercial devices, companion apps, an access point that captures local traffic, and device-specific trigger scripts. An SPECTRA MQTT test on one custom ESP32 is an adaptation of its replay-testing methodology, not a reproduction of the original device study.

For a strict hardware-paper reproduction, **T800** remains the strongest current candidate in this repository: it studies classic ESP32 packet filtering, and the authors provide code and an English reproduction manual. Its TCP port-scan question is separate from the MQTT replay experiment.

**DSEKP** is a technically close ESP32/MQTT session-key paper, but its arXiv version says the firmware and edge-server source are available from the authors on request. It publishes datasets and analysis materials, but that does not provide a complete public firmware reproduction path. Treat its protocol and reported security properties as claims to audit, not as a ready-made baseline.

None of these papers has been reproduced by SPECTRA-32.

## Replay paper: REPLIOT

Lazzaro et al., “Is Your Kettle Smarter Than a Hacker? A Scalable Tool for Assessing Replay Attack Vulnerabilities on Consumer IoT Devices,” IEEE PerCom 2024, DOI 10.1109/PerCom59722.2024.10494466.

The paper's method captures local request/response flows between a companion app and a device, replays captured requests, and checks device responses. The authors report using 41 commercial devices and release the tool and study data at the [author repository](https://github.com/SafeNetIoT/ReplayAttack). The repository reports an AGPL-3.0 license and requires an access point, a smartphone with Android Debug Bridge, local traffic capture, and device-specific trigger/screenshot setup.

**Fit:** strong for the replay threat model and how to structure controlled capture, replay, and outcome observation. It emphasizes local command replay rather than only cloud-facing threats.

**Limits for our setup:** its target population is commercial appliances with companion apps. It does not provide an ESP32 MQTT defense implementation, and its response classifier is not a substitute for a command-level acceptance metric. Reproducing the original 41-device study is outside our hardware scope.

**SPECTRA-32 plan:** use the paper as a methodological reference. For v0.2, define one modeled MQTT command, observe the virtual LED and status response, replay a previously valid command on loopback, and compare a fixed vulnerable model with a separate freshness/authentication defense. Repeat the procedure on the owned ESP32 only after the v0.3 hardware port. Call this an **adaptation/extension**, not an exact REPLIOT reproduction. Do not copy AGPL code into the project unless we intentionally accept and meet its license terms.

Sources: [published PerCom paper](https://doi.org/10.1109/PerCom59722.2024.10494466), [arXiv manuscript](https://arxiv.org/abs/2401.12184), and [authors' artifact](https://github.com/SafeNetIoT/ReplayAttack).

## Paper selection for strict reproduction

| Candidate | Fit | Public reproduction evidence | Decision |
|---|---|---|---|
| **REPLIOT**, IEEE PerCom (2024) | Directly studies local replay against IoT commands; commercial devices and app traffic, not ESP32 firmware | Public author tool/data repository, but original reproduction needs its device corpus, apps, access-point capture, and trigger setup | Best replay-method reference; adapt carefully for the single ESP32 lab target |
| **T800**, JISA (2024) | Direct classic-ESP32 hardware study, but evaluates TCP port-scan filtering rather than MQTT replay | Public MIT-licensed code and English hardware reproduction manual | Best strict ESP32 paper reproduction candidate; keep it separate from replay |
| **Gotham Testbed**, IEEE TDSC (2024) | Reproducible multi-device network-security testbed; emulated rather than ESP32 firmware | Public source repository and setup README; substantially heavier environment | Keep as testbed-design reference |
| **DSEKP**, arXiv (2025) | Directly related to ESP32/MQTT session keys and replay protection | The arXiv version describes public datasets, but says full firmware/server source is available on request; no public source repository was verified here | Do not make it the first code reproduction unless the source becomes available and its claims are independently reviewed |

Sources: [T800 article](https://doi.org/10.5753/jisa.2024.3835), [T800 code](https://github.com/c2dc/T800), [T800 manual](https://github.com/c2dc/T800/blob/main/manual/manual_en.md), [Gotham paper](https://doi.org/10.1109/TDSC.2023.3247166), [Gotham repository](https://github.com/xsaga/gotham-iot-testbed), [DSEKP preprint](https://arxiv.org/abs/2511.02924), [DSEKP experiment dataset](https://doi.org/10.21227/3vw8-3a13), and [DSEKP baseline dataset](https://doi.org/10.21227/rg5z-ge26).

## What T800 studies

T800 adds a packet-classification hook to the ESP-IDF lwIP IPv4/TCP ingress path. The ESP32 evaluates incoming packet-header features and either lets the packet continue through the stack or drops it. The paper's use case is TCP port scanning, not general firmware exploitation or application-layer security. The authors compare a no-filter baseline with Logistic Regression, a linear SVM, a depth-12 Decision Tree, and an MLP. Their reported system measures include CPU use, network throughput, task stack use, and power.

In the arXiv version, the authors describe training with malicious scan traffic from AB-TRAP and benign traffic from MAWILab. They report a 2×2 workload design: 8 or 16 Mbps of benign traffic, with scans absent or present; each experiment runs for 360 seconds and is repeated 30 times. The paper reports classifier F1 scores of 0.79 (Logistic Regression), 0.34 (SVM), 0.93 (Decision Tree), and 0.91 (MLP). These are **paper-reported reference values**, not SPECTRA-32 results or guaranteed reproduction targets. The authors' published article is the target citation; the arXiv manuscript is linked for accessible method details.

Sources: [published JISA article](https://doi.org/10.5753/jisa.2024.3835), [arXiv manuscript](https://arxiv.org/abs/2305.19214), [authors' code](https://github.com/c2dc/T800), and [English reproduction manual](https://github.com/c2dc/T800/blob/main/manual/manual_en.md).

## Why T800 is a separate track

T800 is not an MQTT replay defense, an API security study, or a general-purpose intrusion detector. The v0.1 node and v0.2 replay experiment answer different questions. If the project proceeds with T800, use its dedicated reproduction plan and a separate isolated toolchain; do not combine its results with replay outcomes.

DSEKP is a later protocol candidate. Its paper describes session keys, HMAC authentication, AES-GCM, and a physical ESP32/MQTT testbed. It reports datasets, but its arXiv text says the ESP32 firmware and Python edge server are available from the authors on request and calls for formal protocol verification. The paper's session-key and freshness claims need independent review before SPECTRA adopts or benchmarks that design.

## T800 research question and falsifiable claim

**RQ1.** Can we build and run the authors' T800 filter on the documented ESP32 platform and reproduce its basic packet-filtering behavior against a controlled TCP port-scan workload?

**RQ2.** Under matched benign traffic, how does T800 change scan classification, legitimate traffic delivery, CPU use, stack/heap use, throughput, and (if instrumentation is available) power relative to the unfiltered baseline?

**Working claim to test:** On a classic ESP32 with a pinned ESP-IDF/lwIP setup, T800 can reject the selected port-scan workload while preserving legitimate TCP traffic, with measurable resource costs that can be compared against an unfiltered baseline.

The claim is falsified or needs material qualification if the hook does not run reliably, the scan workload is not distinguished from benign traffic, legitimate traffic is dropped at an unacceptable rate, or the filter's overhead outweighs the resources saved. No novelty claim is made before completing the reproduction and reviewing related work more broadly.

## T800 scope boundary

The T800 study covers **ingress TCP/IP packet filtering for port-scan traffic**. T800 does not, by itself, demonstrate replay protection, BLE security, Wi-Fi evil-twin protection, OTA signature checks, web authentication, or MQTT authorization. Those are separate experiments with their own threat models and baselines.

## Reproduction risks to resolve before hardware runs

1. **The installer modifies the ESP-IDF checkout.** The authors' `install.sh` copies patched lwIP files into `$IDF_PATH`, including `ip4.c` and `ip4.h`. Never run it against a shared/default ESP-IDF installation. Use a dedicated checkout or container/VM, record its exact commit, and inspect the patch first.
2. **Toolchain age and board differences.** The repository documents Python 3.8, ESP-IDF, iperf v2.0.13, and Nmap 7.80; it identifies an ESP32 DevKit V1 / ESP32-WROOM-32 class board. Newer IDF releases, Arduino core, ESP32-S3, or other boards are deviations until verified.
3. **Narrow attack coverage.** The model is trained and evaluated for port scanning. It must not be described as a general IoT IDS or as detecting MQTT replay, BLE spoofing, or arbitrary DoS.
4. **Dataset and split audit.** Before reproducing training metrics, trace the authors' actual dataset files, preprocessing, salting/sampling, and train/test split in the repository. Record seeds and check for leakage. Do not tune on a test split.
5. **Energy instrumentation.** The manual's power setup uses an INA219 and a second board. Without equivalent instrumentation, report a partial replication and omit power claims rather than estimating it from unrelated measurements.
6. **Wireless and workload variance.** RF conditions, access point, board revision, host OS, and traffic-generator versions can shift results. Record these and report confidence intervals rather than expecting exact numbers from the paper.
7. **Upstream scripts are active tools.** Review the traffic-generation code before running it; constrain all scans to the dedicated lab target address.

## What would make this a useful contribution?

The first value is a transparent, independent reproduction with archived environment details and run-level evidence. A stronger follow-on contribution could test whether the filter generalizes to a scanner not used for training, measure false positives on benign services, or compare T800 with a simple allowlist rule. Those are extensions, not part of the faithful-reproduction claim. Freeze the baseline and metrics before trying extensions.

## Review limits

This was a targeted paper/artifact scan, not an exhaustive survey or formal security audit. REPLIOT is the closest replay-method reference; T800 is the cleanest strict ESP32 reproduction candidate among the reviewed papers. All attributed measurements are paper-reported values. SPECTRA-32 has not validated them.
