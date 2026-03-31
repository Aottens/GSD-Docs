# Architecture Research

**Domain:** Industrial FDS/SDS docs engine rearchitecture (v3.0)
**Researched:** 2026-03-31
**Confidence:** HIGH

## Standard Architecture

### System Overview

Current v2.0 system (baseline for integration analysis):

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLI Layer (~/.claude/commands/doc/)          │
│  14 /doc:* commands (frontmatter .md) → Claude Code execution   │
│  Context: gsd-docs-industrial/ (194 files, SPECIFICATION.md)    │
└──────────────────────────────┬──────────────────────────────────┘
                               │ reads/writes
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   File System (project/.planning/)               │
│  STATE.md · CONTEXT.md · PLAN.md · CONTENT.md · VERIFICATION.md │
│  ROADMAP.md · PROJECT.md · REQUIREMENTS.md · SUMMARY.md         │
└──────────────────────────────┬──────────────────────────────────┘
                               │ reads (display only)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     GUI Layer (v2.0 — shipped)                   │
│  React frontend (cockpit) ↔ FastAPI backend (file/project API)  │
│  SQLite (project/file metadata only) · SSE (export progress)    │
└─────────────────────────────────────────────────────────────────┘
```

### What v3.0 Adds

Three new features each touch a different layer of this stack:

```
┌─────────────────────────────────────────────────────────────────────┐
│  FEATURE 1: Flexible FDS Structure                                  │
│  Layer: CLI docs engine (gsd-docs-industrial/)                      │
│  Touch point: fds-structure.json, section templates, new-fds.md,   │
│               plan-phase.md, discuss-phase.md, config_phases.py     │
├─────────────────────────────────────────────────────────────────────┤
│  FEATURE 2: LLM Provider Abstraction                                │
│  Layer: CLI prompts → new abstraction shim                          │
│  Touch point: command .md files (prompt construction), new          │
│               provider config in PROJECT.md/config.json             │
├─────────────────────────────────────────────────────────────────────┤
│  FEATURE 3: Docs Engine Visibility                                  │
│  Layer: New GUI surface + new FastAPI router                        │
│  Touch point: new /api/engine/* endpoints, new React feature,       │
│               reads gsd-docs-industrial/ files (read-only)          │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Boundaries

### What Exists and What Changes

| Component | v2.0 State | v3.0 Change |
|-----------|-----------|-------------|
| `~/.claude/commands/doc/` — 14 command .md files | Unchanged | Pillar 1: modify `new-fds.md`, `discuss-phase.md`, `plan-phase.md` to support system-first discovery; Pillar 2: add provider-config reading |
| `~/.claude/gsd-docs-industrial/templates/fds/` — 5 section templates | Equipment-module only | Pillar 1: add `section-functional-unit.md`, `section-process-step.md`, `section-hybrid.md` for non-EM decomposition |
| `~/.claude/gsd-docs-industrial/templates/fds-structure.json` | EM-centric static structure | Pillar 1: replace with dynamic structure schema — decomposition model selected at `/doc:new-fds` |
| `~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md` | v1.0 context file | Pillar 1: update with system-first discovery rules; Pillar 2: document provider config schema |
| `~/.claude/gsd-docs-industrial/workflows/new-fds.md` | Hardcoded EM classification | Pillar 1: add decomposition model discovery step |
| `~/.claude/gsd-docs-industrial/workflows/plan-phase.md` | Selects EM template only | Pillar 1: selects template from decomposition model registry |
| `~/.claude/gsd-docs-industrial/agents/doc-writer.md` | Claude-specific prompt patterns | Pillar 2: add provider-aware prompt formatting wrapper |
| `~/.claude/gsd-docs-industrial/agents/doc-verifier.md` | Claude-specific prompt patterns | Pillar 2: add provider-aware prompt formatting wrapper |
| `backend/app/config_phases.py` | Hardcoded Types A/B/C/D phase lists | Pillar 1: extend to support dynamic decomposition model phases |
| `backend/app/api/` — 8 existing routers | File/project management API | Pillar 3: add new `engine.py` router |
| `backend/app/services/` — 5 existing services | File/project management services | Pillar 3: add new `engine_service.py` |
| `frontend/src/features/` — 7 existing features | Cockpit features | Pillar 3: add new `engine/` feature directory |
| `.planning/PROJECT.md` per-project | type, language, standards config | Pillar 1: add decomposition model; Pillar 2: add provider config |

### New Components Required

| Component | What It Is | Belongs To |
|-----------|-----------|------------|
| `section-functional-unit.md` | Template for functional unit decomposition (non-EM projects) | Pillar 1 / CLI engine |
| `section-process-step.md` | Template for process-flow decomposition | Pillar 1 / CLI engine |
| `section-isa88-unit.md` | Template for ISA-88 unit/procedure decomposition | Pillar 1 / CLI engine |
| `decomposition-models.json` | Registry of all decomposition models with trigger heuristics | Pillar 1 / CLI engine |
| `provider-config.md` (or schema in SPECIFICATION.md) | LLM provider config schema: model, endpoint, api-key-env, prompt-format | Pillar 2 / CLI engine |
| `backend/app/api/engine.py` | FastAPI router: list files, get file content, get diff, list changes | Pillar 3 / GUI |
| `backend/app/services/engine_service.py` | Reads `gsd-docs-industrial/` directory tree, parses frontmatter, diffs | Pillar 3 / GUI |
| `frontend/src/features/engine/` | React feature: template browser, prompt viewer, change log viewer | Pillar 3 / GUI |

## Recommended Project Structure

The three pillars map to three independent work areas in the repo:

```
~/.claude/gsd-docs-industrial/         # Pillar 1 + 2: CLI engine changes
├── templates/
│   └── fds/
│       ├── section-equipment-module.md    (existing — unchanged)
│       ├── section-interface.md           (existing — unchanged)
│       ├── section-state-machine.md       (existing — unchanged)
│       ├── section-functional-unit.md     (NEW — Pillar 1)
│       ├── section-process-step.md        (NEW — Pillar 1)
│       └── section-isa88-unit.md          (NEW — Pillar 1)
├── templates/fds-structure.json           (REPLACE — Pillar 1)
├── templates/decomposition-models.json    (NEW — Pillar 1)
├── workflows/new-fds.md                   (MODIFY — Pillar 1 + 2)
├── workflows/plan-phase.md                (MODIFY — Pillar 1)
├── workflows/discuss-phase.md             (MODIFY — Pillar 1)
├── agents/doc-writer.md                   (MODIFY — Pillar 2)
├── agents/doc-verifier.md                 (MODIFY — Pillar 2)
└── CLAUDE-CONTEXT.md                      (MODIFY — Pillar 1 + 2)

backend/app/                           # Pillar 3: GUI backend changes
├── api/
│   └── engine.py                          (NEW — Pillar 3)
├── services/
│   └── engine_service.py                  (NEW — Pillar 3)
└── main.py                                (MODIFY — register engine router)

frontend/src/features/                 # Pillar 3: GUI frontend changes
└── engine/
    ├── EngineExplorer.tsx                 (NEW — Pillar 3)
    ├── TemplateViewer.tsx                 (NEW — Pillar 3)
    ├── PromptViewer.tsx                   (NEW — Pillar 3)
    └── ChangeLog.tsx                      (NEW — Pillar 3)
```

### Structure Rationale

- **Pillar 1 stays entirely in `gsd-docs-industrial/`:** The CLI engine is self-contained. GUI reads project type/phase config from `config_phases.py` — that file needs extension but the domain logic stays in the engine.
- **Pillar 2 is a thin shim, not a platform:** Provider abstraction is lightweight (config-driven prompt wrapping) because the constraint is "CLI compatibility maintained." No new orchestration layer.
- **Pillar 3 is additive to the GUI:** Engine visibility is read-only inspection. No existing GUI routes or services are modified — just a new router and new frontend feature.

## Architectural Patterns

### Pattern 1: Decomposition Model Registry

**What:** A single JSON registry (`decomposition-models.json`) maps model IDs to templates, triggers, and section structure. The `new-fds.md` workflow queries this registry during project setup based on how the engineer describes the system.

**When to use:** Any time the docs engine needs to select a structural template. Replaces the current hardcoded EM-centric path in `new-fds.md` and `plan-phase.md`.

**Trade-offs:** Adding a registry introduces indirection but makes adding new decomposition models (e.g., safety-function decomposition for future standards) a config change not a workflow rewrite.

**Example structure:**
```json
{
  "models": [
    {
      "id": "equipment-module",
      "label": "Equipment Module (ISA-88 / PackML)",
      "triggers": ["PLC", "EM", "equipment module", "PackML", "ISA-88"],
      "section_template": "section-equipment-module.md",
      "phase_structure": "type-a-or-b-em-phases",
      "fds_structure": "fds-structure-em.json"
    },
    {
      "id": "functional-unit",
      "label": "Functional Unit (process-flow)",
      "triggers": ["functional block", "process step", "unit operation"],
      "section_template": "section-functional-unit.md",
      "phase_structure": "functional-unit-phases",
      "fds_structure": "fds-structure-functional.json"
    },
    {
      "id": "hybrid",
      "label": "Hybrid (mixed decomposition)",
      "triggers": [],
      "section_template": "section-hybrid.md",
      "phase_structure": "hybrid-phases",
      "fds_structure": "fds-structure-hybrid.json"
    }
  ]
}
```

### Pattern 2: Provider Config in PROJECT.md

**What:** LLM provider configuration lives in per-project `PROJECT.md` (and defaults in `CLAUDE-CONTEXT.md`). The `doc-writer.md` and `doc-verifier.md` agents read provider config at runtime to format prompts correctly.

**When to use:** Any CLI command that constructs prompts. Prompt format varies by provider (Claude system/human turns vs OpenAI messages vs Ollama raw).

**Trade-offs:** Putting provider config in PROJECT.md preserves git-trackability and CLI compatibility (no new config files). Downside: switching provider mid-project requires editing PROJECT.md — acceptable for this use case.

**Example schema addition to PROJECT.md:**
```yaml
llm:
  provider: claude          # claude | openai | ollama | deepseek
  model: claude-opus-4-5    # model ID per provider
  api_key_env: ANTHROPIC_API_KEY   # env var name (not value)
  endpoint: null            # null = use default; set for local/proxy
  prompt_format: anthropic  # anthropic | openai | ollama-raw
```

### Pattern 3: Read-Only Engine Service

**What:** `engine_service.py` walks the `gsd-docs-industrial/` directory tree and exposes file content, metadata, and change history (via git log on the engine files) through a read-only API. No writes — the engine is managed as files, not through the GUI.

**When to use:** All `/api/engine/*` endpoints. The GUI is an inspector, not an editor.

**Trade-offs:** Read-only simplifies the service (no conflict resolution, no versioning logic). Engineers who need to modify templates still do so directly in files. The GUI shows what's there; it doesn't manage it.

**Example endpoint shape:**
```
GET /api/engine/files          → directory tree with file metadata
GET /api/engine/files/{path}   → file content + frontmatter parsed
GET /api/engine/changelog      → git log on engine directory (recent N commits)
GET /api/engine/templates      → filtered list: type=fds|sds|roadmap|workflow
GET /api/engine/prompts        → filtered list: type=agent|command
```

## Data Flow

### Pillar 1: System-First FDS Structure

```
Engineer runs /doc:new-fds
    ↓
new-fds.md: ask "describe your system" (open-ended)
    ↓
new-fds.md: load decomposition-models.json
    → match engineer's description against model triggers
    → present 2-3 candidate models with short explanation
    → engineer confirms or overrides
    ↓
new-fds.md: write chosen decomposition_model to PROJECT.md
    → scaffold ROADMAP.md using model's phase_structure
    → reference model's fds_structure file in PROJECT.md
    ↓
plan-phase.md: reads decomposition_model from PROJECT.md
    → selects correct section template (section-functional-unit.md etc.)
    → generates PLAN.md files using that template's subsection structure
    ↓
doc-writer.md: reads section template path from PLAN.md frontmatter
    → writes CONTENT.md following template structure
    ↓
complete-fds.md: reads fds_structure file named in PROJECT.md
    → assembles final document using that structure (not hardcoded EM structure)
```

### Pillar 2: LLM Provider Abstraction

```
Any /doc:* command that invokes doc-writer.md or doc-verifier.md
    ↓
Agent reads PROJECT.md → llm.provider, llm.model, llm.prompt_format
    ↓
If prompt_format == "anthropic":
    → standard Claude system/human turn format (current behavior)
If prompt_format == "openai":
    → messages array format (system, user roles)
    → strip Claude-specific XML tags if present
If prompt_format == "ollama-raw":
    → single text prompt, no role markers
    → inject <INST> markers if model expects them
    ↓
Agent constructs prompt in correct format
    → calls provider via configured endpoint
    → parses response (provider-specific stop sequences, role markers stripped)
    ↓
Rest of workflow unchanged: write to CONTENT.md, update STATE.md
```

**Note:** This abstraction lives in the agent prompt files themselves (as conditional instructions) and in a thin `provider-format.md` reference doc that agents `@`-include. No new Python infrastructure is needed — Claude Code executes the instructions in the .md files. For actual local model invocation, the engineer configures the endpoint; Claude Code's Bash tool makes the API call.

### Pillar 3: Docs Engine Visibility

```
Engineer opens "Engine" tab in GUI cockpit
    ↓
React EngineExplorer component
    → GET /api/engine/files
        → engine_service.py walks ~/.claude/gsd-docs-industrial/
        → returns tree with file type, size, last-modified
    ↓
Engineer clicks a template file
    → GET /api/engine/files/templates/fds/section-equipment-module.md
        → engine_service.py reads file
        → parses YAML frontmatter (type, language, standards, subsections)
        → returns: { frontmatter, raw_markdown, rendered_html }
    ↓
TemplateViewer renders: frontmatter panel + markdown preview
    ↓
Engineer clicks "Recent Changes"
    → GET /api/engine/changelog?limit=20
        → engine_service.py runs git log on engine directory
        → returns: [{ hash, date, message, files_changed }]
    ↓
ChangeLog renders commit list with diff-on-click
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Current (1-5 engineers, local) | All three pillars as described — no scaling concerns |
| Team server (5-20 users, VM) | Pillar 3 engine service can cache directory tree (5min TTL) to avoid repeated filesystem walks; git log calls are cheap |
| Multi-team (50+ users) | Engine visibility would need a proper changelog store rather than live git log calls; still no concern for Pillars 1-2 (CLI-side changes) |

### Scaling Priorities

1. **First bottleneck (if any):** Pillar 3 engine service doing live git log calls under concurrent load. Mitigation: background-refresh cache on engine service startup and on a 5-minute timer.
2. **Not a concern:** Pillars 1 and 2 are CLI-side changes with no runtime load impact on the server.

## Anti-Patterns

### Anti-Pattern 1: Building LLM Abstraction as a Backend Orchestration Layer

**What people do:** Add a `LLMOrchestrator` service to FastAPI that routes calls to different providers, then rebuild the prompt construction logic in Python.

**Why it's wrong:** The constraint is that AI operations stay in the CLI. The GUI is a file/project management API. Adding LLM orchestration to the backend violates the cockpit architecture decision (Phase 10 of v2.0), doubles maintenance surface, and breaks CLI compatibility because prompts would diverge between CLI and GUI paths.

**Do this instead:** Provider abstraction belongs in the CLI agent files (`doc-writer.md`, `doc-verifier.md`). The agents read `llm.provider` from PROJECT.md and format their prompts accordingly. This is a config-driven prompt pattern, not a software architecture change.

### Anti-Pattern 2: Storing Engine File Snapshots in SQLite

**What people do:** Copy template content into the database for faster querying, then sync on change.

**Why it's wrong:** Templates are already version-controlled (git). Copying them into SQLite creates a second source of truth that drifts. The engine visibility feature's value is showing what's actually on disk — stale DB snapshots undermine that.

**Do this instead:** Read files directly from the filesystem in `engine_service.py`. Cache the directory tree in memory (not in SQLite) with a short TTL for performance.

### Anti-Pattern 3: Making Decomposition Models Mutually Exclusive by Project Type

**What people do:** Map Type A → EM decomposition, Type B → functional unit, etc. Hardcode the mapping.

**Why it's wrong:** Real projects don't follow clean type-to-model mappings. A Type B (Greenfield Flex) project for a batch system needs EM decomposition; a Type A (Standards) project for a conveyor line might use process-step decomposition. The engineer's description of the system should drive model selection, not project type.

**Do this instead:** Project type (A/B/C/D) determines scope and rigor requirements (standards, phases). Decomposition model is a separate independent dimension set during `/doc:new-fds`. Both are stored in PROJECT.md.

### Anti-Pattern 4: Engine Visibility as an Editor

**What people do:** Add edit/save buttons to the template viewer so engineers can modify templates in the GUI.

**Why it's wrong:** Templates are shared infrastructure. GUI edits without version control create divergence between team members. The 194-file engine is its own codebase — it deserves proper version control, not inline editing.

**Do this instead:** The engine viewer is read-only. Show git history. Document the workflow: to modify a template, edit the file directly, commit, and the GUI reflects the change on next load.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Anthropic Claude API | Existing — via CLI agent invocation | Pillar 2 adds provider-conditional prompt formatting, no new API surface |
| OpenAI API | New — via Bash tool in CLI agents | Provider config in PROJECT.md; agent formats prompt as OpenAI messages and calls via curl/python in Bash |
| Ollama (local) | New — via Bash tool in CLI agents | Local endpoint; no API key needed; agent uses ollama-raw format |
| DeepSeek API | New — OpenAI-compatible endpoint | Uses openai prompt_format with DeepSeek endpoint configured |
| Git (engine changelog) | New — subprocess in engine_service.py | `git log --follow` on gsd-docs-industrial/ directory |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| CLI engine ↔ per-project files | Filesystem reads/writes (unchanged) | Pillar 1 adds `decomposition_model` field to PROJECT.md; backward compatible |
| CLI engine ↔ LLM provider | @-includes in agent .md files (unchanged) | Pillar 2 adds conditional prompt-format branch in doc-writer.md |
| GUI backend ↔ CLI engine files | New: `engine_service.py` reads ~/.claude/gsd-docs-industrial/ | Read-only; no writes from GUI to engine |
| GUI backend ↔ existing project files | Existing: phase status derived from filesystem artifacts | Unchanged; Pillar 1 adds decomposition_model to PROJECT.md schema read |
| GUI frontend ↔ engine API | New: `GET /api/engine/*` REST endpoints | New React feature; does not modify existing features |
| `config_phases.py` ↔ frontend | Existing: phase definitions for timeline display | Pillar 1 requires extension to handle dynamic decomposition model phase counts |

## Build Order

The three pillars have minimal cross-dependencies. Correct sequence based on dependencies:

```
PILLAR 1: Flexible FDS Structure
─────────────────────────────────────────────────────────────
Step 1.1  decomposition-models.json — registry of all models
          (no dependencies; defines the schema everything else references)

Step 1.2  New section templates (section-functional-unit.md,
          section-process-step.md, section-isa88-unit.md)
          (depends on: knowing what models exist from 1.1)

Step 1.3  fds-structure variants (fds-structure-functional.json,
          fds-structure-hybrid.json)
          (depends on: new templates from 1.2)

Step 1.4  Modify new-fds.md workflow — add decomposition model discovery
          (depends on: registry from 1.1; writes model to PROJECT.md)

Step 1.5  Modify discuss-phase.md — load decomposition context for discussion
          (depends on: PROJECT.md schema from 1.4)

Step 1.6  Modify plan-phase.md — select section template from model registry
          (depends on: templates from 1.2, registry from 1.1)

Step 1.7  Extend config_phases.py — support dynamic phase structure per model
          (depends on: new phase structures defined in 1.1)

─────────────────────────────────────────────────────────────
PILLAR 2: LLM Provider Abstraction
─────────────────────────────────────────────────────────────
Step 2.1  provider-format.md reference doc — prompt format specs
          per provider (no dependencies; pure documentation)

Step 2.2  Update CLAUDE-CONTEXT.md — document provider config schema
          for PROJECT.md llm block
          (depends on: format spec from 2.1)

Step 2.3  Modify doc-writer.md agent — add provider-conditional
          prompt construction
          (depends on: format spec from 2.1)

Step 2.4  Modify doc-verifier.md agent — add provider-conditional
          prompt construction
          (depends on: format spec from 2.1)

Step 2.5  Test suite: write a simple FDS section with each target
          provider (Claude, OpenAI, Ollama) to verify output quality
          (depends on: 2.3, 2.4; environment with local model available)

─────────────────────────────────────────────────────────────
PILLAR 3: Docs Engine Visibility
─────────────────────────────────────────────────────────────
Step 3.1  engine_service.py — filesystem walker, frontmatter parser,
          git log reader
          (no dependencies on Pillars 1 or 2; can start in parallel)

Step 3.2  backend/app/api/engine.py — FastAPI router with
          /api/engine/* endpoints
          (depends on: service from 3.1)

Step 3.3  Register engine router in main.py
          (depends on: router from 3.2)

Step 3.4  React EngineExplorer + TemplateViewer + ChangeLog components
          (depends on: API from 3.2; can develop against mock data first)

─────────────────────────────────────────────────────────────
SEQUENCING RECOMMENDATION
─────────────────────────────────────────────────────────────
Pillar 3 can run fully in parallel with Pillars 1 and 2 —
it is additive (new router, new frontend feature) with no
dependencies on the CLI engine changes.

Pillar 2 can start after Pillar 1's Step 1.1 (to know the
PROJECT.md schema), but the bulk of Pillar 2 (agent rewrites)
is independent of Pillar 1's template work.

Recommended execution order for a single developer:
  1. Pillar 1 Steps 1.1–1.3  (schema + templates first, no risk)
  2. Pillar 3 Steps 3.1–3.3  (backend service — gives quick feedback
                                on engine file structure while templates
                                are being written)
  3. Pillar 1 Steps 1.4–1.7  (workflow changes — now templates exist)
  4. Pillar 2 Steps 2.1–2.5  (provider abstraction — last because it
                                requires a working project to test against)
  5. Pillar 3 Step 3.4        (frontend — build against real API)
```

## Sources

- v2.0 codebase — `backend/app/` (FastAPI, services, config_phases.py) — HIGH confidence (direct inspection)
- v1.0 CLI engine — `~/.claude/gsd-docs-industrial/` (CLAUDE-CONTEXT.md, workflows/, templates/, agents/) — HIGH confidence (direct inspection)
- `fds-structure.json` v1.0 — assembly structure, EM-centric dynamic sections — HIGH confidence (direct inspection)
- `SPECIFICATION.md v2.7.0` (referenced in CLAUDE-CONTEXT.md) — canonical domain knowledge SSOT
- `.planning/PROJECT.md` v3.0 milestone goals — HIGH confidence (project source of truth)
- v2.0 key decisions table (PROJECT.md) — "No LLM orchestration in GUI" constraint — HIGH confidence

---
*Architecture research for: GSD-Docs Industrial v3.0 Docs Engine Rearchitecture*
*Researched: 2026-03-31*
*Scope: Integration of 3 new features with existing v2.0 architecture*
