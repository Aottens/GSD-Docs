---
phase: 02-discuss-plan-commands
plan: 03
subsystem: commands
tags: [fds, plan-phase, wave-assignment, dependency-graph, self-verification, gap-closure, configurable-subsections, non-interactive]

# Dependency graph
requires:
  - phase: 02-discuss-plan-commands
    plan: 01
    provides: "FDS section templates (equipment module, state machine, interface) referenced via @-paths in generated plans"
  - phase: 02-discuss-plan-commands
    plan: 02
    provides: "discuss-phase command that produces CONTEXT.md consumed by plan-phase"
  - phase: 01-framework-foundation
    provides: "Plugin directory structure, commands/doc/ directory, ui-brand.md, CLAUDE-CONTEXT.md"
provides:
  - "/doc:plan-phase slash command (lean orchestrator, 61 lines)"
  - "plan-phase workflow with 9-step planning logic (587 lines)"
  - "Doc PLAN.md format: ## Goal, ## Sections, ## Context, ## Template, ## Standards, ## Writing Rules, ## Verification"
  - "Wave assignment algorithm based on dependency graph analysis"
  - "Inline self-verification with 7 checks before completing"
  - "Gap closure mode (--gaps flag) generating targeted fix plans from VERIFICATION.md"
affects:
  - "02-discuss-plan-commands (plan 04: end-to-end verification references plan-phase output)"
  - "03-write-verify (write-phase reads PLAN.md files to spawn writer subagents per wave)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Non-interactive command pattern: reads inputs, generates outputs, no AskUserQuestion"
    - "Dependency graph building for wave assignment"
    - "Inline self-verification (7 checks) without subagent spawning"
    - "Doc PLAN.md format distinct from GSD PLAN.md format"
    - "Configurable EM subsections selected per-EM from CONTEXT.md decisions"

key-files:
  created:
    - "commands/doc/plan-phase.md"
    - "gsd-docs-industrial/commands/plan-phase.md"
    - "gsd-docs-industrial/workflows/plan-phase.md"
  modified: []

key-decisions:
  - "plan-phase is non-interactive: no AskUserQuestion, no Task tool -- reads CONTEXT.md and ROADMAP.md autonomously"
  - "Doc PLAN.md format uses ## headings (Goal, Sections, Context, Template, Standards, Writing Rules, Verification) not GSD <task> XML"
  - "Wave assignment algorithm: topological sort on dependency graph -- independent to Wave 1, dependent to earliest valid, overview/summary last"
  - "Self-verification runs 7 inline checks: structure, wave consistency, no circular deps, CONTEXT.md coverage, template refs valid, standards conditional, naming"
  - "Gap closure mode (--gaps) requires VERIFICATION.md from verify-phase -- errors if not found"
  - "EM subsection selection: 5 required always, 4 optional based on CONTEXT.md mentions per EM"
  - "Standards always by reference (name/path), never inline content"
  - "Error boxes use established ui-brand.md pattern, compressed to single-line descriptions for conciseness"

patterns-established:
  - "Non-interactive command: lean command + detailed workflow, no user interaction"
  - "Dependency-based wave assignment for parallel execution"
  - "Inline self-verification before completing (fix-and-retry pattern)"
  - "Gap closure plan generation from VERIFICATION.md gaps"

# Metrics
duration: 7min
completed: 2026-02-08
---

# Phase 2 Plan 3: /doc:plan-phase Command + Workflow Summary

**Non-interactive plan-phase command (61 lines) with 9-step workflow (587 lines) for dependency-based wave assignment, doc PLAN.md generation with configurable EM subsections, inline 7-check self-verification, and --gaps flag gap closure mode**

## Performance

- **Duration:** 7 min
- **Started:** 2026-02-08T07:52:38Z
- **Completed:** 2026-02-08T07:59:00Z
- **Tasks:** 2
- **Files created:** 3

## Accomplishments

- Lean command file (61 lines) with proper frontmatter (no AskUserQuestion, no Task), --gaps argument-hint, and @-references to workflow + ui-brand + CLAUDE-CONTEXT.md
- 9-step workflow (587 lines) covering argument parsing, phase validation, context loading, content type detection, section analysis, dependency graph building, wave assignment, doc PLAN.md generation, self-verification, gap closure, and completion summary
- Doc PLAN.md format with ## Goal, ## Sections, ## Context, ## Template, ## Standards, ## Writing Rules, ## Verification -- clearly distinct from GSD format
- Configurable equipment module subsections: 5 required (description, operating-states, parameters, interlocks, io-table) + 4 optional (manual-controls, alarm-list, maintenance-mode, startup-shutdown) selected per EM from CONTEXT.md
- 7 inline self-verification checks: structure, wave consistency, no circular dependencies, CONTEXT.md coverage, template references valid, standards conditional, naming convention
- Gap closure mode (Step 8): parses VERIFICATION.md gaps, generates targeted fix plans, all Wave 1

## Task Commits

Each task was committed atomically:

1. **Task 1: Create /doc:plan-phase command file** - `751cc5c` (feat)
2. **Task 2: Create plan-phase workflow file** - `f074759` (feat)

## Files Created/Modified

- `commands/doc/plan-phase.md` - Lean command orchestrator (61 lines): non-interactive, --gaps flag, @-references to workflow/ui-brand/CLAUDE-CONTEXT, success criteria checklist
- `gsd-docs-industrial/commands/plan-phase.md` - Version-tracked copy of command file (identical)
- `gsd-docs-industrial/workflows/plan-phase.md` - Complete planning workflow (587 lines): 9 steps with content type detection, configurable EM subsection selection, dependency graph + wave assignment, doc PLAN.md generation, 7-check self-verification, gap closure mode

## Decisions Made

- Command is non-interactive (no AskUserQuestion) since all decisions come from CONTEXT.md -- engineer already made decisions during discuss-phase
- Error messages compressed to single-line descriptions referencing ui-brand.md pattern for conciseness while maintaining clarity
- Verification checklists organized as universal checks (4 items) plus type-specific additions to avoid redundancy
- Wave assignment uses topological sort on dependency graph rather than predefined rules per content type
- Gap closure plans all assigned to Wave 1 since they are independent targeted fixes
- Template references: EM with state machine references BOTH templates, foundation/architecture/HMI/safety sections describe structure directly (no specific template)

## Deviations from Plan

None -- plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- /doc:plan-phase command ready for use after directory junction installation
- Workflow references all 3 FDS section templates (from plan 02-01) and CONTEXT.md output (from plan 02-02)
- Next plan (02-04) can perform end-to-end verification of the complete Phase 2 command suite
- Phase 3 (write-verify) can build write-phase to consume PLAN.md files generated by this command

---
*Phase: 02-discuss-plan-commands*
*Completed: 2026-02-08*
