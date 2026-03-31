# Project Research Summary

**Project:** GSD-Docs Industrial — v3.0 Docs Engine Rearchitecture
**Domain:** Industrial FDS/SDS generation engine — LLM provider abstraction, flexible decomposition structure, engine visibility
**Researched:** 2026-03-31
**Confidence:** HIGH

## Executive Summary

GSD-Docs v3.0 is a targeted rearchitecture of an existing, shipping system. The v2.0 stack (FastAPI, React 19, SQLite, Claude Code CLI) remains intact; v3.0 adds three independent pillars on top of it: (1) flexible FDS decomposition that replaces hardcoded ISA-88 EM-first scaffolding with system-first discovery, (2) LLM provider abstraction via LiteLLM so projects can route to Claude, GPT-4o, or local Ollama models, and (3) a read-only docs engine visibility layer in the GUI. The recommended approach is a thin-addition strategy — no existing architecture is replaced, each pillar adds to the current system with well-defined integration points. The pillars have minimal cross-dependencies and can be developed largely in parallel, converging at a shared PROJECT.md schema contract defined before any pillar work begins.

The primary technical risks are on the LLM abstraction pillar. A supply chain compromise of LiteLLM 1.82.7/1.82.8 was confirmed March 24, 2026 — version 1.83.0 (released March 31, 2026) is clean and must be pinned explicitly. Beyond the dependency risk, multi-provider support introduces the prompt portability trap: the temptation to normalize prompts across providers produces lowest-common-denominator output, which is unacceptable for standards-adjacent industrial documents. Provider-specific prompt variants (Claude, GPT, local) are not optional — they are load-bearing for output quality. Context window enforcement is equally non-negotiable before any local model is tested in production.

The flexible structure pillar's main risk is scope confusion: "system-first discovery" applies to the discovery conversation and ROADMAP scaffolding logic only — it does not mean stripping the 194-file engine of its ISA-88 and PackML domain knowledge. The `section-equipment-module.md` template is locked for this milestone. New section types (functional-unit, process-step) are additions alongside it, not replacements. The visibility pillar is straightforwardly additive and carries the lowest risk, provided it remains strictly read-only at both UI and API layers.

## Key Findings

### Recommended Stack

The existing stack requires three additions: `litellm==1.83.0` (pinned, not open-ended) with `anthropic>=0.86.0` and `openai>=2.30.0` as explicit locked companions for the LLM abstraction pillar; `GitPython>=3.1.46` for git-based template change history in the engine visibility service; and `@monaco-editor/react@^4.7.0` plus `react-diff-viewer-continued@^4.2.0` for the frontend engine viewer. No new configuration library, no ORM changes, no state management changes. The flexible FDS structure pillar requires zero new dependencies — it is entirely a data model and prompt logic change in the `gsd-docs-industrial/` directory.

**Core new technologies:**
- `litellm==1.83.0`: Unified LLM provider interface — single `completion()` call routes to Claude, GPT-4o, or Ollama. Industry standard for multi-provider abstraction. Pin to this exact version (supply chain incident affected 1.82.7/1.82.8).
- `GitPython>=3.1.46`: Read git commit history on `gsd-docs-industrial/` — powers the changelog endpoint in the engine visibility service. Typed objects vs fragile subprocess parsing.
- `@monaco-editor/react@^4.7.0`: Read-only VS Code-quality viewer for template/prompt raw source — v4.7.0 explicitly added React 19 peer dep.
- `react-diff-viewer-continued@^4.2.0`: Side-by-side diff view for template version history — actively maintained fork of abandoned `react-diff-viewer`. React 19 compat unconfirmed; verify with `npm ls react` after install.
- `ollama>=0.6.1` (optional): Only needed if the frontend model picker must list available local models via `ollama.list()`. LiteLLM's `ollama/` prefix handles generation without this SDK.

### Expected Features

