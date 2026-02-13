# Phase 4: State Management + Recovery + Dynamic ROADMAP - Context

**Gathered:** 2026-02-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Engineer can resume work after any interruption without losing progress, track project status across sessions, and have the ROADMAP adapt to project complexity discovered during writing. This covers /doc:status, /doc:resume, /doc:expand-roadmap, STATE.md checkpointing, and partial write detection. It does NOT add new writing/verification capabilities — those exist from Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Status display
- Full breakdown by default — phase table + per-section status within active phase + completion percentages
- Overall progress bar at top + detailed table below with per-phase status
- Active phase shows plans + which artifacts exist (CONTENT.md, SUMMARY.md, VERIFICATION.md) as proof of work
- Recommended next action shown with context: "Next: Write phase 4 (3 plans ready, 0 written)" + the command to run

### Resume experience
- Smart default: auto-resume if only one thing was interrupted; show choices if multiple things are incomplete
- Summary context before continuing: what was running + what completed + what's next
- Both standalone /doc:resume command AND auto-detect when running the same command that was interrupted
- Running a different command than what was interrupted triggers warn + confirm: "Phase 4 write was interrupted. Continue with verify-phase 3 anyway?"

### ROADMAP expansion
- Interactive build: system suggests groupings one by one, engineer approves/modifies each group
- Decimal numbering for inserted phases (4.1, 4.2, etc.) — preserves existing phase numbers
- Both manual (/doc:expand-roadmap) and auto-trigger (when >5 units discovered after System Overview verification)

### Interruption handling
- Partial writes flagged in /doc:status AND /doc:verify-phase refuses to run until partials are resolved
- STATE.md checkpoints before and after every wave — granular recovery points
- Completed plans in an interrupted wave are kept + cross-references re-verified (since wave siblings may be missing)

### Claude's Discretion
- Grouping strategy for ROADMAP expansion (by process area, dependency, complexity, or mix — whatever fits the project)
- Partial write detection heuristics (SUMMARY.md as completion proof, content length, markers, abrupt endings)
- Exact checkpoint format in STATE.md

</decisions>

<specifics>
## Specific Ideas

- SUMMARY.md existence is the completion proof pattern (established in Phase 1, enforced here)
- Forward-only recovery: completed work is never re-executed, only incomplete items retry
- The warn + confirm on command conflict prevents engineers from accidentally orphaning interrupted work

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-state-management-recovery*
*Context gathered: 2026-02-13*
