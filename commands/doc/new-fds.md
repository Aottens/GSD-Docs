---
name: doc:new-fds
description: Create a new FDS project with classification and scaffolding
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

<objective>

Initialize a new FDS/SDS documentation project through a structured flow: prerequisites check, language selection, project classification (Type A/B/C/D), metadata gathering, workspace scaffolding, and auto-commit.

**Creates:**
- `.planning/PROJECT.md` -- project config (type, standards, language)
- `.planning/REQUIREMENTS.md` -- requirement categories by type
- `.planning/ROADMAP.md` -- phase structure from type template
- `.planning/STATE.md` -- progress tracking
- `.planning/BASELINE.md` -- existing system reference (Type C/D only)
- `.planning/config.json` -- project settings
- `intake/`, `output/`, `diagrams/`, `export/` directories

**After this command:** Run `/doc:discuss-phase 1` to start the first phase.

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/new-fds.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md

</execution_context>

<context>

This command creates `.planning/` -- it does not read from it. No project artifacts exist yet.

</context>

<process>

Follow the workflow in `new-fds.md` exactly. It contains all 7 steps: prerequisites, language selection, classification (type determination + metadata), scaffolding, auto-commit, and completion summary.

</process>

<success_criteria>

- [ ] Prerequisites verified (git repo exists, no existing .planning/)
- [ ] Language selected (Dutch or English)
- [ ] Project classified as Type A, B, C, or D
- [ ] Metadata gathered (name, client, location, language)
- [ ] .planning/ scaffolded with all artifacts populated (not empty stubs)
- [ ] For Type C/D: BASELINE.md created
- [ ] All files committed to git
- [ ] Engineer knows next step is `/doc:discuss-phase 1`

</success_criteria>
