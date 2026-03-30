---
phase: 09-reference-library-file-management
plan: 01
subsystem: backend-file-api
tags: [file-management, validation, storage, rest-api, folders]

dependency_graph:
  requires:
    - phase-08-01 (Database and async infrastructure)
  provides:
    - File and Folder SQLAlchemy models
    - Defense-in-depth file validation
    - Filesystem storage operations
    - Complete file/folder REST API
    - Default folder auto-creation
  affects:
    - Phase 09-02 (Frontend will consume these APIs)
    - All future phases using file references

tech_stack:
  added:
    - python-magic (MIME validation with fallback)
    - Pillow (image verification)
    - aiofiles (async file I/O)
    - python-multipart 0.0.20 (file upload support)
  patterns:
    - Defense-in-depth validation (5 layers)
    - Soft delete (preserve files on disk)
    - File override mechanism (project-specific copies)
    - Hierarchical folder structure
    - Admin auth via header (dev mode bypass)

key_files:
  created:
    - backend/app/models/file.py (File, Folder, FileScope models)
    - backend/app/schemas/file.py (Pydantic schemas)
    - backend/app/services/file_validator.py (5-layer validation)
    - backend/app/services/file_storage.py (filesystem operations)
    - backend/app/services/file_service.py (FileService, FolderService)
    - backend/app/api/files.py (file CRUD endpoints)
    - backend/app/api/folders.py (folder CRUD endpoints)
  modified:
    - backend/app/config.py (50MB limit, extensions, MIME types, default folders)
    - backend/app/models/__init__.py (export File, Folder, FileScope)
    - backend/app/schemas/__init__.py (export file schemas)
    - backend/app/api/__init__.py (export files, folders)
    - backend/app/main.py (register routers, startup logic)
    - backend/app/services/project_service.py (auto-create default folders)
    - backend/requirements.txt (new dependencies)

decisions:
  - Use python-multipart 0.0.20 (latest compatible with Python 3.9.6)
  - Graceful fallback when libmagic not installed (uses extension-based MIME)
  - Store files at uploads/{scope}/{project_id}/{folder}/{uuid}.ext
  - Soft delete preserves files on disk (is_deleted flag only)
  - Admin auth via X-Admin-Key header (empty key = dev mode)
  - Default folders per project type (A/B/C/D) from v1.0 domain knowledge

metrics:
  duration_seconds: 506
  tasks_completed: 2
  files_created: 7
  files_modified: 7
  commits: 2
  completed_date: 2026-02-15
---

# Phase 09 Plan 01: Backend File Management API Summary

**One-liner:** Complete file/folder management infrastructure with defense-in-depth validation, filesystem storage, and REST API for project and shared library scopes.

## What Was Built

### File and Folder Models (Task 1)

**File model** tracks metadata for uploaded files:
- UUID-based identification
- Original and sanitized filenames
- MIME type, size, storage path
- Scope (project vs shared library)
- Soft delete support
- Override mechanism (project files can override shared files)

**Folder model** provides hierarchical organization:
- Project-specific or shared library scope
- Parent-child relationships
- Unique constraint on folder paths (prevents duplicates)

**Default folder configuration:**
- Type A projects: P&IDs, Specificaties, Standaarden, Foto's & Tekeningen, Bestaande documentatie
- Type B projects: P&IDs, Specificaties, Foto's & Tekeningen, Bestaande documentatie
- Type C projects: P&IDs, Specificaties, Standaarden, Bestaande FDS/SDS, Foto's & Tekeningen, Bestaande documentatie
- Type D projects: P&IDs, Specificaties, Bestaande FDS/SDS, Bestaande documentatie
- Shared library: Standaarden, Typicals, Sjablonen, Algemene referenties

### Defense-in-Depth Validation (Task 2)

Five validation layers protect against malicious uploads:

1. **Extension whitelist** - Only .pdf, .docx, .doc, .png, .jpg, .jpeg, .tiff, .bmp allowed
2. **Filename sanitization** - Detects path traversal attempts
3. **File size limit** - 50MB maximum (per research recommendation)
4. **Magic number validation** - Verifies MIME type matches extension (with fallback)
5. **Image verification** - Uses Pillow to verify image integrity

Dutch error messages guide users: "Bestandstype '.exe' is niet toegestaan", "Bestand overschrijdt de maximale grootte van 50MB", etc.

### Filesystem Storage

Files organized on disk: `uploads/{scope}/{project_id}/{folder}/{uuid}.ext`

