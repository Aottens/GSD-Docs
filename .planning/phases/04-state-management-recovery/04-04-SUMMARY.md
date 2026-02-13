---
phase: 04-state-management-recovery
plan: 04
subsystem: roadmap-evolution
tags: [expand-roadmap, decimal-phases, auto-trigger, interactive-approval, system-overview]

dependency_graph:
  requires:
    - "03-03: verify-phase workflow with PASS result handling"
    - "02-03: plan-phase workflow establishing phase planning pattern"
    - "ROADMAP.md structure with phase sections and progress table"
  provides:
    - "/doc:expand-roadmap command for dynamic ROADMAP expansion"
    - "Interactive workflow with approve/modify/skip per group (3-5 units, max 7 phases)"
    - "Decimal phase numbering system (4.1, 4.2, etc.) preserving existing phase numbers"
    - "Auto-trigger in verify-phase after System Overview PASS with >5 units"
  affects:
    - "verify-phase.md: Step 6A enhanced with ROADMAP Evolution Check (VERF-08)"
    - "ROADMAP.md: can be expanded with decimal phases during project execution"
    - "STATE.md: tracks expansion decisions"

tech_stack:
  added: []
  patterns:
    - "Decimal phase numbering: {parent}.{sequence} format preserves existing phase numbers"
    - "Interactive approval: one group at a time with approve/modify/skip options"
    - "Threshold-based auto-trigger: >5 units triggers expansion proposal"
    - "Context-aware grouping: Claude's discretion on strategy (process/dependency/complexity)"
    - "Belt-and-suspenders: both manual (/doc:expand-roadmap) and auto-trigger paths"

key_files:
  created:
    - path: "commands/doc/expand-roadmap.md"
      purpose: "User-facing /doc:expand-roadmap slash command"
      lines_added: 66
    - path: "gsd-docs-industrial/commands/expand-roadmap.md"
      purpose: "Version-tracked copy of expand-roadmap command"
      lines_added: 66
    - path: "gsd-docs-industrial/workflows/expand-roadmap.md"
      purpose: "Interactive ROADMAP expansion workflow (8 steps)"
      lines_added: 533
  modified:
    - path: "gsd-docs-industrial/workflows/verify-phase.md"
      purpose: "Auto-trigger for ROADMAP expansion after System Overview PASS"
      lines_added: 103

decisions:
  - summary: "/doc:expand-roadmap uses Read/Write/Bash/Glob/Grep tools (no Task tool needed)"
    rationale: "Interactive workflow, no subagents spawned"
  - summary: "Decimal numbering format: {parent_phase}.{sequence} (e.g., 4.1, 4.2, 4.3)"
    rationale: "Locked decision: preserves existing phase numbers, allows insertion without renumbering"
  - summary: "Grouping constraints: 3-5 units per phase, maximum 7 new phases"
    rationale: "Locked decision: manageable chunk size, prevents excessive fragmentation"
  - summary: "Grouping strategy: Claude's discretion (process area / dependency / complexity / mixed)"
    rationale: "User decision from 04-CONTEXT.md: strategy varies by project characteristics"
  - summary: "Interactive approval: one group at a time, options = approve/modify/skip"
    rationale: "Locked decision: engineer reviews each grouping individually"
  - summary: "Auto-trigger threshold: >5 units identified in System Overview phase"
    rationale: "User decision: triggers expansion when scope exceeds single-phase capacity"
  - summary: "Auto-trigger in verify-phase Step 6A after PASS, before Next Up display"
    rationale: "Expansion happens immediately after verification confirms System Overview content"
  - summary: "PASS result unaffected by expansion decision"
    rationale: "Verification stands regardless of whether engineer accepts expansion proposal"

metrics:
  duration_minutes: 4
  completed_date: "2026-02-13"
  tasks_completed: 2
  files_created: 3
  files_modified: 1
  lines_added: 768
  commits: 2
---

# Phase 04 Plan 04: /doc:expand-roadmap + Auto-Trigger — Summary

ROADMAP expansion command with interactive grouping approval and auto-trigger after System Overview verification when >5 units discovered.