**Must have for v3.0 (P1 table stakes):**
- System-first discovery prompt in `new-fds` — ask "describe your system" before decomposition model selection
- Decomposition model stored in PROJECT.md — enables all downstream commands to behave correctly
- Structure-aware ROADMAP generation for `isa88_em` and `functional` models — the two most common cases
- LiteLLM abstraction wrapper — single function replacing direct Anthropic SDK calls across all commands
- Claude + OpenAI + Ollama provider support — covers all three deployment scenarios (cost, IP-sensitive, fallback)
- Template browser in GUI (read-only) — minimal viable engine visibility
- Engine version displayed in GUI header and export document frontmatter

**Should have after v3.0 core validates (P2):**
- `template_ref` / `prompt_ref` in PLAN.md — section-level traceability to templates used
- Fallback chain configuration — resilience when cloud provider is down
- Changelog / diff viewer for engine updates — git history surfaced in GUI
- Functional and process-flow section templates — needed once first non-EM project runs
- Verification criteria browser — answers "what exactly was checked?"

**Defer to v4+ (P3):**
- Hybrid decomposition model — designing for hypothetical hybrid is premature
- Structure evolution / late promotion (functional to ISA-88 migration)
- Cost / token logging (USAGE.md approach)
- Template health indicators

**Explicit anti-features (never build):**
- In-GUI template editing — file-backed SSOT must remain git-managed, not GUI-modified
- Automatic decomposition model detection from description — LLM classification of decomposition model is unreliable; human confirms before proceeding
- LLM orchestration in the FastAPI backend — AI operations stay in the CLI per the v2.0 cockpit architecture decision

### Architecture Approach

The three pillars map to three independent work areas: Pillar 1 (flexible structure) lives entirely in `~/.claude/gsd-docs-industrial/`; Pillar 2 (LLM abstraction) is a thin config-driven shim in the CLI agent files with no new FastAPI services; Pillar 3 (engine visibility) is purely additive to the GUI — a new `engine.py` FastAPI router, a new `engine_service.py` service, and a new `frontend/src/features/engine/` feature directory. No existing routes, services, or components are modified by Pillar 3.

**Major new components:**
1. `decomposition-models.json` — registry mapping model IDs to templates, phase structures, and trigger heuristics. The single source of truth that `new-fds.md` and `plan-phase.md` query.
2. `provider-format.md` + conditional prompt logic in `doc-writer.md`/`doc-verifier.md` — config-driven prompt formatting without any new Python service.
3. `backend/app/api/engine.py` + `backend/app/services/engine_service.py` — read-only filesystem walker with git log integration for template/prompt inspection.
4. `frontend/src/features/engine/` — EngineExplorer, TemplateViewer, ChangeLog React components consuming the new API.

**Key patterns:**
- Decomposition model and project type are independent dimensions — project type (A/B/C/D) governs scope and rigor; decomposition model governs structural template selection. Both live in PROJECT.md.
- Engine service reads files directly from filesystem (never caches in SQLite) — templates are already version-controlled in git; a DB copy would create a second truth that drifts.
- Provider abstraction belongs in CLI agent files, not FastAPI — preserves the cockpit architecture decision and CLI compatibility.

### Critical Pitfalls

1. **Stripping EM domain knowledge during "flexible structure" work** — The change is in discovery order and ROADMAP scaffolding, NOT in section template content. Lock `section-equipment-module.md` as read-only for this milestone. New section types are additions alongside EM, not replacements of it.

2. **Normalizing prompts across providers destroys output quality** — Prompt portability does not exist. Provider-specific prompt variants are required for each workflow step. Use a layered approach: `prompts/{section-type}/base.md` (shared domain requirements) + `prompts/{section-type}/{provider}.md` (instruction style overlay). An EM section generating 12 interlocks on Claude generating 4 on a local model is a document quality failure, not an acceptable tradeoff.

3. **Context window differences silently truncating SPECIFICATION.md** — Claude handles 200K tokens; GPT-4o clips at 128K; local 8B models have 8K to 32K effective context. Context budget enforcement must be implemented before any local model goes near a real project. Silent truncation produces generic output that passes API calls but fails the document.

4. **Incompatible PROJECT.md schemas from parallel pillar development** — All three pillars add fields to PROJECT.md. Define the full v3.0 schema contract at milestone kickoff (`decomposition_model`, `llm_provider`, `llm_context_budget`, `engine_version`) and treat it as an integration contract no pillar may violate without a schema revision.

