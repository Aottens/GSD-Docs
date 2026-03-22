# Requirements: GSD-Docs Industrial v2.0 GUI

**Defined:** 2026-02-14
**Core Value:** Engineers can create, manage, and review FDS/SDS projects through a visual web interface that guides them through the full document lifecycle

## v1 Requirements

Requirements for v2.0 release. Each maps to roadmap phases.

### Project Setup

- [x] **PROJ-01**: Engineer can create a new FDS project through a guided wizard with type classification (A/B/C/D)
- [x] **PROJ-02**: Engineer can select project language (Dutch/English) during project creation
- [ ] **PROJ-03**: Engineer can upload reference files during project creation
- [x] **PROJ-04**: Engineer can browse all projects in a dashboard with status and type indicators
- [ ] **PROJ-05**: Engineer can open a project from the dashboard to its working view

### Workflow Navigation

- [x] **WORK-01**: Engineer can view phase timeline showing ROADMAP phases with completion status
- [x] **WORK-02**: Engineer can view phase status and next recommended CLI command from the timeline
- [x] **WORK-03**: Engineer can view document outline tree with expandable/collapsible sections
- [x] **WORK-04**: Engineer can navigate to a specific section from the outline tree

### Discussion

~~DISC-01 through DISC-04 dropped — discussions handled by CLI (`/doc:discuss-phase`). GUI is a cockpit, not a conversation engine.~~

### Document Generation

- [x] **DOCG-01**: Engineer can view generated section plans with wave assignments in the GUI

~~DOCG-02 through DOCG-04 dropped — writing triggered via CLI (`/doc:write-phase`). GUI displays results.~~

### Quality & Review

- [x] **QUAL-01**: Engineer can view verification results from CLI output in the GUI
- [x] **QUAL-02**: Engineer can view gaps, severity, and recommendations from verification
- [x] **QUAL-03**: Engineer can see gap closure cycle status (verify → re-plan → re-write)
- [x] **QUAL-04**: Engineer can approve or reject verification results before proceeding
- [x] **QUAL-05**: Engineer can conduct review-phase with approve/reject/request-changes per section
- [x] **QUAL-06**: Engineer can provide text feedback during review that feeds back into the workflow
- [x] **QUAL-07**: Engineer can view PackML/ISA-88 standards compliance results in the GUI
- [x] **QUAL-08**: Engineer can view standards violations with references to standard sections

### Reference Management

- [ ] **REFM-01**: Engineer can upload reference files via drag-and-drop (PDF, DOCX, images)
- [ ] **REFM-02**: Engineer can view and manage per-project reference files
- [ ] **REFM-03**: Engineer can access shared reference library (read-only, admin-managed)
- [ ] **REFM-04**: Engineer can override shared references with project-specific uploads
- [ ] **REFM-05**: Admin can manage shared reference library (add, remove, categorize files)

### Document Output

- [x] **OUTP-01**: Engineer can preview rendered document content with Mermaid diagram rendering
- [x] **OUTP-02**: Engineer can trigger FDS assembly with cross-reference resolution
- [x] **OUTP-03**: Engineer can export FDS/SDS to DOCX with corporate styling
- [x] **OUTP-04**: Engineer can see export progress during DOCX generation
- [x] **OUTP-05**: Engineer can trigger SDS scaffolding from completed FDS with typicals matching
- [x] **OUTP-06**: Engineer can see typicals matching confidence scores and "NEW TYPICAL NEEDED" indicators
- [x] **OUTP-07**: Engineer can generate documents in Dutch or English based on project setting

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
| PROJ-01 | Phase 8 | Complete |
| PROJ-02 | Phase 8 | Complete |
| PROJ-03 | Phase 9 | Pending |
| PROJ-04 | Phase 8 | Complete |
| PROJ-05 | Phase 8 | Pending |
| WORK-01 | Phase 10 | Complete |
| WORK-02 | Phase 10 | Complete |
| WORK-03 | Phase 11 | Complete |
| WORK-04 | Phase 11 | Complete |
| DISC-01 | Dropped | CLI |
| DISC-02 | Dropped | CLI |
| DISC-03 | Dropped | CLI |
| DISC-04 | Dropped | CLI |
| DOCG-01 | Phase 11 | Complete |
| DOCG-02 | Dropped | CLI |
| DOCG-03 | Dropped | CLI |
| DOCG-04 | Dropped | CLI |
| QUAL-01 | Phase 12 | Complete |
| QUAL-02 | Phase 12 | Complete |
| QUAL-03 | Phase 12 | Complete |
| QUAL-04 | Phase 12 | Complete |
| QUAL-05 | Phase 12 | Complete |
| QUAL-06 | Phase 12 | Complete |
| QUAL-07 | Phase 12 | Complete |
| QUAL-08 | Phase 12 | Complete |
| REFM-01 | Phase 9 | Pending |
| REFM-02 | Phase 9 | Pending |
| REFM-03 | Phase 9 | Pending |
| REFM-04 | Phase 9 | Pending |
| REFM-05 | Phase 9 | Pending |
| OUTP-01 | Phase 11 | Complete |
| OUTP-02 | Phase 13 | Complete |
| OUTP-03 | Phase 13 | Complete |
| OUTP-04 | Phase 13 | Complete |
| OUTP-05 | Phase 13 | Complete |
| OUTP-06 | Phase 13 | Complete |
| OUTP-07 | Phase 13 | Complete |
| SYST-01 | Phase 14 | Pending |
| SYST-02 | Phase 14 | Pending |
| SYST-03 | Phase 14 | Pending |
| SYST-04 | Phase 8 | Pending |

**Coverage:**
- v1 requirements: 41 total
- Mapped to phases: 34
- Dropped (CLI handles): 7 (DISC-01–04, DOCG-02–04)

**Coverage validation:** 100% — All GUI requirements mapped to phases 8-14. Dropped requirements handled by v1.0 CLI.

---
*Requirements defined: 2026-02-14*
*Last updated: 2026-03-20 -- Cockpit pivot: phases 10-14 confirmed, 7 requirements dropped*
