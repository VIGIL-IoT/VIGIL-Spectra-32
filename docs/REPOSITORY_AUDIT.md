# Repository Engineering Audit

**Audit dates:** 2026-10-29 to 2026-10-30
**Baseline revision:** `c2e0aaa` (`Add MIT license`)
**Current classification:** prototype / v0.1 software behavior model
**Scope:** source, tests, documentation, firmware source, dependencies, workflows, license files, and repository governance. The locked Streamlit app returned HTTP 200; Python CI passed on 3.12, 3.13, and 3.14; the ESP-IDF 6.1 classic ESP32 build passed in CI; and the Python runtime SBOM artifact was downloaded and validated. No Pages deployment, firmware flash, or hardware experiment was performed.

## Repository Overview

SPECTRA-32 is the experimental embedded-security testbed of VIGIL-IoT. It combines a session-local Streamlit behavior model, a separate loopback Python HTTP/MQTT node, and an ESP-IDF classic ESP32 reference firmware path. Python CI and the firmware compile workflow pass; broker-backed MQTT flow and physical board behavior are not verified. The project is an application and research prototype, not a distributable Python library.

## Initial Condition

At the baseline revision, the repository already contained the Streamlit console, board illustration, deterministic scenario model, standalone Python node, Mosquitto configuration, ESP-IDF source, research notes, and an Archify workflow page. Nine existing tests passed on Python 3.14.7. The root MIT license had just been added. There was no package metadata, release, or Git tag.

The main gaps were incomplete and stale architecture documentation, no requirements baseline or end-to-end traceability, thin contributor/security governance, missing explicit pandas dependency, no dependency vulnerability audit in CI, dead dashboard modules, and a chip-identification path that could classify output even when esptool returned a failure code.

## Major Problems Found

- Documentation implied a dashboard-to-node REST connection that the current code does not implement.
- The Streamlit scenarios, standalone Python node, and ESP-IDF firmware had to be clearly separated to avoid implying live device telemetry or attacks.
- `pandas` was imported by the dashboard but was not declared in the application requirements.
- Chip classification needed to reject unsuccessful esptool invocations.
- Two unused dashboard modules duplicated older board/security model code.
- Research plans lacked one repository-level requirements-to-evidence matrix and explicit separation of simulated, measured, and paper-reported values.
- Existing Archify output embeds upstream code and a font; their license texts and notices were not shipped with the published site allowlist.
- No CI check covered Python tests, Markdown links, or dependency advisories.

## Architecture Findings

The repository has three distinct paths:

1. The Streamlit console keeps session-local state; scenarios do not emit packets or call a broker, node API, firmware, or physical GPIO.
2. The standalone Python node exposes local HTTP routes and optional MQTT behavior. The Streamlit app does not consume its state.
3. The ESP-IDF firmware is a separate vulnerable reference implementation; CI compiles it for classic `esp32`, but it has not been flashed or tested on a board.

The revised [architecture](architecture.md) documents these boundaries, component ownership, data flow, deployment environments, hardware discovery, and trust limits with Mermaid diagrams.

## Improvements Implemented

