---
name: doc:resume
description: Detect and resume interrupted operations with forward-only recovery
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
---

<objective>

Detect interrupted operations and resume from checkpoint with forward-only recovery.

**How it works:**
- Read STATE.md to detect interrupted operations (status: IN_PROGRESS)
- Verify completion proofs against filesystem (SUMMARY.md existence)
- Show context summary: what was running, what completed, what's next
- Apply smart default: auto-resume if only one incomplete operation; show choices if multiple
- Re-execute incomplete work using forward-only recovery (completed plans never re-executed)

**Recovery principle:** SUMMARY.md existence is the ONLY completion proof. STATE.md is a hint only. If filesystem and STATE.md disagree, trust the filesystem.

**Output:**
- Context summary of interrupted operation
- Smart resume prompt with confirmation
- Re-execution of incomplete work from last checkpoint
- Updated STATE.md with final status

</objective>

<execution_context>
@~/.claude/gsd-docs-industrial/workflows/resume.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md
</execution_context>

<context>

@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/PROJECT.md

</context>

<process>

Follow the workflow in resume.md exactly.

</process>

<success_criteria>

- [ ] Interrupted operation detected from STATE.md Current Operation section
- [ ] Completion proofs verified against filesystem (SUMMARY.md existence)
- [ ] Context summary displayed: what was running, what completed, what's next
- [ ] Smart default applied: auto-resume for single incomplete operation
- [ ] Forward-only recovery: completed plans never re-executed
- [ ] STATE.md updated to COMPLETE status after successful resume

</success_criteria>
