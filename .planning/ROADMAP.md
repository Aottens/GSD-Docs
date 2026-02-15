# Roadmap: GSD-Docs Industrial

**Created:** 2026-02-06

## Milestones

- ✅ **v1.0 CLI** - Phases 1-7 (shipped 2026-02-14)
- 🚧 **v2.0 GUI** - Phases 8-17 (in progress)

## Phases

<details>
<summary>✅ v1.0 CLI (Phases 1-7) - SHIPPED 2026-02-14</summary>

Complete Claude Code plugin for FDS/SDS document generation. 14 commands, 194 files, 50,263 lines. All 89 v1.0 requirements satisfied. See `milestones/v1.0-ROADMAP.md` for archived phase details.

</details>

### 🚧 v2.0 GUI (In Progress)

**Milestone Goal:** Web-based GUI that wraps the proven v1.0 CLI workflow in a visual, team-accessible interface with FastAPI backend and React frontend.

#### Phase 8: Core Infrastructure & Project Management

**Goal**: Foundation architecture supports all subsequent workflows with real-time communication, async file handling, LLM abstraction, and basic project management.

**Depends on**: Phase 7 (v1.0 shipped)

**Requirements**: PROJ-01, PROJ-02, PROJ-04, PROJ-05, SYST-04

**Success Criteria** (what must be TRUE):
  1. Engineer can create a new FDS project through the web GUI with type classification (A/B/C/D)
  2. Engineer can select project language (Dutch/English) during project creation
  3. Engineer can browse all projects in a dashboard with status and type indicators
  4. Engineer can open a project from the dashboard to its working view
  5. LLM provider abstracted behind interface for future local model support

**Plans**: 3 plans

Plans:
- [ ] 08-01-PLAN.md — Backend foundation: FastAPI + SQLite + Alembic + Project CRUD API + LLM abstraction
- [ ] 08-02-PLAN.md — Frontend foundation + Dashboard: Vite/React/Tailwind/shadcn setup + project card grid with filters
- [ ] 08-03-PLAN.md — Project wizard + Working view: 3-step creation wizard + three-panel workspace + visual checkpoint

#### Phase 9: Reference Library & File Management

**Goal**: Engineers can upload, browse, and manage reference files (shared and per-project) with defense-in-depth security validation.

**Depends on**: Phase 8

**Requirements**: PROJ-03, REFM-01, REFM-02, REFM-03, REFM-04, REFM-05

**Success Criteria** (what must be TRUE):
  1. Engineer can upload reference files during project creation
  2. Engineer can upload reference files via drag-and-drop (PDF, DOCX, images)
  3. Engineer can view and manage per-project reference files
  4. Engineer can access shared reference library (read-only, admin-managed)
  5. Engineer can override shared references with project-specific uploads
  6. Admin can manage shared reference library (add, remove, categorize files)

**Plans**: TBD

Plans:
- [ ] 09-01: TBD
- [ ] 09-02: TBD

#### Phase 10: Discussion Workflow & Chat Interface

**Goal**: Engineers can conduct discussion phases through an embedded chat panel with real-time AI interaction and conversation persistence.

**Depends on**: Phase 9

**Requirements**: WORK-01, WORK-02, DISC-01, DISC-02, DISC-03, DISC-04

**Success Criteria** (what must be TRUE):
  1. Engineer can view phase timeline showing ROADMAP phases with completion status
  2. Engineer can trigger phase operations (discuss/plan/write/verify/review) from the timeline
  3. Engineer can conduct discussion phases through an embedded chat panel
  4. Chat panel displays AI-generated questions about gray areas in the phase
  5. Engineer can view conversation history for completed discussions
  6. Discussion decisions persist in CONTEXT.md for downstream phases

**Plans**: TBD

Plans:
- [ ] 10-01: TBD
- [ ] 10-02: TBD
- [ ] 10-03: TBD

#### Phase 11: Planning Workflow & Section Organization

**Goal**: Engineers can trigger plan-phase to generate section plans with wave assignments and navigate document outline.

**Depends on**: Phase 10

**Requirements**: WORK-03, WORK-04, DOCG-01

**Success Criteria** (what must be TRUE):
  1. Engineer can view document outline tree with expandable/collapsible sections
  2. Engineer can navigate to a specific section from the outline tree
  3. Engineer can trigger plan-phase to generate section plans with wave assignments

**Plans**: TBD

Plans:
- [ ] 11-01: TBD
- [ ] 11-02: TBD

#### Phase 12: Writing Workflow & Real-Time Progress

**Goal**: Engineers can trigger parallel section writing with real-time progress feedback and document preview capabilities.

**Depends on**: Phase 11

**Requirements**: DOCG-02, DOCG-03, DOCG-04, OUTP-01

**Success Criteria** (what must be TRUE):
  1. Engineer can trigger write-phase to generate section content in parallel waves
  2. Engineer can see real-time progress during AI writing with section-level granularity
  3. Engineer can view which reference docs and context fed each section writer
  4. Engineer can preview rendered document content with Mermaid diagram rendering

