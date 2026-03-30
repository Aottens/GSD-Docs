---
phase: 11-document-preview-outline
plan: "01"
subsystem: api
tags: [fastapi, pydantic, pytest, typescript, fds-structure, yaml]

requires:
  - phase: 10-workflow-status-cleanup
    provides: Project model, get_db dependency, phases router pattern, config.py settings

provides:
  - "GET /api/projects/{id}/documents/outline endpoint returning full FDS section tree"
  - "GET /api/projects/{id}/documents/sections/{section_id}/content endpoint"
  - "PlanInfoSchema with truths (list[str]) and description (Optional[str])"
  - "OutlineNodeSchema with recursive children and status detection"
  - "_parse_plan_frontmatter() helper extracting YAML + must_haves.truths + <objective>"
  - "_build_outline_sections() with Type C/D baseline insertion and equipment placeholders"
  - "13 pytest tests GREEN covering schemas, outline structure, frontmatter parsing"
  - "Frontend TypeScript interfaces mirroring backend schemas exactly"

affects: [11-02, 11-03, document-preview, outline-viewer, plan-info-display]

tech-stack:
  added: [pyyaml>=6.0]
  patterns:
    - "_parse_plan_frontmatter pattern: parse YAML, extract nested must_haves.truths, extract <objective> block"
    - "TDD RED-GREEN: test file commits before implementation, then implementation makes all tests pass"
    - "_build_outline_sections returns raw dicts, _dict_to_outline_node converts to Pydantic at endpoint boundary"
    - "Router prefix /api/projects/{project_id}/documents for all document endpoints"

key-files:
  created:
    - backend/app/schemas/document.py
    - backend/app/api/documents.py
    - backend/tests/__init__.py
    - backend/tests/conftest.py
    - backend/tests/test_documents.py
    - frontend/src/features/documents/types/document.ts
  modified:
    - backend/app/schemas/__init__.py
    - backend/app/api/__init__.py
    - backend/app/main.py
    - backend/requirements.txt

key-decisions:
  - "pyyaml added explicitly to requirements.txt though available as transitive dep — makes dependency intent clear"
  - "_build_outline_sections returns list[dict] (not list[OutlineNodeSchema]) for testability — Pydantic conversion at endpoint boundary"
  - "section_id:path type for /sections/{section_id}/content route — allows dots in IDs like '4.2.3'"
  - "Type C/D baseline insertion shifts original 1.4 (Abbreviations) to 1.5 by mutating id in children list"
  - "Equipment module placeholder 4.0 added when no em-* or equipment-* phase dirs found"
  - "Objective description extracted as first non-empty line of <objective> block content"

patterns-established:
  - "_parse_plan_frontmatter(content: str) -> dict: returns {} on failure, never raises"
  - "_extract_objective(content: str) -> Optional[str]: regex-based <objective> tag extraction"
  - "_enrich_node_status: recursive filesystem scanner for PLAN.md/SUMMARY.md/VERIFICATION.md"

requirements-completed: [WORK-03, WORK-04, DOCG-01]

duration: 4min
completed: "2026-03-21"
---

# Phase 11 Plan 01: Backend Document Outline API + TypeScript Types Summary

**FastAPI document outline API reading fds-structure.json with Type C/D baseline insertion, PLAN.md frontmatter parser extracting truths and objective, and matching TypeScript types**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-21T07:44:43Z
- **Completed:** 2026-03-21T07:48:45Z
- **Tasks:** 3
- **Files modified:** 9 (6 created, 3 modified)

## Accomplishments

- Backend Pydantic schemas: PlanInfoSchema (with truths + description), OutlineNodeSchema, DocumentOutlineResponse, SectionContentResponse
- Two FastAPI endpoints: GET /outline (full section tree) and GET /sections/{section_id:path}/content
- PLAN.md frontmatter parser: extracts YAML, must_haves.truths (nested dict access), and `<objective>` block as description
- Type C/D conditional logic: inserts baseline section 1.4 and shifts abbreviations from 1.4 to 1.5
- Equipment module placeholder: section 4.0 added when no `em-*` phase dirs exist
- 13 pytest tests pass GREEN (TDD RED-GREEN cycle completed)
- Frontend TypeScript interfaces in documents feature directory matching backend schemas exactly

## Task Commits

Each task was committed atomically:

1. **Task 1: Backend Pydantic schemas + test scaffolding** - `2b5e550` (test)
2. **Task 2: Backend documents API endpoints** - `98aa1ab` (feat)
3. **Task 3: Frontend TypeScript types + run backend tests GREEN** - `37a12b0` (feat)

## Files Created/Modified

- `backend/app/schemas/document.py` - PlanInfoSchema, OutlineNodeSchema, DocumentOutlineResponse, SectionContentResponse
- `backend/app/api/documents.py` - Router, 2 endpoints, _parse_plan_frontmatter, _extract_objective, _build_outline_sections
- `backend/tests/__init__.py` - Empty package marker
- `backend/tests/conftest.py` - fds_structure fixture (loads fds-structure.json), tmp_project_dir fixture
- `backend/tests/test_documents.py` - 13 tests: 5 schema, 5 frontmatter parsing, 3 outline structure
- `frontend/src/features/documents/types/document.ts` - PlanInfo, OutlineNode, DocumentOutlineResponse, SectionContentResponse
- `backend/app/schemas/__init__.py` - Added 4 document schema exports
- `backend/app/api/__init__.py` - Added documents module import
- `backend/app/main.py` - Added documents router import and registration
- `backend/requirements.txt` - Added pyyaml>=6.0

## Decisions Made

- Used `section_id:path` path parameter type so section IDs containing dots (e.g., "4.2.3") are captured correctly by FastAPI
- `_build_outline_sections` returns `list[dict]` for testability; Pydantic model conversion happens at the endpoint boundary via `_dict_to_outline_node`
- `_parse_plan_frontmatter` always returns `{}` on failure (never raises) — safe for scanning many files
- `_extract_objective` returns first non-empty line from `<objective>` block as the plan description (keeps it concise)

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Backend outline and content APIs are ready for Phase 11-02 (frontend outline viewer)
- TypeScript type contract established: frontend can import from `frontend/src/features/documents/types/document.ts`
- All 13 tests pass; test infrastructure in `backend/tests/` ready for expansion in future plans

---
*Phase: 11-document-preview-outline*
*Completed: 2026-03-21*
