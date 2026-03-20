# Phase 11: Document Preview & Outline - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Engineers can view rendered FDS content, navigate a section outline tree, see generated section plans with wave assignments, and view Mermaid diagrams inline. The GUI is read-only — it displays content produced by CLI commands, never writes to project files. Review workflow and export are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Outline tree & navigation
- Split view layout: left panel = outline tree, right panel = content preview, with resizable divider (using existing ResizablePanelGroup component)
- Tree nodes show section title + status icon + 1-line preview snippet when content exists
- Full depth from fds-structure.json — all levels including equipment module subsections (e.g., 4.2.3 States)
- Section numbers auto-derived from fds-structure.json (1, 1.1, 4.2.3) — matches final document output
- Clicking a node scrolls to that section in a continuous scrollable document view
- Scroll-spy highlights the currently visible section in the outline tree

### Content rendering
- Document-style typography: generous whitespace, clear heading hierarchy, styled tables and code blocks (Notion/GitBook aesthetic)
- Mermaid code blocks render automatically as inline SVG diagrams, fallback to showing code block if rendering fails
- Subtle section headers: light divider line with section number and phase badge per section
- Auto-numbered sections matching FDS structure (1.1, 4.2.3) derived from fds-structure.json

### Plans & wave display
- Plan info integrated directly into outline tree nodes — wave badge (W1, W2, W3) with color coding (W1=blue, W2=green, W3=orange, etc.)
- Clicking a planned-but-unwritten section shows plan details card in content panel: wave assignment, dependencies, must-haves/truths from frontmatter, plan description — formatted as readable card, not raw YAML
- Dependencies shown as tooltip on hover: "Depends on: 4.1.1, 4.1.2"

### Empty & partial states
- Fresh projects show the full outline tree structure (derived from project type) with all nodes in 'empty' state; content panel shows friendly message with next CLI command
- Progressive status icons per node: empty circle (nothing), clipboard (plan only), document (content written), checkmark (verified) — gray for empty, colored for active states
- Clicking an empty section shows section info + next action: section title, FDS structure position, next CLI command needed
- Auto-refresh via polling every 10-30 seconds (matching PhaseTimeline pattern) — picks up new CONTENT.md or PLAN.md written by CLI

### Claude's Discretion
- Exact polling interval within the 10-30s range
- Outline tree panel default width and min/max constraints
- Mermaid rendering library choice and configuration
- Loading skeleton design for content panel
- Scroll-spy implementation approach
- Exact color palette for wave badges
- Typography scale and spacing for document-style rendering
- How to handle malformed or partial markdown files

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### FDS document structure
- `gsd-docs-industrial/templates/fds-structure.json` — Canonical FDS section hierarchy: 7 top-level sections, equipment modules dynamic subsections, bilingual titles (en/nl), depth levels, required flags, source_type
- `gsd-docs-industrial/SPECIFICATION.md` — SSOT for document generation logic, project directory layout, phase structure, section content format

### Project type definitions
- `backend/app/config_phases.py` — PROJECT_TYPE_PHASES mapping: A(6 phases), B(5), C(4), D(2) with phase names and goals

### Existing filesystem status detection
- `backend/app/api/phases.py` — `_derive_phase_status()` pattern for globbing `.planning/phases/{NN}-*/` files, `_get_project_dir()` helper, `_extract_decisions()` XML parser
- `backend/app/config.py` — PROJECT_ROOT configuration

### Frontend integration points
- `frontend/src/features/projects/components/ProjectWorkspace.tsx` — Main workspace layout, activeSection state, documents slot ready
- `frontend/src/features/projects/components/ProjectNavigation.tsx` — Navigation items, `documents` item stubbed but disabled
- `frontend/src/features/projects/components/ProjectOverview.tsx` — "Documenten bekijken" quick action button (disabled, marked Fase 11)
- `frontend/src/features/timeline/hooks/usePhaseStatus.ts` — React Query patterns for phase data fetching

### Existing UI components
- `frontend/src/components/ui/resizable.tsx` — ResizablePanelGroup for split-pane layout
- `frontend/src/components/ui/` — Full shadcn/ui component set (Badge, Skeleton, Tabs, Tooltip, etc.)

### v1.0 FDS templates (content format reference)
- `gsd-docs-industrial/templates/section-state-machine.md` — Example of Mermaid diagram usage in FDS content
- `gsd-docs-industrial/templates/` — All section templates defining expected markdown structure

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `react-markdown@10.1.0` + `remark-gfm@4.0.1`: Already installed, not yet used — zero setup cost for markdown rendering
- `ResizablePanelGroup` + `ResizablePanel` + `ResizableHandle`: Installed and wrapped in `ui/resizable.tsx` — ready for outline/content split
- `react-pdf` + `docx-preview`: Already used in `FilePreviewPanel.tsx` — precedent for document preview patterns
- `Badge`, `Skeleton`, `Tabs`, `Tooltip`: shadcn/ui components for tree node badges, loading states, view switching, dependency tooltips
- `cn()` utility in `lib/utils.ts` for conditional classnames

### Established Patterns
- All UI in Dutch — consistent with Phase 8/9/10
- React Query with `useQuery` for data fetching — `usePhaseTimeline` polls at 10s interval
- API client `api.get<T>()` in `lib/api.ts` with typed responses and 204 handling
- Filesystem-based status detection in `phases.py` — no DB queries for content status
- `PROJECT_ROOT` config for project file paths
- Toast notifications via Sonner for async operations

### Integration Points
- `ProjectWorkspace.tsx`: Add `documents` case to activeSection switch — renders new DocumentsTab
- `ProjectNavigation.tsx`: Enable `documents` nav item (currently disabled)
- `ProjectOverview.tsx`: Enable "Documenten bekijken" quick action button
- `backend/app/api/phases.py` or new `documents.py`: New endpoints for outline, content, and plan data
- `fds-structure.json`: Backend reads this to build outline tree API response, filtered by project type

</code_context>

<specifics>
## Specific Ideas

- Split view inspired by IDE file explorer + editor (VS Code) — outline on the left, content on the right, resizable divider
- Document rendering should feel like Notion or GitBook — clean, readable, not a code preview
- Wave badges on outline nodes provide at-a-glance parallelism info without needing a separate view
- Empty sections are informative, not dead-ends — always show what CLI command to run next

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 11-document-preview-outline*
*Context gathered: 2026-03-20*