5. **Visibility layer enabling template edits, corrupting the SSOT** — Read-only must be enforced at the API layer (not just the UI). The engine viewer must return 403 on any write attempt. "Disabled by default" edit controls are not acceptable — the constraint is architectural.

## Implications for Roadmap

Based on the combined research, the architecture's build order recommendation (ARCHITECTURE.md) and the pitfall-to-phase mapping (PITFALLS.md) converge on the following phase structure.

### Phase 1: Shared Schema Contract + Foundation
**Rationale:** The single highest-risk integration point is incompatible PROJECT.md schemas across three parallel pillars. Define this contract first, before any pillar code is written. This is also the natural moment to define the decomposition model registry and canonical ROADMAP heading format — both are zero-dependency schema definitions that everything else references.
**Delivers:** v3.0 PROJECT.md schema, `decomposition-models.json` registry, ROADMAP heading format spec, `section-functional-unit.md` and `section-process-step.md` template stubs
**Addresses:** System-first discovery foundation, provider config schema
**Avoids:** Pitfall 14 (incompatible schemas), Pitfall 3 (undetermined ROADMAP at project start), Pitfall 2 (broken wave assignments from heading format drift)

### Phase 2: LLM Provider Abstraction
**Rationale:** Must be built before the flexible structure workflows are modified — commands cannot be updated to use system-first discovery until the provider abstraction wrapper exists and is tested. Also has a hard dependency on LiteLLM 1.83.0 (clean supply chain) being pinned correctly.
**Delivers:** `provider-format.md`, updated `doc-writer.md` and `doc-verifier.md` with provider-conditional prompt construction, context budget enforcement, quality disclosure in provider selection
**Uses:** `litellm==1.83.0`, `anthropic>=0.86.0`, `openai>=2.30.0`
**Implements:** Thin provider shim — 4 pieces: config in PROJECT.md, factory, prompt variant selection, context budget enforcement. Not a framework.
**Avoids:** Pitfall 5 (lowest-common-denominator prompts), Pitfall 6 (silent context truncation), Pitfall 7 (IP-sensitive projects without quality gate), Pitfall 8 (over-engineering abstraction)

### Phase 3: Flexible FDS Structure — Workflows
**Rationale:** With the registry (Phase 1) and provider abstraction (Phase 2) in place, modify the CLI workflows. `new-fds.md` is the entry point and must establish the provider lock and decomposition model in a single PROJECT.md write. `plan-phase.md` and `discuss-phase.md` follow.
**Delivers:** Updated `new-fds.md` (system-first discovery, decomposition model selection, provider lock), updated `plan-phase.md` (template selected from model registry), updated `discuss-phase.md`, extended `config_phases.py`
**Addresses:** System-first discovery prompt, structure-aware ROADMAP generation for `isa88_em` and `functional` models, decomposition model in PROJECT.md
**Avoids:** Pitfall 1 (EM domain knowledge stripped), Pitfall 13 (mid-project provider switching), Pitfall 4 (selective ISA-88 compliance in hybrid projects)

### Phase 4: Engine Visibility — Backend
**Rationale:** Can start in parallel with Phase 3 (no dependencies on CLI changes). Backend-first because the frontend can develop against a real API shape rather than invented mock data.
**Delivers:** `engine_service.py` (filesystem walker, frontmatter parser, git log reader), `engine.py` FastAPI router (`/api/engine/files`, `/api/engine/changelog`, `/api/engine/templates`, `/api/engine/prompts`), registered in `main.py`
**Uses:** `GitPython>=3.1.46`
**Implements:** Read-only engine service pattern — no SQLite for template storage, files served only from pre-registered manifest paths (not arbitrary paths to prevent path traversal)
**Avoids:** Pitfall 9 (over-building custom viewer when a CLI command suffices for simpler needs), Pitfall 10 (SSOT corruption via API writes)

