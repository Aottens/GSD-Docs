# Phase 13: Export & Assembly - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Engineers can assemble FDS with cross-reference resolution, export to DOCX with corporate styling, trigger SDS scaffolding with typicals matching, and download versioned artifacts — all from the GUI. The backend reimplements core assembly/export logic in Python (no CLI dependency at runtime). SDS gets its own workspace tab as foundation for a future library manager.

</domain>

<decisions>
## Implementation Decisions

### Trigger model
- GUI triggers assembly, export, and SDS scaffolding directly via backend API endpoints — these are deterministic file-processing operations, not AI
- Backend reimplements core logic in Python: cross-reference resolution, Pandoc invocation, typicals matching from CATALOG.json — no shelling out to CLI commands
- Assembly has two modes: Draft (allows partial/unreviewed content, produces watermarked DOCX) and Final (requires all phases reviewed)
- Each assembly/export stored as versioned artifact (e.g., FDS_v1.0_draft.docx) — engineer can download previous versions

### Export workflow UX
- New "Export" tab in workspace (alongside Overzicht, Fasering, Documenten, Referenties)
- Pipeline view layout: three-stage visual flow Assembleren -> Exporteren -> Downloaden, left to right
- Each pipeline stage shows status, action button, and result
- Export options: mode (Draft with watermark / Final) and language (Dutch/English from project setting, overridable per export)
- Version history as simple table below pipeline: Version, Type (Draft/Final), Language, Date, Size, Download button — most recent at top
- SDS scaffolding in separate section below FDS pipeline (but within same Export tab)

### SDS scaffolding display
- SDS gets its own workspace tab — foundation for future library manager / code scaffolding vision
- Phase 13 scope: display scaffolding results with typicals matching only (no library browser, no inline editing)
- Equipment-to-typical mapping table: Equipment Module | Matched Typical | Confidence Score | Status
- Status indicators: matched (green), low confidence (amber), "NIEUW TYPICAL NODIG" (red)
- Table is sortable and filterable
- Click to expand: shows why matching failed (missing I/O, no use_case match), closest match, CLI hint for /doc:generate-sds to refine
- Read-only catalog browser deferred to future library manager phase

### Progress & status feedback
- Step-by-step progress bar with named steps: "Cross-referenties oplossen" -> "Secties samenvoegen" -> "DOCX genereren" -> "Diagrammen renderen"
- Each step ticks as it completes — engineer sees exactly where the process is
- SSE streaming for real-time progress updates (sse-starlette already installed from Phase 10)
- Cancel button available during operations — aborts gracefully, cleans up partial files, pipeline returns to previous state
- Errors shown inline in the pipeline step that failed: expandable detail block with what went wrong and fix hint (e.g., "Pandoc niet gevonden — installeer via brew install pandoc")
- Pipeline stays visible on error, failed step highlighted red

### Claude's Discretion
- Exact pipeline visual design (card-based steps, stepper, or connected flow)
- SSE event schema for progress updates
- Version numbering scheme for stored artifacts
- Exact Pandoc invocation flags and fallback behavior
- How to detect Pandoc installation and version
- Draft watermark implementation approach
- SDS tab navigation item placement and icon
- Loading/error states for long operations

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### FDS assembly workflow (v1.0 SSOT)
- `gsd-docs-industrial/workflows/complete-fds.md` — 15-step assembly pipeline: section ordering from fds-structure.json, IEC-style hierarchical numbering, cross-reference resolution, standards checking
- `gsd-docs-industrial/templates/fds-structure.json` — Canonical FDS section hierarchy: 7 top-level sections, equipment modules dynamic subsections, bilingual titles (en/nl), Type C/D baseline handling

### DOCX export workflow (v1.0 SSOT)
- `gsd-docs-industrial/workflows/export.md` — 10-step DOCX pipeline: Pandoc invocation, Mermaid rendering, corporate styling, graceful degradation (--draft/--skip-diagrams)
- `gsd-docs-industrial/references/huisstijl-README.md` — Corporate styling spec: heading styles (16/14/12pt bold dark blue), body (11pt Calibri), table headers (light blue), header/footer layout

