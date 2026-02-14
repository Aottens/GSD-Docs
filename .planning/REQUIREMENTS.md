# Requirements: GSD-Docs Industrial v2.0 GUI

**Defined:** 2026-02-14
**Core Value:** Engineers can create, manage, and review FDS/SDS projects through a visual web interface that guides them through the full document lifecycle

## v1 Requirements

Requirements for v2.0 release. Each maps to roadmap phases.

### Project Setup

- [ ] **PROJ-01**: Engineer can create a new FDS project through a guided wizard with type classification (A/B/C/D)
- [ ] **PROJ-02**: Engineer can select project language (Dutch/English) during project creation
- [ ] **PROJ-03**: Engineer can upload reference files during project creation
- [ ] **PROJ-04**: Engineer can browse all projects in a dashboard with status and type indicators
- [ ] **PROJ-05**: Engineer can open a project from the dashboard to its working view

### Workflow Navigation

- [ ] **WORK-01**: Engineer can view phase timeline showing ROADMAP phases with completion status
- [ ] **WORK-02**: Engineer can trigger phase operations (discuss/plan/write/verify/review) from the timeline
- [ ] **WORK-03**: Engineer can view document outline tree with expandable/collapsible sections
- [ ] **WORK-04**: Engineer can navigate to a specific section from the outline tree

### Discussion

- [ ] **DISC-01**: Engineer can conduct discussion phases through an embedded chat panel
- [ ] **DISC-02**: Chat panel displays AI-generated questions about gray areas in the phase
- [ ] **DISC-03**: Engineer can view conversation history for completed discussions
- [ ] **DISC-04**: Discussion decisions persist in CONTEXT.md for downstream phases

### Document Generation

- [ ] **DOCG-01**: Engineer can trigger plan-phase to generate section plans with wave assignments
- [ ] **DOCG-02**: Engineer can trigger write-phase to generate section content in parallel waves
- [ ] **DOCG-03**: Engineer can see real-time progress during AI writing with section-level granularity
- [ ] **DOCG-04**: Engineer can view which reference docs and context fed each section writer

### Quality & Review

- [ ] **QUAL-01**: Engineer can trigger verify-phase to run 5-level verification cascade
- [ ] **QUAL-02**: Engineer can view verification results with gaps, severity, and recommendations
- [ ] **QUAL-03**: Engineer can see gap closure cycles (verify → re-plan → re-write, max 2 iterations)
- [ ] **QUAL-04**: Engineer can approve or reject verification results before proceeding
- [ ] **QUAL-05**: Engineer can conduct review-phase with approve/reject/request-changes per section
- [ ] **QUAL-06**: Engineer can provide text feedback during review that feeds back into the workflow
- [ ] **QUAL-07**: Engineer can enable opt-in PackML/ISA-88 standards compliance checking
- [ ] **QUAL-08**: Engineer can view standards violations with references to standard sections

### Reference Management

- [ ] **REFM-01**: Engineer can upload reference files via drag-and-drop (PDF, DOCX, images)
- [ ] **REFM-02**: Engineer can view and manage per-project reference files
- [ ] **REFM-03**: Engineer can access shared reference library (read-only, admin-managed)
- [ ] **REFM-04**: Engineer can override shared references with project-specific uploads
- [ ] **REFM-05**: Admin can manage shared reference library (add, remove, categorize files)

### Document Output

- [ ] **OUTP-01**: Engineer can preview rendered document content with Mermaid diagram rendering
- [ ] **OUTP-02**: Engineer can trigger FDS assembly with cross-reference resolution
- [ ] **OUTP-03**: Engineer can export FDS/SDS to DOCX with corporate styling
- [ ] **OUTP-04**: Engineer can see export progress during DOCX generation
- [ ] **OUTP-05**: Engineer can trigger SDS scaffolding from completed FDS with typicals matching
- [ ] **OUTP-06**: Engineer can see typicals matching confidence scores and "NEW TYPICAL NEEDED" indicators
- [ ] **OUTP-07**: Engineer can generate documents in Dutch or English based on project setting

### System & Deployment

- [ ] **SYST-01**: System detects incomplete phases and offers resume from last checkpoint
- [ ] **SYST-02**: Application deploys on VM with Nginx reverse proxy and systemd services
- [ ] **SYST-03**: Project files remain compatible with v1.0 CLI /doc:* commands
- [ ] **SYST-04**: LLM provider abstracted behind interface for future local model support

## v2 Requirements

Deferred to v2.x releases. Tracked but not in current roadmap.

### Enhanced Navigation

- **ENAV-01**: Engineer can batch export multiple variants (draft, final, with/without diagrams)

### Team Features

- **TEAM-01**: Role-based access control for projects
- **TEAM-02**: Project sharing with activity logs
- **TEAM-03**: Client portal with read-only review access

### Advanced Features

- **ADVN-01**: Version comparison UI (diff between FDS versions)
- **ADVN-02**: Full-text search across all projects
- **ADVN-03**: Local LLM support via provider swap (v3.0 milestone)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Real-time collaborative editing | Single-engineer workflow by design; review-phase handles collaboration |
| Full auto-generation (zero human input) | Equipment details cannot be inferred; results in hallucinated/unsafe content |
| Inline Markdown editing in GUI | Creates divergence from file-backed state; breaks CLI compatibility |
| Database-backed document storage | STATE.md must remain human-readable and git-trackable; SQLite for metadata only |
| Live DOCX preview (Word-perfect) | Requires Word rendering engine; Markdown preview sufficient |
| AI provider selection per project | Single provider per deployment; v3.0 adds local model support |
| Undo/redo for AI operations | Forward-only by design; review-phase and gap closure handle corrections |
| Mobile/tablet UI | Engineering work is desktop-based; no field use cases identified |
| PLC code generation | SDS describes design, not executable code; safety risk |
| P&ID / electrical diagram generation | Engineering Package items requiring CAD tools |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| *(populated by roadmapper)* | | |

**Coverage:**
- v1 requirements: 41 total
- Mapped to phases: 0
- Unmapped: 41 (pending roadmap)

---
*Requirements defined: 2026-02-14*
*Last updated: 2026-02-14 after initial definition*
