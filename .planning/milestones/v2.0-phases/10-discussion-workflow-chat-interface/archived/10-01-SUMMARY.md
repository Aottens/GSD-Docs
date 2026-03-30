---
phase: 10-discussion-workflow-chat-interface
plan: 01
subsystem: discussion-workflow-data-layer
tags: [database, models, schemas, migration, sse]
dependencies:
  requires:
    - "08-01: Database infrastructure (SQLite + SQLAlchemy)"
    - "08-01: Pydantic schemas pattern"
  provides:
    - "Conversation/Message SQLAlchemy models with migration applied"
    - "PhaseInfo Pydantic model for phase status"
    - "Conversation and phase timeline Pydantic schemas"
    - "sse-starlette for Server-Sent Events streaming"
    - "V1_DOCS_PATH config setting"
  affects:
    - "10-02: Discussion API routes (depends on models/schemas)"
    - "10-03: Phase timeline service (depends on PhaseInfo model)"
    - "10-04: Chat interface frontend (depends on schemas)"
tech_stack:
  added:
    - sse-starlette>=2.2.0
  patterns:
    - SQLAlchemy models with JSON columns for structured data
    - Self-referential relationships (parent_id for revision chains)
    - Pydantic models for non-DB data (PhaseInfo derived from filesystem)
    - SSE event type enums for streaming API
key_files:
  created:
    - backend/app/models/conversation.py
    - backend/app/models/phase.py
    - backend/app/schemas/conversation.py
    - backend/app/schemas/phase.py
    - backend/alembic/versions/fb17f556ba07_add_conversations_and_messages_tables.py
  modified:
    - backend/app/models/__init__.py
    - backend/app/schemas/__init__.py
    - backend/app/config.py
    - backend/requirements.txt
decisions:
  - JSON columns for summary_data and metadata_json (flexible structure)
  - Self-referential parent_id for revision chains (continuing discussions)
  - PhaseInfo as Pydantic model not SQLAlchemy (derived from filesystem, not stored)
  - StreamEventType enum for SSE events (type safety for streaming API)
  - V1_DOCS_PATH points to gsd-docs-industrial (source of domain knowledge)
metrics:
  duration_seconds: 178
  tasks_completed: 2
  files_created: 5
  files_modified: 4
  commits: 2
  completed_at: "2026-02-15T20:36:08Z"
---

# Phase 10 Plan 01: Database Foundation Summary

**One-liner:** Conversation/Message SQLAlchemy models with JSON columns, PhaseInfo Pydantic model, SSE schemas, and sse-starlette for streaming discussions.

## What Was Built

Created the complete data layer for the discussion workflow:

1. **Database Models:**
   - `Conversation` model with project/phase tracking, status, summary_data (JSON), and parent_id for revision chains
   - `Message` model with role/content/type, metadata_json (JSON), and conversation relationship
   - Proper indexes on (project_id, phase_number) and (conversation_id, timestamp)
   - Cascade delete-orphan for messages when conversation deleted

2. **Phase Status Model:**
   - `PhaseInfo` Pydantic model for phase timeline (NOT a database model)
   - Derived from filesystem artifacts (CONTEXT.md, PLAN.md, etc.)
   - Tracks status, sub_status, available_actions, has_* flags, conversation_id

3. **Pydantic Schemas:**
   - Conversation CRUD: ConversationCreate, ConversationResponse, ConversationListResponse
   - Message CRUD: MessageCreate, MessageResponse, SendMessageRequest
   - SSE: StreamEvent, StreamEventType enum (message_delta, question_card, summary_card, etc.)
   - Phase timeline: PhaseStatusResponse, PhaseTimelineResponse

4. **Configuration & Dependencies:**
   - V1_DOCS_PATH config setting pointing to gsd-docs-industrial
   - sse-starlette>=2.2.0 installed for Server-Sent Events streaming

5. **Database Migration:**
   - Alembic migration fb17f556ba07 creates conversations and messages tables
   - Applied migration to database

## Task Breakdown

| Task | Name                                                                 | Commit  | Files                                                                                                    |
| ---- | -------------------------------------------------------------------- | ------- | -------------------------------------------------------------------------------------------------------- |
| 1    | Conversation/Message models, PhaseInfo model, and database migration | 7732c6c | conversation.py, phase.py, models/__init__.py, fb17f556ba07_add_conversations_and_messages_tables.py     |
| 2    | Pydantic schemas, config update, and dependency installation         | c3c261d | conversation.py (schemas), phase.py (schemas), schemas/__init__.py, config.py, requirements.txt          |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking Issue] Alembic database not stamped**
- **Found during:** Task 1, creating migration
- **Issue:** Database had tables from Phase 8/9 but Alembic version table was empty, causing "table already exists" errors
- **Fix:** Ran `alembic stamp head` to mark database at current migration head (73e05ffb68dc)
- **Files modified:** None (database state only)
- **Commit:** Included in Task 1 commit (7732c6c)

This was a critical blocking issue preventing migration creation. The fix was simple and non-destructive.

## Technical Decisions

**JSON columns vs. relational tables:**
- Used JSON for `summary_data` (accumulated decisions) and `metadata_json` (flexible message data)
- Rationale: Flexible schema for evolving discussion structures, no rigid table design needed
- Trade-off: Less queryable, but enables rapid iteration on discussion features

**PhaseInfo as Pydantic model:**
- NOT a SQLAlchemy model - derived from filesystem artifacts at runtime
- Rationale: Phase status is already stored in CONTEXT.md, PLAN.md, etc. - don't duplicate
- Pattern: Read .planning directory structure, detect artifacts, build PhaseInfo dynamically

**Self-referential parent_id:**
- Enables revision chains: new conversation can reference parent for context
- Use case: "Continue discussing Phase 3" creates new conversation linked to original
- Alternative considered: Separate ConversationRevision table (rejected - adds complexity)

**StreamEventType enum:**
- Type-safe SSE event types for streaming API
- Prevents typos in event strings, enables exhaustive switch/case
- Maps to Server-Sent Events specification

## Verification Results

All success criteria met:

- ✓ Conversation and Message tables exist in SQLite with proper indexes and foreign keys
- ✓ PhaseInfo Pydantic model provides typed structure for phase status
- ✓ All schemas validate for conversation CRUD, message streaming, and phase timeline
- ✓ sse-starlette installed and importable
- ✓ V1_DOCS_PATH configured in Settings
- ✓ All imports pass

Import verification:
```python
from app.models.conversation import Conversation, Message
from app.models.phase import PhaseInfo
from app.schemas.conversation import ConversationCreate, MessageResponse, SendMessageRequest
from app.schemas.phase import PhaseStatusResponse, PhaseTimelineResponse
from app.config import Settings
import sse_starlette
```

All imports successful.

## Self-Check: PASSED

**Created files verified:**
- ✓ backend/app/models/conversation.py exists
- ✓ backend/app/models/phase.py exists
- ✓ backend/app/schemas/conversation.py exists
- ✓ backend/app/schemas/phase.py exists
- ✓ backend/alembic/versions/fb17f556ba07_add_conversations_and_messages_tables.py exists

**Commits verified:**
- ✓ 7732c6c: feat(10-01): add Conversation/Message models, PhaseInfo model, and database migration
- ✓ c3c261d: feat(10-01): add Pydantic schemas, V1_DOCS_PATH config, and sse-starlette

**Database verified:**
- ✓ Alembic migration fb17f556ba07 applied
- ✓ Migration at head revision

All checks passed.
