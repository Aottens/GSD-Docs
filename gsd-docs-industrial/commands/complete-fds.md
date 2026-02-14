---
name: doc:complete-fds
description: Assemble all verified phases into a single FDS document with section numbering, cross-reference resolution, and standards compliance
argument-hint: ""
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

<objective>

Assemble all verified phase outputs into a single, numbered, versioned FDS document with resolved cross-references, standards compliance checks, orphan detection, and source archiving.

**Core promise:** This command delivers the core Phase 5 value -- transforming distributed phase content (verified via /doc:verify-phase) into a professional, deliverable FDS document ready for client review.

**Process:**
- Verify all phases PASS before assembly proceeds (or use --force flag)
- Reorder phase content to match canonical FDS structure template ordering (not ROADMAP phase order)
- Apply IEC-style hierarchical section numbering (1, 1.1, 1.2, 2, 2.1, 2.1.1, etc.)
- Resolve symbolic cross-references to final section numbers (plain text, not clickable links)
- Run standards compliance checks (if enabled in PROJECT.md)
- Generate professional front matter (title page, TOC, revision history, abbreviations)
- Detect orphan sections (sections never referenced by any other section)
- Flag complex diagrams requiring manual creation in ENGINEER-TODO.md
- Archive phase files to .planning/archive/vN.M/ for version control

**Output:** FDS-{PROJECT_NAME}-v{VERSION}.md in project root, with XREF-REPORT.md and COMPLIANCE.md in .planning/assembly/v{VERSION}/

**Optional flag:** `--force` - Generate document with [BROKEN REF] placeholders and DRAFT suffix when broken references exist

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/complete-fds.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md

</execution_context>

<context>

@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/PROJECT.md

</context>

<process>

Follow the workflow in complete-fds.md exactly. The workflow contains 15 comprehensive steps covering the full assembly pipeline from pre-flight verification through final document generation and archiving.

</process>

<success_criteria>

- [ ] All phases verified PASS (or --force flag used)
- [ ] Phase content reordered to match fds-structure.json canonical ordering
- [ ] IEC-style hierarchical numbering applied (1.1, 1.2, 2.1.1)
- [ ] Cross-references resolved to final section numbers
- [ ] Broken references handled: block without --force, [BROKEN REF] placeholders with --force
- [ ] Orphan sections detected and reported in XREF-REPORT.md
- [ ] Standards compliance checked (if enabled)
- [ ] Professional front matter generated (title page, TOC, revision history, abbreviations)
- [ ] Complex diagrams flagged in ENGINEER-TODO.md
- [ ] Phase files archived to .planning/archive/v{VERSION}/
- [ ] Final FDS document written to project root
- [ ] XREF-REPORT.md and COMPLIANCE.md (if applicable) generated
- [ ] STATE.md updated with assembly completion

</success_criteria>
