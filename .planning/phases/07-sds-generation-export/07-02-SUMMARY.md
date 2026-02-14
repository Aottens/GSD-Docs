---
phase: 07-sds-generation-export
plan: 02
subsystem: docx-export
tags:
  - export
  - pandoc
  - mermaid
  - docx
  - corporate-styling
dependency_graph:
  requires:
    - phase-05/complete-fds (FDS assembly pattern)
    - gsd-docs-industrial/references/ui-brand.md (DOC > banner prefix)
  provides:
    - /doc:export command
    - gsd-docs-industrial/workflows/export.md (10-step DOCX conversion pipeline)
  affects:
    - ENGINEER-TODO.md (deferred diagrams)
    - STATE.md (export tracking)
tech_stack:
  added:
    - Pandoc 3.9+ for DOCX conversion
    - mermaid-cli 11.12+ for diagram rendering
  patterns:
    - Lean command + detailed workflow separation
    - Complexity budget enforcement (40/100 node limits)
    - Graceful degradation with --draft and --skip-diagrams flags
    - Prerequisite validation with clear error messages
key_files:
  created:
    - commands/doc/export.md (101 lines)
    - gsd-docs-industrial/commands/export.md (101 lines)
    - gsd-docs-industrial/workflows/export.md (829 lines)
  modified: []
decisions:
  - Pandoc as conversion tool (de facto standard, 150K+ citations)
  - mermaid-cli for server-side PNG rendering (no browser dependency)
  - Complexity budgets: 40-node soft limit (warning), 100-node hard limit (defer)
  - 60-second timeout per diagram render
  - Deferred diagrams routed to ENGINEER-TODO.md (not blocking errors)
  - huisstijl.docx optional (warning if missing, use Pandoc defaults)
  - Auto-detect input document from output/ if not specified
  - --draft flag omits list of figures/tables, adds DRAFT suffix
  - --skip-diagrams replaces Mermaid blocks with code blocks (no rendering)
metrics:
  duration: 4m 1s
  tasks_completed: 2
  files_created: 3
  commits: 2
  lines_added: 930
completed: 2026-02-14
---

# Phase 07 Plan 02: DOCX Export Command and Workflow Summary

**One-liner:** Pandoc-based DOCX export with corporate styling, Mermaid PNG rendering, complexity budgets, and graceful degradation flags (--draft, --skip-diagrams)

## Tasks Completed

### Task 1: Create /doc:export command file
**Commit:** f1489cf

Created lean command orchestrator following the established pattern from /doc:complete-fds:
- 101 lines (target: 60-100)
- Argument parsing: [document] --draft --skip-diagrams --output [path]
- Prerequisite validation: Pandoc (required), mermaid-cli (optional), huisstijl.docx (optional)
- Auto-detect input document from output/ directory if not specified (latest FDS or SDS by modification time)
- Identical files in commands/doc/ (Claude Code discovery) and gsd-docs-industrial/commands/ (version tracking)
- DOC > prefix for all banners per ui-brand.md

**Key decisions:**
- Pandoc is required (blocks with clear installation instructions if missing)
- mermaid-cli is optional (auto-enables --skip-diagrams if missing with informational message)
- huisstijl.docx is optional (warning if missing, export continues with Pandoc defaults)

### Task 2: Create DOCX export workflow with Mermaid rendering and Pandoc conversion
**Commit:** 375da93

Created comprehensive 10-step export pipeline:
- 829 lines (target: 800-1200)
- Step 1: Validate Prerequisites - Pandoc version check, mermaid-cli detection, huisstijl.docx verification, input document discovery, output directory creation
- Step 2: Parse Document Metadata - YAML frontmatter extraction, output filename determination, draft suffix handling
- Step 3: Extract and Render Mermaid Diagrams - Complexity analysis (node/edge counting), 40-node soft limit (warning), 100-node hard limit (defer), 60s timeout per diagram, PNG rendering with mmdc, failed/timeout diagrams deferred to ENGINEER-TODO.md
- Step 4: Handle External Diagrams - Scan for diagrams/external/ references, verify PNG exists, replace missing with text placeholders
- Step 5: Prepare Pandoc Input - Process markdown with diagram replacements, add draft metadata to frontmatter
- Step 6: Build Pandoc Command - Base flags (from markdown+yaml, to docx, standalone, toc, number-sections), conditional --reference-doc for huisstijl.docx, conditional --lof/--lot unless --draft
- Step 7: Execute Pandoc Conversion - Run conversion, error handling with common fix suggestions, output file verification, size sanity check (>10KB unless draft)
- Step 8: Generate ENGINEER-TODO.md for Deferred Diagrams - Structured table entries for each deferred/failed diagram with issue type, details, priority, and suggestions
- Step 9: Update STATE.md - Record export completion with date, document, format, version, draft flag, diagram counts
- Step 10: Display Summary - Completion banner with file size, diagram counts, styling source, contextual notes for draft/deferred/missing-huisstijl

