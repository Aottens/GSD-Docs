# Phase 1: Framework Foundation + /doc:new-fds - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Engineer runs `/doc:new-fds`, classifies a project by type (A/B/C/D), and receives a fully scaffolded `.planning/` workspace with populated artifacts — ready for the discuss-plan-write-verify cycle. This phase delivers the entry point command, classification logic, template composition, and project scaffolding. All downstream commands (discuss, plan, write, verify) depend on this foundation.

</domain>

<decisions>
## Implementation Decisions

### Classification flow
- **Hybrid approach:** Ask targeted questions to suggest a project type, then let engineer confirm or override
- **Two-stage process:** First classify (new vs existing, scope, deliverables), then gather metadata (project name, client, location, language) — keeps concerns separate
- **Three question axes drive classification:**
  - New vs existing system (primary split)
  - Scope-based (number of units, interfaces, complexity)
  - Deliverable-based (full FDS+SDS, FDS only, modification spec, TWN)
- **Override with warning:** If classification answers suggest Type A but engineer picks D, show brief warning about potentially missing sections, then proceed with engineer's choice

### Project type definitions
- **Type A** = Greenfield + formal standards (PackML, ISA-88) → 6 phases. Standards are a requirement from the start and must be enforced
- **Type B** = Greenfield + flexible standards → 4-5 phases. Standards are considered and applied pragmatically, not strictly enforced
- **Type C** = Modification + large scope → 3-4 phases + BASELINE.md. Standards come from whatever the existing system uses
- **Type D** = Modification + small scope (TWN - Technische Wijzigingsnotitie) → 2 phases. Formal technical change notification

### BASELINE.md (Type C/D)
- **Both paths available:** Offer document import if existing docs exist (previous FDS, P&ID references), fall back to structured interview if not
- Claude extracts baseline from imported docs; interview asks about existing units, interfaces, what's changing vs staying

### Scaffolded output
- **ROADMAP.md:** Fully populated with phase descriptions, success criteria, and dependency chains — this is the backbone
- **PROJECT.md:** Fully filled from metadata gathered in stage two (language, client, project type, standards config)
- **REQUIREMENTS.md:** Category structure pre-built from project type (Type A gets all categories, Type D gets subset), but individual requirements discovered during discuss phases
- **STATE.md:** Minimal but functional — current phase = 1, status = pending, progress = 0%
- **Output after completion:** Full summary (project type, phase count, language) + file tree of .planning/ directory + clear next step
- **Auto-commit:** All scaffolded files committed automatically with descriptive message

### Command experience
- **Language selection:** Always ask during project creation, no default assumed
- **Command language matches output language:** If project is Dutch, prompts and messages are in Dutch; if English, in English
- **Prerequisites check:** Verify git repo exists, check for .planning/ conflict, warn about missing optional tools (mermaid-cli) — before starting the flow

### Claude's Discretion
- Phase directory creation strategy (all upfront vs on-demand)
- Re-run behavior when .planning/ already exists (safe approach that preserves existing work)
- Template composition approach (base + overlays vs modular sections — whatever minimizes duplication and stays maintainable)
- Exact classification question wording and flow
- REQUIREMENTS.md category structure per type

</decisions>

<specifics>
## Specific Ideas

- 1-op-1 mapping with GSD workflow: `/gsd:new-project` → `/doc:new-fds`, same conceptual flow adapted for documentation
- The classification tree from CLAUDE-CONTEXT.md section 3 is the canonical reference for type determination logic
- TWN (Technische Wijzigingsnotitie) is the specific document type for Type D — this is a known format in the domain
- Folder structure from CLAUDE-CONTEXT.md section 12 is the target: `.planning/`, `output/`, `diagrams/`, `export/`
- Standards config in PROJECT.md uses opt-in YAML block (`packml: enabled: true`, `isa88: enabled: true`)
- Dynamic ROADMAP evolution after System Overview phase (>5 units detected) — scaffolding should anticipate this pattern

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-framework-foundation*
*Context gathered: 2026-02-07*
