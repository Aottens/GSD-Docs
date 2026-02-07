---
phase: 01-framework-foundation
plan: 02
subsystem: templates
tags: [roadmap, project-scaffold, fds, baseline, packml, isa88]

requires:
  - phase: 01-framework-foundation (plan 01)
    provides: plugin directory structure at ~/.claude/gsd-docs-industrial/

provides:
  - 4 ROADMAP templates (Type A/B/C/D) with correct phase counts
  - PROJECT.md template with YAML config block (standards, language)
  - REQUIREMENTS.md template with type-conditional categories
  - STATE.md template initializing at Phase 1
  - BASELINE.md template with bilingual immutability instruction

affects: [01-03 new-fds command, 01-04 verification, phase-2 discuss/plan commands]

tech-stack:
  added: []
  patterns: [placeholder-variable-templates, base-override-composition, bilingual-instructions]

key-files:
  created:
    - "~/.claude/gsd-docs-industrial/templates/roadmap/type-a-nieuwbouw-standaard.md"
    - "~/.claude/gsd-docs-industrial/templates/roadmap/type-b-nieuwbouw-flex.md"
    - "~/.claude/gsd-docs-industrial/templates/roadmap/type-c-modificatie.md"
    - "~/.claude/gsd-docs-industrial/templates/roadmap/type-d-twn.md"
    - "~/.claude/gsd-docs-industrial/templates/project.md"
    - "~/.claude/gsd-docs-industrial/templates/requirements.md"
    - "~/.claude/gsd-docs-industrial/templates/state.md"
    - "~/.claude/gsd-docs-industrial/templates/baseline.md"
  modified: []

key-decisions:
  - "Standalone templates per type rather than base+overlay composition -- each type has genuinely different phase structures, duplication minimal and acceptable"
  - "BASELINE.md INSTRUCTIE block is bilingual (Dutch + English) as safety-critical instruction"
  - "Templates define structure only (50-109 lines each) -- /doc:new-fds fills content"

patterns-established:
  - "Placeholder variables: {PROJECT_NAME}, {CLIENT}, {DATE}, {LANGUAGE}, {TYPE} etc."
  - "Phase entry format: Goal (one-line), Description (3 bullets), Success Criteria (3 items), Dependencies"
  - "YAML config block in PROJECT.md for standards and language settings"

duration: 4min
completed: 2026-02-07
---

# Phase 01 Plan 02: Scaffold Templates Summary

**8 template files covering all 4 project types: ROADMAP templates (A=6, B=5, C=4, D=2 phases), PROJECT.md with YAML config, REQUIREMENTS.md with type categories, STATE.md at Phase 1, BASELINE.md with bilingual immutability instruction**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-07T08:40:58Z
- **Completed:** 2026-02-07T08:44:57Z
- **Tasks:** 2
- **Files created:** 8

## Accomplishments

- Created 4 ROADMAP templates with correct phase counts per project type (A=6, B=5, C=4, D=2)
- Created PROJECT.md template with YAML config block including standards (PackML/ISA-88) and language settings
- Created REQUIREMENTS.md with type-conditional category guidance and traceability table
- Created BASELINE.md with bilingual INSTRUCTIE block for Type C/D modification projects
- All templates use placeholder variables and stay under 120 lines each

## Task Commits

Each task was committed atomically:

1. **Task 1: Create ROADMAP templates for all 4 project types** - `61a7720` (feat)
2. **Task 2: Create planning artifact templates (project, requirements, state, baseline)** - `ca7c947` (feat)

## Files Created/Modified

- `~/.claude/gsd-docs-industrial/templates/roadmap/type-a-nieuwbouw-standaard.md` - Type A ROADMAP, 6 phases with PackML/ISA-88
- `~/.claude/gsd-docs-industrial/templates/roadmap/type-b-nieuwbouw-flex.md` - Type B ROADMAP, 5 phases flexible standards
- `~/.claude/gsd-docs-industrial/templates/roadmap/type-c-modificatie.md` - Type C ROADMAP, 4 phases delta + BASELINE
- `~/.claude/gsd-docs-industrial/templates/roadmap/type-d-twn.md` - Type D ROADMAP, 2 phases TWN + BASELINE
- `~/.claude/gsd-docs-industrial/templates/project.md` - PROJECT.md skeleton with YAML config
- `~/.claude/gsd-docs-industrial/templates/requirements.md` - REQUIREMENTS.md with type-conditional categories
- `~/.claude/gsd-docs-industrial/templates/state.md` - STATE.md initialization skeleton
- `~/.claude/gsd-docs-industrial/templates/baseline.md` - BASELINE.md with bilingual INSTRUCTIE

## Decisions Made

- **Standalone templates per type:** Each ROADMAP type has genuinely different phase structures (6 vs 5 vs 4 vs 2 phases with different content). Using separate files keeps each template self-contained and easy to understand. Anti-duplication effort goes into command logic, not templates.
- **Bilingual INSTRUCTIE:** The BASELINE.md immutability instruction is in both Dutch and English because it's a safety-critical directive that must be understood regardless of project language setting.
- **Lean templates:** Templates define structure only (44-109 lines). The `/doc:new-fds` command fills in project-specific content. This mitigates Pitfall 5 (template explosion).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created templates directory structure**
- **Found during:** Task 1 (ROADMAP template creation)
- **Issue:** `~/.claude/gsd-docs-industrial/templates/roadmap/` directory did not exist (plan 01-01 created the base directory but not the templates/roadmap subdirectory)
- **Fix:** Created `~/.claude/gsd-docs-industrial/templates/roadmap/` directory
- **Verification:** Directory exists and files created successfully
- **Committed in:** `61a7720` (part of Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Minimal -- directory creation was necessary for file placement. No scope creep.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All 8 templates ready for consumption by `/doc:new-fds` command (plan 01-03)
- ROADMAP templates provide correct phase structures for each project type
- PROJECT.md config block ready for standards and language configuration
- BASELINE.md template ready for Type C/D modification projects
- No blockers for plan 01-03 (new-fds command implementation)

---
*Phase: 01-framework-foundation*
*Completed: 2026-02-07*
