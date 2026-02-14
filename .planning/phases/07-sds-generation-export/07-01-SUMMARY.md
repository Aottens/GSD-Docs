---
phase: 07-sds-generation-export
plan: 01
subsystem: sds-infrastructure
tags:
  - sds
  - templates
  - structure
  - typicals
  - traceability
dependency_graph:
  requires:
    - phase-05/fds-structure.json (parallel structure pattern)
    - phase-01/fds/section-equipment-module.md (frontmatter pattern)
  provides:
    - gsd-docs-industrial/templates/sds-structure.json (canonical SDS section ordering)
    - gsd-docs-industrial/references/typicals/CATALOG-SCHEMA.json (typicals catalog validation)
    - gsd-docs-industrial/templates/sds/section-equipment-software.md (equipment module SDS template)
    - gsd-docs-industrial/templates/sds/section-typicals-overview.md (typicals overview template)
    - gsd-docs-industrial/templates/reports/traceability.md (FDS-to-SDS linking template)
  affects:
    - Phase 7 Plan 2+ (all SDS generation workflows depend on these templates)
tech_stack:
  added:
    - JSON Schema for typicals catalog validation
    - SDS structure preset configuration (equipment-first/software-first)
  patterns:
    - Parallel structure to FDS (7 top-level sections, dynamic equipment expansion)
    - Bilingual template support (en/nl dual headers)
    - Typical matching with confidence levels (HIGH/MEDIUM/LOW)
    - NEW TYPICAL NEEDED marker pattern for unmatched equipment
    - FDS-to-SDS traceability with coverage analysis
key_files:
  created:
    - gsd-docs-industrial/templates/sds-structure.json (317 lines)
    - gsd-docs-industrial/references/typicals/CATALOG-SCHEMA.json (269 lines)
    - gsd-docs-industrial/templates/sds/section-equipment-software.md (104 lines)
    - gsd-docs-industrial/templates/sds/section-typicals-overview.md (87 lines)
    - gsd-docs-industrial/templates/reports/traceability.md (134 lines)
  modified: []
decisions:
  - SDS structure follows equipment-first preset (matches FDS for cross-reference)
  - Structure preset configuration supports future software-first alternative
  - Equipment modules have 6 required subsections (vs 5 required + 4 optional in FDS)
  - Typical assignment includes confidence levels and NEW TYPICAL NEEDED status
  - Typicals documented via summary + reference pattern (no internal documentation)
  - CATALOG-SCHEMA.json is a validation schema, not an actual catalog (project-specific)
  - TRACEABILITY.md is internal quality check (not client deliverable)
  - Coverage analysis enforces 100% FDS-to-SDS requirement traceability
metrics:
  duration: 5m 28s
  tasks_completed: 2
  files_created: 5
  commits: 2
  lines_added: 911
completed: 2026-02-14
---

# Phase 07 Plan 01: SDS Document Infrastructure Summary

**One-liner:** SDS structure template with 7 sections and dynamic equipment expansion, CATALOG-SCHEMA for typicals validation, equipment-software template with 6 subsections and typical matching, typicals overview template, and FDS-to-SDS traceability report with coverage analysis.

## Tasks Completed

### Task 1: Create SDS structure template and typicals catalog schema
**Commit:** e019ebe

Created sds-structure.json following the exact pattern as fds-structure.json but for SDS documents:
- 7 top-level sections: Introduction, Software Architecture Overview, Typicals Library Reference, Equipment Modules (dynamic), Interfaces, HMI/SCADA Integration, Appendices
- Bilingual titles (en/nl) for all sections and subsections
- Dynamic equipment module expansion with 6 required subsections: Typical Assignment, FB Composition, Instantiation, Parameter Configuration, Data Flow, State Machine Implementation
- Structure preset configuration field supporting equipment-first (default) and software-first alternatives
- based_on metadata field for cross-referencing source FDS version
- Comprehensive mapping conventions and assembly workflow instructions

Created CATALOG-SCHEMA.json as a JSON Schema (not an actual catalog):
- schema_version 1.0 for future evolution
- library object with name, version, platform (TIA Portal V18+), updated date, load_mode (external/imported)
- typicals array definition with required fields: id (FB_NAME pattern), type, category, description, interfaces (inputs/outputs)
- Optional fields: use_cases, states (for PackML typicals), documentation path
- Complete example entry showing FB_AnalogIn typical with full interface definition (6 inputs, 4 outputs)

### Task 2: Create SDS section templates and traceability report template
**Commit:** 1ac7dc7

Created section-equipment-software.md template for SDS equipment modules:
- Frontmatter: type equipment-software, language placeholder, standards [tia-portal, packml]
- 6 required subsections (all equipment modules get all 6, no optional subsections)
- Subsection 1 (Typical Assignment): table with Equipment Module ID, Matched Typical, Confidence (HIGH/MEDIUM/LOW), Status (Matched/NEW TYPICAL NEEDED), Library Reference
- NEW TYPICAL NEEDED marker pattern for unmatched equipment modules
- Typical summary section using summary + reference pattern (brief description of purpose and interfaces, not full documentation)
- Subsection 2 (FB Composition): FB hierarchy table and Mermaid diagram placeholder showing calling relationships
- Subsection 3 (Instantiation): instance names, DB numbers, PLC/CPU mapping
- Subsection 4 (Parameter Configuration): values derived from FDS, typical defaults, or engineer overrides with source tracking
- Subsection 5 (Data Flow): signal connections between FBs with Mermaid flowchart placeholder
- Subsection 6 (State Machine Implementation): mapping from FDS states (section 4.x.2) to FB state variables
- Bilingual column headers throughout (English / Nederlands pattern)
- HTML comment documentation block explaining template usage