**Complexity budget enforcement:**
- Soft limit: 40 nodes → warning but render proceeds
- Hard limit: 100 nodes → defer to ENGINEER-TODO.md, replace with placeholder
- Timeout: 60 seconds per diagram → defer if exceeded
- Graceful degradation: failed renders don't block export, documented in ENGINEER-TODO.md

**Flags implementation:**
- --draft: Omits --lof/--lot flags, adds "draft: true" to YAML frontmatter, appends -DRAFT to output filename, skips file size validation
- --skip-diagrams: Skips Step 3 entirely, Mermaid blocks appear as code blocks in DOCX (Pandoc default)
- --output [path]: Custom output path instead of default export/{TYPE}-{PROJECT}-v{VERSION}.docx

**DOC > branding:**
- All stage banners use "DOC > " prefix (not "GSD >")
- Consistent with ui-brand.md established pattern
- Stage names: EXPORTING (main banner), completion summary, diagram counts, next steps

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

**Command files:**
- ✓ Identical files in both locations (diff returns no differences)
- ✓ Frontmatter with allowed-tools: Read, Write, Bash, Glob, Grep, Task
- ✓ References workflows/export.md via @-reference
- ✓ Handles --draft and --skip-diagrams flags
- ✓ DOC > banner prefix

**Workflow file:**
- ✓ 10 steps (grep -c "^## Step" returns 10)
- ✓ Contains all required patterns: pandoc, mmdc/mermaid, skip-diagrams, draft, ENGINEER-TODO, huisstijl, DOC >
- ✓ Complexity limits enforced: 40-node soft, 100-node hard, 60s timeout
- ✓ Deferred diagrams routed to ENGINEER-TODO.md
- ✓ Pandoc called with --reference-doc for corporate styling
- ✓ TOC, list of figures, list of tables generated (unless --draft)

**Requirements coverage:**
- ✓ EXPT-01: Engineer runs /doc:export and receives DOCX with corporate styling
- ✓ EXPT-02: Mermaid diagrams rendered to PNG and embedded
- ✓ EXPT-03: huisstijl.docx reference document used for styling
- ✓ EXPT-04: --draft flag omits lists, adds DRAFT suffix
- ✓ EXPT-05: --skip-diagrams flag replaces Mermaid with code blocks
- ✓ EXPT-06: Complex diagrams routed to ENGINEER-TODO.md with structured entries

## Cross-References

**Dependencies:**
- Phase 5 complete-fds.md (lean command + detailed workflow pattern)
- ui-brand.md (DOC > prefix, stage banners, checkpoint boxes)

**Provides to:**
- Phase 7 Plan 3 (SDS generation will reuse export workflow)
- Phase 7 Plan 5 (pilot project will test full export pipeline)

**Related:**
- complete-fds.md workflow (similar assembly → output pattern)
- ENGINEER-TODO.md (receives deferred diagram entries)
- STATE.md (tracks export history)

## Technical Notes

**Pandoc version compatibility:**
- Workflow checks version and compares against 3.9+ recommendation
- Adapts --lof/--lot flags based on version (modern vs metadata approach)
- Warns if version < 3.9 but continues (non-blocking)

**Mermaid rendering approach:**
- Server-side rendering via mermaid-cli (no browser dependency)
- PNG output at --scale 2 --width 1200 for high-resolution embedding
- Neutral theme with white background for professional appearance
- Complexity analysis counts nodes (lines matching `^\s*[A-Za-z0-9_]+[\[\(\{]`) and edges (lines with -->, ---, ==>, ===)

**Bash complexity note:**
- Step 3 (Mermaid rendering) and Step 4 (external diagrams) involve complex markdown parsing
- Workflow provides the algorithm; implementation may benefit from a small Node.js/Python script or remark plugin for production-grade reliability
- For MVP, bash approach with sed/awk is acceptable with careful testing

**huisstijl.docx reference document:**
- Path: ~/.claude/gsd-docs-industrial/references/huisstijl.docx
- Optional (warning if missing, not blocking)
- Pandoc uses it as style template (fonts, headings, spacing, colors)
- Engineer provides this file (one corporate template for all projects)

## Next Steps

1. Create huisstijl.docx reference document (or use Pandoc default for testing)
2. Test export workflow on a sample assembled FDS document
3. Proceed to Phase 7 Plan 3: SDS generation scaffolding
4. Validate export pipeline in Phase 7 Plan 5 pilot project

## Self-Check: PASSED

All claims verified:
- ✓ FOUND: commands/doc/export.md
- ✓ FOUND: gsd-docs-industrial/commands/export.md
- ✓ FOUND: gsd-docs-industrial/workflows/export.md
- ✓ FOUND: commit f1489cf
- ✓ FOUND: commit 375da93

---

*Completed: 2026-02-14*
*Duration: 4m 1s*
*Commits: f1489cf, 375da93*