### SDS scaffolding workflow (v1.0 SSOT)
- `gsd-docs-industrial/workflows/generate-sds.md` — 12-step SDS scaffolding: typicals matching from CATALOG.json, confidence scoring, "NEW TYPICAL NEEDED" indicators
- `gsd-docs-industrial/references/typicals/CATALOG-SCHEMA.json` — JSON Schema for catalog structure: FB typicals with interfaces (I/O), use_cases for matching, categories

### SPECIFICATION (SSOT)
- `gsd-docs-industrial/SPECIFICATION.md` — SSOT for all document generation logic, project directory layout, section content format

### Backend integration points
- `backend/app/api/documents.py` — Document API (outline, section content) — extend or add export endpoints alongside
- `backend/app/api/phases.py` — Phase API with filesystem-based status detection pattern
- `backend/app/models/project.py` — Project model with Language enum (nl/en), ProjectStatus, project type (A/B/C/D)
- `backend/app/config_phases.py` — PROJECT_TYPE_PHASES for phase structure per project type

### Frontend integration points
- `frontend/src/features/projects/components/ProjectWorkspace.tsx` — Workspace layout, activeSection state — add "export" and "sds" cases
- `frontend/src/features/projects/components/ProjectNavigation.tsx` — Navigation items — add Export and SDS tabs
- `frontend/src/features/documents/components/DocumentsTab.tsx` — Reference for split-pane layout, React Query patterns, async data loading

### Existing SSE infrastructure
- `sse-starlette` package already installed — reuse for progress streaming

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `sse-starlette`: Already installed, used in Phase 10 — reuse for assembly/export progress streaming
- `react-query`: Established pattern for data fetching and cache invalidation — use for version history, SDS results
- `Sonner` toast system: For non-blocking notifications (export complete, download ready)
- `Badge`, `Table`, `Button`, `Skeleton`: shadcn/ui components ready for pipeline UI, version table, SDS mapping table
- `api.ts` client with typed responses and 204 handling
- `Language` enum in project model — already stores nl/en per project

### Established Patterns
- All UI in Dutch (consistent with Phase 8-12)
- Filesystem-based status detection in `phases.py` — extend for assembly/export status
- React Query polling at 10-30s for background updates
- ProjectWorkspace activeSection switch pattern for new tabs
- ProjectNavigation items array for adding tabs
- Inline error display pattern from verification detail (Phase 12)

### Integration Points
- `ProjectWorkspace.tsx`: Add "export" and "sds" cases to activeSection switch
- `ProjectNavigation.tsx`: Add "Export" and "SDS" nav items
- `backend/app/api/`: New `export.py` router for assembly/export/download endpoints + `sds.py` for scaffolding
- `backend/app/main.py`: Register new routers
- Project model: May need export_versions relationship or separate ExportArtifact model

</code_context>

<specifics>
## Specific Ideas

- Pipeline view should feel like a CI/CD pipeline — clear stages, visual flow from left to right
- SDS tab is the seed for a future library manager that generates Siemens TIA and Ignition typicals/building blocks/faceplates — from documentation to scaffolded PLC/SCADA project in one go
- Draft mode with watermark enables early reviews without implying the document is final
- Version table keeps it simple — engineers need to find and download specific versions quickly

</specifics>

<deferred>
## Deferred Ideas

- **SDS Library Manager** — Future tab evolution: browse/manage typicals catalog, generate Siemens TIA and Ignition building blocks/faceplates dynamically, go from FDS documentation to scaffolded TIA/Ignition Designer project. Own phase.
- **Batch export** — ENAV-01 in v2 requirements: export multiple variants (draft, final, with/without diagrams) in one action
- **Read-only catalog browser** — Browse available typicals from CATALOG.json alongside matching results

</deferred>

---

*Phase: 13-export-assembly*
*Context gathered: 2026-03-21*
