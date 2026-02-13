---
name: doc:status
description: Display project progress with per-phase status, artifact details, and recommended next action
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

<objective>

Display comprehensive project status derived from three sources: STATE.md (operation state), ROADMAP.md (phase structure), and filesystem (actual file existence as proof of work). Status is read-only and never modifies any files.

**Key displays:**
- Overall progress bar with completion percentage
- Per-phase status table (Pending, In Progress, Complete, Verified, Blocked)
- Active phase detail with per-plan artifact existence (CONTENT.md, SUMMARY.md, VERIFICATION.md)
- Partial write flags with reason and suggested fix
- Recommended next action with exact command

**Output:** Status display in terminal with DOC > branding.

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/status.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md

</execution_context>

<context>

@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/PROJECT.md

</context>

<process>

Follow the workflow in status.md exactly. This workflow renders overall progress, per-phase status table, active phase detail with artifact existence, partial write warnings, current operation info, and recommended next action.

</process>

<success_criteria>

- [ ] Overall progress bar displayed with percentage
- [ ] Per-phase status table shows all phases from ROADMAP.md
- [ ] Active phase shows per-plan artifact existence
- [ ] Partial writes flagged with reason
- [ ] Recommended next action shown with exact command
- [ ] No files modified (read-only command)

</success_criteria>
