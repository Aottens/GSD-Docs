# Phase 5: Complete-FDS + Standards + Assembly - Context

**Gathered:** 2026-02-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Assemble all verified FDS phase outputs into a single document with hierarchical section numbering, resolved cross-references, opt-in standards compliance checks, and version management for internal and client releases. Individual section writing and verification are Phase 3 concerns; this phase takes verified content and produces a complete, numbered, versioned FDS document.

</domain>

<decisions>
## Implementation Decisions

### Assembly structure
- Hierarchical (IEC-style) section numbering: 1.1, 1.2, 2.1.1, etc.
- Full auto-generated front matter: title page, revision history, table of contents, abbreviations list
- Section ordering follows a predefined FDS structure template (not ROADMAP phase order) — template defines the canonical order
- Unwritten sections appear as placeholder stubs with "[TO BE COMPLETED]" markers — shows the full intended document structure even when incomplete

### Cross-reference resolution
- Unresolved references (target section doesn't exist) render as [BROKEN REF] placeholders — assembly continues
- Always generate XREF-REPORT.md listing all references, resolution status, and orphan sections
- Orphan handling: Claude's discretion on severity based on section type
- Cross-references render as plain text section numbers (e.g., "see Section 3.2.1"), not clickable links

### Standards enforcement
- Configurable severity per standard in PROJECT.md — engineer sets each standard to error (blocking) or warning (non-blocking)
- Standards checks run both automatically during /doc:complete-fds AND available as standalone /doc:check-standards command
- PackML state name enforcement: Claude's discretion based on PackML specification requirements
- Standalone COMPLIANCE.md report per standard with pass/fail per check, overall score, and remediation hints

### Versioning + release
- Semantic versioning (vX.Y): minor bumps (v0.1, v1.1) are internal, major bumps (v1.0, v2.0) are client releases
- Previous version files archived to .planning/archive/vX.Y/ on new release
- Revision history: hybrid approach — auto-generated from git as starting draft, engineer edits before release
- Client release gate: all phases must pass verification, but --force flag allows release with warnings

### Claude's Discretion
- Orphan section severity classification
- PackML state name enforcement approach (exact match vs synonym mapping)
- FDS structure template section ordering details
- ENGINEER-TODO.md format for diagrams exceeding Mermaid complexity

</decisions>

<specifics>
## Specific Ideas

- Version scheme already established in project brief: v0.x internal, v1.0 first customer-facing release, v1.1 internal revision, v2.0 next customer release
- FDS/SDS versioned independently (SDS references its source FDS version)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-complete-fds-standards*
*Context gathered: 2026-02-14*
