---
phase: 05-complete-fds-standards
plan: 01
subsystem: standards-validation
tags:
  - standards
  - PackML
  - ISA-88
  - validation
  - compliance
dependency_graph:
  requires:
    - phase-03-verified
  provides:
    - packml-reference-data
    - isa88-reference-data
    - standards-validation-workflow
    - compliance-reporting
  affects:
    - verify-phase-level-5
    - complete-fds-assembly
tech_stack:
  added:
    - markdown-table-parsing
  patterns:
    - opt-in-standards-loading
    - composable-validators
    - severity-based-enforcement
key_files:
  created:
    - gsd-docs-industrial/references/standards/packml/STATE-MODEL.md
    - gsd-docs-industrial/references/standards/packml/UNIT-MODES.md
    - gsd-docs-industrial/references/standards/isa-88/EQUIPMENT-HIERARCHY.md
    - gsd-docs-industrial/references/standards/isa-88/TERMINOLOGY.md
    - commands/doc/check-standards.md
    - gsd-docs-industrial/commands/check-standards.md
    - gsd-docs-industrial/workflows/check-standards.md
    - gsd-docs-industrial/templates/reports/compliance-report.md
  modified: []
decisions:
  - key: "PackML state validation uses exact match enforcement"
    rationale: "ISA-TR88.00.02 defines exact state names; common synonyms mapped to remediation hints"
    context: "STND-03a check in workflow"
  - key: "ISA-88 terminology context-aware - enforced in hierarchy sections, relaxed in I/O tables"
    rationale: "Engineering documents legitimately use non-ISA terms in vendor/technical contexts"
    context: "STND-04a check in workflow"
  - key: "Standards severity configurable per standard (error vs warning)"
    rationale: "Engineer controls whether violations block assembly or produce warnings only"
    context: "PROJECT.md configuration pattern"
metrics:
  duration: "6m 56s"
  completed: "2026-02-14"
  tasks: 2
  commits: 2
  files_created: 8
  reference_data_files: 4
  workflow_steps: 7
  check_ids: 6
---

# Phase 5 Plan 1: Standards Reference Data + Validation Workflow

**One-liner:** Created PackML (ISA-TR88.00.02) and ISA-88 reference data files with composable validation workflow producing COMPLIANCE.md reports with per-check pass/fail, severity levels, and remediation hints.

## Implementation Summary

Created complete standards validation infrastructure as opt-in modules for FDS quality enforcement:

**Task 1: Reference Data Files (4 files)**
- PackML STATE-MODEL.md: 17 valid states, 40+ transitions, state categories per ISA-TR88.00.02
- PackML UNIT-MODES.md: 6 valid modes (PRODUCTION, MAINTENANCE, MANUAL, SETUP, DRY_RUN, CLEAN) with mode-state mapping
- ISA-88 EQUIPMENT-HIERARCHY.md: 4-level hierarchy (Process Cell > Unit > Equipment Module > Control Module) with nesting rules
- ISA-88 TERMINOLOGY.md: Canonical terms with 30+ common incorrect alternatives mapped to correct terms

All reference files use markdown tables for human readability, parsed at load time for validation checks. Standards-accurate content based on authoritative sources (ISA-TR88.00.02-2022, ISA-88.01-1995).

**Task 2: Validation Infrastructure (4 files)**
- /doc:check-standards command (lean orchestrator pattern: 62 lines)
- Workflow (7-step composable validator: 370 lines)
- COMPLIANCE.md template (per-check structure with severity + remediation)
- Identical command copy in gsd-docs-industrial for version tracking

**Workflow architecture (7 steps):**
1. Load PROJECT.md standards config, exit cleanly if none enabled (STND-06 compliance)
2. Lazy load reference data (only enabled standards, performance optimization)
3. Discover target CONTENT.md files (phase-specific or all phases)
4. PackML checks: STND-03a (state names), STND-03b (transitions), STND-03c (modes)
5. ISA-88 checks: STND-04a (terminology), STND-04b (hierarchy depth), STND-04c (hierarchy consistency)
6. Generate COMPLIANCE.md with per-check results, severity, evidence, remediation
7. Display summary with DOC > banner, overall compliance status

**Key patterns:**
- Standards never pushed: disabled by default, loaded only when explicitly enabled in PROJECT.md
- Severity-based enforcement: engineer sets error (blocking) vs warning (non-blocking) per standard
- Composable validators: workflow reusable by both /doc:check-standards and verify-phase Level 5
- Context-aware terminology checking: strict in hierarchy sections, relaxed in I/O tables

## Deviations from Plan

None - plan executed exactly as written.

## Verification Passed

All verification criteria met:
- ✓ All 4 reference data files exist under gsd-docs-industrial/references/standards/
- ✓ PackML STATE-MODEL.md contains all 17 valid states from ISA-TR88.00.02
- ✓ ISA-88 TERMINOLOGY.md contains canonical hierarchy terms with incorrect alternatives
- ✓ /doc:check-standards command exists and follows established command pattern
- ✓ check-standards workflow has conditional loading (enabled check before reference data load)
- ✓ COMPLIANCE.md template exists with per-check structure and remediation hints
- ✓ Standards are never pushed (workflow exits cleanly when standards disabled)
- ✓ DOC > prefix used throughout (never GSD >)
- ✓ Requirements covered: STND-01, STND-02, STND-03, STND-04, STND-05, STND-06

## Success Criteria Met

1. ✓ PackML and ISA-88 reference data files contain standards-accurate content usable for automated validation
2. ✓ /doc:check-standards produces a COMPLIANCE.md report with pass/fail per check, severity levels, and remediation hints
3. ✓ Validation logic is conditionally loaded (only when standards enabled) and structured for reuse by verify-phase
4. ✓ Standards are never pushed -- disabled by default, only activated by explicit PROJECT.md configuration

## Self-Check: PASSED

**Created files verification:**
```bash
✓ FOUND: gsd-docs-industrial/references/standards/packml/STATE-MODEL.md (6.5K)
✓ FOUND: gsd-docs-industrial/references/standards/packml/UNIT-MODES.md (6.0K)
✓ FOUND: gsd-docs-industrial/references/standards/isa-88/EQUIPMENT-HIERARCHY.md (7.6K)
✓ FOUND: gsd-docs-industrial/references/standards/isa-88/TERMINOLOGY.md (8.4K)
✓ FOUND: commands/doc/check-standards.md (2.9K)
✓ FOUND: gsd-docs-industrial/commands/check-standards.md (2.9K)
✓ FOUND: gsd-docs-industrial/workflows/check-standards.md (19K)
✓ FOUND: gsd-docs-industrial/templates/reports/compliance-report.md (8.6K)
```

**Commits verification:**
```bash
✓ FOUND: 38b6bfc - feat(05-01): create PackML and ISA-88 reference data files
✓ FOUND: a030e7c - feat(05-01): create /doc:check-standards command, workflow, and compliance template
```

**Content quality verification:**
```bash
✓ PackML STATE-MODEL.md contains all 17 states (73 table rows)
✓ ISA-88 TERMINOLOGY.md contains canonical terms with incorrect alternatives
✓ Workflow has 7 steps (Step 1-7 structure verified)
✓ DOC > prefix used (not GSD >)
✓ Conditional loading logic present (standards.enabled checks)
✓ Command files are identical (commands/doc and gsd-docs-industrial/commands)
```

All files created, all commits exist, all content quality checks passed.

---

**Completed:** 2026-02-14
**Duration:** 6m 56s
**Commits:** 38b6bfc, a030e7c
