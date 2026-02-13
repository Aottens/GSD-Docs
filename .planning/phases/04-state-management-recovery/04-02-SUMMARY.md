---
phase: 04-state-management-recovery
plan: 02
subsystem: status-reporting
tags: [status-display, progress-tracking, next-action, partial-detection, read-only]

dependency_graph:
  requires:
    - "04-01: STATE.md Current Operation section structure"
    - "04-01: 4-heuristic partial write detection pattern"
  provides:
    - "/doc:status command for project progress overview"
    - "8-step status workflow with filesystem-first verification"
    - "Next action derivation with 9 logic branches"
  affects:
    - "04-03: /doc:resume command (users discover interrupts via /doc:status)"
    - "Engineers: single command to understand project state across sessions"

tech_stack:
  added: []
  patterns:
    - "Read-only status display (no Write tool, no state modification)"
    - "Filesystem as source of truth over STATE.md status field"
    - "SUMMARY.md existence as definitive completion proof"
    - "Multi-source data aggregation (STATE.md + ROADMAP.md + filesystem)"
    - "Priority-based phase status derivation (7 status types)"
    - "Context-aware next action recommendation (9 branches)"

key_files:
  created:
    - path: "commands/doc/status.md"
      purpose: "/doc:status command entry point"
      lines_added: 57
    - path: "gsd-docs-industrial/commands/status.md"
      purpose: "Version-tracked copy of status command"
      lines_added: 57
    - path: "gsd-docs-industrial/workflows/status.md"
      purpose: "Status rendering workflow with 8 steps"
      lines_added: 450

decisions:
  - summary: "Status command is read-only (Read/Bash/Glob/Grep tools only, no Task/Write)"
    rationale: "Status display should never modify project state — pure information retrieval"
  - summary: "Filesystem verification takes precedence over STATE.md status field"
    rationale: "File existence is authoritative, STATE.md is hint only (prevents corruption issues)"
  - summary: "Active phase is first non-verified, non-pending phase"
    rationale: "Surfaces actionable work (blocked → gaps → in-progress → written → planned)"
  - summary: "Next action logic has 9 branches in priority order"
    rationale: "Covers all project states from crash recovery to completion"
  - summary: "Workflow is 450 lines (over 300-400 target but comprehensive)"
    rationale: "Complete 8-step workflow with examples and error handling"

metrics:
  duration_minutes: 3
  completed_date: "2026-02-13"
  tasks_completed: 2
  files_created: 3
  lines_added: 564
  commits: 2
---

# Phase 04 Plan 02: /doc:status Command — Summary

Single-command project status display showing overall progress bar, per-phase table, active phase artifacts, partial write warnings, and recommended next action.

## Facts

**What was built:**
- commands/doc/status.md with Read/Bash/Glob/Grep tools only (no Task/Write for read-only operation)
- Identical version-tracked copy at gsd-docs-industrial/commands/status.md
- gsd-docs-industrial/workflows/status.md with 8 comprehensive steps (450 lines)
- Step 1: Load state from STATE.md + ROADMAP.md + PROJECT.md
- Step 2: Calculate progress from filesystem (SUMMARY.md counts, partial detection)
- Step 3: Display overall progress bar (30-char bar, percentage)
- Step 4: Display per-phase status table (7 status types: Verified/Written/In Progress/Gaps Found/Planned/Pending/Blocked)
- Step 5: Display active phase detail with per-plan artifact table (CONTENT.md size, SUMMARY.md word count)
- Step 6: Display partial write warnings (4-heuristic cascade from Plan 01)
- Step 7: Display current operation info if IN_PROGRESS
- Step 8: Derive and display next action (9 logic branches covering all project states)

**Technical foundation:**
- Filesystem as source of truth: SUMMARY.md existence is completion proof, never trust STATE.md status alone
- Read-only command: no state modification, pure information display
- Multi-source aggregation: STATE.md (operation state) + ROADMAP.md (phase structure) + filesystem (file existence)
- Priority-based status derivation: Verified > Gaps Found > Blocked > Written > In Progress > Planned > Pending
- Context-aware recommendations: next action includes both description and exact command
- DOC > branding throughout (following ui-brand.md patterns)

