# Architecture Patterns: GSD-Docs Industrial

**Domain:** Claude Code documentation plugin (FDS/SDS generation)
**Researched:** 2026-02-06
**Confidence:** HIGH (derived from live GSD reference implementation + specification v2.7.0)

---

## 1. Recommended Architecture

GSD-Docs Industrial is a **command-driven orchestration system** where Markdown command files define workflows, subagents execute heavy operations with fresh context, and a file-based state machine tracks progress across sessions.

### 1.1 System Topology

```
                    USER
                     |
                     v
          ┌──────────────────────┐
          |   Claude Code CLI    |
          |  (command dispatch)  |
          └──────────┬───────────┘
                     |
                     v
    ┌────────────────────────────────────┐
    |     COMMAND LAYER                  |
    |  ~/.claude/commands/doc/*.md       |
    |                                    |
    |  new-fds   discuss-phase           |
    |  plan-phase  write-phase           |
    |  verify-phase  review-phase        |
    |  complete-fds  generate-sds        |
    |  export  status  resume            |
    └────────────┬───────────────────────┘
                 |
       ┌─────────┴──────────┐
       v                    v
┌──────────────┐   ┌───────────────────┐
| ORCHESTRATOR |   | REFERENCE LAYER   |
| (main ctx)   |   |                   |
| Reads state, |   | references/       |
| spawns agents|   |   standards/      |
|              |   |   typicals/       |
└──────┬───────┘   |   writing-guide   |
       |           |   verification    |
       v           | templates/        |
┌──────────────┐   |   roadmap/        |
| SUBAGENTS    |   |   fds/            |
| (fresh ctx)  |   |   project, plan   |
|              |   └───────────────────┘
| doc-writer   |            ^
| doc-verifier |            |
| doc-planner  |     (loaded via @-refs
| doc-reviewer |      per command)
└──────┬───────┘
       |
       v
┌──────────────────────────────────────┐
|     PROJECT STATE LAYER              |
|  [project-dir]/.planning/            |
|                                      |
|  PROJECT.md  REQUIREMENTS.md         |
|  ROADMAP.md  STATE.md                |
|  CROSS-REFS.md  config.json          |
|  BASELINE.md (Type C/D)              |
|                                      |
|  phases/                             |
|    01-foundation/                    |
|      CONTEXT.md                      |
|      01-01-PLAN.md                   |
|      01-01-CONTENT.md                |
|      01-01-SUMMARY.md                |
|      VERIFICATION.md                 |
└──────────────────────────────────────┘
       |
       v
┌──────────────────────────────────────┐
|     OUTPUT LAYER                     |
|  [project-dir]/                      |
|                                      |
|  output/                             |
|    FDS-[Name]-v[X.Y].md             |
|    SDS-[Name]-v[X.Y].md             |
|    RATIONALE.md                      |
|    EDGE-CASES.md                     |
|    ENGINEER-TODO.md                  |
|    TRACEABILITY.md                   |
|                                      |
|  diagrams/                           |
|    mermaid/  rendered/  external/    |
|                                      |
|  export/                             |
|    *.docx                            |
└──────────────────────────────────────┘
```

### 1.2 How It Maps to GSD

GSD-Docs follows a 1:1 mapping from GSD's code-producing architecture to a documentation-producing architecture. The structural patterns are identical; only the _payload_ changes.

| GSD Component | GSD-Docs Equivalent | What Changes |
|---------------|---------------------|--------------|
| `~/.claude/commands/gsd/*.md` | `~/.claude/commands/doc/*.md` | Namespace only |
| `~/.claude/get-shit-done/` | `~/.claude/gsd-docs-industrial/` | Content files |
| `workflows/*.md` | `workflows/*.md` | Execution steps adapted for docs |
| `templates/phase-prompt.md` | `templates/plan.md` | Output is CONTENT.md, not code |
| `references/verification-patterns.md` | `references/verification-patterns.md` | Checks content completeness, not code stubs |
| `gsd-executor` subagent | `doc-writer` subagent | Writes prose sections instead of code |
| `gsd-verifier` subagent | `doc-verifier` subagent | Checks documentation completeness instead of codebase |
| `gsd-planner` subagent | `doc-planner` subagent | Plans sections instead of code tasks |
| Per-task git commits | Per-plan git commits (optional) | Documents have different commit granularity |
| `SUMMARY.md` (AI-readable) | `SUMMARY.md` (AI-readable, max 150 words) | Same purpose, more constrained |

---

## 2. Component Boundaries

### 2.1 Component Registry

