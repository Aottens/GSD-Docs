---
phase: 14-project-setup-cli-handoff
plan: 01
subsystem: backend
tags: [api, models, alembic, setup-state, doc-types, cli-handoff]
dependency_graph:
  requires: []
  provides:
    - DOC_TYPE_CONFIG in config_phases.py
    - File.doc_type column
    - Project.skipped_doc_types column
    - SetupStateResponse schema
    - GET /api/projects/{id}/setup-state
    - GET /api/doc-types/{project_type}
    - PATCH /api/projects/{id}/skipped-doc-types
  affects:
    - backend/app/api/files.py (upload extended with doc_type)
    - backend/app/main.py (doc_types_router registered)
tech_stack:
  added: []
  patterns:
    - Alembic autogenerate migration for nullable column additions
    - Optional[str] for Python 3.9 compatibility instead of str | None
key_files:
  created:
    - backend/app/schemas/setup_state.py
    - backend/alembic/versions/5fad8e9a85f3_add_doc_type_to_files_and_skipped_doc_.py
    - backend/tests/test_setup_state.py
  modified:
    - backend/app/config_phases.py
    - backend/app/models/file.py
    - backend/app/models/project.py
    - backend/app/schemas/file.py
    - backend/app/api/projects.py
    - backend/app/api/files.py
    - backend/app/main.py
decisions:
  - "DOC_TYPE_CONFIG uses Optional[str] for Python 3.9 compat (str | None fails on 3.9)"
  - "doc_types_router as separate APIRouter in projects.py with /api/doc-types prefix — avoids route collision with /api/projects prefix"
  - "skipped_doc_types stored as JSON string in String(500) column — simple, no join table needed for small list"
  - "File paths in setup-state use absolute path via UPLOAD_DIR setting resolve"
metrics:
  duration: 4m
  completed_date: "2026-03-22"
  tasks_completed: 2
  files_created: 3
  files_modified: 7
---

# Phase 14 Plan 01: Backend Foundation for Doc-Type Metadata and Setup-State Summary

**One-liner:** DOC_TYPE_CONFIG for A/B/C/D project types, File.doc_type + Project.skipped_doc_types columns with Alembic migration, SetupStateResponse schema, and three new API endpoints for CLI handoff.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add DOC_TYPE_CONFIG, model columns, migration, and schemas | 7068fd3 | config_phases.py, models/file.py, models/project.py, schemas/setup_state.py, schemas/file.py, migration |
| 2 | Add setup-state endpoint, doc-types endpoint, extend upload, and tests | 55ca81e | api/projects.py, api/files.py, main.py, tests/test_setup_state.py |

## What Was Built

### DOC_TYPE_CONFIG (config_phases.py)

Added `DOC_TYPE_CONFIG` dict with document type definitions for each project type:
- **Type A**: fds_old, pid, machine_spec (required), risk_assess, standards (required)
- **Type B**: fds_old, pid (required), machine_spec (required), risk_assess
- **Type C**: baseline (required), pid (required), machine_spec (required), risk_assess, change_order
- **Type D**: pid, change_order (required), machine_spec

### Database Columns (Alembic migration 5fad8e9a85f3)

- `files.doc_type` — String(50), nullable, indexed — classifies upload into a doc type
- `projects.skipped_doc_types` — String(500), nullable — JSON list of skipped doc type IDs

### Schemas

- `DocTypeConfigEntry` — config shape (id, label, required)
- `DocTypeEntry` — coverage shape (id, label, required, status, file_count, file_paths)
- `SetupStateResponse` — full CLI handoff shape (project metadata + doc coverage + scaffolding + next command)
- `FileResponse.doc_type` and `FileUploadResponse.doc_type` fields added

### API Endpoints

- `GET /api/projects/{id}/setup-state` — Computes doc-type coverage, scaffolding presence, and next CLI command
- `GET /api/doc-types/{project_type}` — Returns DOC_TYPE_CONFIG list for a given type (frontend wizard)
- `PATCH /api/projects/{id}/skipped-doc-types` — Persists skipped doc types from 'Niet beschikbaar' toggle

### Upload Extension

`POST /api/projects/{id}/files` now accepts `?doc_type=<id>` query param, persists to DB, returns in response.

### Tests

9 unit tests in `tests/test_setup_state.py` — all passing:
- DOC_TYPE_CONFIG structure validation for all 4 types
- Type-specific presence checks (standards in A, baseline in C, change_order in D)
- DocTypeConfigEntry, DocTypeEntry, SetupStateResponse schema validation
- Serialization correctness

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Python 3.9 incompatibility with `str | None` union syntax**
- **Found during:** Task 1 verification
- **Issue:** `next_cli_command: str | None` in SetupStateResponse raises `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'` on Python 3.9
- **Fix:** Changed to `Optional[str]` with `from typing import Optional` import
- **Files modified:** backend/app/schemas/setup_state.py
- **Commit:** 7068fd3

**2. [Rule 3 - Blocking] DB not at head before autogenerate**
- **Found during:** Task 1 migration step
- **Issue:** DB was at `fb17f556ba07` but alembic head was `a7b46367f8f0` (drop_conversation_tables migration had not been applied)
- **Fix:** Ran `alembic upgrade head` to apply the pending drop_conversation_tables migration first, then ran autogenerate
- **Files modified:** None (operational step)

**3. [Rule 2 - Missing functionality] doc_types_router needs registration in main.py**
- **Found during:** Task 2 implementation
- **Issue:** The plan said to add endpoints to projects.py but the `/api/doc-types/{project_type}` route requires a different prefix than `/api/projects`
- **Fix:** Created `doc_types_router = APIRouter(prefix="/api/doc-types")` in projects.py and registered it in main.py

## Self-Check: PASSED

All created files exist on disk. All commits verified in git log. Tests pass (9/9).
