# Repository Engineering Audit

**Audit dates:** 2026-10-29 to 2026-10-30
**Baseline revision:** `c2e0aaa` (`Add MIT license`)
**Current classification:** prototype / v0.1 software behavior model
**Scope:** source, tests, documentation, firmware source, dependencies, workflows, license files, and repository governance. The Streamlit app was also started locally and returned HTTP 200. No Pages deployment or hardware test was performed.

## Repository Overview

SPECTRA-32 is the experimental embedded-security testbed of VIGIL-IoT. It combines a session-local Streamlit behavior model, a separate loopback Python HTTP/MQTT node, and an ESP-IDF classic ESP32 reference firmware path. The firmware, broker-backed MQTT flow, and physical board behavior are not verified. The project is an application and research prototype, not a distributable Python library.

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
3. The ESP-IDF firmware is a separate vulnerable reference implementation that has not been built or tested on a board.

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
- Added Python CI for Python 3.12 and 3.14, a dependency audit, correctness-focused Ruff checks, documentation-link checking, and Dependabot updates.
- Pinned CI developer tools in `requirements-dev.txt` so security scanning and linting are reproducible.
- Added contribution, security, conduct, citation, changelog, issue-template, and pull-request-template files.
- Added Archify and JetBrains Mono third-party license texts and made them available through the workflow-page allowlist.
- Added `.gitignore` rules for captures, serial logs, and local generated Archify QA receipts.

## Files Added

- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/dependabot.yml`
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
- `licenses/third-party/JetBrains-Mono-OFL.txt`
- `licenses/third-party/archify-MIT.txt`
- `requirements-dev.txt`
- `tests/test_node_http.py`
- `tools/check_docs.py`

## Files Modified

- `.github/workflows/deploy-workflow-page.yml`
- `.gitignore`
- `README.md`
- `docs/ARCHITECTURE.md` → `docs/architecture.md`
- `docs/ROADMAP.md`
- `docs/SAFETY_AND_DATA.md`
- `docs/site/workflow/index.html`
- `services/hardware.py`
- `simulator/README.md`
- `simulator/requirements.txt`
- `tests/test_scenarios.py`

The two unused legacy dashboard modules listed above were removed.

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
- Configuration: GitHub Actions, Dependabot, and issue-template YAML parsed successfully; `git diff --check` reported no whitespace errors.
- Secret scan: no high-confidence GitHub token, AWS access-key, private-key, or `client_secret` pattern matched tracked or untracked project files.

The Streamlit AppTest suite emits benign `missing ScriptRunContext` warnings in bare test mode. This did not fail the tests.

## Test Results

On Python 3.14.7, the clean-environment suite ran **16 tests: all passed in 16.73 seconds**. Compilation, focused Ruff lint, documentation-link checks, clean-environment dependency validation, runtime dependency audit, Streamlit HTTP smoke, workflow YAML parsing, and `git diff --check` also passed. The development-tool dependency audit could not be resolved locally because PyPI timed out. Local checks cover Python 3.14 only; Python 3.12 remains delegated to the CI matrix and has not yet run on GitHub.

## Security Findings

- Desktop HTTP/MQTT examples are unauthenticated and must remain loopback-only. The future firmware baseline is deliberately vulnerable and must be used only in an isolated, owned lab.
- Host-side chip identification requires an explicit action and does not issue flash-write or erase commands; it may reset the selected board.
- The dashboard cannot access a user's USB device when hosted in Streamlit Community Cloud.
- No high-confidence hardcoded-secret pattern was found in the repository scan.
- The initial runtime dependency audit flagged Pillow 12.3.0. After updating Streamlit to 1.66.1 and explicitly pinning its compatible Pillow 13.0.0 release, `pip-audit` reported no known vulnerabilities in runtime requirements.
- CI is configured to scan both runtime and development requirements. The local development-tool scan was blocked by a PyPI timeout. There is still no SBOM artifact or scheduled release bill of materials.

## Personal Path Audit

- Scanned working-tree files for absolute Windows user-profile paths and Unix home paths. The matches were confined to ignored local QA/cache outputs; 23 JSON reports now use a generic `<USERPROFILE>` placeholder, and 14 opaque Ruff cache entries have been normalized. A repeat byte-level scan of workspace files found no remaining absolute profile/home path strings.
- Scanned all 27 commits reachable from `origin/main`, including their blob contents, for Windows profile and Unix home paths. No matches were found, so no historical commit rewrite is needed and the existing commit IDs remain intact.
- A local Codex checkpoint tree is separate from the branch commit history and is not sent by the explicit branch push. The application-managed checkpoint is not part of the published repository.

## Dependency Findings

Direct runtime requirements are pinned in `simulator/requirements.txt`, including pandas, Streamlit, and Pillow. The root `requirements.txt` delegates to that file. The Python support floor is 3.11; the CI matrix targets 3.12 and 3.14. Transitive Python dependencies are resolved by pip rather than a checked-in lockfile, and ESP-IDF component versions are not locked.

The repository is not packaged as a Python library: there is no `pyproject.toml`, build backend, wheel, or source distribution. This is intentional for the current Streamlit application.

## Documentation Improvements

The README now describes the working product and limitations, while the architecture, requirements, methodology, benchmarks, limitations, roadmap, safety, repository map, and traceability documents distinguish implementation from plans. The new audit and contributor documents explain how evidence, decisions, security reports, and future results should be maintained.

## Research Improvements

The repository now maps requirements to objectives, decisions, implementation, tests, evidence, and status. Experiment plans distinguish simulated behavior from future hardware measurements; SDG alignment is described as potential and indirect only. No research result, hardware result, performance measurement, or societal impact is claimed.

## Reproducibility Improvements

Local install and test commands are documented; direct runtime dependencies are pinned; CI runs compile, documentation-link, and unit/UI checks on Python 3.12 and 3.14; the workflow page publishes a reviewed file allowlist with third-party notices. Clean installation was verified locally on Python 3.14.7. GitHub-hosted CI and Pages were not triggered as part of this audit.

## Traceability Status

The [traceability matrix](traceability.md) contains functional and nonfunctional requirements with bounded verification statuses. No requirement is marked as hardware-verified. MQTT broker integration, ESP-IDF build, physical chip identification, and all security experiments remain unverified or untested.

## Remaining Limitations

- No Mosquitto executable or ESP-IDF toolchain was available for an MQTT integration run or firmware build.
- No physical ESP32 or calibrated measurement setup was used.
- No attack/defense experiment has run; the Streamlit outcomes remain deterministic model behavior.
- No transitive dependency lockfile exists.
- GitHub CI and Pages deployment were not run after these changes.
- The workflow-page workflow is configured to deploy on `main`; this audit did not publish a Pages update.

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
| Testing | 11/15 | 16 tests, loopback HTTP coverage, AppTest, clean-environment run | One local Python version; no MQTT, hardware-in-loop, or CI result yet |
| Security | 8/10 | Loopback boundaries, safe chip-ID behavior, no secret match, runtime dependency audit clean | Vulnerable firmware by design; dev-tool scan pending CI; no SBOM; no physical validation |
| Reproducibility | 8/10 | Pinned direct dependencies, clean Python 3.14 install, CI matrix, test and docs commands | No full transitive lock; no ESP-IDF component lock or verified build |
| Open Source Governance | 9/10 | MIT license, third-party notices, contribution/security/conduct/citation docs, templates, changelog | No tagged release or public CI result from this change set |
| Research Rigor & Traceability | 7/10 | Requirements traceability, evidence labels, protocols, ADRs, benchmark plan, conservative SDG statement | No experiment has been run; protocols still require lab and statistical review |
| **Total** | **79/100** |  |  |

The increase from **55/100 to 79/100** reflects better engineering controls and evidence handling, not a change in device security or experimental capability.

## Recommended Next Actions

1. Run the GitHub Actions test and dependency-audit matrix on Python 3.12 and 3.14.
2. Build the classic ESP32 firmware in a pinned ESP-IDF environment and record any board-specific differences.
3. Run the optional Python node with Mosquitto on loopback and add broker-backed integration tests.
4. Freeze EXP-01 protocol details, then collect authorized lab runs with commit/configuration provenance and raw evidence.
5. Add a transitive dependency lock and generate an SPDX or CycloneDX SBOM when preparing a distributable release artifact.