| Component | Location | Responsibility | Communicates With |
|-----------|----------|----------------|-------------------|
| **Command Files** | `~/.claude/commands/doc/*.md` | Entry points; define allowed tools, load execution context | Claude Code CLI, Workflow files |
| **Workflow Files** | `~/.claude/gsd-docs-industrial/workflows/*.md` | Execution logic; step-by-step process for each command | Subagents, State files, Templates |
| **Templates** | `~/.claude/gsd-docs-industrial/templates/` | Scaffolding for output files (ROADMAP, PLAN, CONTENT structure) | Workflow files (read at generation time) |
| **References** | `~/.claude/gsd-docs-industrial/references/` | Domain knowledge (standards, writing guidelines, verification patterns) | Subagents (loaded via @-refs) |
| **ROADMAP Templates** | `templates/roadmap/type-{a,b,c,d}*.md` | Phase structure per project type | `new-fds` command (read during classification) |
| **FDS Section Templates** | `templates/fds/section-*.md` | Structured output format for content sections | `doc-writer` subagent (loaded during writing) |
| **Standards References** | `references/standards/packml/`, `references/standards/isa-88/` | Authoritative standard definitions | Loaded conditionally based on PROJECT.md config |
| **Typicals Library** | `references/typicals/CATALOG.json` + `library/` | Reusable software block definitions | `generate-sds` command |
| **PROJECT.md** | `[project]/.planning/PROJECT.md` | Project identity, configuration, constraints | All commands read this |
| **STATE.md** | `[project]/.planning/STATE.md` | Checkpoint/recovery, progress tracking, decisions | All commands read/write this |
| **ROADMAP.md** | `[project]/.planning/ROADMAP.md` | Phase structure with goals and requirements mapping | plan-phase, write-phase, verify-phase, status |
| **CROSS-REFS.md** | `[project]/.planning/CROSS-REFS.md` | Cross-reference registry between sections | write-phase (write), verify-phase (check), complete-fds (validate) |

### 2.2 Boundary Rules

**Rule 1: Commands are thin orchestrators.**
A command file (.md in commands/doc/) should contain:
- Frontmatter (name, tools, hints)
- @-references to workflow and context files
- Process steps that delegate to subagents for heavy work
- Routing logic (what to show user, what to spawn next)

The command file itself should NOT contain domain logic, verification patterns, or template content. Those live in workflows/, references/, and templates/.

**Rule 2: Subagents get fresh context with explicit boundaries.**
Each subagent receives ONLY:
- The specific workflow file (e.g., `workflows/write-section.md`)
- The current PLAN.md
- PROJECT.md (for configuration)
- CONTEXT.md (for decisions about this phase)
- Relevant standards (if enabled)
- Relevant templates (for output format)

A subagent NEVER receives:
- Other phases' CONTENT.md files
- Other plans' CONTENT.md files
- Previous conversation history
- The full ROADMAP (only the relevant phase goal)

**Rule 3: STATE.md is the system's memory.**
Every command reads STATE.md first and writes it last. If a session crashes, STATE.md tells the next session exactly where to resume. This is the single most important file for crash recovery.

**Rule 4: Standards are opt-in and isolated.**
PackML and ISA-88 references live in their own directories. They are loaded ONLY when `PROJECT.md` has `standards.packml.enabled: true` or `standards.isa88.enabled: true`. No command should assume standards are present. The conditional loading pattern from the spec (section 6.2) must be followed.

**Rule 5: CROSS-REFS.md is the integration registry.**
Cross-references between sections are tracked centrally, not embedded in individual files. `write-phase` logs references as they're created. `verify-phase` checks them. `complete-fds` validates them strictly and blocks on broken refs.

---

## 3. Data Flow

### 3.1 Primary Flow: Project Lifecycle

```
/doc:new-fds
     |
     | Creates: PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md
     | Reads: User input, ROADMAP templates, classification logic
     |
     v
/doc:discuss-phase N
     |
     | Reads: ROADMAP.md (phase goal), STATE.md
     | Creates: phases/0N-name/CONTEXT.md
     | Updates: STATE.md, RATIONALE.md (on decisions)
     |
     v
/doc:plan-phase N
     |
     | Reads: CONTEXT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md
     | Loads: FDS section templates, standards (if enabled)
     | Spawns: doc-planner subagent
     | Creates: phases/0N-name/*-PLAN.md (with wave assignments)
     | Updates: STATE.md
     |
     v
/doc:write-phase N
     |
     | Reads: PLAN.md files (discovers and groups by wave)
     | Per plan (parallel within wave):
     |   Spawns: doc-writer subagent
     |   Writer reads: PLAN.md, CONTEXT.md, PROJECT.md, standards
     |   Writer creates: CONTENT.md, SUMMARY.md
     |   Writer logs: cross-references to CROSS-REFS.md
     |   Writer logs: edge cases to EDGE-CASES.md
     | Updates: STATE.md (after each wave)
     |
     v
/doc:verify-phase N
     |
     | Reads: ROADMAP.md (phase goal), all CONTENT.md, SUMMARY.md
     | Reads: CROSS-REFS.md (for reference checks)
     | Spawns: doc-verifier subagent
     | Verifier checks: completeness, consistency, standards compliance
     | Creates: VERIFICATION.md
     | Routes: PASS -> next phase | GAPS -> plan-phase --gaps
     | Optional: Fresh Eyes review
     |
     v
/doc:review-phase N (optional)
     |
     | Reads: CONTENT.md files for the phase
     | Interacts: User presents to client/engineer
     | Creates: REVIEW.md with feedback
     | Routes: OK -> next phase | Issues -> plan-phase --gaps
     |
     v
/doc:complete-fds
     |
     | Reads: ALL phases' CONTENT.md, CROSS-REFS.md
     | Validates: Cross-references (strict), orphan sections
     | Concatenates: All CONTENT.md into single FDS document
     | Creates: output/FDS-[Name]-v[X.Y].md
     | Creates: output/RATIONALE.md, EDGE-CASES.md, ENGINEER-TODO.md
     | Archives: .planning/archive/v[X.Y]/
     |
     v
/doc:generate-sds
     |
     | Reads: output/FDS-*.md
     | Reads: references/typicals/CATALOG.json
     | Matches: Each equipment to typicals
     | Creates: output/SDS-[Name]-v[X.Y].md, TRACEABILITY.md
     |
     v
/doc:export
     |
     | Reads: output/*.md
     | Reads: templates/huisstijl.docx
     | Renders: Mermaid diagrams -> PNG (or flags complex ones)
     | Creates: export/*.docx
```

