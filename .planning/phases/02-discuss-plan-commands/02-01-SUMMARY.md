---
phase: 02-discuss-plan-commands
plan: 01
subsystem: templates
tags: [fds, equipment-module, state-machine, interface, context, packml, isa88, mermaid, bilingual]

# Dependency graph
requires:
  - phase: 01-framework-foundation
    provides: "Plugin directory structure, templates/ and templates/fds/ directories"
provides:
  - "Equipment module section template with 5 required + 4 optional configurable subsections"
  - "State machine section template with Mermaid stateDiagram-v2 and transition table"
  - "Interface section template with overview, signals, and protocol details"
  - "CONTEXT.md template with XML-tagged sections for discuss-phase output"
affects:
  - "02-discuss-plan-commands (plan 02+: commands reference these templates via @-paths)"
  - "03-write-verify (writer subagents use templates as structural guides)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bilingual column headers: {English / Nederlands} pattern in all tables"
    - "Configurable subsections: YAML frontmatter lists required vs optional"
    - "XML section tags: <domain>, <decisions>, <specifics>, <deferred>"
    - "Mermaid stateDiagram-v2 for PackML state machines"

key-files:
  created:
    - "gsd-docs-industrial/templates/fds/section-equipment-module.md"
    - "gsd-docs-industrial/templates/fds/section-state-machine.md"
    - "gsd-docs-industrial/templates/fds/section-interface.md"
    - "gsd-docs-industrial/templates/context.md"
  modified: []

key-decisions:
  - "Equipment module template has 9 subsections (5 required, 4 optional) with HTML comment markers for optional sections"
  - "I/O table uses all 9 columns: Tag, Description, Type, Signal Range, Eng. Unit, PLC Address, Fail-safe State, Alarm Limits, Scaling"
  - "State machine template includes full PackML state set (14 states) with pre-populated transition table rows"
  - "Interface template protocol details structured with Connection, Data Exchange, Error Handling sub-groups"
  - "CONTEXT.md template uses XML section tags matching CLAUDE-CONTEXT.md established pattern"

patterns-established:
  - "FDS section templates: structural-only with {PLACEHOLDER} values, no content"
  - "Template comment blocks: usage documentation in HTML comments at top"
  - "Bilingual tables: {English / Nederlands} in column headers for language selection"

# Metrics
duration: 4min
completed: 2026-02-08
---

# Phase 2 Plan 1: FDS Section Templates + CONTEXT.md Template Summary

**Structural FDS templates (equipment module with 9-column I/O, PackML state machine with Mermaid diagram, interface with protocol details) plus XML-tagged CONTEXT.md template for discuss-phase output**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-08T07:38:01Z
- **Completed:** 2026-02-08T07:42:09Z
- **Tasks:** 2
- **Files created:** 4

## Accomplishments

- Equipment module template with 5 required + 4 optional subsections, full 9-column I/O table, and bilingual headers
- State machine template with Mermaid stateDiagram-v2 containing all standard PackML states plus structured transition table
- Interface template with overview, signal list, and type-adaptive protocol details sections
- CONTEXT.md template with XML-tagged semantic sections, Claude's Discretion subsection, and Pitfall 7 size guideline

## Task Commits

Each task was committed atomically:

1. **Task 1: Create FDS section templates** - `61589d6` (feat)
2. **Task 2: Create CONTEXT.md template** - `941107d` (feat)

## Files Created/Modified

- `gsd-docs-industrial/templates/fds/section-equipment-module.md` - Equipment module section template (88 lines): description, operating states, parameters, interlocks, 9-column I/O, manual controls, alarm list, maintenance mode, startup/shutdown
- `gsd-docs-industrial/templates/fds/section-state-machine.md` - State machine section template (75 lines): Mermaid stateDiagram-v2 with full PackML states, state description table, transition table
- `gsd-docs-industrial/templates/fds/section-interface.md` - Interface section template (56 lines): overview key-value table, signal list, protocol details with Connection/Data Exchange/Error Handling groups
- `gsd-docs-industrial/templates/context.md` - CONTEXT.md template (77 lines): XML-tagged sections (domain, decisions, specifics, deferred) with Claude's Discretion and Type C/D delta instruction

## Decisions Made

- Equipment module operating states table includes pre-populated rows for IDLE, STARTING, EXECUTE to guide writers on expected granularity
- I/O table shows example rows per signal type (DI, DO, AI, AO) to clarify format expectations
- Interface template adds Physical Layer and Redundancy to overview table beyond the plan specification (these are standard interface properties)
- Interface protocol details organized into three sub-groups (Connection, Data Exchange, Error Handling) for clarity across different protocol types
- State machine transition table pre-populated with all 16 standard PackML transitions as reference rows

## Deviations from Plan

None -- plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All 4 templates ready for plan-phase commands to reference via @-paths
- CONTEXT.md template ready for discuss-phase workflow to use as output structure
- Next plans in Phase 2 (02-02, 02-03) can create the discuss-phase and plan-phase commands that reference these templates

---
*Phase: 02-discuss-plan-commands*
*Completed: 2026-02-08*
