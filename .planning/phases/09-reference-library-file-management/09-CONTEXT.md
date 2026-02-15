# Phase 9: Reference Library & File Management - Context

**Gathered:** 2026-02-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Engineers can upload, browse, and manage reference files (shared and per-project) with defense-in-depth security validation. Files include PDFs, DOCX, and images used as input for FDS/SDS generation. Shared library is admin-managed; project files are engineer-managed. File content extraction and AI processing are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Upload experience
- Uploads available in three locations: project creation wizard (as a step), workspace tab, and sidebar section
- Large drag-and-drop zone with a "browse files" button fallback — both options always visible
- Per-file progress bars showing status (uploading, validating, done)
- Accepted file types and max file size displayed upfront in the upload zone

### Library layout & browsing
- File list with metadata (table-like): filename, type icon, size, upload date — compact, scannable
- User-created folder structure for organization
- Predefined default folders based on project type (e.g., P&IDs, Specificaties, Standaarden) — user can add more
- Search bar with file type filter dropdown (PDF, DOCX, image) to find files across folders

### Shared vs project boundary
- Separate tabs: "Project bestanden" and "Gedeelde bibliotheek" — clearly separated views
- Explicit override action: user selects a shared file and clicks "Override" to upload a project-specific version
- Dedicated admin page for managing shared library files — only visible to admins

### File actions & preview
- Clicking a file opens a slide-in detail panel (reuse Sheet pattern from assistant) with preview, metadata, and actions
- Full inline preview for all types: PDF, images, AND rendered DOCX
- File management actions: delete, replace with new version, download, rename, move between folders
- Deletion requires confirmation dialog before proceeding

### Claude's Discretion
- Admin authentication mechanism for shared library (considering 5-20 user scale)
- Default folder names per project type (A/B/C/D)
- File size limits and exact supported file types beyond PDF/DOCX/images
- Upload validation error message design
- Detail panel layout and metadata fields shown

</decisions>

<specifics>
## Specific Ideas

- Reuse the slide-in Sheet component (from Phase 8 assistant panel) for file detail/preview panel
- Default folders should be domain-appropriate for industrial documentation (P&IDs, Specificaties, Standaarden, etc.)
- All UI in Dutch (consistent with Phase 8 decision)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 09-reference-library-file-management*
*Context gathered: 2026-02-15*
