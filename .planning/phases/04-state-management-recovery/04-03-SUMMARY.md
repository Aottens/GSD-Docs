---
phase: 04-state-management-recovery
plan: 03
subsystem: crash-recovery-ui
tags: [resume, auto-detect, command-conflict, smart-defaults, forward-recovery]

dependency_graph:
  requires:
    - "04-01: STATE.md checkpointing with Current Operation structure"
    - "03-02: write-phase workflow with wave execution pattern"
    - "03-03: verify-phase workflow with completion proof pattern"
  provides:
    - "/doc:resume command for standalone crash recovery"
    - "Resume workflow with 6-step execution (detect → verify → display → decide → execute → complete)"
    - "Auto-detect resume when re-running interrupted write-phase"
    - "Command-conflict warnings in write-phase and verify-phase"
  affects:
    - "write-phase.md: Step 3 enhanced with 3a (conflict warning) and 3b (auto-detect resume)"
    - "verify-phase.md: Step 1a added for command-conflict detection"

tech_stack:
  added: []
  patterns:
    - "Smart default: auto-resume with Y/n confirmation (default: Y) for single incomplete operation"
    - "Command-conflict detection: warn + confirm when different command running during interruption"
    - "Belt-and-suspenders verification: STATE.md hint + filesystem proof before resume"
    - "Forward-only recovery: completed plans (SUMMARY.md exists) never re-executed"

key_files:
  created:
    - path: "commands/doc/resume.md"
      purpose: "User-facing /doc:resume slash command"
      lines_added: 66
    - path: "gsd-docs-industrial/commands/resume.md"
      purpose: "Version-tracked copy of resume command"
      lines_added: 66
    - path: "gsd-docs-industrial/workflows/resume.md"
      purpose: "Resume detection and execution workflow"
      lines_added: 346
  modified:
    - path: "gsd-docs-industrial/workflows/write-phase.md"
      purpose: "Auto-detect resume (Step 3b) and command-conflict warning (Step 3a)"
      lines_added: 143
    - path: "gsd-docs-industrial/workflows/verify-phase.md"
      purpose: "Command-conflict detection (Step 1a)"
      lines_added: 111

decisions:
  - summary: "/doc:resume command uses Read/Write/Bash/Glob/Grep/Task tools (Task needed for re-spawning subagents)"
    rationale: "Resume may need to re-run write-phase or verify-phase, requiring Task tool for subagent spawning"
  - summary: "Smart default: auto-resume with Y/n confirmation (default: Y) for single incomplete operation"
    rationale: "Locked user decision from 04-CONTEXT.md"
  - summary: "Command-conflict warning triggers on: different command OR different phase during IN_PROGRESS status"
    rationale: "Prevents engineers from accidentally orphaning interrupted work"
  - summary: "Verify-phase is idempotent: re-running same phase shows 'Re-running verification' message, proceeds normally"
    rationale: "Verification produces new VERIFICATION.md, safe to re-run"
  - summary: "Auto-detect resume in write-phase Step 3b with completion proof verification before offering resume"
    rationale: "Locked user decision: 'Both standalone /doc:resume command AND auto-detect when running the same command'"
  - summary: "Warning text matches locked decision pattern: 'Phase 4 write was interrupted. Continue with verify-phase 3 anyway?'"
    rationale: "Direct quote from 04-CONTEXT.md locked decisions"

metrics:
  duration_minutes: 4
  completed_date: "2026-02-13"
  tasks_completed: 2
  files_created: 3
  files_modified: 2
  lines_added: 732
  commits: 2
---

# Phase 04 Plan 03: /doc:resume Command + Auto-Detect Resume Logic — Summary

Standalone /doc:resume command with smart defaults, auto-detect resume for write-phase re-runs, and command-conflict warnings in write-phase and verify-phase.

## Facts

**What was built:**
- /doc:resume command (66 lines) with Read/Write/Bash/Glob/Grep/Task tools
- Resume workflow (346 lines, 6 steps): detect → verify proofs → display context → smart default → execute → complete
- Write-phase Step 3 split into 3a (command conflict) and 3b (auto-detect resume) with 143 lines added
- Verify-phase Step 1a added for command-conflict detection (111 lines)
- Version-tracked command copy at gsd-docs-industrial/commands/resume.md

**Resume workflow capabilities:**
- Detects interrupted operations from STATE.md Current Operation (IN_PROGRESS status)
- Verifies completion proofs via filesystem (SUMMARY.md + CONTENT.md existence)
- Builds three lists: verified complete, incomplete, partial writes (using 04-01 heuristics)
- Displays context summary: what was running, what completed, what's next
- Smart default: Y/n confirmation for single incomplete operation (default: Y)
- Multiple options: resume, view status, or abandon (preserves completed work)
- Re-executes incomplete work using forward-only recovery (skip verified plans)