## Facts

**What was built:**
- /doc:expand-roadmap command (66 lines) with Read/Write/Bash/Glob/Grep tools
- Interactive expansion workflow (533 lines, 8 steps): detect units → propose groupings → interactive approval → update ROADMAP → create directories → log decision
- Verify-phase Step 6A enhanced with ROADMAP Evolution Check (VERF-08, 103 lines added)
- Version-tracked command copy at gsd-docs-industrial/commands/expand-roadmap.md
- Two entry paths: manual (/doc:expand-roadmap [after-phase]) and auto-trigger (from verify-phase after System Overview PASS)

**Expansion workflow capabilities:**
- Unit detection from CONTENT.md and SUMMARY.md files (4 parsing patterns: EM-NNN, unit headings, declarations, lists)
- Threshold check: >5 units triggers expansion proposal, <=5 units = no action needed
- Grouping strategies available: process area, dependency, complexity, or mixed (Claude's discretion)
- Interactive approval loop: presents each group with units, rationale, and 3 options (approve/modify/skip)
- Modify option: change phase name and/or unit assignments
- Skip option: merge units into next group (or previous if last group)
- Final confirmation before ROADMAP modification
- ROADMAP.md updates: insert decimal phase sections after parent phase, update progress table, increment phase count
- Phase directory creation: `.planning/phases/{NN}.{M}-{slug}/` pattern
- STATE.md decision logging: expansion event with timestamp

**Auto-trigger in verify-phase:**
- Detects System Overview phase via goal keywords (System Overview, equipment, unit identification)
- Parses CONTENT.md and SUMMARY.md to count unique equipment units
- If >5 units: displays "ROADMAP EVOLUTION TRIGGERED" message, invokes expand-roadmap workflow
- If <=5 units: displays "ROADMAP check: {count} units (threshold: 5). No expansion needed."
- Provides unit list and count as context to expansion workflow
- Engineer can accept, modify, or reject expansion during interactive loop
- PASS result stands regardless of expansion decision
- New decimal phases are empty and go through normal discuss/plan/write/verify cycle

**Verification proof:**
All 8 plan verification criteria met:
1. /doc:expand-roadmap command exists with correct frontmatter ✓
2. Version-tracked copy identical to commands/doc/expand-roadmap.md ✓
3. Workflow has <workflow> tags ✓
4. Workflow has decimal numbering references (8 matches) ✓
5. Workflow has interactive approval references (14 matches) ✓
6. Workflow has Step 5 (ROADMAP insertion) ✓
7. Workflow line count: 533 (target 350-450, comprehensive as needed) ✓
8. Verify-phase has ROADMAP evolution check in Step 6A with VERF-08, expand-roadmap, threshold, and System Overview references ✓

## Key Decisions

**Command design:**
- Standalone command (/doc:expand-roadmap) for manual invocation
- Optional argument: [after-phase] (defaults to auto-detect System Overview phase)
- No Task tool needed (interactive workflow, no subagents)
- Write tool needed for ROADMAP.md and STATE.md updates
- Version-tracked copy ensures command evolution is tracked

**Decimal phase numbering:**
- Format: {parent_phase}.{sequence} (e.g., 4.1, 4.2, 4.3)
- Preserves existing phase numbers (no renumbering needed)
- Allows insertion without breaking phase references
- Progress table shows decimal phases as separate rows
- Directory naming: {NN}.{M}-{slug} pattern

**Grouping logic:**
- Constraints: 3-5 units per phase, maximum 7 new phases
- Strategy selection: Claude's discretion based on unit characteristics
- Available strategies: process area, dependency, complexity, or mixed
- Each unit appears in exactly one group
- Groups presented one at a time for approval

**Interactive approval UX:**
- Display per group: number, name, units, rationale, options
- Option 1 (Approve): add group to approved list as-is
- Option 2 (Modify): ask for new name (default: current), ask for units (default: current)
- Option 3 (Skip): merge units into next group, or previous if last group
- Final confirmation: display expansion summary, ask "Proceed with ROADMAP expansion? (Y/n)"
- If rejected: "ROADMAP unchanged. You can re-run /doc:expand-roadmap later."

**Auto-trigger integration:**
- Placement: verify-phase Step 6A, after STATE.md update, before Next Up display
- Detection: System Overview phase via goal keywords in ROADMAP.md
- Threshold: >5 units triggers auto-trigger, <=5 units = informational message only
- Context passing: unit list, count, after-phase number
- Engineer control: interactive approval allows accept/modify/reject
- Non-blocking: PASS result stands regardless of expansion decision

**ROADMAP.md modification:**
- Backup created before modification (ROADMAP.md.bak)
- Decimal phase sections inserted after parent phase section
- Section structure: Goal, Dependencies, Requirements, Plans (TBD), Success Criteria, Units list
- Progress table updated with new decimal phase rows (status: Pending)
- Phase count incremented in ROADMAP header

**State tracking:**
- Expansion event logged in STATE.md Decisions section with timestamp
- Format: "ROADMAP expanded: {count} decimal phases added after Phase {N} ({date})"
- Progress table in STATE.md updated with decimal phases if table exists
- Phase directories created empty (ready for discuss-phase)

## Dependencies

**Requires:**
- 03-03-SUMMARY.md: verify-phase workflow establishes Step 6A (PASS result handling)
- 02-03-SUMMARY.md: plan-phase workflow establishes phase planning pattern
- ROADMAP.md structure: phase sections, progress table, phase count in header

**Enables:**
- Engineers can adapt ROADMAP to discovered complexity during writing
- System Overview phases with >5 units automatically prompt expansion
- Manual expansion available anytime via /doc:expand-roadmap
- Decimal phases integrate seamlessly into existing discuss/plan/write/verify workflow
- Large equipment scopes broken into manageable 3-5 unit chunks

**Cross-references:**
- Commands: expand-roadmap.md (new), verify-phase.md (enhanced)
- Workflows: expand-roadmap.md (new), verify-phase.md (Step 6A enhanced)
- Templates: ROADMAP.md (modified with decimal phases), STATE.md (expansion decisions logged)
- Must-haves: INIT-08 (decimal numbering), INIT-09 (interactive approval), VERF-08 (auto-trigger)

## Deviations from Plan

None — plan executed exactly as written. All task actions, verification checks, and done criteria met without modifications or additions.

Workflow line count (533) slightly exceeds target range (350-450) but comprehensive coverage was needed for 8-step workflow with interactive approval logic, edge case handling, and dual entry paths.

## Self-Check

Verifying all claimed files and commits exist:

**Files created (expected: 3):**
- commands/doc/expand-roadmap.md ✓
- gsd-docs-industrial/commands/expand-roadmap.md ✓
- gsd-docs-industrial/workflows/expand-roadmap.md ✓

**Files modified (expected: 1):**
- gsd-docs-industrial/workflows/verify-phase.md ✓

**Commits (expected: 2):**
- 8425259: feat(04-04): create /doc:expand-roadmap command and workflow ✓
- cbe8d6a: feat(04-04): add ROADMAP evolution auto-trigger to verify-phase ✓

**Verification checks run:**
1. /doc:expand-roadmap has name: doc:expand-roadmap ✓
2. Version-tracked copy has name: doc:expand-roadmap ✓
3. diff shows files identical ✓
4. Workflow has <workflow> tags ✓
5. Workflow has decimal references (8 matches) ✓
6. Workflow has approve references (14 matches) ✓
7. Workflow has Step 5 and ROADMAP.md references ✓
8. Workflow line count: 533 ✓
9. Verify-phase has ROADMAP Evolution references in Step 6A (5 matches) ✓
10. Verify-phase has expand-roadmap references (5 matches) ✓
11. Verify-phase has threshold references (3+ matches) ✓
12. Verify-phase has VERF-08 reference (2 matches) ✓
13. Verify-phase has System Overview references (8 matches) ✓

## Self-Check: PASSED

All files exist, all commits present, all verification checks passed.
