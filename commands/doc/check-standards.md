---
name: doc:check-standards
description: Run standalone standards compliance checks and generate COMPLIANCE.md report
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

<objective>

Run standalone standards compliance checks (PackML, ISA-88) on FDS phase content and generate a COMPLIANCE.md report with pass/fail per check, overall score, and remediation hints.

**Key functionality:**
- Conditionally loads standards reference data (only when enabled in PROJECT.md)
- Validates PackML state names, transitions, and modes (if PackML enabled)
- Validates ISA-88 equipment hierarchy and terminology (if ISA-88 enabled)
- Produces COMPLIANCE.md report with per-check results and severity levels
- Optional phase argument (defaults to all phases)

**Output:** COMPLIANCE.md report at `.planning/phases/{NN}-{slug}/COMPLIANCE.md` (phase-specific) or `.planning/COMPLIANCE.md` (all phases).

**Standards are opt-in:** If no standards enabled in PROJECT.md, displays info message and exits cleanly. Never suggests enabling standards (engineer decision only).

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/check-standards.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/references/standards/packml/STATE-MODEL.md
@~/.claude/gsd-docs-industrial/references/standards/packml/UNIT-MODES.md
@~/.claude/gsd-docs-industrial/references/standards/isa-88/EQUIPMENT-HIERARCHY.md
@~/.claude/gsd-docs-industrial/references/standards/isa-88/TERMINOLOGY.md

</execution_context>

<context>

@.planning/PROJECT.md
@.planning/STATE.md
@.planning/ROADMAP.md

</context>

<process>

Follow the workflow in check-standards.md exactly. This workflow:
1. Loads PROJECT.md and checks standards configuration
2. Conditionally loads enabled reference data (PackML and/or ISA-88)
3. Discovers and reads target CONTENT.md files (phase-specific or all phases)
4. Runs PackML checks if enabled (state names, transitions, modes)
5. Runs ISA-88 checks if enabled (terminology, hierarchy depth, hierarchy consistency)
6. Generates COMPLIANCE.md report using compliance-report.md template
7. Displays summary with DOC > banner and standards check result table

</process>

<success_criteria>

- [ ] Standards configuration loaded from PROJECT.md
- [ ] Reference data loaded conditionally (only when standard enabled)
- [ ] If no standards enabled: info message displayed, exits cleanly
- [ ] Target CONTENT.md files discovered (phase-specific or all)
- [ ] PackML checks run (if enabled): state names, transitions, modes
- [ ] ISA-88 checks run (if enabled): terminology, hierarchy depth, consistency
- [ ] COMPLIANCE.md generated with per-check pass/fail, severity, remediation hints
- [ ] Summary displayed with DOC > banner, table format
- [ ] No modifications to source CONTENT.md files (read-only validation)

</success_criteria>
