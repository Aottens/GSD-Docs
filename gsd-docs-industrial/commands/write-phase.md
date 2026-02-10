---
name: doc:write-phase
description: Generate FDS section content through parallel writing with fresh context per section
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

Generate substantive FDS section content through parallel writing with strict context isolation.

**How it works:**
- Discover all PLAN.md files in phase N and group by wave number
- For each wave (sequential): spawn doc-writer subagents for all plans in the wave (parallel)
- Each writer receives ONLY: PROJECT.md + phase CONTEXT.md + its own PLAN.md + standards (if enabled)
- Checkpoint STATE.md before and after each wave for crash recovery
- Aggregate CROSS-REFS.md from all writers
- Output: one CONTENT.md + one SUMMARY.md per plan, CROSS-REFS.md for the phase

**Context isolation:** The orchestrator builds the EXACT file list for each writer. Writers never receive other plans' files, other CONTENT.md files, or session history. Each section is written with fresh, isolated context to prevent cross-contamination.

**Output:**
- {plan-id}-CONTENT.md (substantive technical content, not stubs)
- {plan-id}-SUMMARY.md (max 150 words, facts only)
- {phase}-CROSS-REFS.md (aggregated cross-references from all writers)

</objective>

<execution_context>
@~/.claude/gsd-docs-industrial/workflows/write-phase.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md
</execution_context>

<context>

**Phase number:** $ARGUMENTS (required)

@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/PROJECT.md

</context>

<process>

Follow the workflow in write-phase.md exactly.

</process>

<success_criteria>

- [ ] All PLAN.md files in phase discovered and grouped by wave
- [ ] Each writer spawned with isolated context (only own PLAN.md, not others)
- [ ] Writers in same wave execute in parallel
- [ ] STATE.md checkpointed before and after each wave
- [ ] Each plan has CONTENT.md (substantive) and SUMMARY.md (150 words max)
- [ ] CROSS-REFS.md created/updated with all cross-references
- [ ] Engineer sees completion summary and knows next step

</success_criteria>
