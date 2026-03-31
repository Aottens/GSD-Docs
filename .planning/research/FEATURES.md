# Feature Research

**Domain:** Docs engine rearchitecture — flexible FDS structure, LLM provider abstraction, engine visibility
**Researched:** 2026-03-31
**Confidence:** HIGH (core patterns), MEDIUM (industrial-specific research limited by niche domain)

> **Note:** This file supersedes the v2.0 FEATURES.md (2026-02-14). That research covered the GUI cockpit; this covers v3.0 docs engine internals.

---

## Pillar 1: Flexible FDS Structure

### What Engineers Actually Need

Currently, `/doc:new-fds` forces EM (Equipment Module) decomposition immediately. In practice, engineers first describe a system functionally — "a filling machine with a loader, filler, and unloader" — before knowing the ISA-88 hierarchy. The problem is not that ISA-88 is wrong; it is that it is premature. Real project discovery reveals the hierarchy rather than prescribing it upfront.

ISA-88 itself separates the **procedural model** (Procedure → Unit Procedure → Operation → Phase) from the **physical model** (Process Cell → Unit → EM → CM). The current system conflates them by hardcoding the physical hierarchy at project start. The fix is to let the structural model emerge from discovery.

### Table Stakes (Engineers Expect These)

Features the rearchitecture must deliver for the new approach to feel coherent.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **System-first discovery prompt** | Engineers describe what they have, not what ISA-88 says they should have | LOW | `new-fds` asks "describe your system" before asking decomposition model. Decomposition choice follows discovery, not precedes it. |
| **Decomposition model selection** | Every project is different — batch plant, filling line, DCS continuous process, SCADA discrete | MEDIUM | Support: ISA-88 hierarchy, functional blocks, process-flow, hybrid. Selection at project create time stored in PROJECT.md. |
| **Structure-aware ROADMAP generation** | The phase plan must reflect the chosen decomposition, not a hardcoded EM template | HIGH | ROADMAP generator reads decomposition model and produces appropriate phase structure. Replaces 4 hardcoded templates (A/B/C/D) with parameterized generation. |
| **Decomposition model stored in project config** | All commands must know the structure without re-asking | LOW | `PROJECT.md` gains a `decomposition_model` field. All downstream commands (discuss, plan, write, verify) read it. |
| **Backward compatibility with existing Type A/B/C/D projects** | v1.0 projects must continue working | MEDIUM | Default decomposition model = `isa88_em` (current behavior). Type A/B map to `isa88_em`; Type B-flex gets `functional` as a valid alternative. Existing projects unaffected. |
| **Template selection by decomposition model** | Section templates (equipment module, state machine, interface) are EM-specific | HIGH | New template sets per decomposition model. `isa88_em` uses existing templates. `functional` uses functional-block templates. Templates selected at write time from PROJECT.md config. |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Hybrid decomposition** | Some projects are partially ISA-88, partially functional — e.g., a DCS system where the reactor unit follows ISA-88 but the utility section is described functionally | HIGH | `hybrid` decomposition allows phase-level model selection. Phase 2 might be `isa88_em`, Phase 3 might be `functional`. Requires per-phase config in ROADMAP.md. |
| **Structure evolution / late promotion** | Project starts functional, discovers EM hierarchy during discuss-phase, promotes sections to ISA-88 structure without rewrite | HIGH | `expand-roadmap` extended to support structure promotion: functional → isa88_em migration path. Complex; defer unless engineers hit this repeatedly. |
| **ISA-88 conformance check on functional projects** | Engineer gets told "your functional description maps to these EM/CM boundaries" | MEDIUM | A verification level that attempts ISA-88 mapping and surfaces ambiguities. Opt-in, not automatic. |

### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Free-form structure (no model)** | "Let the engineer decide everything" | No structure = no phase templates, no verification criteria, no consistent output; the entire value of the system evaporates | Offer 4 opinionated models. Hybrid covers edge cases. |
| **Automatic structure detection from description** | "Let the AI figure out the decomposition" | LLM classification of decomposition model is unreliable; a wrong choice poisons the entire project's ROADMAP | Ask explicitly, confirm, store. Human confirms before proceeding. |
| **GUI-driven structure editor** | Engineers want drag-and-drop hierarchy builder | Massive scope; breaks file-backed STATE.md; CLI incompatibility | Decomposition model set once at project create time via CLI wizard. GUI displays; CLI edits. |

