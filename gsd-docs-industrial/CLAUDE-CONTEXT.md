# GSD-Docs Industrial - Claude Context

**Version:** 0.1.0
**Source:** Condensed from SPECIFICATION.md v2.7.0
**Purpose:** Quick context loading for all /doc:* commands. Load this file to understand project types, workflow, folder structure, and agent rules.

---

<section name="what-is-gsd-docs">

## 1. What GSD-Docs Is

GSD-Docs is a **1:1 mapping of GSD to documentation**. The same workflow GSD uses for code, GSD-Docs uses for FDS/SDS documents.

| GSD (code) | GSD-Docs (documentation) |
|---|---|
| /gsd:new-project | /doc:new-fds |
| /gsd:discuss-phase N | /doc:discuss-phase N |
| /gsd:plan-phase N | /doc:plan-phase N |
| /gsd:execute-phase N | /doc:write-phase N |
| /gsd:verify-phase N | /doc:verify-phase N |
| /gsd:verify-work N | /doc:review-phase N |
| /gsd:complete-milestone | /doc:complete-fds |
| - | /doc:generate-sds |
| - | /doc:export |

### Core Principles

1. **GSD workflow** - Proven system, do not reinvent
2. **Fresh context per task** - No context pollution between sections
3. **Goal-backward verification** - Goals achieved, not just tasks completed
4. **Gap closure loop** - Verify finds gaps, fix, re-verify
5. **4 project types** - Structure adapts to project scope
6. **Standards as opt-in** - PackML, ISA-88 never pushed, only loaded when enabled

</section>

<section name="workflow">

## 2. Complete Workflow

```
/doc:new-fds
    |-- Classification (Type A/B/C/D)
    |-- PROJECT.md, REQUIREMENTS.md, ROADMAP.md
    v
PER PHASE:
    /doc:discuss-phase N --> CONTEXT.md (gray areas, decisions)
    /doc:plan-phase N ----> *-PLAN.md (section plans, wave assignments)
    /doc:write-phase N ---> *-CONTENT.md + *-SUMMARY.md (parallel writing)
    /doc:verify-phase N --> VERIFICATION.md
        |-- PASS --> next phase
        |-- GAPS --> /doc:plan-phase N --gaps --> fix --> re-verify
    /doc:review-phase N --> REVIEW.md (optional, with client)
    v
/doc:complete-fds --> FDS-[Project]-v[X.Y].md (assembly + cross-ref validation)
/doc:generate-sds --> SDS-[Project]-v[X.Y].md + TRACEABILITY.md
/doc:export --------> *.docx (Pandoc + huisstijl.docx)
```

**State management:** STATE.md tracks progress (current phase, plan, wave, status). Updated before and after each operation. Forward-only recovery on interrupts.

</section>

<section name="project-types">

## 3. Project Type Classification

```
/doc:new-fds asks:

New or Modification?
|-- NEW --> Standards required?
|   |-- Yes --> TYPE A (Greenfield + Standards)
|   +-- No  --> TYPE B (Greenfield Flex)
+-- MODIFICATION --> Scope?
    |-- Substantial --> TYPE C (Modification Large)
    +-- Limited     --> TYPE D (Modification Small / TWN)
```

### Type Overview

| Type | Description | ROADMAP Phases | Template |
|---|---|---|---|
| **A** | Greenfield + Standards (PackML, ISA-88) | 6 phases | fds-nieuwbouw-standaard |
| **B** | Greenfield Flex (pragmatic standards) | 4-5 phases | fds-nieuwbouw-flex |
| **C** | Modification Large (delta from baseline) | 3-4 phases | fds-modificatie |
| **D** | Modification Small (TWN) | 2 phases | twn-template |

### Type A Phases
1. Foundation (intro, definitions, standards scope)
2. System Architecture (overview, equipment hierarchy, operating modes)
3. Equipment Modules (per EM: description, states, parameters, interlocks)
4. Control and HMI (control philosophy, HMI requirements, screen descriptions)
5. Interfaces and Safety (external interfaces, safety, interlocks overview)
6. Appendices (signal list, parameter list, state transition tables)

### Type B Phases
1. Foundation (intro, definitions, scope)
2. System Overview (description, functional blocks, process flow)
3. Functional Units (per unit: description, operation, parameters, interlocks)
4. HMI and Interfaces (operation, external connections, communication)
5. Appendices (optional)

### Type C Phases
1. Scope and Baseline (change description, BASELINE.md reference, change/no-change scope)
2. Delta Functional (modified functionality, new equipment, impact on existing)
3. Delta HMI and Interfaces (modified/new screens, interface changes)
4. Verification and Appendices (test criteria, regression check, delta signal list)

### Type D Phases
1. Change Description (description, reason, scope in/out)
2. Implementation (technical changes, impact analysis, test criteria)

