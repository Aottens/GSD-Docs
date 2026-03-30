---
phase: 10-discussion-workflow-chat-interface
plan: 01
subsystem: api
tags: [fastapi, python, alembic, sqlite, filesystem-status, phase-timeline]

# Dependency graph
requires:
  - phase: 08-core-infrastructure
    provides: FastAPI backend with project CRUD and SQLAlchemy models
  - phase: 09-file-management
    provides: File/Folder models and filesystem storage patterns
provides:
  - Filesystem-based phase status detection via _derive_phase_status()
  - config_phases.py with PROJECT_TYPE_PHASES (A/B/C/D) and CLI command mapping
  - Phase timeline API returning cli_command for next /doc:* step
  - Context-files endpoint reading CONTEXT.md decisions and VERIFICATION.md score
  - Alembic migration to drop conversations and messages tables
  - Zero-LLM-dependency backend
affects: [frontend-phase-timeline, 10-02-frontend-rework]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Filesystem artifact detection for phase status (CONTEXT.md/PLAN.md/SUMMARY.md/VERIFICATION.md/REVIEW.md)
    - CLI command mapping from status string via STATUS_CLI_COMMANDS dict
    - XML regex extraction for decisions from CONTEXT.md <decisions> blocks

key-files:
  created:
    - backend/app/config_phases.py
    - backend/alembic/versions/a7b46367f8f0_drop_conversation_tables.py
  modified:
    - backend/app/config.py
    - backend/app/schemas/phase.py
    - backend/app/models/phase.py
    - backend/app/models/__init__.py
    - backend/app/api/phases.py
    - backend/app/api/__init__.py
    - backend/app/schemas/__init__.py
    - backend/app/services/__init__.py
    - backend/app/main.py
    - backend/requirements.txt

key-decisions:
  - "Filesystem status detection replaces conversation DB queries — phase status derived from CONTEXT.md, PLAN.md, SUMMARY.md, VERIFICATION.md, REVIEW.md presence"
  - "PROJECT_TYPE_PHASES extracted from deleted prompts module into standalone config_phases.py"
  - "STATUS_CLI_COMMANDS maps each phase status to its next /doc:* CLI command"
  - "ContextFilesResponse extracts decisions from <decisions> XML blocks and verification score from VERIFICATION.md"
  - ".env cleaned to remove deleted LLM_PROVIDER and LLM_MODEL settings"

patterns-established:
  - "config_phases.py: standalone module for project type definitions, no external dependencies"
  - "Phase status hierarchy: reviewed > verified > written > planned > discussed > not_started"
  - "_extract_decisions(): regex on <decisions> XML block, returns bullet items"
  - "_extract_verification_summary(): regex for N/N levels passed and CRITICAL/MAJOR/MINOR severity table"

requirements-completed: [WORK-01, WORK-02]

# Metrics
duration: 3min
completed: 2026-03-20
---

# Phase 10 Plan 01: Backend Cleanup and Rework Summary

**Filesystem-based phase status API with CLI command mapping, replacing 12+ discussion/LLM files removed in cockpit pivot**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-03-20T20:13:35Z
- **Completed:** 2026-03-20T20:17:14Z
- **Tasks:** 2
- **Files modified:** 10 modified, 2 created, 12 deleted

## Accomplishments

- Surgically removed all discussion engine and LLM infrastructure: 12 files deleted (llm/, prompts/, conversations model/schema, 6 service files)
- Created `config_phases.py` with `PROJECT_TYPE_PHASES` (A/B/C/D), `STATUS_CLI_COMMANDS`, and `get_cli_command()` helper
- Rewired phase timeline API to derive status from filesystem artifacts instead of conversation DB records
- Added `/context-files` endpoint that reads CONTEXT.md decisions and VERIFICATION.md score
- Created Alembic migration `a7b46367f8f0` to drop messages and conversations tables
- Backend starts clean with zero import errors and zero LLM dependencies

## Task Commits

