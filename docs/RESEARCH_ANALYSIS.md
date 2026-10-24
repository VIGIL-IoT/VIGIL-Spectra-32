# SPECTRA-32 Research Analysis

**Status:** desk research and experiment planning only; no code, attack traffic, or measurements have been run in this repository.  
**Research checked:** 24 October 2026.

## Recommendation

Use **T800** as the first paper to reproduce. It is a published ESP32 study, its authors provide a public implementation and English reproduction manual, and its method is narrow enough to implement and measure with an ESP32, a Linux host, and an isolated access point. It gives SPECTRA-32 a concrete first result instead of starting with a collection of unrelated attack demos.

The proposed first project is therefore:

> Reproduce the T800 ingress packet-filtering experiment on a classic ESP32-WROOM-32/DevKit V1, record any deviations from the authors' setup, and publish the code, configuration, run logs, and measurements needed to repeat our result.

This is a **replication plan**, not a claim that T800 has already been reproduced. A follow-on experiment may test generalization to a held-out scanner or another board, but that extension starts only after the reproduction target is frozen.

## What T800 studies

T800 adds a packet-classification hook to the ESP-IDF lwIP IPv4/TCP ingress path. The ESP32 evaluates incoming packet-header features and either lets the packet continue through the stack or drops it. The paper's use case is TCP port scanning, not general firmware exploitation or application-layer security. The authors compare a no-filter baseline with Logistic Regression, a linear SVM, a depth-12 Decision Tree, and an MLP. Their reported system measures include CPU use, network throughput, task stack use, and power.

In the arXiv version, the authors describe training with malicious scan traffic from AB-TRAP and benign traffic from MAWILab. They report a 2×2 workload design: 8 or 16 Mbps of benign traffic, with scans absent or present; each experiment runs for 360 seconds and is repeated 30 times. The paper reports classifier F1 scores of 0.79 (Logistic Regression), 0.34 (SVM), 0.93 (Decision Tree), and 0.91 (MLP). These are **paper-reported reference values**, not SPECTRA-32 results or guaranteed reproduction targets. The authors' published article is the target citation; the arXiv manuscript is linked for accessible method details.

Sources: [published JISA article](https://doi.org/10.5753/jisa.2024.3835), [arXiv manuscript](https://arxiv.org/abs/2305.19214), [authors' code](https://github.com/c2dc/T800), and [English reproduction manual](https://github.com/c2dc/T800/blob/main/manual/manual_en.md).

## Candidate paper comparison

| Candidate | Fit to SPECTRA-32 | Reproduction evidence | Decision |
|---|---|---|---|
| **T800**, JISA (2024) | Direct: physical ESP32, lwIP packet filtering, port-scan workload, resource measurements | Authors' public [MIT-licensed repository](https://github.com/c2dc/T800) includes models, collected experiment data, code, and an English manual. README documents Python 3.8, ESP-IDF, iperf v2.0.13, and Nmap 7.80. | **Select for the first reproduction.** Strongest match and clearest artifact trail. |
| **Gotham Testbed**, IEEE TDSC (2024) | Strong for future repeatable multi-device scenarios, but its published environment is an emulated network with GNS3/Docker rather than an ESP32 firmware experiment. | Public [source repository](https://github.com/xsaga/gotham-iot-testbed) and a detailed setup README. The full environment is substantially heavier than our first target. | Keep as testbed-design reference; do not make it the first hardware reproduction. |
| **DSEKP**, arXiv preprint (2025) | Directly related to ESP32/MQTT session keys and replay resistance, and closer to the earlier replay-attack idea. | The preprint describes an ESP32–Raspberry Pi 5 MQTT setup and public datasets, but says the firmware/server source will be provided on request; no public implementation was verified in this review. It also lists formal security verification as future work. | Do not select yet. Revisit only if code becomes available and its security claims are independently checked. |

Sources: [Gotham paper](https://doi.org/10.1109/TDSC.2023.3247166), [Gotham repository](https://github.com/xsaga/gotham-iot-testbed), and [DSEKP preprint](https://arxiv.org/abs/2511.02924).

### Why not start with DSEKP?

DSEKP is an interesting later candidate for an MQTT replay-defense module, but it is weaker as a first reproduction: the paper is a preprint, and its full text says the firmware and edge-server source are available from the authors on request. The paper's security table labels its symmetric HKDF construction as providing forward secrecy. **Our cryptographic assessment:** deriving a new key from a long-term secret plus public/fresh values can give key separation and session freshness, but without an ephemeral secret exchange it does not provide forward secrecy after compromise of the long-term secret. The authors themselves list formal protocol verification as future work. Treat its security claims as hypotheses to examine, not established guarantees.

## Research question and falsifiable claim

**RQ1.** Can we build and run the authors' T800 filter on the documented ESP32 platform and reproduce its basic packet-filtering behavior against a controlled TCP port-scan workload?

**RQ2.** Under matched benign traffic, how does T800 change scan classification, legitimate traffic delivery, CPU use, stack/heap use, throughput, and (if instrumentation is available) power relative to the unfiltered baseline?

**Working claim to test:** On a classic ESP32 with a pinned ESP-IDF/lwIP setup, T800 can reject the selected port-scan workload while preserving legitimate TCP traffic, with measurable resource costs that can be compared against an unfiltered baseline.

The claim is falsified or needs material qualification if the hook does not run reliably, the scan workload is not distinguished from benign traffic, legitimate traffic is dropped at an unacceptable rate, or the filter's overhead outweighs the resources saved. No novelty claim is made before completing the reproduction and reviewing related work more broadly.

## Scope boundary

The first study covers **ingress TCP/IP packet filtering for port-scan traffic**. T800 does not, by itself, demonstrate replay protection, BLE security, Wi-Fi evil-twin protection, OTA signature checks, web authentication, or MQTT authorization. Those ideas appeared in the initial project brainstorming, but mixing them into the first reproduction would make the claim and evaluation ambiguous. They can become separate, later experiments with their own threat models and baselines.

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

This was a targeted paper/artifact scan, not an exhaustive survey or formal security audit. T800 was selected because its published ESP32 scope and public author artifacts match this repository unusually well. All findings and results above attributed to the paper are the authors' reported claims; SPECTRA-32 has not yet validated them.