Created section-typicals-overview.md template for section 3 of SDS:
- Frontmatter: type typicals-overview, section 3, required subsections [library-metadata, typicals-summary], optional [unmatched-equipment]
- Subsection 3.1 (Library Metadata): table with library name, version, platform, last updated, load mode, path
- Load mode explanation section (External vs Imported)
- Subsection 3.2 (Typicals Summary): table listing all typicals used in project with category, description, which equipment modules use them, interfaces summary
- Documentation references list (paths to typical documentation)
- Subsection 3.3 (Unmatched Equipment Modules): optional section listing equipment needing NEW TYPICAL development with reason, priority, recommendation

Created traceability.md template for FDS-to-SDS requirement linking:
- Frontmatter: type traceability-report, purpose internal-quality-check, deliverable false
- Header: project name, FDS version, SDS version, generation date
- Requirements Traceability table: FDS Req ID, FDS Section, SDS Section, Implementation (FB/DB reference), Status (Complete/Partial/Not Applicable)
- Coverage Analysis section: total FDS requirements, mapped to SDS count/percentage, N/A count, missing implementation count
- Coverage Status: PASS/FAIL based on 100% coverage requirement
- Missing Implementations section (conditional): lists gaps with issue description and required action
- Not Applicable Requirements section (optional): documents why certain FDS requirements don't need software implementation
- Release Gate section: checks all conditions for SDS release with --force override option and justification field
- Engineer Sign-Off section: reviewed by, review date, approval status, comments
- Comprehensive generation notes in HTML comments explaining auto-generation algorithm and quality gate enforcement

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

**sds-structure.json:**
- Valid JSON (node parse check passed)
- Has bilingual titles: YES
- Has 7 top-level sections: YES
- Section 4 is dynamic equipment: YES
- Has sds_structure preset field: YES
- Equipment modules have 6 subsections: YES
- Has based_on field: YES

**CATALOG-SCHEMA.json:**
- Valid JSON (node parse check passed)
- Has schema_version: YES
- Has library definition: YES
- Has typicals array spec: YES
- Has example entry: YES
- Example has FB_AnalogIn: YES

**section-equipment-software.md:**
- Has frontmatter: YES
- Has 6 required subsections: YES (grep count returns 6)
- Has bilingual headers: YES (English / Nederlands pattern verified)
- Has NEW TYPICAL NEEDED pattern: YES (in typical assignment table)
- Has typical reference patterns: YES (summary + reference approach)

**section-typicals-overview.md:**
- Has library metadata section: YES
- Has typicals summary section: YES
- Has CATALOG reference: YES (in HTML comments)

**traceability.md:**
- Has frontmatter with deliverable: false: YES
- Has FDS Req ID column: YES
- Has coverage analysis section: YES

## Cross-References

**Dependencies:**
- fds-structure.json (parallel structure pattern, dynamic expansion approach)
- section-equipment-module.md (frontmatter pattern, bilingual headers, HTML comment documentation)

**Provides to:**
- Phase 7 Plan 2+: All SDS generation workflows depend on these templates
- /doc:generate-sds command: Uses sds-structure.json for scaffolding
- SDS write-phase: Uses section-equipment-software.md and section-typicals-overview.md
- SDS verify-phase: Uses traceability.md for coverage validation

**Related:**
- fds-structure.json (parallel structure for cross-reference)
- CATALOG.json (project-specific files that validate against CATALOG-SCHEMA.json)

## Technical Notes

**SDS structure design:**
- Section 4 equipment modules maintain same numbering as FDS (4.x) for cross-reference
- Section 2 (Software Architecture) is unique to SDS (no FDS equivalent)
- Section 3 (Typicals Library) is unique to SDS (no FDS equivalent)
- Section 6 (HMI/SCADA Integration) expands on FDS section 5.2 with software implementation details
- Appendices (section 7) are auto-generated from equipment module content

**Typical matching strategy:**
- Confidence levels guide engineer review: HIGH = auto-approve, MEDIUM/LOW = manual check
- NEW TYPICAL NEEDED status triggers custom FB development workflow
- Summary + reference pattern avoids duplicating library documentation in SDS

**Traceability coverage model:**
- 100% coverage required: every FDS requirement must be Complete, Partial, or N/A
- Missing Implementation status blocks SDS release (quality gate)
- --force override allowed but requires written justification
- Coverage percentage calculated: (Mapped + N/A) / Total

**Structure preset rationale:**
- equipment-first (default) matches FDS structure for easy cross-reference
- software-first alternative deferred to future (structure revision may be needed after MVP experience per user decision)
- Preset field provides migration path without breaking existing projects

## Self-Check

**Files verification:**
- ✓ FOUND: gsd-docs-industrial/templates/sds-structure.json
- ✓ FOUND: gsd-docs-industrial/references/typicals/CATALOG-SCHEMA.json
- ✓ FOUND: gsd-docs-industrial/templates/sds/section-equipment-software.md
- ✓ FOUND: gsd-docs-industrial/templates/sds/section-typicals-overview.md
- ✓ FOUND: gsd-docs-industrial/templates/reports/traceability.md

**Commits verification:**
- ✓ FOUND: e019ebe
- ✓ FOUND: 1ac7dc7

**Result: PASSED** - All claimed files exist and all commits are in git history.

## Next Steps

1. Create /doc:generate-sds command scaffolding (Plan 02 likely covers this)
2. Implement typical matching algorithm
3. Create SDS-specific workflows (discuss-phase, plan-phase, write-phase, verify-phase adaptations)
4. Test SDS generation on a sample FDS project

---

*Completed: 2026-02-14*
*Duration: 5m 28s*
*Commits: e019ebe, 1ac7dc7*