### Phase 5: Engine Visibility — Frontend
**Rationale:** Builds against the real API from Phase 4. Monaco and diff viewer dependency compatibility against React 19 should be confirmed before this phase starts.
**Delivers:** `EngineExplorer.tsx`, `TemplateViewer.tsx`, `ChangeLog.tsx`, engine version in GUI header, Engine navigation entry
**Uses:** `@monaco-editor/react@^4.7.0`, `react-diff-viewer-continued@^4.2.0`
**Avoids:** Pitfall 10 (no edit affordances anywhere), Pitfall 11 (scope creep to prompt management), Pitfall 13 (provider config shown as editable)

### Phase 6: Cross-Pillar Integration + Validation
**Rationale:** The three pillars must be tested in combination, particularly the section-type times provider cross-product and the end-to-end `discuss to plan to write to verify` pipeline on each provider. Backward compatibility with existing Type A/B/C/D projects must be confirmed.
**Delivers:** End-to-end test on each provider (Claude, GPT-4o, Ollama), backward compatibility verification on a Type A project, `doc:status` updated to display v3.0 PROJECT.md fields, "looks done but isn't" checklist cleared
**Avoids:** Pitfall 12 (cross-pillar context isolation break), regression on existing project types

### Phase Ordering Rationale

- Schema contract first prevents the highest-probability integration failure — three pillars independently adding incompatible PROJECT.md fields is nearly guaranteed without an explicit contract.
- LLM abstraction before flexible structure workflow changes because commands cannot be migrated away from direct Anthropic SDK calls piecemeal — the wrapper must exist and be tested first.
- Engine visibility backend before frontend because the frontend develops against real API shapes rather than mocked data, which prevents rework.
- Pillars 1+2 (CLI engine changes) and Pillar 3 (GUI changes) are genuinely independent and can be developed in parallel by separate threads from Phase 2 onward.
- Cross-pillar integration phase is explicit, not assumed to emerge automatically — the prompt times provider times section-type matrix must be validated systematically before the milestone is closed.

### Research Flags

Phases likely needing `/gsd:research-phase` during planning:
- **Phase 2 (LLM Abstraction):** Provider-specific prompt variant authoring for EM sections needs real output comparison across Claude, GPT-4o, and a local model. The quality thresholds for `verify-phase.md` completeness checks (e.g. minimum interlock count per section type) cannot be designed in advance — they require iteration against actual output quality from each provider.
- **Phase 3 (Flexible Structure — Workflows):** `config_phases.py` extension for dynamic decomposition-model phase counts may have non-obvious interactions with the existing phase timeline React component. Worth a targeted research pass on the current `config_phases.py` to frontend boundary before implementation.

Phases with standard patterns (research-phase likely unnecessary):
- **Phase 1 (Schema Contract):** Pure data model definition — no technical unknowns, no external dependencies.
- **Phase 4 (Engine Visibility Backend):** GitPython and FastAPI router patterns are well-documented. Filesystem walker is straightforward.
- **Phase 5 (Engine Visibility Frontend):** Monaco and diff viewer are well-documented. Standard read-only viewer pattern.
- **Phase 6 (Integration):** Standard end-to-end testing — the test scenarios are already defined in the PITFALLS.md "looks done but isn't" checklist.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Official sources for all packages. LiteLLM supply chain incident verified via official LiteLLM blog and corroborating news source. Monaco React 19 peer dep confirmed in release notes. Only gap is `react-diff-viewer-continued` React 19 compat which is unconfirmed. |
| Features | HIGH (core), MEDIUM (industrial-specific) | ISA-88 decomposition patterns confirmed via ISA-88 spec references and control engineering sources. LLM abstraction patterns verified against industry consensus. Niche industrial domain limits external validation for some edge cases. |
| Architecture | HIGH | Based on direct inspection of v2.0 codebase and `gsd-docs-industrial/` engine — not inferred from documentation alone. Architecture decisions are grounded in existing system constraints. |
| Pitfalls | HIGH | Cross-referenced with industry sources on prompt portability, over-abstraction anti-patterns, LLM context limits, and ISA-88 decomposition design. Multiple independent sources converge on the same conclusions. |

**Overall confidence:** HIGH

### Gaps to Address