### 3.2 Secondary Flow: State Management

```
Every command entry:
     |
     ├─ Read STATE.md
     |    ├─ Current position (phase, plan, status)
     |    ├─ Accumulated decisions
     |    ├─ Blockers/concerns
     |    └─ Last operation (for crash detection)
     |
     ├─ Update STATE.md before operation
     |    └─ status: IN_PROGRESS, command, phase, wave
     |
     ├─ [Execute operation]
     |
     └─ Update STATE.md after operation
          ├─ status: COMPLETE (or INTERRUPTED on failure)
          ├─ Current position updated
          └─ New decisions logged
```

### 3.3 Secondary Flow: Gap Closure Loop

```
verify-phase N
     |
     ├─ PASS → proceed to next phase
     |
     └─ GAPS_FOUND
          |
          v
     plan-phase N --gaps
          |
          | Reads: VERIFICATION.md (gaps list)
          | Creates: additional PLAN.md files (e.g., 03-07-fix-PLAN.md)
          |
          v
     write-phase N
          |
          | Discovers: only unwritten plans (those without SUMMARY.md)
          | Writes: fix CONTENT.md files
          |
          v
     verify-phase N (re-verify)
          |
          ├─ PASS → proceed
          └─ GAPS_FOUND → loop again (max 3 iterations)
```

### 3.4 Secondary Flow: Dynamic ROADMAP Evolution

```
verify-phase 2 (System Overview) → PASS
     |
     ├─ Analyze CONTENT.md from System Overview
     |    ├─ Count identified units/equipment
     |    └─ Group by functional area
     |
     ├─ Decision gate:
     |    ├─ <=5 units → keep static ROADMAP (single "Functional Units" phase)
     |    └─ >5 units → propose expanded ROADMAP
     |
     └─ If expanding:
          ├─ Present grouping proposal to user
          ├─ User approves or adjusts
          ├─ Rewrite ROADMAP.md with new phases (3-5 units per phase)
          └─ Update STATE.md
```

### 3.5 Context Loading Pattern Per Subagent

This is the most critical architectural pattern. Each subagent must have precisely scoped context.

**doc-writer subagent context (writing a section):**
```
LOADED:
  PROJECT.md                    (project identity, config)
  CONTEXT.md                    (phase-level decisions)
  [current]-PLAN.md             (what to write, verification criteria)
  templates/fds/section-*.md    (output format templates)
  references/standards/*        (IF enabled in PROJECT.md)
  references/writing-guidelines.md

NOT LOADED:
  Other plans' PLAN.md          (prevents cross-contamination)
  Other plans' CONTENT.md       (prevents context pollution)
  ROADMAP.md                    (not needed for writing)
  Previous conversation         (fresh context)
```

**doc-verifier subagent context (verifying a phase):**
```
LOADED:
  ROADMAP.md                    (phase goal - the verification target)
  All CONTENT.md in this phase  (what to verify)
  All SUMMARY.md in this phase  (quick overview of each section)
  CONTEXT.md                    (decisions that content should match)
  CROSS-REFS.md                 (reference validation)
  references/verification-patterns.md
  references/standards/*        (IF enabled - for compliance checks)

NOT LOADED:
  Other phases' content         (only verifying this phase)
  PLAN.md files                 (verifying outcome, not process)
```

---

## 4. Component Details

### 4.1 Command Files (Entry Points)

Each command file follows the GSD frontmatter pattern:

```markdown
---
name: doc:write-phase
description: Write all sections of a phase with wave-based parallelization
argument-hint: "<phase-number>"
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
  - AskUserQuestion
---

<objective>
[What this command accomplishes]
</objective>

<execution_context>
@~/.claude/gsd-docs-industrial/workflows/write-phase.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
</execution_context>

<context>
Phase: $ARGUMENTS
@.planning/ROADMAP.md
@.planning/STATE.md
</context>

<process>
[Orchestration steps - validate, discover plans, spawn subagents, collect results]
</process>
```

**Key insight from GSD:** The command file is the ORCHESTRATOR. It stays lean (15% context budget). Heavy work happens in subagents with fresh context.

