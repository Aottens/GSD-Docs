---
phase: 01-framework-foundation
plan: 03
subsystem: commands
tags: [slash-command, workflow, classification, scaffolding, bilingual, frontmatter]

# Dependency graph
requires:
  - phase: 01-framework-foundation (plan 01)
    provides: Plugin directory tree, CLAUDE-CONTEXT.md, ui-brand.md
  - phase: 01-framework-foundation (plan 02)
    provides: ROADMAP templates (4 types), planning artifact templates (project, requirements, state, baseline)
provides:
  - /doc:new-fds slash command entry point
  - new-fds workflow with complete 7-step initialization logic
  - Classification flow (Type A/B/C/D) with override support
  - Bilingual prompts (Dutch/English)
  - Template composition pattern (read + fill, not copy)
  - SUMMARY.md = completion proof pattern established
affects: [01-framework-foundation plan 04, 02-discuss-plan-commands, all downstream /doc:* commands]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Lean command file + detailed workflow file separation"
    - "Frontmatter-driven slash command registration (name, description, allowed-tools)"
    - "@-reference context injection (workflow, ui-brand, CLAUDE-CONTEXT.md)"
    - "AskUserQuestion for structured choices, inline for freeform"
    - "Template composition: read template, fill placeholders, synthesize descriptions"
    - "SUMMARY.md existence as completion proof (not STATE.md status)"

key-files:
  created:
    - "~/.claude/commands/doc/new-fds.md"
    - "~/.claude/gsd-docs-industrial/commands/new-fds.md"
    - "~/.claude/gsd-docs-industrial/workflows/new-fds.md"
  modified: []

key-decisions:
  - "Command file kept lean (62 lines) as orchestrator; all logic in workflow file (544 lines)"
  - "Language selection always first, no default assumed"
  - "Classification uses 2-stage process: type determination then metadata gathering"
  - "Override allowed with explicit warning about consequences"
  - "DOC > prefix on all banners (never GSD >)"
  - "config.json stores project_type, language, git_integration, standards"
  - "Command file also stored in plugin repo under commands/ for version tracking"

patterns-established:
  - "Lean command + detailed workflow: command file is ~50 lines, delegates to workflow for logic"
  - "Bilingual instruction pattern: all user-facing text matches chosen language"
  - "7-step workflow structure: prerequisites, language, classification, metadata, scaffold, commit, summary"
  - "Template composition: never copy templates verbatim, always read and fill with project-specific content"
  - "Completion proof: SUMMARY.md existence, not STATE.md status"

# Metrics
duration: 5min
completed: 2026-02-07
---

# Phase 1 Plan 3: /doc:new-fds Command + Workflow Summary

**/doc:new-fds command file (62-line lean orchestrator) and workflow file (544-line execution logic) implementing full project initialization: prerequisites, bilingual language selection, 4-type classification with override, metadata gathering, template-based scaffolding, and auto-commit**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-07T08:48:13Z
- **Completed:** 2026-02-07T08:53:34Z
- **Tasks:** 2
- **Files created:** 3

## Accomplishments

- Created `/doc:new-fds` command file with proper frontmatter (name, description, 7 allowed-tools) and @-references to workflow, ui-brand, and CLAUDE-CONTEXT.md
- Created comprehensive workflow with all 7 steps: prerequisites check (git, .planning/ conflict, optional tools), language selection (Dutch/English always first), two-stage classification (new/mod split then standards/scope then type A/B/C/D with override warning), metadata gathering (name, client, location, EM count, standards for A, existing system for C/D), scaffold generation from templates, auto-commit, and completion summary with Next Up block
- Established template composition pattern (read and fill, never copy verbatim) and SUMMARY.md = completion proof pattern

## Task Commits

Each task was committed atomically:

1. **Task 1: Create /doc:new-fds command file** - `3c107fa` (feat)
2. **Task 2: Create new-fds workflow file** - `eae29a3` (feat)

## Files Created

- `~/.claude/commands/doc/new-fds.md` - Slash command entry point (62 lines, lean orchestrator)
- `~/.claude/gsd-docs-industrial/commands/new-fds.md` - Version-tracked copy of command file
- `~/.claude/gsd-docs-industrial/workflows/new-fds.md` - Full execution logic (544 lines, 7 steps)

## Decisions Made

- Command file kept to 62 lines (plan target was 40-60) -- slightly above due to complete success criteria checklist, but still lean
- All logic delegated to workflow file, keeping command file as pure orchestrator
- Command file also tracked in plugin repo under `commands/` directory for version control (the `~/.claude/commands/doc/` path is not in any git repo)
- Workflow uses `@~/.claude/gsd-docs-industrial/templates/...` @-references for template loading (not hardcoded paths)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created ~/.claude/commands/doc/ directory**
- **Found during:** Task 1 (command file creation)
- **Issue:** The `~/.claude/commands/doc/` directory did not exist yet
- **Fix:** Created the directory with `mkdir -p ~/.claude/commands/doc`
- **Files modified:** Directory creation only
- **Verification:** Directory exists, command file written successfully

**2. [Rule 2 - Missing Critical] Added version tracking for command file**
- **Found during:** Task 1 (command file creation)
- **Issue:** Command file at `~/.claude/commands/doc/` is outside any git repo, so it would not be version-tracked
- **Fix:** Created `commands/` directory in plugin repo and stored a copy there
- **Files modified:** `~/.claude/gsd-docs-industrial/commands/new-fds.md`
- **Verification:** File committed to plugin repo, git log shows commit

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 missing critical)
**Impact on plan:** Both fixes necessary for correct operation. No scope creep.

## Issues Encountered

None -- plan executed smoothly.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Command file is installed and discoverable by Claude Code at `~/.claude/commands/doc/new-fds.md`
- Workflow file references all templates from plans 01-01 and 01-02
- Ready for plan 01-04 (end-to-end verification checkpoint)
- No blockers

---
*Phase: 01-framework-foundation*
*Completed: 2026-02-07*
