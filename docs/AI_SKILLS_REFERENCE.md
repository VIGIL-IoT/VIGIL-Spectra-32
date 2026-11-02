# AI Skills and Specialized Tools Reference

This registry distinguishes tools named by the repository engineering prompt from tools actually available or used for this SPECTRA-32 audit. Presence in the source prompt does not mean a skill ran. No personal installation paths or credentials are recorded.

| Skill or tool | Repository / source | Purpose and trigger | Availability and use here | Output and validation |
|---|---|---|---|---|
| Taste Skill | [leonxlnx/taste-skill](https://github.com/leonxlnx/taste-skill) | Frontend and dashboard visual review; use when changing a user-facing screen. | Local skill available and used for responsive visual inspection. No redesign was needed. | Existing Streamlit UI retained; desktop and narrow viewport screenshots inspected. Findings are recorded in `docs/REPOSITORY_AUDIT.md`. |
| Anatomy | [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy) | Isometric physical system explanation when spatial relationships materially help. | Local skill available and evaluated, not used. The exact board is unknown and the existing SVG board plus architecture flow already communicate the verified boundary without inventing physical placement. | No Anatomy artifact created. Revisit after exact board and lab apparatus are documented. |
| Diagram Design | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | Editorial architecture or relationship diagrams when they add information beyond Mermaid or an existing diagram. | Local skill available and evaluated, not invoked. Current Mermaid architecture and Archify workflow serve different existing purposes; a new diagram would be redundant. | No new diagram created. Current documentation links were checked by `tools/check_docs.py`. |
| ManimGX | [academa-labs/manimgx](https://github.com/academa-labs/manimgx), [documentation](https://manimgx.academa.ai/llms.txt) | Animation for concepts that materially change over time, such as signal propagation or algorithm steps. | Not installed. Skipped because this maintenance audit has no new temporal concept requiring animation. | No animation or generated video. |
| Crawl4AI | [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | Crawl official docs and repositories when external research can affect technical decisions. | Installed in the environment and used to inspect Espressif, esptool, and GitHub Actions primary sources. | Sources and decisions recorded in `docs/research-sources.md` and `docs/hardware-references.md`. |
| Archify | [tt-a1i/archify](https://github.com/tt-a1i/archify) | Render the existing repository workflow page from its checked-in candidate source. | Existing repository workflow and generated page retained. No renderer was run during this audit. | Existing deployment workflow is SHA-pinned and verifies generated output against the committed page. |
| README writing references | `adewale/good-readme`; `indubitably-ai/readme-writing`; `JayRHa/agent-skills` (`readme-generator`, `technical-writer`); `riekelt/technical-writer`; `Shpigford/readme`; `matt-riley/writing-and-editing` | README structure, technical prose, and editing. | These names appear in the master prompt, but exact repository URLs were not supplied. No specific remote skill was installed or invoked. | Existing README and docs were checked against the source code and repository link validation. Do not treat these specific skills as used. |
| GitHub profile README skill | `boffti/github-profile-readme` | Personal GitHub profile content. | Not applicable to this product repository. Exact URL was not supplied. | No profile README artifact. |
| KiCad Happy | [aklofas/kicad-happy](https://github.com/aklofas/kicad-happy) | KiCad design automation when schematics or boards are being edited. | Repository is referenced by the prompt; no KiCad files exist in this project, so it was not installed or used. | No PCB or schematic output. |
| AI PCB Layout | [ChengminLi/AI-PCB-layout](https://github.com/ChengminLi/AI-PCB-layout) | PCB placement/routing support when a PCB design is in scope. | Not applicable: no KiCad PCB file. | No layout output. |
| KiCad MCP Pro | [oaslananka/kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro) | MCP-based KiCad control for a live schematic or board design. | Not applicable: no KiCad file or KiCad session. | No MCP PCB actions. |
| KiStack | [American-Embedded/KiStack](https://github.com/American-Embedded/KiStack) | KiCad engineering workflow and validation. | Not applicable: this repository has no PCB source. | No hardware design output. |
| Circuit Skills | [punkfab/circuit-skills](https://github.com/punkfab/circuit-skills) | Circuit-oriented design and review skills. | Not applicable: no circuit schematic or PCB is present. | No circuit artifact. |
| Matplotlib, Plotly, R and ggplot2 | Tools named in the master prompt, without a single repository URL | Quantitative plots when the repository has validated data. | Not used. The current charts display bounded simulated session values, and this audit produced no research dataset. | No publication chart or benchmark figure created. |

## Token-efficient agent stack

The following projects were named in the companion token-efficient stack prompt. Their URLs are preserved from that prompt. Availability was checked in the current tool catalog, local skills, and command environment. None of these integrations was configured or installed.

| Project | Official repository | Purpose | Availability and use in this task | Fallback or validation |
|---|---|---|---|---|
| Ponytail | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Minimize implementation and avoid duplicate or unnecessary abstractions. | No tool, skill, or CLI exposed. Its anti-overengineering principles were applied manually. | Existing components were reused; no new runtime dependency or subsystem was added. |
| Lean Coding Agent | [JeremyFaubert/lean-coding-agent-skill](https://github.com/JeremyFaubert/lean-coding-agent-skill) | Retrieve repository context just in time and verify based on risk. | No tool or skill exposed. Its task-scoping principles were applied manually. | Bounded file reads and diffs were used. The final full verification ran because this was a repository-wide audit. |
| Serena | [oraios/serena](https://github.com/oraios/serena) | Semantic symbol and reference navigation. | No Serena MCP tool, skill, or CLI exposed. | Native `rg` and direct file reads were used for the small set of changed files. |
| skill-search | [sowhan/skill-search](https://github.com/sowhan/skill-search) | Retrieve relevant skills from a large skill library. | No skill-search tool or CLI exposed. | The native skill catalog was used; only Taste, Anatomy, Diagram Design, and Crawl4AI were relevant to the prior audit. |
| Token Optimizer MCP | [ooples/token-optimizer-mcp](https://github.com/ooples/token-optimizer-mcp) | Compress or externalize large tool results. | No Token Optimizer MCP tool exposed. | Output was bounded at the source and summarized; the full audit results were retained where needed. |

No upstream code or skill instructions were copied into SPECTRA-32. Recheck availability only when a future environment exposes these integrations or when one can materially improve a task.

## Activation rule

Use a specialized tool only when it can produce a source-grounded improvement. Record the exact repository, invocation, generated files, and validation when one is used. Do not add an empty PCB project, animation, or duplicate diagram to satisfy a checklist.