**Completion proof:**
All 8 verification criteria met:
1. /doc:status command exists with correct frontmatter (Read/Bash/Glob/Grep only) ✓
2. Version-tracked copy at gsd-docs-industrial/commands/status.md is identical ✓
3. Workflow has 8 steps (Step 1 through Step 8) ✓
4. Progress calculation uses SUMMARY.md existence as completion proof ✓
5. Active phase shows per-plan artifact existence (CONTENT.md/SUMMARY.md/VERIFICATION.md) ✓
6. Partial writes flagged with reason and suggested fix ✓
7. Next action derived from project state with exact command ✓
8. STAT-03 requirement fully addressed (status display with next-action derivation) ✓

## Key Decisions

**Command architecture:**
- Read-only operation: no Write or Task tools (status never modifies files)
- Lean command file (57 lines) delegates to comprehensive workflow (450 lines)
- Follows established pattern from verify-phase, write-phase commands
- Version-tracked copy ensures plugin updates don't lose command definition

**Status derivation priority:**
- 7 status types in priority order: Verified (highest) → Written → In Progress → Gaps Found → Planned → Pending → Blocked
- Active phase = first phase that is not Verified and not Pending (surfaces actionable work)
- Phase status determined by filesystem verification, STATE.md is hint only

**Next action logic:**
- 9 branches covering all states: interrupted operation → partial writes → blocked → gaps → needs verification → needs writing → needs planning → needs discussion → complete
- Context provided for each action (e.g., "5 plans ready, 0 written")
- Exact command shown (copy-paste ready)

**Display format:**
- Overall progress bar: 30-char width using █ (filled) and ░ (empty)
- Phase table: Plan counts (N/M or -/- for pending), status indicators (✓ ⚙ ○ ✗)
- Active phase table: File sizes (KB) and word counts for CONTENT.md/SUMMARY.md
- Partial warnings: Reason + fix command
- Next action: Separator lines with prominent command display

## Dependencies

**Requires:**
- 04-01-SUMMARY.md: STATE.md Current Operation section structure (8 fields for Step 7)
- 04-01-SUMMARY.md: 4-heuristic partial detection pattern (used in Step 6)
- ui-brand.md: DOC > banner pattern, status symbols, table formatting
- Phase 3 patterns: SUMMARY.md as completion proof, verification workflow

**Enables:**
- 04-03: /doc:resume command (users discover interrupted operations via status display)
- Engineers: single command to understand project state across sessions
- Next action recommendation guides workflow progression

**Cross-references:**
- Commands: status.md (created), verify-phase.md (pattern reference), write-phase.md (pattern reference)
- Workflows: status.md (created), verify-phase.md (referenced), write-phase.md (referenced)
- References: ui-brand.md (banner/table patterns), CLAUDE-CONTEXT.md (context reference)
- Templates: state.md (Current Operation parsing), roadmap.md (phase structure parsing)
- Must-haves: STAT-03 (status display requirement fully implemented)

## Deviations from Plan

None — plan executed exactly as written. All task actions, verification checks, and done criteria met without modifications or additions.

**Note on line count:** Workflow is 450 lines (target was 300-400). Comprehensive 8-step workflow with examples, error handling, and detailed next-action logic required additional lines. All essential functionality implemented as specified.

## Self-Check

Verifying all claimed files and commits exist:

**Files created (expected: 3):**
- commands/doc/status.md (57 lines) ✓
- gsd-docs-industrial/commands/status.md (57 lines) ✓
- gsd-docs-industrial/workflows/status.md (450 lines) ✓

**Commits (expected: 2):**
- bf20c42: feat(04-02): create /doc:status command and version-tracked copy ✓
- 30212d0: feat(04-02): create status workflow with progress rendering and next-action logic ✓

**Verification checks run:**
1. /doc:status command has correct frontmatter (Read/Bash/Glob/Grep, no Task/Write) ✓
2. Version-tracked copy is identical to command file ✓
3. Workflow has 8 steps (Step 1 through Step 8) ✓
4. Progress calculation uses SUMMARY.md as completion proof ✓
5. Active phase shows per-plan artifact existence ✓
6. Partial writes flagged with reason and fix ✓
7. Next action derived with exact command ✓
8. DOC > branding used throughout ✓

## Self-Check: PASSED

All files exist, all commits present, all verification checks passed.