**Plans**: TBD

Plans:
- [ ] 12-01: TBD
- [ ] 12-02: TBD
- [ ] 12-03: TBD

#### Phase 13: Verification & Gap Closure

**Goal**: Engineers can run 5-level verification cascade with gap detection, closure loops, and opt-in standards compliance.

**Depends on**: Phase 12

**Requirements**: QUAL-01, QUAL-02, QUAL-03, QUAL-04, QUAL-07, QUAL-08

**Success Criteria** (what must be TRUE):
  1. Engineer can trigger verify-phase to run 5-level verification cascade
  2. Engineer can view verification results with gaps, severity, and recommendations
  3. Engineer can see gap closure cycles (verify → re-plan → re-write, max 2 iterations)
  4. Engineer can approve or reject verification results before proceeding
  5. Engineer can enable opt-in PackML/ISA-88 standards compliance checking
  6. Engineer can view standards violations with references to standard sections

**Plans**: TBD

Plans:
- [ ] 13-01: TBD
- [ ] 13-02: TBD

#### Phase 14: Review & Human-in-the-Loop

**Goal**: Engineers can conduct review-phase with approve/reject/request-changes workflow and text feedback capture.

**Depends on**: Phase 13

**Requirements**: QUAL-05, QUAL-06

**Success Criteria** (what must be TRUE):
  1. Engineer can conduct review-phase with approve/reject/request-changes per section
  2. Engineer can provide text feedback during review that feeds back into the workflow

**Plans**: TBD

Plans:
- [ ] 14-01: TBD

#### Phase 15: FDS Assembly & Export

**Goal**: Engineers can assemble complete FDS with cross-reference resolution and export to DOCX with corporate styling.

**Depends on**: Phase 14

**Requirements**: OUTP-02, OUTP-03, OUTP-04, OUTP-07

**Success Criteria** (what must be TRUE):
  1. Engineer can trigger FDS assembly with cross-reference resolution
  2. Engineer can export FDS/SDS to DOCX with corporate styling
  3. Engineer can see export progress during DOCX generation
  4. Engineer can generate documents in Dutch or English based on project setting

**Plans**: TBD

Plans:
- [ ] 15-01: TBD
- [ ] 15-02: TBD

#### Phase 16: SDS Generation

**Goal**: Engineers can generate SDS scaffolding from completed FDS with typicals matching and confidence scoring.

**Depends on**: Phase 15

**Requirements**: OUTP-05, OUTP-06

**Success Criteria** (what must be TRUE):
  1. Engineer can trigger SDS scaffolding from completed FDS with typicals matching
  2. Engineer can see typicals matching confidence scores and "NEW TYPICAL NEEDED" indicators

**Plans**: TBD

Plans:
- [ ] 16-01: TBD

#### Phase 17: Production Hardening & Deployment

**Goal**: Application deployed on VM with crash recovery, graceful shutdown, and production monitoring.

**Depends on**: Phase 16

**Requirements**: SYST-01, SYST-02, SYST-03

**Success Criteria** (what must be TRUE):
  1. System detects incomplete phases and offers resume from last checkpoint
  2. Application deploys on VM with Nginx reverse proxy and systemd services
  3. Project files remain compatible with v1.0 CLI /doc:* commands

**Plans**: TBD

Plans:
- [ ] 17-01: TBD
- [ ] 17-02: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Framework Foundation | v1.0 | 4/4 | Complete | 2026-02-07 |
| 2. Discuss + Plan | v1.0 | 4/4 | Complete | 2026-02-08 |
| 3. Write + Verify | v1.0 | 5/5 | Complete | 2026-02-10 |
| 4. State Management | v1.0 | 5/5 | Complete | 2026-02-13 |
| 5. Complete-FDS + Standards | v1.0 | 5/5 | Complete | 2026-02-14 |
| 6. Knowledge Transfer | v1.0 | 5/5 | Complete | 2026-02-14 |
| 7. SDS + Export | v1.0 | 5/5 | Complete | 2026-02-14 |
| 8. Core Infrastructure | v2.0 | 0/3 | Planned | - |
| 9. File Management | v2.0 | 0/2 | Not started | - |
| 10. Discussion Workflow | v2.0 | 0/3 | Not started | - |
| 11. Planning Workflow | v2.0 | 0/2 | Not started | - |
| 12. Writing Workflow | v2.0 | 0/3 | Not started | - |
| 13. Verification | v2.0 | 0/2 | Not started | - |
| 14. Review | v2.0 | 0/1 | Not started | - |
| 15. FDS Assembly | v2.0 | 0/2 | Not started | - |
| 16. SDS Generation | v2.0 | 0/1 | Not started | - |
| 17. Production Hardening | v2.0 | 0/2 | Not started | - |

---
*Roadmap created: 2026-02-06*
*Last updated: 2026-02-14 -- v2.0 milestone added*
