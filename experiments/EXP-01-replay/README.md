# EXP-01 — MQTT Command Replay

**Status:** design only. The v0.1 software model has not been run and no attack experiment has been performed.

## Research question

When a previously valid command is submitted again to the vulnerable node, does it apply again? Can a separate hardened implementation reject the stale command while continuing to accept legitimate commands, and what are the costs?

## Threat model and scope

- Target: the project's own node model, with an ESP32 implementation planned later.
- Current network scope: one computer, with the simulator and MQTT broker bound to loopback.
- Attacker capability in the software experiment: a local process can publish to the loopback broker, record or create one valid command payload, and submit the same payload later.
- In the future hardware replication, the test host can publish to the owned ESP32 through the dedicated isolated lab broker.
- The attacker does not modify the target firmware or extract the hardened variant's per-device secret.
- Scope: MQTT command-level replay. This does not claim raw 802.11 frame replay, TCP packet injection, or tests against third-party devices.
- The current output is a virtual LED. A physical test later uses a low-voltage LED only.

## Variants

### Vulnerable baseline

Use simulator/vulnerable/basic_node.py. It accepts plain ON/OFF payloads on spectra/device01/cmd with no application authentication or freshness check. The software model counts each accepted command, including a repeated command, and changes virtual LED state.

### Hardened implementation

Create the defense separately under simulator/hardened/EXP-01-replay. Before coding, select and document the command envelope, key provisioning, freshness policy, reboot behavior, and failure handling. Candidate freshness mechanisms are a monotonic sequence counter or a timestamp plus unique nonce. Authenticate the complete canonical command with a per-device MAC; transport encryption alone does not establish freshness.

Freeze the vulnerable baseline and use identical command semantics in both variants. Do not silently add anti-replay behavior to the baseline.

## Controlled procedure

1. Record the source commit, Python and Paho versions, Mosquitto version/configuration, loopback ports, and current virtual state.
2. Set the virtual LED to OFF and issue one legitimate ON command. Save the exact command envelope and application payload.
3. Issue a legitimate OFF command so a later stale ON has an observable effect.
4. Submit the saved ON command unchanged to the same model.
5. Record whether it was applied, the resulting virtual LED state, the MQTT status, and the command counter.
6. Repeat with the hardened model using a valid fresh command followed by the exact replay.
7. Retain failed, interrupted, and ambiguous runs. Do not discard runs to improve a result.

Use a small pilot to validate the procedure, then freeze the command format, primary metric, and repeat count before confirmatory collection. A candidate design is 30 independent fresh-command/replay pairs per variant.

## Outcomes

Primary:

- Replay success rate = stale replay attempts that change the virtual output divided by replay attempts delivered to the model.
- Legitimate command acceptance rate = valid fresh commands applied divided by valid fresh commands sent.

Secondary:

- Host-measured end-to-end command latency.
- MQTT payload bytes and published message count.
- Software-process memory and CPU, labeled as host-side only.
- Recovery behavior after restarting the model.

The simulator cannot produce ESP32 RAM/flash usage, Wi-Fi latency, GPIO timing, or power measurements. Repeat those metrics only after porting the experiment to hardware. Report per-run counts before aggregate statistics; include confidence intervals and effect sizes where the design supports them.

## Paper relationship

The closest reviewed work is Lazzaro et al., “Is Your Kettle Smarter Than a Hacker? A Scalable Tool for Assessing Replay Attack Vulnerabilities on Consumer IoT Devices,” IEEE PerCom 2024 ([paper](https://doi.org/10.1109/PerCom59722.2024.10494466), [arXiv version](https://arxiv.org/abs/2401.12184)). The authors publish [REPLIOT](https://github.com/SafeNetIoT/ReplayAttack), licensed AGPL-3.0, and study captured local app/device flows and replay outcomes across a commercial-device testbed.

SPECTRA-32 uses one custom MQTT model and adds a separate defense comparison. This experiment adapts the paper's controlled replay-testing idea; it is not an exact reproduction of the paper's tool, ML response classifier, device population, or reported accuracy. The research analysis tracks T800 separately as a reproducible ESP32 paper about TCP port-scan filtering.

## Run ledger

No runs yet.

| Run ID | Variant | Source commit | Trial | Fresh command accepted | Stale replay changed state | Latency | Status/deviation |
|---|---|---|---:|---|---|---:|---|
| — | — | — | — | — | — | — | No experiments run |