- **`react-diff-viewer-continued` React 19 compatibility:** Unconfirmed. Before Phase 5 begins, run `npm install react-diff-viewer-continued@^4.2.0` and verify `npm ls react` shows no peer dep conflict. If conflict appears, use `--legacy-peer-deps` or wait for a confirmed React 19 release. Low severity — fallback is trivial.
- **Local model output quality thresholds:** The pitfalls research establishes that local models produce fewer interlocks and less precise technical content than Claude, but the specific quantitative completeness thresholds for `verify-phase.md` (e.g. "fewer than N interlocks triggers a warning") need to be determined empirically against actual local model output. Establish these during Phase 2 testing before building verification integration.
- **`config_phases.py` to frontend coupling depth:** The architecture research flags this as an extension point for dynamic decomposition-model phase counts, but the current coupling between `config_phases.py` and the phase timeline React component was not fully mapped during research. A targeted code read during Phase 3 planning is recommended before modifying this boundary.

## Sources

### Primary (HIGH confidence)
- [LiteLLM Docs](https://docs.litellm.ai/docs/) — provider support, routing conventions, install
- [LiteLLM PyPI](https://pypi.org/project/litellm/) — v1.83.0 confirmed current as of 2026-03-31
- [LiteLLM Supply Chain Incident Report](https://docs.litellm.ai/blog/security-update-march-2026) — versions 1.82.7/1.82.8 compromised, 1.83.0 clean
- [The Hacker News: TeamPCP Backdoors LiteLLM](https://thehackernews.com/2026/03/teampcp-backdoors-litellm-versions.html) — corroborating incident source
- [Anthropic Python SDK PyPI](https://pypi.org/project/anthropic/) — v0.86.0 current
- [OpenAI Python SDK PyPI](https://pypi.org/project/openai/) — v2.30.0 current
- [GitPython PyPI](https://pypi.org/project/GitPython/) — v3.1.46 current
- [@monaco-editor/react npm](https://www.npmjs.com/package/@monaco-editor/react) — v4.7.0, React 19 peer dep confirmed
- [monaco-react GitHub releases](https://github.com/suren-atoyan/monaco-react/releases) — React 19 confirmation
- [ollama-python GitHub](https://github.com/ollama/ollama-python) — v0.6.1
- v2.0 codebase — `backend/app/` (direct inspection)
- v1.0 CLI engine — `~/.claude/gsd-docs-industrial/` (direct inspection)
- `SPECIFICATION.md v2.7.0` — canonical domain knowledge SSOT

### Secondary (MEDIUM confidence)
- [react-diff-viewer-continued npm](https://www.npmjs.com/package/react-diff-viewer-continued) — v4.2.0 current, React 19 compat unconfirmed
- [ISA-88 and Modular Automation — Yokogawa](https://www.yokogawa.com/us/library/resources/media-publications/isa-88-and-modular-automation/)
- [6 Steps to Designing a Flexible Control System with ISA-88 — Control Engineering](https://www.controleng.com/6-steps-to-designing-a-flexible-control-system-with-isa-88/)
- [Portability of LLM Prompts — Vivek Haldar](https://vivekhaldar.com/articles/portability-of-llm-prompts/) — confirms prompt portability does not exist
- [Moving Beyond Over Abstraction — HatchWorks AI](https://hatchworks.com/blog/gen-ai/llm-projects-production-abstraction/)
- [LLM Abstraction Layer — ProxAI](https://www.proxai.co/blog/archive/llm-abstraction-layer)
- [On-Prem LLMs vs Cloud APIs — Unified AI Hub](https://www.unifiedaihub.com/blog/on-premise-llms-vs-cloud-apis-when-to-run-your-ai-models-on-premise)
- [Prompt Versioning: The Complete Guide — Agenta](https://agenta.ai/blog/prompt-versioning-guide)
- [Failover Routing Strategies for LLMs — Portkey](https://portkey.ai/blog/failover-routing-strategies-for-llms-in-production/)

### Tertiary (LOW confidence / inference)
- Industrial decomposition model selection heuristics — inferred from ISA-88 spec structure and project history; no directly comparable published pattern exists for this specific use case

---
*Research completed: 2026-03-31*
*Ready for roadmap: yes*
