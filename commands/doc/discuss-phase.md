---
name: doc:discuss-phase
description: Identify gray areas and capture implementation decisions for an FDS phase
argument-hint: "<phase>"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>

Extract implementation decisions that downstream plan and write commands need. For the given phase:

1. Read ROADMAP.md to identify the phase goal and content type
2. Identify gray areas specific to the FDS domain (equipment parameters, interfaces, HMI, safety, architecture)
3. Present gray areas grouped by topic -- let the engineer select which to discuss
4. Deep-dive each selected area at functional spec depth (not surface-level questions)
5. Capture decisions in phase-N/CONTEXT.md

**Output:** `{phase}-CONTEXT.md` -- decisions clear enough that `/doc:plan-phase` and `/doc:write-phase` can act without re-asking the engineer.

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/discuss-phase.md
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

Follow the workflow in `discuss-phase.md` exactly. It contains all 7 steps: phase validation, content type detection, gray area identification, topic presentation, deep-dive discussion, CONTEXT.md capture, and completion summary.

</process>

<success_criteria>

- [ ] Phase validated against ROADMAP.md
- [ ] Gray areas identified specific to phase content type
- [ ] Engineer selected which areas to discuss
- [ ] Each area explored at functional spec depth
- [ ] Scope creep redirected to deferred ideas
- [ ] CONTEXT.md captures decisions, not vague requirements
- [ ] Items marked Claude's Discretion documented but not asked
- [ ] For Type C/D: delta focus maintained via BASELINE.md reference
- [ ] Engineer knows next step is `/doc:plan-phase N`

</success_criteria>