**Auto-detect resume (write-phase Step 3b):**
- Detects same command + same phase + IN_PROGRESS status
- Verifies completed plans via file existence before offering resume
- Shows context: started time, wave, completed count, remaining count
- Confirmation: "Resume from wave N? (Y/n)" with default Y
- If declined: asks "Start fresh? (y/N)" with default N (don't re-execute completed work)
- Exports SKIP_PLANS array to wave execution for filtering

**Command-conflict warnings:**
- Write-phase Step 3a: detects different command OR different phase during IN_PROGRESS
- Verify-phase Step 1a: detects interrupted operation before validation
- Warning format: shows interrupted command/phase/wave, explains risk, offers continue or cancel
- Special note for verify-phase when write-phase interrupted: "Verification may find incomplete content"
- Re-running verify-phase for same phase shows: "Previous verify-phase was interrupted. Re-running verification."

**Completion proof:**
All 7 plan verification criteria met:
1. /doc:resume command exists with correct frontmatter ✓
2. Resume workflow has 6 steps (detect → verify → display → decide → execute → complete) ✓
3. Write-phase Step 3 enhanced with auto-detect resume (Step 3b) ✓
4. Write-phase Step 3 enhanced with command-conflict warning (Step 3a) ✓
5. Verify-phase Step 1a added for command-conflict detection ✓
6. Forward-only recovery enforced: SUMMARY.md existence check before skip ✓
7. All locked decisions honored: smart defaults, both standalone + auto-detect, warn + confirm on conflict ✓

## Key Decisions

**Resume command design:**
- Standalone command (/doc:resume) for explicit crash recovery
- Uses Task tool for re-spawning write-phase or verify-phase subagents
- Write tool needed for STATE.md updates after successful resume
- No argument-hint (auto-detects what to resume from STATE.md)
- Version-tracked copy ensures command evolution is tracked

**Smart default logic:**
- Single incomplete operation: auto-resume with Y/n confirmation (default: Y)
- Multiple options (rare): present choices (resume, view status, abandon)
- Filesystem always trusted over STATE.md: completion proofs verified before resume
- Partial writes included in incomplete count for context display

**Auto-detect integration:**
- Write-phase Step 3 checks for interrupted state BEFORE wave execution
- Command-conflict check (Step 3a) runs BEFORE auto-detect check (Step 3b)
- Auto-detect shows context summary with verified vs incomplete plans
- If resume declined, asks about fresh start (prevents accidental re-execution of completed work)

**Command-conflict UX:**
- Warning displays: interrupted command/phase/wave, risk explanation, options (continue or cancel)
- Continue option: proceeds with current command, interrupted operation remains in STATE.md
- Cancel option: displays "Run /doc:resume to complete the interrupted operation." and exits
- Verify-phase idempotent: re-running same phase is safe (produces new VERIFICATION.md)

**Recovery strategy:**
- Forward-only: completed work (SUMMARY.md + CONTENT.md exist) never re-executed
- Completion proof verification: SKIP_PLANS array populated from verified complete list
- Resume from lowest wave number among incomplete plans
- Atomic checkpoints preserved: wave execution logic unchanged from 03-02

## Dependencies

**Requires:**
- 04-01-SUMMARY.md: STATE.md Current Operation section with 8 structured fields
- 03-02-SUMMARY.md: write-phase workflow establishes wave execution pattern and checkpointing
- 03-03-SUMMARY.md: verify-phase workflow establishes completion proof pattern

**Enables:**
- Engineers can recover from crashes without losing completed work
- Re-running interrupted commands auto-detects and offers resume
- Command conflicts prevent accidental state corruption
- /doc:status (04-02) can recommend /doc:resume when interrupted operation detected

**Cross-references:**
- Commands: resume.md (new), write-phase.md (enhanced), verify-phase.md (enhanced)
- Workflows: resume.md (new), write-phase.md (Step 3 split into 3a/3b), verify-phase.md (Step 1a added)
- Templates: state.md (Current Operation section used for detection)
- Must-haves: STAT-03 (resume command), STAT-04 (auto-detect), STAT-07 (command conflict), STAT-06 (forward-only)

## Deviations from Plan

None — plan executed exactly as written. All task actions, verification checks, and done criteria met without modifications or additions.

## Self-Check

Verifying all claimed files and commits exist:

**Files created (expected: 3):**
- commands/doc/resume.md ✓
- gsd-docs-industrial/commands/resume.md ✓
- gsd-docs-industrial/workflows/resume.md ✓

**Files modified (expected: 2):**
- gsd-docs-industrial/workflows/write-phase.md ✓
- gsd-docs-industrial/workflows/verify-phase.md ✓

**Commits (expected: 2):**
- 1096e19: feat(04-03): create /doc:resume command and workflow ✓
- dcf02cd: feat(04-03): add auto-detect resume and command-conflict warnings ✓

**Verification checks run:**
1. /doc:resume has name: doc:resume ✓
2. Version-tracked copy identical to commands/doc/resume.md ✓
3. Resume workflow has <workflow> tags ✓
4. Resume workflow has forward-only recovery references ✓
5. Resume workflow has SUMMARY.md completion proof references (10 matches) ✓
6. Resume workflow has Step 5 (execute resume) ✓
7. Resume workflow line count: 346 (within 250-350 range) ✓
8. Write-phase has auto-detect references (3 matches) ✓
9. Write-phase has interrupted references (16 matches) ✓
10. Write-phase has warning references (6 matches) ✓
11. Verify-phase has interrupted references (15 matches) ✓
12. Verify-phase has warning references (5 matches) ✓
13. Both workflows have resume references (write: 14, verify: 5) ✓

## Self-Check: PASSED

All files exist, all commits present, all verification checks passed.