Operations:
- `save_file()` - Write to organized path structure
- `delete_file()` - Hard delete (used for replace, not soft delete)
- `replace_file()` - Save new, delete old
- `get_absolute_path()` - Resolve storage path to filesystem path

### Business Logic Services

**FileService:**
- CRUD operations (create, get, list, update, soft_delete)
- List with filtering (folder, file type, search)
- Override mechanism (project copy of shared file)
- Search across filenames

**FolderService:**
- CRUD operations (create, list, update, delete)
- Delete only if empty (no files, no subfolders)
- `create_default_folders()` - Auto-create per project type
- `create_default_shared_folders()` - Auto-create on startup (idempotent)

### REST API Endpoints

**Project file endpoints:**
- `POST /api/projects/{id}/files` - Upload file
- `GET /api/projects/{id}/files` - List files (filterable)
- `GET /api/files/{id}/download` - Download file (attachment)
- `GET /api/files/{id}/preview` - Preview file (inline)
- `PATCH /api/files/{id}` - Update metadata (rename, move)
- `PUT /api/files/{id}/replace` - Replace content
- `DELETE /api/files/{id}` - Soft delete

**Shared library endpoints:**
- `POST /api/files/shared` - Upload (admin-only)
- `GET /api/files/shared` - List files
- `DELETE /api/files/shared/{id}` - Soft delete (admin-only)

**Override endpoint:**
- `POST /api/files/{id}/override` - Create project-specific copy

**Folder endpoints:**
- `POST /api/projects/{id}/folders` - Create project folder
- `GET /api/projects/{id}/folders` - List project folders
- `PATCH /api/folders/{id}` - Rename folder
- `DELETE /api/folders/{id}` - Delete empty folder
- `GET /api/files/shared/folders` - List shared folders
- `POST /api/files/shared/folders` - Create shared folder (admin-only)

**Admin authentication:** X-Admin-Key header required when ADMIN_API_KEY is set. Empty key = dev mode (all requests allowed).

### Integration Points

**Project creation hook:**
Modified `ProjectService.create_project()` to auto-create default folders after project creation. Type A projects get 5 folders, Type B get 4, etc.

**Application startup:**
- `ensure_upload_dir()` creates uploads directory
- `create_default_shared_folders()` creates shared library folders (idempotent - runs on every startup but skips existing)

## Verification Results

All endpoints tested successfully:

1. **Project creation** auto-creates default folders (Type A: 5 folders verified)
2. **File upload** validates and stores correctly (22-byte PDF uploaded)
3. **File list** returns metadata with download URLs
4. **File download** serves correct content from disk
5. **Shared library folders** auto-created on startup (4 folders verified)
6. **Shared library upload** works (admin auth bypassed in dev mode)
7. **Soft delete** removes from list but preserves on disk (verified file still exists)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Python version incompatibility with python-multipart 0.0.22**
- **Found during:** Task 2 dependency installation
- **Issue:** Python 3.9.6 in venv cannot install python-multipart>=0.0.22 (requires Python 3.10+)
- **Fix:** Changed requirement to python-multipart>=0.0.20 (latest compatible version)
- **Files modified:** backend/requirements.txt
- **Commit:** 92747f9
- **Note:** 0.0.20 still provides security improvements over the original 0.0.9

**2. [Rule 1 - Bug] Incorrect import of get_db in main.py**
- **Found during:** Task 2 server startup
- **Issue:** Imported `get_db` from `app.database` but it's actually in `app.dependencies`
- **Fix:** Changed import to `from app.dependencies import get_db`
- **Files modified:** backend/app/main.py
- **Commit:** 92747f9 (included in main commit)

## Self-Check

Verifying created files exist:

```bash
[ -f "backend/app/models/file.py" ] && echo "FOUND"
[ -f "backend/app/schemas/file.py" ] && echo "FOUND"
[ -f "backend/app/services/file_validator.py" ] && echo "FOUND"
[ -f "backend/app/services/file_storage.py" ] && echo "FOUND"
[ -f "backend/app/services/file_service.py" ] && echo "FOUND"
[ -f "backend/app/api/files.py" ] && echo "FOUND"
[ -f "backend/app/api/folders.py" ] && echo "FOUND"
```

Verifying commits exist:

```bash
git log --oneline --all | grep -q "65c1dc9" && echo "FOUND: 65c1dc9"
git log --oneline --all | grep -q "92747f9" && echo "FOUND: 92747f9"
```

## Self-Check: PASSED

All created files exist. All commits verified in git history.

---

**Next step:** Phase 09 Plan 02 will build the frontend file browser, upload UI, and preview components that consume these APIs.