- Rewrote the README and architecture description around current code behavior and the VIGIL-IoT / SPECTRA-32 identity.
- Added project requirements, methodology, benchmarks, limitations, traceability, SDG alignment, and experiment-index documentation.
- Added three retrospective ADRs; each states that its rationale is inferred from current repository evidence.
- Added an empty-by-design experiment index so planned work cannot be mistaken for completed results.
- Corrected esptool failure handling and added tests for command failure, replay profile differences, and bounded event history.
- Added loopback HTTP route tests for initial state, valid and invalid forms, and unknown routes.
- Removed unreferenced legacy `simulator/dashboard/board.py` and `simulator/dashboard/security_model.py` modules.
- Declared pandas and refreshed Streamlit to 1.66.1. A dependency audit found 39 advisories against transitive Pillow 12.3.0; Streamlit 1.66.1 supports Pillow 13, so Pillow 13.0.0 is explicitly pinned. The follow-up `pip-audit` scan reported no known vulnerabilities.
- Added Python CI for Python 3.12 and 3.14, runtime and development dependency audits, correctness-focused Ruff checks, and documentation-link checking. Removed the short-lived Dependabot version-update schedule after its initial run opened duplicate pandas update PRs (#1 and #2); both PRs were closed, and dependency auditing remains active in CI.
- Replaced the split pip requirement files with `pyproject.toml` and a cross-platform, hash-bearing `uv.lock`. Runtime dependencies and development checks are now declared separately; the hosted Streamlit app does not install development tools.
- Pinned uv 0.13.6 and changed CI to use locked installs across Python 3.12, 3.13, and 3.14.
- Added an ESP-IDF 6.1 build workflow for classic `esp32`; CI passed and generated the checked-in component lock for ESP-IDF 6.1.0 and `espressif/mqtt` 1.1.0.
- Added a Python 3.14 CI step that exports CycloneDX 1.5 from the locked runtime dependencies, validates its format and contents, then uploads a 30-day artifact. Run `41094597806` passed; its downloaded artifact contains 51 runtime components and excludes the development tools.
- Refined the bounded session counter chart with an explicit zero-based scale, readable integer ticks, visible latest-sample points, and second-resolution time labels. A local visual review at 1280×720 confirmed both series and their axes are visible below the board; this remains software-model UI, not device telemetry.
- Aligned the Streamlit theme and board component with `docs/BRAND.md`; self-hosted DM Sans, Manrope, and DM Mono at a pinned upstream revision with local OFL texts and SHA-256 provenance.
- Added contribution, security, conduct, citation, changelog, issue-template, and pull-request-template files.
- Added Archify and JetBrains Mono third-party license texts and made them available through the workflow-page allowlist.
- Added `.gitignore` rules for captures, serial logs, and local generated Archify QA receipts.

## Files Added

- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/workflows/esp32-firmware.yml`
- `.github/workflows/python-quality.yml`
- `CHANGELOG.md`
- `CITATION.cff`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `THIRD_PARTY_NOTICES.md`
- `docs/REPOSITORY_AUDIT.md`
- `docs/benchmarks.md`
- `docs/decisions/ADR-001-software-model-boundary.md`
- `docs/decisions/ADR-002-session-local-scenarios.md`
- `docs/decisions/ADR-003-host-chip-identification.md`
- `docs/experiments/README.md`
- `docs/limitations.md`
- `docs/methodology.md`
- `docs/requirements.md`
- `docs/sdg-alignment.md`
- `docs/site/workflow/third-party-notices.html`
- `docs/traceability.md`
- `firmware/vulnerable/basic-node/dependencies.lock`
- `licenses/third-party/JetBrains-Mono-OFL.txt`
- `licenses/third-party/archify-MIT.txt`
- `pyproject.toml`
- `uv.lock`
- `tests/test_node_http.py`
- `tools/check_docs.py`

## Files Modified

- `.github/workflows/python-quality.yml` — configured CycloneDX runtime SBOM export, validation, and artifact upload
- `CHANGELOG.md`
- `docs/REPOSITORY_AUDIT.md`
- `docs/requirements.md`
- `docs/traceability.md`
- `.github/workflows/deploy-workflow-page.yml`
- `.gitignore`
- `README.md`
- `docs/ARCHITECTURE.md` → `docs/architecture.md`
- `docs/ROADMAP.md`
- `docs/SAFETY_AND_DATA.md`
- `docs/site/workflow/index.html`
- `services/hardware.py`
- `simulator/README.md`
- `tests/test_scenarios.py`

The two unused legacy dashboard modules listed above were removed.
The original `requirements.txt`, `requirements-dev.txt`, and `simulator/requirements.txt` manifests were later replaced by the single uv project and lock files.

## Testing Performed

- Baseline: 9 existing tests passed on Python 3.14.7 before edits.
- Final suite: 16 tests passed in 16.73 seconds in the clean environment on Python 3.14.7.
- Python compilation: `python -m compileall -q data services components simulator tests tools`.
- Documentation links: `python tools/check_docs.py`.
- Dependency resolution: clean temporary Python 3.14 virtual environment installed `simulator/requirements.txt`; `python -m pip check` reported no broken requirements.
- Runtime dependency audit: `pip-audit 2.10.1 -r requirements.txt` reported no known vulnerabilities after the Pillow update.
- Developer-tool dependency audit: configured in CI, but the local resolver timed out against PyPI while resolving the `requirements-dev.txt` scan; no local result is claimed.
- Lint: Ruff 0.17.3 with the CI rule set `E4,E7,E9,F` passed for application, test, and tooling sources.
- Streamlit 1.66.1 smoke: app started from the clean environment on a separate local port and returned HTTP 200.
- Configuration: GitHub Actions and issue-template YAML parsed successfully; git diff --check reported no whitespace errors.
- Secret scan: no high-confidence GitHub token, AWS access-key, private-key, or `client_secret` pattern matched tracked or untracked project files.

The Streamlit AppTest suite emits benign `missing ScriptRunContext` warnings in bare test mode. This did not fail the tests.

## Test Results

On Python 3.14.7, the clean-environment suite ran **16 tests: all passed in 16.73 seconds**. Compilation, focused Ruff lint, documentation-link checks, clean-environment dependency validation, runtime dependency audit, Streamlit HTTP smoke, workflow YAML parsing, and `git diff --check` also passed. The development-tool dependency audit could not be resolved locally because PyPI timed out. Local checks were performed on Python 3.14. The subsequent main-branch GitHub Actions run passed both Python 3.12 and Python 3.14 matrix jobs.

## Follow-up Verification: Locked Python Environment

- `uv lock --check` confirmed the checked-in lock is current and resolves 71 packages.
- A fresh temporary Python 3.14.7 environment installed all 70 runtime and development packages from the lock; `pip check` reported no broken requirements.
- A separate runtime-only sync installed 51 packages and confirmed that neither Ruff nor pip-audit is installed in the default app environment; Streamlit launched from it and returned HTTP 200.
- The existing suite passed again: **16 tests passed in 21.81 seconds**.
- Ruff, Python compilation, and documentation-link checks passed against the locked environment; the documentation checker verified 33 files.
- `pip-audit` reported **no known vulnerabilities** in the locked runtime and development environment. It emitted cache-deserialization warnings but completed successfully.
- `git diff --check` passed. The Python 3.12/3.13/3.14 GitHub Actions run passed.
- GitHub Actions [built the classic ESP32 firmware with ESP-IDF 6.1](https://github.com/VIGIL-IoT/VIGIL-Spectra-32/actions/runs/41031092858); the generated component lock contains ESP-IDF 6.1.0 and `espressif/mqtt` 1.1.0.
- Python quality run [41094597806](https://github.com/VIGIL-IoT/VIGIL-Spectra-32/actions/runs/41094597806) passed. The uploaded runtime SBOM was downloaded and parsed locally: CycloneDX 1.5, 51 runtime components, correct project metadata, and no Ruff or pip-audit components.

## Follow-up Verification: Session Counter Chart

- Updated the local chart to use an explicit zero-based integer scale, two separately colored counters, and latest-sample markers so a fresh or flat series remains visible. Time labels include seconds to distinguish samples recorded close together.
- Matched the chart's Vega-Lite schema to the bundled v6 renderer and set a finite x-axis domain, including a padded domain when the chart has only one timestamp.
- Local visual review at 1280×720 showed the chart and adjacent lower dashboard cards aligned without overlap. The chart represents only this Streamlit session.
- The 16-test suite, focused Ruff checks, Python compilation, documentation-link check, and `git diff --check` passed after this change; CI confirmation is recorded by the associated main-branch run.

## Follow-up Verification: Dashboard Brand Assets

- The local Streamlit app served all three bundled fonts with HTTP 200. Browser font checks passed for DM Sans, Manrope, and DM Mono; the board iframe also reported DM Sans loaded.
- Local browser review showed the updated mint/amber palette across the board, counter chart, and lower cards. The `static/` directory is app-local and contains only the three font files.
- Taste Skill lint reported 0 failures and 0 warnings. Responsive screenshots at 1440, 768, and 390 pixels confirmed the header no longer collides with navigation; the board fits the desktop/tablet canvas, and the lower cards align in the reviewed desktop layout.
- The visual inspector still reports compact text (46% below 13 px) and three font families. The small text is concentrated in schematic pin labels, chart axes, and metadata; the three families are explicitly required by `docs/BRAND.md`. It also reports that most dashboard panels are below the first screen, consistent with this scrollable console.
- NFR-08 is verified for the local UI and its static assets; hosted deployment rendering has not been independently observed in this audit.

## Security Findings

- GitHub reports that main has no branch protection rule. This is a repository setting, not evidence of a suspicious commit; no protection settings were changed during the audit.
- GitHub Secret Scanning is disabled for this repository. The local full-history scan found no common credential patterns, but platform secret scanning could not be verified.
- Desktop HTTP/MQTT examples are unauthenticated and must remain loopback-only. The future firmware baseline is deliberately vulnerable and must be used only in an isolated, owned lab.
- Host-side chip identification requires an explicit action and does not issue flash-write or erase commands; it may reset the selected board.
- The dashboard cannot access a user's USB device when hosted in Streamlit Community Cloud.
- No high-confidence hardcoded-secret pattern was found in the repository scan.
- The initial runtime dependency audit flagged Pillow 12.3.0. After updating Streamlit to 1.66.1 and explicitly pinning its compatible Pillow 13.0.0 release, `pip-audit` reported no known vulnerabilities in runtime requirements.
- CI is configured to scan both runtime and development requirements. The local development-tool scan was blocked by a PyPI timeout. The verified runtime SBOM artifact is retained for 30 days; a release-specific SBOM archive is not configured.

## Personal Path Audit

- Scanned working-tree files for absolute Windows user-profile paths and Unix home paths. The matches were confined to ignored local QA/cache outputs; 23 JSON reports now use a generic `<USERPROFILE>` placeholder, and 14 opaque Ruff cache entries have been normalized. A repeat byte-level scan of workspace files found no remaining absolute profile/home path strings.
- At audit start, the pre-existing 27-commit main history had no personal home-path matches. After the repository modernization was pushed, the full current main history was scanned for personal paths and common credential patterns; no matches were found, so no historical content rewrite is needed.
- A local Codex checkpoint tree is separate from the branch commit history and is not sent by the explicit branch push. The application-managed checkpoint is not part of the published repository.

## Dependency Findings

Runtime dependencies are pinned in `pyproject.toml`; development-only audit and lint tools are in the `dev` dependency group. `uv.lock` fixes transitive package versions and distribution hashes across supported platforms and Python 3.12–3.14. CI installs with `uv sync --locked`; Streamlit Community Cloud recognizes the root `uv.lock`. The Python 3.14 CI job exports and validates a CycloneDX 1.5 runtime SBOM from that lock. The firmware's `dependencies.lock` pins ESP-IDF 6.1.0 and `espressif/mqtt` 1.1.0 for target `esp32`.

The repository is not packaged as a Python library. Its `pyproject.toml` defines application dependencies, while `tool.uv.package = false` keeps uv from trying to build a wheel or source distribution.

## Documentation Improvements

The README now describes the working product and limitations, while the architecture, requirements, methodology, benchmarks, limitations, roadmap, safety, repository map, and traceability documents distinguish implementation from plans. The new audit and contributor documents explain how evidence, decisions, security reports, and future results should be maintained.

## Research Improvements

The repository now maps requirements to objectives, decisions, implementation, tests, evidence, and status. Experiment plans distinguish simulated behavior from future hardware measurements; SDG alignment is described as potential and indirect only. No research result, hardware result, performance measurement, or societal impact is claimed.

## Reproducibility Improvements

Local install and test commands use a pinned uv version and checked-in cross-platform lock; CI runs locked installs, dependency auditing, compile, documentation-link, and unit/UI checks on Python 3.12, 3.13, and 3.14. The Streamlit runtime excludes development tools. Python quality run `41094597806` generated, validated, and uploaded the runtime SBOM artifact for 30 days. The workflow page publishes a reviewed file allowlist with third-party notices. The Pages deployment workflow is manual-only and was not run.

## Traceability Status

The [traceability matrix](traceability.md) contains functional and nonfunctional requirements with bounded verification statuses. NFR-07 is verified by Python quality run `41094597806`; no requirement is marked as hardware-verified. MQTT broker integration, physical chip identification, model/firmware parity, and all security experiments remain unverified or untested.

## Remaining Limitations

- Mosquitto and a local ESP-IDF toolchain were unavailable; the firmware compile is verified only in the pinned GitHub Actions environment, and MQTT broker integration remains untested.
- No physical ESP32 or calibrated measurement setup was used.
- No attack/defense experiment has run; the Streamlit outcomes remain deterministic model behavior.
- The Python 3.12/3.13/3.14 matrix and ESP-IDF 6.1 build passed in GitHub Actions. Pages deployment was not run.
- The workflow-page workflow runs only through manual workflow dispatch; no page was deployed during this audit.

## Initial Maturity Score

| Dimension | Score | Evidence at baseline | Remaining gap at baseline |
|---|---:|---|---|
| Architecture & Modularity | 8/15 | Three real implementation paths and existing modular source | Incorrect dashboard/node coupling description; dead modules; incomplete system boundaries |
| Documentation | 9/15 | README, safety, roadmap, research notes | Missing formal requirements, methodology, traceability, dependency and limitations records |
| Code Quality | 9/15 | Existing Python app and model functions | Missing pandas dependency declaration; esptool failure result not checked; dead code |
| Testing | 6/15 | 9 tests passed at baseline | No node HTTP route tests or explicit checks for failure classification and replay distinction |
| Security | 6/10 | Loopback defaults and existing safety guidance | No dependency audit, threat boundary documentation, or third-party license notices |
| Reproducibility | 6/10 | Direct dependencies mostly pinned and manual setup available | No CI test matrix or complete dependency/build evidence |
| Open Source Governance | 5/10 | MIT license and README | Missing contributor, security, conduct, citation, and issue/PR templates |
| Research Rigor & Traceability | 6/10 | Existing research analysis and experiment ideas | No repository-level evidence matrix, explicit current baseline, or audit trail |
| **Total** | **55/100** |  |  |

## Final Maturity Score

| Dimension | Score | Evidence after changes | Remaining gap |
|---|---:|---|---|
| Architecture & Modularity | 12/15 | Three paths separated in architecture, diagrams, docs, and ADRs; unused duplicates removed | No hardware/model parity verification or modular package boundary |
| Documentation | 13/15 | Requirements, architecture, method, metrics, limitations, safety, roadmap, audit, and traceability | No published experiment results or firmware bring-up guide backed by hardware |
| Code Quality | 11/15 | Explicit dependencies, esptool failure handling, bounded state tests, dead code removed, Ruff correctness checks | No type checker or firmware static analysis configured; stylistic and broader opinionated lint rules remain disabled |
| Testing | 13/15 | 16 tests, loopback HTTP coverage, AppTest, clean locked-environment run; Python 3.12/3.13/3.14 CI and ESP-IDF 6.1 classic ESP32 build pass | MQTT integration and hardware-in-loop validation remain unverified |
| Security | 8/10 | Loopback boundaries, safe chip-ID behavior, no local history-scan matches, runtime and developer dependency audits pass in CI, and the runtime SBOM is validated and uploaded | Vulnerable firmware by design; main is unprotected; GitHub secret scanning is disabled; no physical validation |
| Reproducibility | 9/10 | Cross-platform hash-bearing Python lock, pinned uv, locked CI installs, ESP-IDF component lock, and passing pinned firmware build | No physical firmware flash/build evidence or board-specific configuration record |
| Open Source Governance | 8/10 | MIT license, third-party notices, contribution/security/conduct/citation docs, templates, changelog | No tagged release or main-branch protection rule |
| Research Rigor & Traceability | 7/10 | Requirements traceability, evidence labels, protocols, ADRs, benchmark plan, conservative SDG statement | No experiment has been run; protocols still require lab and statistical review |
| **Total** | **81/100** |  |  |

The updated score of **81/100**, from an initial 55/100, reflects better engineering controls and evidence handling, not a change in device security or experimental capability.

## Recommended Next Actions

1. Add a main-branch ruleset that blocks force-pushes and deletion and requires the Python quality checks to pass.
2. Enable GitHub Secret Scanning if available for this organization and repository.
3. Flash the built firmware on the selected classic ESP32 board and record board-specific behavior and differences.
4. Run the optional Python node with Mosquitto on loopback and add broker-backed integration tests.
5. Freeze EXP-01 protocol details, then collect authorized lab runs with commit/configuration provenance and raw evidence.
6. Add a release-specific SBOM archive when a tagged release process is introduced; include firmware components as well as Python runtime dependencies.
