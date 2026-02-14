---
phase: 07-sds-generation-export
plan: 03
subsystem: sds-generation-scaffolding
tags:
  - sds
  - generate-sds
  - workflow
  - typicals-matching
  - traceability
  - scaffolding
dependency_graph:
  requires:
    - phase-07/07-01 (SDS structure template, CATALOG-SCHEMA, section templates)
    - phase-05/release workflow (FDS assembly and versioning patterns)
    - phase-01/new-fds command and workflow (scaffolding pattern reference)
  provides:
    - commands/doc/generate-sds.md (command entry point for SDS generation)
    - gsd-docs-industrial/workflows/generate-sds.md (12-step SDS scaffolding workflow)
  affects:
    - Phase 7 Plan 4+ (SDS-specific command adaptations will reference this workflow)
    - All future SDS projects (scaffolding entry point)
tech_stack:
  added:
    - SDS project scaffolding pipeline (12-step workflow)
    - Typicals matching algorithm (confidence-scored with 4 weighted factors)
    - FDS-to-SDS requirement traceability generation
  patterns:
    - Lean command + detailed workflow separation (62 lines command, 1520 lines workflow)
    - Three typicals loading modes (external reference, imported copy, no typicals)
    - Suggest + confirm matching pattern (never auto-applied)
    - Structured skeleton for unmatched modules (not stubs)
    - Independent SDS versioning with based_on FDS cross-reference
    - Parallel .planning/sds/ directory for SDS workflow
key_files:
  created:
    - commands/doc/generate-sds.md (100 lines)
    - gsd-docs-industrial/commands/generate-sds.md (100 lines, identical to commands/doc/)
    - gsd-docs-industrial/workflows/generate-sds.md (1520 lines)
  modified: []
decisions:
  - SDS generation is scaffolding (not transform) — creates project for discuss-plan-write-verify cycle
  - Typicals matching uses suggest + confirm pattern — engineer reviews and confirms during SDS Phase 1
  - Three typicals modes: external reference (PROJECT.md path), imported copy (--import flag), no typicals (skeleton mode)
  - Matching confidence scoring: I/O 40%, keywords 30%, states 20%, category 10% weights
  - Unmatched modules get structured skeleton from FDS with NEW TYPICAL NEEDED status (not empty stubs)
  - SDS project lives in parallel .planning/sds/ directory with independent STATE.md
  - SDS PROJECT.md has independent version (v0.1) with based_on FDS version cross-reference
  - TRACEABILITY.md is internal quality check (not client deliverable) with 100% coverage requirement
  - MATCHING-REPORT.md provides human-readable analysis for engineer review during Phase 1 discuss
  - Equipment module seeds saved to sds-02-equipment/ as starting points for SDS write-phase
metrics:
  duration: 7m 7s
  tasks_completed: 2
  files_created: 3
  commits: 2
  lines_added: 1720
completed: 2026-02-14
---

# Phase 07 Plan 03: SDS Generation Command + Workflow Summary

**One-liner:** /doc:generate-sds command and comprehensive 12-step workflow scaffold SDS project from completed FDS with typicals library loading (external/imported/none modes), confidence-scored equipment matching (I/O 40%, keywords 30%, states 20%, category 10%), structured skeleton generation for unmatched modules, TRACEABILITY.md linking FDS requirements to SDS sections, and parallel .planning/sds/ project structure ready for discuss-plan-write-verify cycle.

## Tasks Completed

### Task 1: Create /doc:generate-sds command file
**Commit:** a5b1447

Created /doc:generate-sds command following the established lean orchestrator pattern (same pattern as /doc:new-fds):
- Command frontmatter with allowed-tools: Read, Write, Bash, Glob, Grep, Task (same as new-fds for scaffolding)
- Three arguments: --typicals [path] for library location, --import for copy mode, --structure [equipment-first|software-first] for SDS structure preset
- Prerequisites check: assembled FDS exists in output/, FDS version available, .planning/ directory exists
- Workflow delegation to gsd-docs-industrial/workflows/generate-sds.md via @-reference
- Identical files created in commands/doc/ (for Claude Code discovery) and gsd-docs-industrial/commands/ (for version tracking)
- DOC > prefix for all stage banners per ui-brand.md pattern

Command handles three typicals modes:
1. External reference: --typicals [path] points to project-specific catalog (SDS references external library)
2. Imported copy: --typicals [path] --import copies catalog into references/typicals/ for self-containment
3. No typicals: proceed without catalog — all modules flagged as NEW TYPICAL NEEDED

Structure preset supports equipment-first (default, matches FDS for cross-reference) and software-first (alternative for future flexibility).

### Task 2: Create SDS generation workflow with typicals matching and project scaffolding
**Commit:** baed616

