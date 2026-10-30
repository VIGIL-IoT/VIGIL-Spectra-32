# Contributing to SPECTRA-32

Thank you for helping improve the VIGIL-IoT embedded-security research testbed. Keep changes evidence-based, scoped, and safe to reproduce.

## Development setup

Use Python 3.11 or newer. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

Run the checks before opening a pull request:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q data services components simulator tests tools
python tools/check_docs.py
ruff check --select E4,E7,E9,F data services components simulator tests tools
pip-audit -r requirements.txt
pip-audit -r requirements-dev.txt
```

The Streamlit tests use `AppTest`; the node HTTP tests bind to loopback and use a fake MQTT link. Neither suite requires a physical ESP32 or broker.

## Change expectations

- Describe whether behavior is implemented, modeled, experimental, or planned. Do not describe session values as device telemetry.
- Preserve the boundary between dashboard scenarios, the standalone node service, and firmware unless a reviewed design adds an explicit interface.
- For security changes, update the threat model, safety notes, traceability row, and tests. Keep offensive validation limited to project-owned or explicitly authorized lab targets.
- For firmware changes, identify the exact board/target, toolchain, configuration, and test status. Never claim hardware validation without run evidence.
- Do not commit secrets, local credentials, raw packet captures, unredacted serial logs, personal data, or device identifiers. Sanitize and document any released data.
- Check licenses before copying code, paper artifacts, fonts, datasets, or models. Preserve third-party notices.
- Add or update a requirement and a verification source in `docs/traceability.md` for meaningful behavior changes.
- Keep experiment failures and deviations; do not fabricate measurements or drop failed runs without an explanation.

## Pull requests

Use the pull request template. Include the motivation, scope, test output, documentation changes, and whether the change was exercised against simulation, a broker, or hardware. Keep unrelated UI or repository changes in separate pull requests.
