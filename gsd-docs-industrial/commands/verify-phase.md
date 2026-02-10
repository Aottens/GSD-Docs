---
name: doc:verify-phase
description: Verify FDS section content against phase goals using 5-level cascade verification
argument-hint: "<phase>"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
---

<objective>

Verify that phase N documentation achieves its goals (not just that files exist).

**Core innovation:** Goal-backward verification. Derive must-have truths from ROADMAP.md phase goal, verify those truths at 5 levels (exists, substantive, complete, consistent with CONTEXT.md, standards-compliant), then route gaps through a self-correcting loop.

**Process:**
- Read phase goal from ROADMAP.md
- Derive 3-7 observable truths that must be true for goal achievement
- Spawn doc-verifier subagent to check each truth at 5 levels
- Produce VERIFICATION.md with pass/gap status
- Track gap closure cycle count (max 2)
- Route gaps to /doc:plan-phase N --gaps OR escalate to ENGINEER-TODO.md + block phase

**Output:** VERIFICATION.md in phase directory with summary table (quick scan) and detailed findings.

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/verify-phase.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md

</execution_context>

<context>

Phase number: $ARGUMENTS (required)

@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/PROJECT.md

</context>

<process>

Follow the workflow in verify-phase.md exactly.

</process>

<success_criteria>

- [ ] Phase goals read from ROADMAP.md
- [ ] Must-have truths derived (goal-backward)
- [ ] 5-level cascade run for each truth
- [ ] Cross-references checked (warn-only for unwritten targets)
- [ ] VERIFICATION.md produced with summary table + detailed findings
- [ ] Status is PASS or GAPS_FOUND
- [ ] If GAPS_FOUND: engineer knows to run /doc:plan-phase N --gaps
- [ ] If max cycles reached: ENGINEER-TODO.md created and phase blocked
- [ ] Cycle count tracked in VERIFICATION.md and STATE.md

</success_criteria>