Created comprehensive 12-step SDS generation workflow (1520 lines) implementing the complete FDS-to-SDS scaffolding pipeline:

**Steps 1-2: FDS Validation and Typicals Loading**
- Step 1: Validate FDS prerequisites (scan output/ for FDS-*.md, extract metadata from frontmatter, verify content > 1KB, read STATE.md)
- Step 2: Load typicals library in one of three modes:
  - External reference: read CATALOG.json from configured path, validate against CATALOG-SCHEMA.json
  - Imported copy: copy CATALOG.json and documentation to references/typicals/
  - Skeleton mode: no catalog loaded, all modules will be NEW TYPICAL NEEDED
- Extract library metadata: name, version, platform (TIA Portal V18+), updated date
- Validate catalog structure: schema_version, library object, typicals array with required fields (id, type, category, description, interfaces)

**Steps 3-4: Equipment Module Extraction and Matching**
- Step 3: Extract FDS equipment module profiles from section 4.x:
  - Module ID (EM-XXX pattern or derived from section number)
  - I/O interface: count by type (DI, DO, AI, AO), extract data types (BOOL, INT, REAL)
  - Operating states: extract state names and count from subsection 4.x.2
  - Parameters: extract names, ranges, units from subsection 4.x.3
  - Interlocks: count and types from subsection 4.x.4 if present
  - Keywords: derive from module name and description for matching
- Step 4: Match equipment modules against typicals catalog (skipped if skeleton mode):
  - Matching algorithm with confidence scoring:
    - I/O interface match (40% weight): compare input/output counts and data types (exact = 10, ±1 = 7, ±2 = 5, else 0)
    - Keyword/use-case match (30% weight): Jaccard similarity between module keywords and typical use_cases
    - State complexity match (20% weight): compare state count similarity (exact = 20, ±1 = 15, ±2 = 10, else 5)
    - Category match (10% weight): exact category match = 10, else 0
  - Filter matches with confidence >= 30%, rank by confidence descending, take top 3 suggestions per module
  - Classify confidence levels: HIGH (>=80%), MEDIUM (60-79%), LOW (40-59%), VERY LOW (30-39%)
  - Mark modules with no matches >= 30% as NEW TYPICAL NEEDED immediately
  - Generate comparison table for each module with FDS requirements summary, suggested typical, interface match analysis, and recommendation

**Steps 5-6: SDS Content Seeding and Traceability**
- Step 5: Generate SDS equipment module seeds as starting points for SDS write-phase:
  - Matched modules: pre-fill section-equipment-software.md template with typical assignment (confidence, library reference), inferred FB composition, merged parameters (FDS + typical defaults), preliminary state mapping, data flow placeholder, mark as NEEDS ENGINEER REVIEW
  - Unmatched modules (NEW TYPICAL NEEDED): generate structured skeleton from FDS (not stub) with NEW TYPICAL specification (I/O profile, state machine, parameters from FDS), empty FB composition template with requirements, all parameters marked "Source: FDS" with no defaults, all I/O signals with "Destination: [TO BE DESIGNED]", all states with "FB State: [TO BE DESIGNED]"
  - Save seeds to .planning/sds/phases/sds-02-equipment/{section}-{module-id}-seed.md
- Step 6: Generate TRACEABILITY.md using template from Plan 07-01:
  - Parse FDS for requirements (from REQUIREMENTS.md or inline markers)
  - Map requirements to target SDS sections (equipment module requirements 4.x → SDS 4.x, system requirements 2.x → SDS 2, interface requirements 5.x → SDS 5)
  - Create traceability rows: FDS Req ID, FDS Section, SDS Section, Implementation (placeholder "[TO BE IMPLEMENTED]"), Status (Pending)
  - Calculate coverage analysis: total requirements, mapped count, N/A count (0 during scaffolding), missing implementation count
  - Coverage Status: FAIL (expected during scaffolding — becomes PASS when engineer completes SDS)
  - Release gate section: checks for 100% coverage, --force override option with justification field

**Steps 7-8: Project Scaffolding and Matching Report**
- Step 7: Scaffold SDS project structure in parallel .planning/sds/ directory:
  - Create phase directories: sds-01-foundation, sds-02-equipment, sds-03-integration
  - SDS PROJECT.md: copy language/client/name from FDS, add type: SDS, version: 0.1, based_on (FDS version/date), typicals (mode/path/catalog), sds_structure preset
  - SDS ROADMAP.md: 3-phase structure (Foundation + Typicals Matching → Equipment Module Details → Integration + Assembly) with detailed phase goals and engineer tasks
  - SDS STATE.md: initialize at SDS Phase 1, Pending status, progress bar at 0%
  - SDS REQUIREMENTS.md: derive from FDS requirements, rephrased for software focus (system architecture, equipment module software behavior, interfaces)
