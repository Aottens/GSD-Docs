---
name: doc:plan-phase
description: Generate section plans with wave assignments for parallel FDS writing
argument-hint: "<phase> [--gaps]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

<objective>

Create one PLAN.md per section for FDS phase N with wave assignments.

**Default flow:** Read context --> Analyze sections --> Generate plans --> Assign waves --> Self-verify --> Done
**Gap closure flow:** Read VERIFICATION.md --> Generate fix plans --> Done

Each plan tells a writer subagent: what to write, what context to load, which template to use, which standards apply, and how to verify quality.

**Output:** `NN-MM-PLAN.md` files in the phase directory, one per section.

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/plan-phase.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md

</execution_context>

<context>

Phase number and flags: $ARGUMENTS (parse for phase number and --gaps flag)

@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/PROJECT.md

</context>

<process>

Follow the workflow in plan-phase.md exactly. It contains all 9 steps: argument parsing (with --gaps detection), phase validation, context loading, section analysis, dependency graph building, wave assignment, plan generation, self-verification, and completion summary.

</process>

<success_criteria>

- [ ] Phase validated against ROADMAP.md
- [ ] CONTEXT.md read for decisions
- [ ] One PLAN.md per section generated (NN-MM-PLAN.md format)
- [ ] Each plan has: goal, sections, context, template reference, verification checklist
- [ ] Wave assignments based on dependency analysis
- [ ] Plans self-verified before completing
- [ ] Standards referenced by name, not inline
- [ ] Engineer sees wave summary and knows next step

</success_criteria>