### 4.2 Workflow Files (Execution Logic)

Workflow files contain the detailed execution logic that subagents follow. They are loaded via `@`-references in the command's `<execution_context>`.

Needed workflows:
| Workflow | Purpose | Spawned By |
|----------|---------|------------|
| `write-section.md` | How to write a single FDS section (the doc-writer agent's instructions) | write-phase orchestrator |
| `verify-phase.md` | How to verify phase completeness (doc-verifier instructions) | write-phase/verify-phase orchestrator |
| `plan-phase.md` | How to create section plans (doc-planner instructions) | plan-phase orchestrator |
| `generate-sds.md` | How to transform FDS into SDS | generate-sds command |
| `complete-fds.md` | How to merge phases into final document | complete-fds command |
| `review-phase.md` | How to conduct client review | review-phase command |

### 4.3 Templates (Scaffolding)

Templates provide structure for generated files. They are NOT content -- they are skeletons with placeholders.

| Template Category | Files | Used By |
|-------------------|-------|---------|
| **ROADMAP templates** | `type-a-nieuwbouw-standaard.md`, `type-b-nieuwbouw-flex.md`, `type-c-modificatie.md`, `type-d-twn.md` | `/doc:new-fds` |
| **FDS section templates** | `section-equipment-module.md`, `section-state-machine.md`, `section-interface.md` | doc-writer subagent |
| **Planning templates** | `project.md`, `requirements.md`, `context.md`, `plan.md` | `/doc:new-fds`, `/doc:discuss-phase`, `/doc:plan-phase` |
| **Reporting templates** | `verification-report.md`, `summary.md` | doc-verifier, doc-writer |
| **Export template** | `huisstijl.docx` | `/doc:export` |

### 4.4 References (Domain Knowledge)

References are loaded conditionally and provide authoritative domain information.

| Reference | Loaded When | Purpose |
|-----------|------------|---------|
| `standards/packml/STATE-MODEL.md` | `standards.packml.enabled: true` | PackML state definitions, transitions |
| `standards/packml/UNIT-MODES.md` | `standards.packml.enabled: true` | PackML operating modes |
| `standards/isa-88/EQUIPMENT-HIERARCHY.md` | `standards.isa88.enabled: true` | ISA-88 hierarchy (Unit > EM > CM) |
| `standards/isa-88/TERMINOLOGY.md` | `standards.isa88.enabled: true` | ISA-88 standard terms |
| `writing-guidelines.md` | Always (for doc-writer) | Prose quality, style, terminology |
| `verification-patterns.md` | Always (for doc-verifier) | How to detect stubs, incomplete sections |
| `typicals/CATALOG.json` | Only for generate-sds | Typical software blocks for SDS matching |

### 4.5 State Machine (STATE.md)

STATE.md serves three purposes:
1. **Progress tracking** - Where are we in the workflow?
2. **Decision memory** - What has been decided across sessions?
3. **Crash recovery** - What was happening when we stopped?

```markdown
# STATE.md

## Current Position
- Phase: 3 (Equipment Modules - Intake)
- Plan: 03-02 (EM-102 Weigh Station)
- Status: writing

## Current Operation
- command: write-phase
- phase: 3
- wave: 1
- wave_total: 2
- plans_done: [03-01]
- plans_pending: [03-02, 03-03]
- started: 2026-02-06T21:45:00Z
- status: IN_PROGRESS

## Completed
- Phase 1: PASS (verified)
- Phase 2: PASS (verified, ROADMAP expanded to 9 phases)
- Phase 3: 03-01 PASS, 03-02 in progress

## Decisions
| Phase | Decision | Rationale |
|-------|----------|-----------|
| 1 | PackML enabled | Client requirement |
| 2 | 5 functional areas | System analysis |
| 3 | Settling time = 3s | Weegcel spec + marge |

## Versions
- FDS: v0.2 (draft)
- SDS: - (not started)

## Blockers
- Wacht op capaciteit info voor EM-400
```

### 4.6 Subagent Types

| Agent Type | Role | Context Budget | Spawned By |
|------------|------|---------------|------------|
| **doc-writer** | Write a single FDS section (CONTENT.md + SUMMARY.md) | 100% fresh | write-phase orchestrator |
| **doc-planner** | Create PLAN.md files for a phase | 100% fresh | plan-phase orchestrator |
| **doc-verifier** | Verify phase completeness against goals | 100% fresh | write-phase/verify-phase orchestrator |
| **doc-reviewer** | Conduct structured review with user | Main context | review-phase command |
| **doc-sds-generator** | Transform FDS section to SDS section | 100% fresh | generate-sds command |

---

## 5. Patterns to Follow

### Pattern 1: Orchestrator + Subagent Delegation

**What:** Command files orchestrate; subagents execute. The orchestrator uses ~15% of context for coordination; each subagent gets a fresh 200K context window.

**When:** Any operation that involves reading multiple files + producing substantial output (writing sections, verifying phases, planning sections).

**Why:** Documentation writing consumes enormous context. A single FDS section for an equipment module can easily be 2-3K words. Writing multiple sections sequentially in one context would degrade quality. Fresh context per section means consistent quality throughout.

**GSD precedent:** `execute-phase.md` spawns `gsd-executor` subagents per plan. GSD-Docs `write-phase` spawns `doc-writer` subagents per plan.

### Pattern 2: Wave-Based Parallelization

**What:** Group plans into waves based on dependencies. All plans in a wave execute in parallel (multiple `Task` calls in one message). Waves execute sequentially.

**When:** `write-phase` with multiple independent sections. Equipment modules within the same functional area can often be written in parallel.

**Why:** Equipment modules EM-100 and EM-200 don't need each other's CONTENT.md to be written. But EM-200's CONTENT.md might need to reference EM-100's interlock, which is captured at the PLAN level (in CONTEXT.md decisions), not by reading EM-100's output.

**Wave assignment happens at plan-phase time**, not at write-phase time. The planner assigns waves based on:
- `wave: 1` - Independent sections, no cross-references needed
- `wave: 2` - Sections that reference wave 1 outputs (via SUMMARY.md, not full CONTENT)
- `wave: 3` - Integration sections (e.g., "Algemene Interlocks" that references all EMs)

### Pattern 3: Goal-Backward Verification

**What:** Verify that the phase GOAL was achieved, not just that tasks were completed. Start from desired outcome and work backwards to check evidence.

**When:** After all plans in a phase are written.

**Why adapted for docs:** In code, verification checks that functions exist and are wired. In documentation, verification checks that:
- All required sections exist and have substantive content (not stubs)
- Parameters have ranges and units (not placeholders)
- State tables have entry/exit conditions (not just state names)
- Interlocks have conditions and actions (not just IDs)
- Cross-references point to real sections

**Verification levels for documents:**
| Level | Code Equivalent | Doc Equivalent |
|-------|----------------|----------------|
| Exists | File exists | Section exists in CONTENT.md |
| Substantive | Not a stub (real implementation) | Not a placeholder (real technical content) |
| Complete | All exports/functions present | All required subsections present (states, params, interlocks, I/O) |
| Consistent | Types match, APIs wired | Matches CONTEXT.md decisions, standards compliance |
| Wired | Imports work, calls succeed | Cross-references resolve, section numbers correct |

### Pattern 4: Conditional Standards Loading

**What:** PackML and ISA-88 references are only loaded when enabled in PROJECT.md. Commands check configuration before injecting @-references.

**When:** Any command or subagent that might need standards content.

**Implementation:**
```markdown
<execution_context>
@~/.claude/gsd-docs-industrial/workflows/write-section.md
@~/.claude/gsd-docs-industrial/references/writing-guidelines.md

<!-- Conditional: loaded by orchestrator based on PROJECT.md config -->
<!-- IF standards.packml.enabled -->
@~/.claude/gsd-docs-industrial/references/standards/packml/STATE-MODEL.md
<!-- IF standards.isa88.enabled -->
@~/.claude/gsd-docs-industrial/references/standards/isa-88/TERMINOLOGY.md
</execution_context>
```

The orchestrator (command file) reads PROJECT.md, checks the standards config, and constructs the subagent prompt with appropriate @-references included or excluded.

### Pattern 5: Forward-Only Recovery

**What:** If a session crashes, completed work is preserved. Resume always goes forward -- never rolls back.

**When:** Any interruption (token limit, network error, user close).

**How:** STATE.md tracks `Current Operation` with fine-grained progress. On resume:
1. Read STATE.md
2. Identify incomplete operation
3. Check which plans have CONTENT.md + SUMMARY.md (complete)
4. Skip completed plans
5. Continue from first incomplete plan

A CONTENT.md is considered "partial" (needs rewrite) if:
- Missing entirely
- Less than 200 characters
- Contains `[TO BE COMPLETED]` marker
- Ends abruptly (no proper closing)

### Pattern 6: SUMMARY.md as Cross-Phase Bridge

**What:** Each written section gets a compact SUMMARY.md (max 150 words, facts only) that other agents can read without loading the full CONTENT.md.

**When:** After each section is written. Used by later phases that need to reference earlier content.

**Why:** A full equipment module CONTENT.md might be 3K words. A verification agent checking 6 modules would consume 18K tokens just on content. With SUMMARY.md, the same check costs ~900 tokens for the summaries.

**SUMMARY.md format:**
```markdown
# SUMMARY: 03-02 EM-200 Bovenloopkraan

## Facts
- Type: Equipment Module
- States: 6 (PackML compliant)
- Parameters: 4
- Interlocks: 3
- I/O: 8 DI, 4 DO, 2 AI

## Key Decisions
- No collision detection (client choice)
- E-stop = controlled stop, position maintained

## Dependencies
- Interlock with EM-100 (waterbad niveau)
- Interface to SCADA via Modbus TCP

## Cross-refs
- Interlock IL-200-01 -> see phase-5
- HMI screen -> see phase-8/08-02
```

---

## 6. Anti-Patterns to Avoid

### Anti-Pattern 1: Cross-Context Content Loading

**What:** Loading another section's CONTENT.md into a writer's context to "maintain consistency."

**Why bad:** Consumes context budget, creates false dependencies, and actually reduces quality by diluting focus. A writer working on EM-200 does not need to read EM-100's full content.

**Instead:** Use SUMMARY.md for cross-references. If EM-200 needs to know about EM-100's interlock, the PLAN.md for EM-200 should state the interlock ID and behavior (sourced from CONTEXT.md decisions). The writer doesn't need EM-100's prose.

### Anti-Pattern 2: Monolithic Phase Writing

**What:** Writing all sections of a phase in a single context window sequentially.

**Why bad:** Context degrades with each section. Section 6 of a 6-section phase will be noticeably lower quality than section 1. For a Type A project with 18 equipment modules, this would be catastrophic.

**Instead:** Each section gets its own doc-writer subagent with fresh context. Quality is uniform across all sections.

### Anti-Pattern 3: Hardcoded Standards

**What:** Embedding PackML state names or ISA-88 terminology directly in templates or workflow logic.

**Why bad:** Type B projects (Nieuwbouw Flex) explicitly do NOT use PackML/ISA-88. Hardcoding standards would produce incorrect output for half the project types.

**Instead:** Standards are reference files loaded conditionally. Templates use generic placeholders (`{STATES_TABLE}`) that are filled differently based on whether standards are enabled.

### Anti-Pattern 4: Stateless Commands

**What:** Commands that don't read STATE.md first or don't update it after.

**Why bad:** Without STATE.md as the ground truth, crash recovery is impossible. The system loses track of where it is, what's been decided, and what's pending.

**Instead:** Every command reads STATE.md as its FIRST action and updates it as its LAST action. Long operations (write-phase with multiple waves) update STATE.md between waves.

### Anti-Pattern 5: Premature Cross-Reference Resolution

**What:** Trying to resolve all cross-references during section writing (e.g., exact section numbers for future sections).

**Why bad:** During phase 3 writing, phases 4-8 don't exist yet. Section numbers aren't assigned. Cross-references to future content will be wrong.

**Instead:** Use phase-relative references during writing (`see phase-5/HMI`). Exact section numbers (`see par 8.2.4`) are resolved during `/doc:complete-fds` when all content exists. CROSS-REFS.md tracks these for final resolution.

### Anti-Pattern 6: Over-Specifying Language in Framework

**What:** Hardcoding Dutch or English text in templates, workflow instructions, or reference content.

**Why bad:** The framework must support both Dutch and English output. Hardcoded language makes the framework single-language.

**Instead:** Framework files (commands, workflows) are in English (operational language). FDS templates have language-neutral structure with language-specific content loaded from the `output.language` config. Section headers, field labels, and standard terminology come from language-specific reference files.

---

## 7. Suggested Build Order

Build order follows dependency chains. Each phase produces artifacts that later phases consume.

### Phase 1: Skeleton + new-fds

**What to build:**
- Command registration pattern (`~/.claude/commands/doc/new-fds.md`)
- Framework directory structure (`~/.claude/gsd-docs-industrial/`)
- ROADMAP templates for all 4 project types
- PROJECT.md, REQUIREMENTS.md, STATE.md, config.json generation
- Classification flow (Type A/B/C/D)
- CLAUDE-CONTEXT.md (condensed spec for quick loading)

**Why first:** Every subsequent command depends on the `.planning/` structure that new-fds creates. Without valid PROJECT.md and ROADMAP.md, nothing else can run.

**Depends on:** Nothing (foundation)

**Produces:** Working `/doc:new-fds` that creates a valid project skeleton

### Phase 2: discuss-phase + plan-phase

**What to build:**
- `/doc:discuss-phase` command + workflow
- CONTEXT.md template
- Gray area identification per domain (equipment, interfaces, HMI, safety)
- `/doc:plan-phase` command + workflow (orchestrator)
- PLAN.md template adapted for documentation (sections instead of code tasks)
- Wave assignment logic
- doc-planner subagent prompt/workflow
- FDS section templates (equipment-module, state-machine, interface)

**Why second:** Planning depends on ROADMAP + PROJECT from phase 1. Writing (phase 3) depends on PLANs from this phase.

**Depends on:** Phase 1 (project skeleton must exist)

**Produces:** Working discuss + plan flow that creates CONTEXT.md and PLAN.md files

### Phase 3: write-phase + Core Verification

**What to build:**
- `/doc:write-phase` command (orchestrator with wave execution)
- doc-writer subagent prompt/workflow (`write-section.md`)
- CONTENT.md generation from PLAN + CONTEXT + templates
- SUMMARY.md generation (max 150 words)
- CROSS-REFS.md logging during writing
- EDGE-CASES.md logging during writing
- `/doc:verify-phase` command
- doc-verifier subagent prompt/workflow
- Documentation-specific verification patterns
- Gap closure flow (verify -> plan --gaps -> write -> re-verify)

**Why third:** This is the core value delivery -- actually producing FDS content. Verification is bundled here because write + verify is an inseparable cycle (gap closure loop).

**Depends on:** Phase 2 (PLAN.md files must exist to write from)

**Produces:** Working write + verify cycle that produces verified FDS sections

### Phase 4: State Management + Recovery

**What to build:**
- `/doc:status` command
- `/doc:resume` command
- Interrupt detection (STATE.md status: INTERRUPTED)
- Partial write detection
- Forward-only recovery logic
- Dynamic ROADMAP evolution (post-System Overview expansion)
- `/doc:review-phase` command (client review)
- REVIEW.md template

**Why fourth:** Once the core write/verify cycle works, robustness features (crash recovery, status) and user-facing review make the system production-ready for the core workflow. Dynamic ROADMAP evolution is here because it triggers after phase 2 verification (System Overview), so the verify-phase infrastructure must exist first.

**Depends on:** Phase 3 (write/verify must work before recovery can be meaningful)

**Produces:** Robust core workflow with recovery and status tracking

### Phase 5: Standards Integration

**What to build:**
- PackML reference files (STATE-MODEL.md, UNIT-MODES.md)
- ISA-88 reference files (EQUIPMENT-HIERARCHY.md, TERMINOLOGY.md)
- Conditional loading mechanism in orchestrators
- Standards compliance verification in doc-verifier
- Standards-aware FDS section templates (equipment module with PackML states)

**Why fifth:** Standards are opt-in enhancements to the core workflow. The core must work without them first (Type B and D projects never use them). Building them as an overlay ensures the conditional loading pattern is correct.

**Depends on:** Phase 3 (write/verify working) -- standards plug into the writer and verifier

**Produces:** Full Type A project support with PackML/ISA-88

### Phase 6: complete-fds + Knowledge Transfer

**What to build:**
- `/doc:complete-fds` command
- Cross-phase content merging
- Cross-reference strict validation
- Orphan section detection
- RATIONALE.md aggregation (from per-phase entries)
- EDGE-CASES.md aggregation
- ENGINEER-TODO.md generation
- Fresh Eyes review feature
- Versioning (`/doc:release`)
- Archive workflow

**Why sixth:** complete-fds is the "end of the line" for FDS. It needs all upstream content to exist. Knowledge transfer (RATIONALE, EDGE-CASES) has been accumulated during phases 2-4 and is aggregated here.

**Depends on:** Phases 1-5 (all phases complete to have content to merge)

**Produces:** Complete FDS document output

### Phase 7: SDS Generation + Export

**What to build:**
- `/doc:generate-sds` command
- CATALOG.json schema and initial typicals
- FDS-to-SDS transformation logic
- Typicals matching algorithm
- TRACEABILITY.md generation
- `/doc:export` command
- Pandoc + huisstijl.docx integration
- Mermaid diagram rendering (with fallback to ENGINEER-TODO)

**Why last:** SDS depends on a complete FDS. Export depends on final documents. These are downstream transformations, not core authoring.

**Depends on:** Phase 6 (complete FDS must exist)

**Produces:** Full pipeline: FDS -> SDS -> DOCX

### Build Order Summary

```
Phase 1: Skeleton + new-fds
    |
    v
Phase 2: discuss-phase + plan-phase
    |
    v
Phase 3: write-phase + Verification (CORE VALUE)
    |
    v
Phase 4: State Management + Recovery + Review
    |
    v
Phase 5: Standards Integration (PackML, ISA-88)
    |
    v
Phase 6: complete-fds + Knowledge Transfer
    |
    v
Phase 7: SDS Generation + Export
```

**Critical path:** Phases 1-3 are the minimum viable pipeline. After phase 3, you can manually run the discuss -> plan -> write -> verify cycle for any project type and produce verified FDS sections.

---

## 8. File Inventory: What to Create

### 8.1 Command Files (in `~/.claude/commands/doc/`)

| File | Maps to GSD | Priority |
|------|-------------|----------|
| `new-fds.md` | `new-project.md` | Phase 1 |
| `discuss-phase.md` | `discuss-phase.md` | Phase 2 |
| `plan-phase.md` | `plan-phase.md` | Phase 2 |
| `write-phase.md` | `execute-phase.md` | Phase 3 |
| `verify-phase.md` | (part of execute-phase) | Phase 3 |
| `review-phase.md` | `verify-work.md` | Phase 4 |
| `status.md` | `progress.md` | Phase 4 |
| `resume.md` | `resume-work.md` | Phase 4 |
| `complete-fds.md` | `complete-milestone.md` | Phase 6 |
| `generate-sds.md` | (new, no GSD equivalent) | Phase 7 |
| `export.md` | (new, no GSD equivalent) | Phase 7 |
| `release.md` | (new, no GSD equivalent) | Phase 6 |

### 8.2 Workflow Files (in `~/.claude/gsd-docs-industrial/workflows/`)

| File | Purpose | Priority |
|------|---------|----------|
| `new-fds.md` | Classification, project setup | Phase 1 |
| `discuss-phase.md` | Gray area identification, CONTEXT creation | Phase 2 |
| `plan-phase.md` | Section planning, wave assignment | Phase 2 |
| `write-section.md` | Single section writing (doc-writer agent) | Phase 3 |
| `write-phase.md` | Wave orchestration for multiple sections | Phase 3 |
| `verify-phase.md` | Goal-backward documentation verification | Phase 3 |
| `review-phase.md` | Client/engineer review process | Phase 4 |
| `complete-fds.md` | Merging, cross-ref validation | Phase 6 |
| `generate-sds.md` | FDS-to-SDS transformation | Phase 7 |
| `export.md` | DOCX export pipeline | Phase 7 |

### 8.3 Templates (in `~/.claude/gsd-docs-industrial/templates/`)

| File | Purpose | Priority |
|------|---------|----------|
| `roadmap/type-a-nieuwbouw-standaard.md` | Type A ROADMAP skeleton | Phase 1 |
| `roadmap/type-b-nieuwbouw-flex.md` | Type B ROADMAP skeleton | Phase 1 |
| `roadmap/type-c-modificatie.md` | Type C ROADMAP skeleton | Phase 1 |
| `roadmap/type-d-twn.md` | Type D ROADMAP skeleton | Phase 1 |
| `project.md` | PROJECT.md skeleton | Phase 1 |
| `requirements.md` | REQUIREMENTS.md skeleton | Phase 1 |
| `state.md` | STATE.md skeleton | Phase 1 |
| `context.md` | CONTEXT.md skeleton | Phase 2 |
| `plan.md` | PLAN.md skeleton (adapted from GSD phase-prompt) | Phase 2 |
| `fds/section-equipment-module.md` | EM section structure | Phase 2 |
| `fds/section-state-machine.md` | State diagram section | Phase 2 |
| `fds/section-interface.md` | Interface section structure | Phase 2 |
| `summary.md` | SUMMARY.md skeleton (max 150 words) | Phase 3 |
| `verification-report.md` | VERIFICATION.md skeleton | Phase 3 |
| `review.md` | REVIEW.md skeleton | Phase 4 |
| `huisstijl.docx` | Corporate styling template | Phase 7 |

### 8.4 References (in `~/.claude/gsd-docs-industrial/references/`)

| File | Purpose | Priority |
|------|---------|----------|
| `writing-guidelines.md` | Prose quality, terminology, style rules | Phase 3 |
| `verification-patterns.md` | Doc-specific completeness checks | Phase 3 |
| `standards/packml/STATE-MODEL.md` | PackML state definitions | Phase 5 |
| `standards/packml/UNIT-MODES.md` | PackML operating modes | Phase 5 |
| `standards/isa-88/EQUIPMENT-HIERARCHY.md` | ISA-88 hierarchy | Phase 5 |
| `standards/isa-88/TERMINOLOGY.md` | ISA-88 terminology | Phase 5 |
| `typicals/CATALOG.json` | Typicals library catalog | Phase 7 |
| `typicals/library/` | Individual typical files | Phase 7 |
| `ui-brand.md` | UI formatting guidelines (from GSD) | Phase 1 |

### 8.5 Root File

| File | Purpose | Priority |
|------|---------|----------|
| `CLAUDE-CONTEXT.md` | Condensed spec for quick Claude context loading | Phase 1 |

---

## 9. Scalability Considerations

| Concern | Type D (2 phases) | Type B (5-9 phases) | Type A (9-20+ phases) |
|---------|-------------------|---------------------|----------------------|
| **Context per section** | ~50% per section (small) | ~70% per section (medium) | ~80%+ per section (large EMs) |
| **Parallel writers** | 1-2 (sequential OK) | 3-4 per wave | 3-5 per wave (memory-bound) |
| **ROADMAP management** | Static (2 phases) | May expand (>5 units) | Will expand (dynamic) |
| **Cross-references** | Minimal | Moderate (20-40 refs) | Heavy (100+ refs) |
| **Verification time** | Quick (check 2-3 sections) | Moderate (check 10-15 sections) | Long (check 20+ sections) |
| **Session management** | Single session possible | 3-5 sessions | 10-20+ sessions |

**Scaling strategy:** The wave-based parallelization and per-section fresh context patterns scale linearly. The only bottleneck is cross-reference management at `complete-fds` time, which requires reading all SUMMARY.md files at once. For a 20-section FDS with 150-word summaries, that's ~3000 words -- well within context budget.

---

## Sources

- GSD reference implementation: `~/.claude/get-shit-done/` (v1.6.4) -- read directly
- GSD command files: `~/.claude/commands/gsd/` -- read directly (new-project, plan-phase, execute-phase, progress, discuss-phase)
- GSD workflow files: `~/.claude/get-shit-done/workflows/` -- read directly (execute-phase, execute-plan, verify-phase, discuss-phase)
- GSD templates: `~/.claude/get-shit-done/templates/phase-prompt.md` -- read directly
- SPECIFICATION.md v2.7.0: `C:\Users\Aotte\Documents\Projects\GSD-Docs\SPECIFICATION.md` -- read directly
- PROJECT.md: `C:\Users\Aotte\Documents\Projects\GSD-Docs\.planning\PROJECT.md` -- read directly

All findings are HIGH confidence -- derived from reading actual source files, not from web search or training data.