- Step 8: Generate MATCHING-REPORT.md as human-readable report for engineer review:
  - Summary table: Equipment Module, Module Name, Suggested Typical, Confidence, Status
  - Statistics: total modules, matched by confidence level, NEW TYPICAL NEEDED count
  - Detailed comparison per module: FDS requirements summary, suggested typical with confidence scoring breakdown, interface match analysis (inputs/outputs/data types), recommendation based on confidence level
  - NEW TYPICAL NEEDED modules: reason, I/O profile from FDS, state machine from FDS, parameters table, design notes, priority
  - Engineer instructions: how to confirm/override matches during discuss-phase, override mechanism

**Steps 9-12: State Updates and Completion**
- Step 9: Update main .planning/PROJECT.md with SDS configuration section (version, based_on FDS, structure preset, typicals mode/library/path)
- Step 10: Update main .planning/STATE.md with SDS version tracking, session continuity (SDS scaffolded from FDS version), decision entry
- Step 11: Git commit all SDS project files with structured message (feat(sds): scaffold SDS project from FDS vX.Y)
- Step 12: Display comprehensive summary with success banner, created files list, matching statistics, next steps (review MATCHING-REPORT.md, design custom FBs if needed, run /doc:discuss-phase 1 --sds)

**Key workflow characteristics:**
- Bridge pattern: creates SDS project infrastructure and seeds initial content, enabling engineer to run full discuss-plan-write-verify cycle independently
- Suggest + confirm matching: system proposes matches, engineer confirms or overrides during SDS Phase 1 discuss (matching NEVER auto-applied)
- Structured skeletons for unmatched modules: complete starting point with FDS requirements extracted (I/O, states, parameters), not empty stubs
- Three typicals modes supported: external reference, imported copy (--import), skeleton mode (no catalog)
- Independent SDS versioning: v0.1 during scaffolding, with based_on FDS vX.Y cross-reference for traceability
- Parallel .planning/sds/ directory: SDS has its own STATE.md, ROADMAP.md, PROJECT.md for independent workflow tracking
- 1520 lines (target: 1200-1600) — most complex workflow in project due to FDS analysis + typicals matching + scaffolding

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

**Command files verification:**
```bash
diff commands/doc/generate-sds.md gsd-docs-industrial/commands/generate-sds.md
# (no output — files identical)
```

**Command file contains required elements:**
- ✓ Has frontmatter with allowed-tools
- ✓ References workflows/generate-sds.md
- ✓ Has --typicals flag
- ✓ Has --import flag
- ✓ Has --structure flag

**Workflow verification:**
- ✓ Has 12 steps (grep -c "^## Step" returns 12)
- ✓ Has CATALOG references (for typicals loading)
- ✓ Has NEW TYPICAL NEEDED pattern (for unmatched modules)
- ✓ Has TRACEABILITY references (for FDS-to-SDS mapping)
- ✓ Has based_on references (for SDS versioning)
- ✓ Has equipment-first and software-first patterns (structure presets)
- ✓ Has suggest + confirm pattern (matching confirmation)
- ✓ Has DOC > prefix (ui-brand pattern)
- ✓ Has MATCHING-REPORT references (engineer review document)
- ✓ File is 1520 lines (within target range 1200-1600)

**All requirements covered:**
- SDS-01: SDS generation reads completed FDS ✓ (Step 1)
- SDS-02: Equipment modules matched against typicals with confidence ✓ (Steps 3-4)
- SDS-03: Typicals documented via summary + reference ✓ (Step 5 matched modules)
- SDS-04: Unmatched modules flagged as NEW TYPICAL NEEDED with structured skeleton ✓ (Step 5 unmatched modules)
- SDS-05: TRACEABILITY.md links FDS requirements to SDS sections ✓ (Step 6)
- SDS-06: SDS has independent version with based_on FDS reference ✓ (Step 7 PROJECT.md)

## Cross-References

**Dependencies:**
- gsd-docs-industrial/templates/sds-structure.json (SDS section ordering for scaffolding)
- gsd-docs-industrial/references/typicals/CATALOG-SCHEMA.json (typicals catalog validation)
- gsd-docs-industrial/templates/sds/section-equipment-software.md (equipment module SDS template for seeds)
- gsd-docs-industrial/templates/reports/traceability.md (FDS-to-SDS linking template)
- gsd-docs-industrial/workflows/new-fds.md (scaffolding pattern reference)
- gsd-docs-industrial/workflows/release.md (FDS assembly and versioning pattern)

