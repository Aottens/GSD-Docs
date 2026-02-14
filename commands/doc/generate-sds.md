---
name: doc:generate-sds
description: Scaffold SDS project from completed FDS with typicals matching
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
---

<objective>

Scaffold a Software Design Specification (SDS) project from a completed Functional Design Specification (FDS) through a structured pipeline: FDS validation, typicals library loading (external reference or imported copy), equipment module extraction and matching, SDS project structure creation, TRACEABILITY.md generation, and workflow preparation.

**Creates:**
- `.planning/sds/` -- SDS project directory (parallel to FDS .planning/)
- `.planning/sds/PROJECT.md` -- SDS-specific config with independent versioning
- `.planning/sds/ROADMAP.md` -- 3-phase SDS workflow structure
- `.planning/sds/STATE.md` -- SDS progress tracking
- `.planning/sds/REQUIREMENTS.md` -- SDS requirements derived from FDS
- `.planning/sds/TRACEABILITY.md` -- FDS-to-SDS requirement mapping
- `.planning/sds/MATCHING-REPORT.md` -- Equipment-to-typical matching analysis

**After this command:** Run `/doc:discuss-phase 1 --sds` to start the SDS Phase 1 workflow.

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/generate-sds.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md

</execution_context>

<context>

This command reads an existing assembled FDS document and creates a scaffolded SDS project alongside it. The SDS gets its own discuss-plan-write-verify cycle (not a single-pass transform).

**Prerequisites:**
- Assembled FDS exists in `output/` directory (FDS-*.md file)
- FDS version available (from STATE.md or FDS frontmatter)
- `.planning/` directory exists (project initialized)

**Typicals library modes:**
1. **External reference:** `--typicals [path]` points to a project-specific catalog
2. **Imported copy:** `--import` copies catalog into `references/typicals/` for self-containment
3. **No typicals:** Proceed without matching — all modules flagged as NEW TYPICAL NEEDED

</context>

<arguments>

**--typicals [path]** (optional)
Path to project-specific typicals library CATALOG.json. Can be absolute or relative to project root.

**--import** (optional, requires --typicals)
Copy external typicals library into `references/typicals/` for self-containment. Without this flag, SDS references the external path.

**--structure [equipment-first|software-first]** (optional, default: equipment-first)
SDS structure preset. Default matches FDS for cross-reference. Software-first is an alternative for future flexibility.

</arguments>

<process>

Follow the workflow in `generate-sds.md` exactly. It contains all 12 steps:

1. Validate FDS prerequisites
2. Load typicals library (external/imported/none mode)
3. Extract FDS equipment modules
4. Match equipment modules against typicals with confidence scoring
5. Generate SDS equipment module seeds (matched + unmatched)
6. Generate TRACEABILITY.md
7. Scaffold SDS project structure (.planning/sds/)
8. Generate typicals matching report
9. Update PROJECT.md with SDS configuration
10. Update STATE.md
11. Git commit
12. Display summary

The workflow is a MARKDOWN document with step-by-step instructions for Claude to follow, NOT a script.

</process>

<success_criteria>

- [ ] FDS prerequisites validated (assembled FDS exists)
- [ ] Typicals library loaded (external/imported/none mode)
- [ ] Equipment modules extracted from FDS
- [ ] Matching confidence scores calculated for each module
- [ ] SDS project scaffolded in .planning/sds/
- [ ] TRACEABILITY.md generated with FDS-to-SDS requirement mapping
- [ ] MATCHING-REPORT.md generated with confidence-scored suggestions
- [ ] All SDS files committed to git
- [ ] Engineer knows next step is `/doc:discuss-phase 1 --sds`

</success_criteria>