### BASELINE.md (Type C/D Only)

For modifications, the existing system is captured as immutable reference:
- Lists existing equipment with UNCHANGED/MODIFIED markers
- Defines change scope (what changes vs what does not)
- AI must treat baseline as given, describe only the DELTA
- Never suggest rewriting existing unchanged functionality

### Dynamic ROADMAP Evolution

After System Overview phase completion (>5 units identified):
- System proposes ROADMAP expansion with units grouped into phases (3-5 units each, max 7)
- Engineer can accept, adjust groupings, or reject
- Types A/B: triggered after phase 2. Type C: after phase 1. Type D: never (too small)

</section>

<section name="context-loading">

## 4. Context Loading Rules

Each write subagent receives fresh, scoped context:

**LOADED:**
- PROJECT.md (project config, standards settings, language)
- phase-N/CONTEXT.md (decisions from discuss-phase)
- Current PLAN.md (this section's plan only)
- Standards references (if enabled in PROJECT.md)

**NOT LOADED:**
- Other PLAN.md files
- Other CONTENT.md files
- Previous conversation history

This prevents context pollution. Each section is written independently. Cross-references use symbolic references (never hardcoded section numbers).

</section>

<section name="summary-pattern">

## 5. SUMMARY.md Pattern

Each written section produces a SUMMARY.md -- a compact AI-readable summary enabling quick cross-reference checks without loading full CONTENT.md.

**Rules:**
- Maximum 150 words
- Facts only, no prose
- Always include: key decisions, dependencies, cross-references
- Counts: states, parameters, interlocks, I/O points

**Structure:**
```markdown
# SUMMARY: NN-MM [Section Name]

## Facts
- Type: [Equipment Module / Interface / State Machine / ...]
- [Quantified metrics]

## Key Decisions
- [Decision and rationale]

## Dependencies
- [Links to other sections/equipment]

## Cross-refs
- [Symbolic references to other sections]
```

SUMMARY.md existence is the **completion proof** for a section. STATE.md status alone is not reliable -- verify by checking SUMMARY.md files.

</section>

<section name="folder-structure">

## 6. Folder Structure

### Framework (in ~/.claude/gsd-docs-industrial/)
```
gsd-docs-industrial/
|-- workflows/              # Command definitions
|-- templates/
|   |-- roadmap/            # Type A/B/C/D ROADMAP templates
|   +-- fds/                # Section templates (equipment, state-machine, interface)
|-- references/
|   |-- standards/
|   |   |-- packml/         # PackML state model, unit modes
|   |   +-- isa-88/         # Equipment hierarchy, terminology
|   |-- typicals/           # CATALOG.json + library
|   |-- ui-brand.md         # DOC-branded UI patterns
|   +-- writing-guidelines.md
+-- CLAUDE-CONTEXT.md       # This file
```

### Per-Project Structure
```
project-folder/
|-- .planning/
|   |-- PROJECT.md          # Project config (type, standards, language)
|   |-- REQUIREMENTS.md     # Functional requirements
|   |-- ROADMAP.md          # Phases and goals
|   |-- BASELINE.md         # (Type C/D only) existing system reference
|   |-- STATE.md            # Progress tracking
|   +-- phases/
|       |-- 01-foundation/
|       |   |-- CONTEXT.md
|       |   |-- 01-01-PLAN.md
|       |   |-- 01-01-CONTENT.md
|       |   |-- 01-01-SUMMARY.md
|       |   +-- VERIFICATION.md
|       +-- 02-architecture/
|           +-- ...
|-- intake/                 # Source documents, drawings, meetings
|-- output/                 # Final FDS/SDS markdown
|-- diagrams/               # Mermaid source + rendered PNG
+-- export/                 # DOCX exports
```

</section>

<section name="standards-integration">

## 7. Standards Integration

Standards are **opt-in only**, configured in PROJECT.md:

```yaml
standards:
  packml:
    enabled: true
    modes: [PRODUCTION, MANUAL, MAINTENANCE]
  isa88:
    enabled: true
    hierarchy_depth: 3
```

When enabled:
- PackML: Use exact state names (IDLE, STARTING, EXECUTE, COMPLETING, COMPLETE, RESETTING, etc.)
- ISA-88: Use hierarchy (Unit > Equipment Module > Control Module)
- Verification checks compliance against reference lists

When not enabled: Do not load standards references, do not enforce terminology.

</section>

<section name="versioning">

## 8. Versioning

Schema: `v[MAJOR].[MINOR]`
- MAJOR = Client releases (1.0, 2.0, ...)
- MINOR = Internal iterations (0.1-0.9, 1.1-1.9, ...)

FDS and SDS versioned independently. SDS always references its source FDS version.

</section>

---
*Condensed from SPECIFICATION.md v2.7.0*
*Framework version: 0.1.0*