### Dependencies on Existing System

- `new-fds.md` command must be extended with discovery-first questions
- `PROJECT.md` template gains `decomposition_model` field
- `fds-structure.json` gains variant entries per decomposition model
- ROADMAP templates (currently 4 hardcoded) become parameterized generators
- Section templates under `templates/fds/` need counterparts for `functional` and `process-flow` models
- `check-standards.md` ISA-88 checking only applies to `isa88_em` and `hybrid` models
- `expand-roadmap.md` must understand decomposition model when proposing expansion

---

## Pillar 2: LLM Provider Abstraction

### What Engineers Actually Need

Industrial clients often cannot send project content to cloud APIs due to IP sensitivity, NDA obligations, or compliance requirements. The current system hardwires Claude (Anthropic API). Engineers need: (a) swap Claude for GPT-4o for cost reasons, (b) run locally on a VM for IP-sensitive projects, (c) fallback if a cloud provider is down.

The dominant pattern in 2025-2026 is LiteLLM: a unified Python interface to 100+ providers including Ollama (local), Claude, OpenAI, and any OpenAI-compatible endpoint. It uses a single `litellm.completion()` call regardless of provider, with routing config in YAML.

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Single provider abstraction interface** | All commands must work identically regardless of provider | MEDIUM | One function wraps LLM calls across all commands. LiteLLM is the standard pattern for this. Replaces direct Anthropic SDK calls. |
| **Provider configured per project (PROJECT.md)** | IP-sensitive projects use local; development uses cloud | LOW | `PROJECT.md` gains `llm_provider` and `llm_model` fields. Commands read config, not hardcoded. |
| **Claude (Anthropic) support** | Current provider; existing behavior unchanged | LOW | LiteLLM supports Claude natively via `anthropic/claude-opus-4-5` model string. |
| **OpenAI / GPT support** | Cost flexibility for non-IP-sensitive projects | LOW | LiteLLM supports OpenAI natively. `openai/gpt-4o` model string. |
| **Local model support via Ollama** | IP-sensitive deployment requirement | MEDIUM | LiteLLM supports Ollama via `ollama/llama3` + `api_base=http://localhost:11434`. Ollama must be running on the machine. |
| **API key management (per provider)** | Engineers should not hardcode keys in project files | LOW | Keys in `.env` or environment variables, never in PROJECT.md. LiteLLM reads standard env vars (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`). |
| **Graceful error on misconfiguration** | Engineer who picks wrong provider gets clear error, not Python traceback | LOW | Wrapper validates provider config before first LLM call in a command. |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Fallback chain** | If cloud provider is down or rate-limited, fall back to backup model | MEDIUM | LiteLLM router supports fallback chains: `claude-3-5-sonnet → gpt-4o → ollama/llama3`. Config in YAML. Adds resilience for long writes. |
| **Per-phase provider override** | Some phases (e.g. standards-heavy verification) work best with specific models | LOW | `decomposition_model` / `llm_provider` can be overridden at command invocation time via env var. Does not need to be in PROJECT.md. |
| **OpenAI-compatible endpoint support** | Client has their own self-hosted LLM gateway (Azure OpenAI, custom proxy) | LOW | LiteLLM supports `openai/` prefix with custom `api_base`. No extra code needed. |
| **Cost/token logging (local only)** | Engineers want to know how much a project costs | MEDIUM | LiteLLM has built-in usage tracking. Append token counts to STATE.md or a separate USAGE.md. Useful for estimating project costs. |

### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **GUI-based provider config** | "Switch providers from the cockpit" | GUI has no LLM operations (cockpit pivot decision). Adding provider config to GUI creates false impression of GUI-driven AI. | CONFIG.md or PROJECT.md for provider config; CLI wizard at project create time. |
| **Real-time model comparison** | "Let engineer see Claude vs GPT output side by side" | Doubles token cost and complexity; creates decision fatigue; the FDS content should be deterministic given the same inputs | Provider is a project-level setting. Engineer chooses once per project based on IP sensitivity. |
| **Fine-tuned models** | "Train a model on our past FDSs" | Training data management, infrastructure, and retraining cycles are enormous scope; model drift risk for safety-adjacent documents | Few-shot examples in prompts + strong system prompts already achieve domain specificity without fine-tuning. |
| **Streaming output in CLI** | "Show text as it generates for long sections" | Claude Code already handles this at the host level; streaming in subagents creates partial-write risk in file-backed state | Keep current write-on-complete pattern. Streaming is cosmetic; forward-only safety matters more. |

### Dependencies on Existing System

- Every command that calls Claude directly (write-phase.md, verify-phase.md, discuss-phase.md, etc.) must be updated to use the abstraction wrapper
- `PROJECT.md` template gains `llm_provider` and `llm_model` fields
- Install setup (`install.ps1`) must document how to set provider env vars
- LiteLLM added as a Python dependency (`pip install litellm`)
- Commands that construct prompts must remain provider-agnostic — no Claude-specific XML tags in prompts (currently prompts use `<section>` XML which is Claude-optimal; verify GPT-4o handles gracefully)
- Context window sizes differ by model (Claude claude-opus-4-5: 200k, GPT-4o: 128k, Llama-3.1-70b: 128k) — context loading rules in commands must be aware of target model's limits

---

## Pillar 3: Docs Engine Visibility

### What Engineers Actually Need

The docs engine is 194 Markdown files: templates, prompts, workflows, command definitions. Engineers cannot see what the system is doing, cannot tell which template was used to generate a section, cannot track what changed between updates, and cannot answer client questions like "what verification criteria are applied to the state machine section?". The system is a black box.

The goal is a **read-only inspection layer** — not editing (that stays in the file system / version control), but visibility into what exists, what it does, and what changed.

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Template browser** | Engineers need to see what template was used for any section | MEDIUM | Web GUI page listing all files under `gsd-docs-industrial/templates/`, `commands/`, `workflows/`. Rendered Markdown view. No editing. |
| **Current config summary** | "What provider, model, decomposition model, and standards flags is this project using?" | LOW | Per-project summary panel in GUI showing PROJECT.md config values. Already partially present in cockpit; extend to show engine config. |
| **Template-to-section traceability** | For a given section in the document, which template and prompts were used? | MEDIUM | Add `template_ref` and `prompt_ref` fields to PLAN.md entries at plan-phase time. GUI shows these in the document outline. |
| **Command documentation viewer** | "What does /doc:write-phase do?" readable by non-engineers | LOW | Browse commands/*.md files rendered in GUI. Read-only. Demystifies the system for engineers who want to understand before trusting output. |
| **Engine version display** | Engineers need to know which version of the docs engine generated a document | LOW | `VERSION` file already exists in `gsd-docs-industrial/`. Surface it in GUI header and in exported document frontmatter. |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Changelog / diff viewer for engine updates** | When the system is updated, engineers can see what changed (prompt improvements, new templates, verification criteria) | MEDIUM | Git log on `gsd-docs-industrial/` filtered to template/prompt files. Rendered as readable changelog in GUI. Requires git to be available on deployment machine. |
| **Verification criteria browser** | "What exactly does verify-phase check for a state machine section?" | LOW | Browse verification criteria extracted from verify-phase.md and section templates. Engineers can validate that the system checks what they care about. |
| **Template health indicators** | Flag templates that haven't been updated in >6 months, or that are missing required fields | MEDIUM | Lightweight linter over template Markdown files. Surface warnings in the template browser. Prevents silently stale templates. |
| **Usage statistics per template** | "Which templates get used most across all projects?" | LOW | Count section plan entries by template_ref across all projects. Simple SQLite aggregate query. Useful for prioritizing template improvements. |

### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **In-GUI template editing** | "Let engineers tweak prompts without touching files" | File-backed templates are the SSOT; GUI edits create divergence, break version control, and risk prompt corruption in production | Read-only browser with a "copy to clipboard" for the prompt text. Engineers edit via file system, commit via git. |
| **Per-project template overrides** | "Let project X use a different state machine template" | Template divergence across projects creates inconsistent output quality; makes QA impossible | One set of canonical templates. If a template needs improvement, update it for all projects. |
| **AI-assisted template improvement** | "Let the AI suggest better prompts" | Meta-prompting creates a loop where the system's own quality becomes dependent on AI judgment; safety risk for standards-adjacent content | Engineers review and improve templates manually based on output quality patterns. |
| **Real-time prompt preview** | "Show what the full prompt will look like for section X before running write-phase" | Pre-execution preview requires rendering variable substitution, which replicates the execution engine in the GUI | Post-execution traceability (template_ref in PLAN.md) is more useful than pre-execution preview. |

### Dependencies on Existing System

- GUI gains a new "Engine" section in the navigation
- FastAPI backend gains read-only endpoints to serve template/command files
- PLAN.md template gains `template_ref` and `prompt_ref` fields (populated by `plan-phase.md`)
- `VERSION` file surfaced in GUI header
- Git integration (read-only `git log`) needed for changelog feature — must handle gracefully if git is unavailable
- Traceability fields in PLAN.md are additive and backward-compatible with v1.0 projects

---

## Feature Dependencies

```
[Flexible FDS Structure]
    └──requires──> [Decomposition model in PROJECT.md]
                       └──requires──> [new-fds discovery prompt]
    └──requires──> [Structure-aware ROADMAP generation]
                       └──requires──> [Parameterized ROADMAP templates]
    └──requires──> [Template sets per decomposition model]

[LLM Provider Abstraction]
    └──requires──> [LiteLLM wrapper function]
                       └──requires──> [Provider config in PROJECT.md]
    └──enhances──> [Fallback chain]
                       └──requires──> [LiteLLM router config]

[Docs Engine Visibility]
    └──requires──> [Template browser in GUI]
                       └──requires──> [FastAPI file-serving endpoints]
    └──enhances──> [Template-to-section traceability]
                       └──requires──> [template_ref in PLAN.md]

[Flexible FDS Structure] ──enhances──> [Docs Engine Visibility]
    (decomposition model visible in engine config summary)

[LLM Provider Abstraction] ──feeds──> [Docs Engine Visibility]
    (provider/model visible in per-project config summary)
```

### Dependency Notes

- **Decomposition model requires PROJECT.md changes:** All three pillars touch PROJECT.md — coordinate schema changes into a single migration to avoid multiple backwards-compat gaps.
- **LiteLLM wrapper must be added before any command refactoring:** Commands cannot be updated piecemeal — the wrapper must exist and be tested before migrating commands away from direct Anthropic SDK.
- **Template browser does not depend on traceability:** Template browser is useful standalone. Traceability (template_ref in PLAN.md) enhances it but is independent.
- **Hybrid decomposition conflicts with simple ROADMAP generator:** Implement single-model ROADMAP generation first, then extend to hybrid as a follow-on.

---

## MVP Definition for v3.0

### Launch With (v3.0 core)

Minimum set for the milestone to deliver on its promise.

- [ ] **System-first discovery in `new-fds`** — functional description before decomposition choice; essential for the pillar to exist at all
- [ ] **Decomposition model in PROJECT.md** — enables all downstream commands to behave correctly for the chosen model
- [ ] **Structure-aware ROADMAP for `functional` and `isa88_em` models** — the two most common cases; process-flow and hybrid can follow
- [ ] **LiteLLM abstraction wrapper** — single function replacing direct Anthropic SDK calls across all commands
- [ ] **Claude + OpenAI + Ollama provider support** — covers all three deployment scenarios (cost, IP-sensitive, fallback)
- [ ] **Template browser in GUI (read-only)** — minimal viable visibility: engineers can see what templates exist and what they contain
- [ ] **Engine version in GUI + export frontmatter** — traceability at document level

### Add After Validation (v3.x)

Add once core behavior is proven stable.

- [ ] **`template_ref` / `prompt_ref` in PLAN.md** — trigger: engineers start asking "which template generated this section?"
- [ ] **Fallback chain configuration** — trigger: cloud provider outages cause project interruptions
- [ ] **Changelog / diff viewer for engine updates** — trigger: team starts updating templates and loses track of what changed
- [ ] **Functional and process-flow section templates** — trigger: first project using non-EM decomposition reveals template gaps
- [ ] **Verification criteria browser** — trigger: client asks "what exactly was verified?"

### Future Consideration (v4+)

- [ ] **Hybrid decomposition model** — defer until a real project needs it; designing for hypothetical hybrid is premature
- [ ] **Structure evolution / late promotion** — defer; rarely needed; high complexity
- [ ] **Cost/token logging** — useful but not blocking; USAGE.md approach can be added standalone
- [ ] **Template health indicators** — useful ops tooling; non-urgent

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| System-first discovery in `new-fds` | HIGH | LOW | P1 |
| Decomposition model in PROJECT.md | HIGH | LOW | P1 |
| Structure-aware ROADMAP generation | HIGH | HIGH | P1 |
| LiteLLM abstraction wrapper | HIGH | MEDIUM | P1 |
| Ollama / local model support | HIGH | MEDIUM | P1 |
| Template browser (read-only) | MEDIUM | MEDIUM | P1 |
| Engine version display | LOW | LOW | P1 |
| Functional decomposition templates | HIGH | HIGH | P2 |
| template_ref in PLAN.md | MEDIUM | LOW | P2 |
| Fallback chain | MEDIUM | MEDIUM | P2 |
| Changelog / diff viewer | MEDIUM | MEDIUM | P2 |
| Verification criteria browser | MEDIUM | LOW | P2 |
| Hybrid decomposition | LOW | HIGH | P3 |
| Structure evolution/promotion | LOW | HIGH | P3 |
| Cost/token logging | LOW | MEDIUM | P3 |
| Template health indicators | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Must have for v3.0 launch
- P2: Should have, add when core is stable
- P3: Nice to have, future milestone

---

## Industrial Automation Domain Specifics

### Why Standard Document Generation Patterns Don't Fully Apply

Most document generation research covers general-purpose tools or software engineering docs. FDS/SDS generation is different in ways that affect feature design:

1. **Standards compliance is load-bearing.** ISA-88, PackML, IEC 61131-3 are contractual requirements for batch and safety systems. The flexible structure feature must not weaken standards compliance — the opt-in ISA-88 check must remain intact for EM-based projects.

2. **IP sensitivity is structural, not optional.** Industrial project content (control logic, equipment specifications, process parameters) is core IP. This is not a "nice to have" for local LLMs — it is a blocking requirement for some clients. Local model support must be first-class, not an afterthought.

3. **Engineers are not prompt engineers.** The visibility layer must explain the system in engineering terms (what verification criteria apply, which template section covers interlocks) — not in LLM terms (prompt tokens, temperature settings).

4. **The document is a legal artifact.** Version numbers, approval status, and traceability to requirements matter. The engine version surfaced in exports is not cosmetic — it answers "which version of the generation system was used for this approved document?"

5. **Context window limits hit differently.** A single Equipment Module section for a complex reactor can be 3,000–5,000 words. With multiple context files loaded (PROJECT.md, CONTEXT.md, standards references), some local models (70B at 128k context) hit limits that cloud models do not. The LLM abstraction must surface this as a configuration concern, not a silent truncation.

---

## Sources

- [LiteLLM documentation — Ollama provider](https://docs.litellm.ai/docs/providers/ollama)
- [LiteLLM — Getting Started](https://docs.litellm.ai/docs/)
- [LiteLLM — OpenAI-compatible endpoints](https://docs.litellm.ai/docs/providers/openai_compatible)
- [LiteLLM proxy configuration](https://docs.litellm.ai/docs/proxy/configs)
- [The LLM Abstraction Layer: Why Your Codebase Needs One in 2025](https://www.proxai.co/blog/archive/llm-abstraction-layer)
- [ISA-88 and Modular Automation — Yokogawa](https://www.yokogawa.com/us/library/resources/media-publications/isa-88-and-modular-automation/)
- [ISA-88 Wikipedia — Physical and Procedural model separation](https://en.wikipedia.org/wiki/ISA-88)
- [6 Steps to Designing a Flexible Control System with ISA-88](https://www.controleng.com/6-steps-to-designing-a-flexible-control-system-with-isa-88/)
- [Run LLMs Locally with Ollama — Privacy-First AI for Developers 2025](https://www.cohorte.co/blog/run-llms-locally-with-ollama-privacy-first-ai-for-developers-in-2025)
- [Prompt Versioning: The Complete Guide](https://agenta.ai/blog/prompt-versioning-guide)
- [Prompt Versioning and Management — LaunchDarkly](https://launchdarkly.com/blog/prompt-versioning-and-management/)
- v1.0/v2.0 system internals: `gsd-docs-industrial/CLAUDE-CONTEXT.md`, `commands/`, `templates/`

---
*Feature research for: v3.0 Docs Engine Rearchitecture (flexible structure, LLM abstraction, engine visibility)*
*Researched: 2026-03-31*