**Provides to:**
- Phase 7 Plan 4+ (SDS-specific command adaptations: discuss-phase --sds, plan-phase --sds, write-phase --sds, verify-phase --sds, complete-fds --sds)
- All future SDS projects (entry point for SDS scaffolding workflow)

**Related:**
- commands/doc/new-fds.md (FDS scaffolding parallel — same pattern for SDS)
- gsd-docs-industrial/workflows/complete-fds.md (document assembly pattern for future /doc:complete-fds --sds)

## Technical Notes

**Typicals matching algorithm rationale:**
- I/O interface (40% weight): most objective and critical match factor — exact I/O alignment reduces FB customization
- Keywords/use-cases (30% weight): semantic match indicating similar equipment function
- State complexity (20% weight): state machine complexity indicator — PackML typicals match PackML equipment
- Category (10% weight): tiebreaker for otherwise similar matches

**Confidence level thresholds:**
- HIGH (>=80%): engineer can confidently accept match
- MEDIUM (60-79%): engineer should review interface details before accepting
- LOW (40-59%): manual decision required, but typical is still a candidate
- VERY LOW (30-39%): shown but not recommended (border case)
- <30%: filtered out, module marked as NEW TYPICAL NEEDED

**Structured skeleton design (NEW TYPICAL NEEDED modules):**
- NOT an empty stub — complete starting point with all FDS requirements extracted
- I/O profile: all DI/DO/AI/AO from FDS subsection 4.x.1 with signal names and types
- State machine: all states from FDS subsection 4.x.2 with transition logic if documented
- Parameters: all parameters from FDS subsection 4.x.3 with ranges, units, source tracking
- Design notes: placeholder for engineer to design custom FB during SDS Phase 1
- Becomes candidate for project typicals library: reusable for similar equipment in future

**SDS project separation rationale:**
- Parallel .planning/sds/ directory (not nested under .planning/phases/) enables independent STATE.md tracking
- SDS has different phase structure than FDS (3 phases vs 5-6 phases), so separate ROADMAP.md needed
- SDS version is independent (v0.1, v0.2, v1.0) with based_on FDS vX.Y cross-reference for traceability
- SDS workflow uses same commands (discuss-phase, plan-phase, write-phase, verify-phase) with --sds flag to target .planning/sds/ instead of .planning/

**TRACEABILITY.md coverage model:**
- 100% coverage required: every FDS requirement must be Complete, Partial, or N/A (no Pending or Missing for release)
- Coverage percentage: (Complete + Partial + N/A) / Total
- Missing Implementation status blocks SDS release (quality gate) unless --force override used
- N/A requirements documented with justification: why certain FDS requirements don't need software implementation

**Matching report usage:**
- Generated during scaffolding, reviewed during /doc:discuss-phase 1 --sds (SDS Foundation phase)
- Engineer confirms HIGH confidence matches (auto-accept pattern)
- Engineer reviews MEDIUM/LOW confidence matches (manual verification of I/O alignment and parameter compatibility)
- Engineer can override any match: update .planning/sds/phases/sds-02-equipment/{module}-seed.md manually
- Override mechanism documented in report instructions section

## Self-Check

**Files verification:**
- ✓ FOUND: commands/doc/generate-sds.md
- ✓ FOUND: gsd-docs-industrial/commands/generate-sds.md
- ✓ FOUND: gsd-docs-industrial/workflows/generate-sds.md

**Files are identical (commands/doc/ and gsd-docs-industrial/commands/):**
```bash
diff commands/doc/generate-sds.md gsd-docs-industrial/commands/generate-sds.md
# (no output — files identical)
```

**Commits verification:**
- ✓ FOUND: a5b1447 (Task 1 - command files)
- ✓ FOUND: baed616 (Task 2 - workflow file)

**Result: PASSED** - All claimed files exist, files are identical where required, and all commits are in git history.

## Next Steps

1. Create SDS-specific command adaptations (Plan 04 likely covers this):
   - discuss-phase --sds flag to target .planning/sds/
   - plan-phase --sds flag
   - write-phase --sds flag (with sds-02-equipment/ seeds as starting points)
   - verify-phase --sds flag (with TRACEABILITY.md coverage verification)
   - complete-fds --sds to assemble final SDS document from sds-structure.json

2. Test SDS generation workflow on sample FDS project:
   - Run /doc:generate-sds with external typicals library
   - Run /doc:generate-sds --import to test imported copy mode
   - Run /doc:generate-sds without --typicals to test skeleton mode
   - Verify MATCHING-REPORT.md quality and engineer usability

3. Implement /doc:export for DOCX conversion (Plan 05 likely covers this)

4. Create pilot project (Plan 05) to validate full FDS → SDS → DOCX pipeline

---

*Completed: 2026-02-14*
*Duration: 7m 7s*
*Commits: a5b1447, baed616*