Each task was committed atomically:

1. **Task 1: Extract PROJECT_TYPE_PHASES, update schemas/models** - `f0fc05d` (feat)
2. **Task 2: Rework phase API, delete LLM code, create migration** - `96adffd` (feat)

## Files Created/Modified

- `backend/app/config_phases.py` — PROJECT_TYPE_PHASES dict, STATUS_CLI_COMMANDS, get_cli_command()
- `backend/app/config.py` — Removed LLM fields, added PROJECT_ROOT setting
- `backend/app/schemas/phase.py` — PhaseStatusResponse with cli_command, context_decisions, verification fields; new ContextFilesResponse
- `backend/app/models/phase.py` — PhaseInfo without conversation_id/available_actions, with cli_command
- `backend/app/models/__init__.py` — Removed conversation model imports
- `backend/app/api/phases.py` — Full rewrite: _derive_phase_status(), _extract_decisions(), _extract_verification_summary(), context-files endpoint
- `backend/app/api/__init__.py` — Removed discussions and context imports
- `backend/app/schemas/__init__.py` — Removed conversation schemas, added ContextFilesResponse
- `backend/app/services/__init__.py` — Removed llm_service, kept only ProjectService
- `backend/app/main.py` — Removed discussions.router and context.router registrations
- `backend/requirements.txt` — Removed litellm and sse-starlette
- `backend/alembic/versions/a7b46367f8f0_drop_conversation_tables.py` — Drops messages and conversations tables

**Deleted:** backend/app/llm/ (3 files), backend/app/prompts/ (2 files), backend/app/api/discussions.py, backend/app/api/context.py, backend/app/models/conversation.py, backend/app/schemas/conversation.py, backend/app/services/llm_service.py, backend/app/services/discussion_engine.py, backend/app/services/conversation_state.py, backend/app/services/decision_extractor.py, backend/app/services/context_generator.py, backend/app/services/structured_output_parser.py

## Decisions Made

- Filesystem status detection: phase status hierarchy = reviewed > verified > written > planned > discussed > not_started, derived from presence of specific artifact files
- Cleaned `.env` to remove deleted LLM_PROVIDER and LLM_MODEL settings (would have caused pydantic ValidationError with extra fields)
- context-files endpoint routes BEFORE /{phase_number} to avoid FastAPI treating "context-files" as an integer path segment

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Cleaned .env file of deleted LLM settings**
- **Found during:** Task 1 verification
- **Issue:** `.env` contained LLM_PROVIDER and LLM_MODEL which became "extra fields" after removing them from Settings, causing pydantic ValidationError on startup
- **Fix:** Cleaned `.env` to remove the two deleted LLM variables
- **Files modified:** backend/.env
- **Verification:** `get_settings()` call succeeds without ValidationError
- **Committed in:** f0fc05d (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Necessary correctness fix, no scope creep.

## Issues Encountered

None beyond the .env auto-fix above.

## User Setup Required

None — no external service configuration required. Alembic migration `a7b46367f8f0` should be run against the database when deploying to drop the old conversation tables.

## Next Phase Readiness

- Backend is clean and starts without errors
- Phase timeline API ready for frontend consumption with cli_command field
- Context-files endpoint ready for frontend phase detail panels
- Ready for Phase 10 Plan 02: Frontend rework of phase timeline component

## Self-Check: PASSED

- FOUND: backend/app/config_phases.py
- FOUND: backend/alembic/versions/a7b46367f8f0_drop_conversation_tables.py
- FOUND: .planning/phases/10-discussion-workflow-chat-interface/10-01-SUMMARY.md
- VERIFIED: backend/app/api/discussions.py deleted
- VERIFIED: backend/app/llm/ deleted
- VERIFIED: backend/app/prompts/ deleted
- FOUND: commit f0fc05d (Task 1)
- FOUND: commit 96adffd (Task 2)

---
*Phase: 10-discussion-workflow-chat-interface*
*Completed: 2026-03-20*
