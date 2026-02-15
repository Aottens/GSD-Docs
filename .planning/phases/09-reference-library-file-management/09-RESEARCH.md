# Phase 9: Reference Library & File Management - Research

**Researched:** 2026-02-15
**Domain:** File upload, validation, storage, and preview in FastAPI + React
**Confidence:** HIGH

## Summary

Phase 9 implements secure file upload, management, and preview for PDF, DOCX, and images in a two-tier system (shared library + per-project files). The research confirms that defense-in-depth security validation is critical and well-established, with multiple Python libraries for magic number validation beyond MIME types. React has mature drag-and-drop libraries with progress tracking, and document preview requires separate libraries per file type (react-pdf for PDFs, docx-preview for DOCX). File storage should use filesystem paths (not BLOBs) with metadata in SQLite, and FastAPI's UploadFile handles chunked streaming natively. The existing Sheet component (Radix Dialog) can be reused for file detail panels.

**Primary recommendation:** Use python-magic for content-based validation, react-dropzone for uploads, react-pdf + docx-preview for previews, and FastAPI UploadFile with filesystem storage. Implement OWASP defense-in-depth: validate magic numbers, sanitize filenames, set size limits, and store outside webroot.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Upload experience:**
- Uploads available in three locations: project creation wizard (as a step), workspace tab, and sidebar section
- Large drag-and-drop zone with a "browse files" button fallback — both options always visible
- Per-file progress bars showing status (uploading, validating, done)
- Accepted file types and max file size displayed upfront in the upload zone

**Library layout & browsing:**
- File list with metadata (table-like): filename, type icon, size, upload date — compact, scannable
- User-created folder structure for organization
- Predefined default folders based on project type (e.g., P&IDs, Specificaties, Standaarden) — user can add more
- Search bar with file type filter dropdown (PDF, DOCX, image) to find files across folders

**Shared vs project boundary:**
- Separate tabs: "Project bestanden" and "Gedeelde bibliotheek" — clearly separated views
- Explicit override action: user selects a shared file and clicks "Override" to upload a project-specific version
- Dedicated admin page for managing shared library files — only visible to admins

**File actions & preview:**
- Clicking a file opens a slide-in detail panel (reuse Sheet pattern from assistant) with preview, metadata, and actions
- Full inline preview for all types: PDF, images, AND rendered DOCX
- File management actions: delete, replace with new version, download, rename, move between folders
- Deletion requires confirmation dialog before proceeding

### Claude's Discretion
- Admin authentication mechanism for shared library (considering 5-20 user scale)
- Default folder names per project type (A/B/C/D)
- File size limits and exact supported file types beyond PDF/DOCX/images
- Upload validation error message design
- Detail panel layout and metadata fields shown

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope

</user_constraints>

## Standard Stack

### Core Backend (File Upload & Validation)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| python-multipart | >=0.0.22 | Multipart form data parsing | Required by FastAPI for file uploads; recent CVE-2026-24486 fixed in 0.0.22+ |
| python-magic | latest | Magic number validation | Industry standard for content-based file type detection; interfaces with libmagic |
| FastAPI UploadFile | built-in | File upload handling | Native FastAPI support for chunked streaming and metadata |
| Pillow | latest | Image validation/processing | De facto Python image library for format verification |

### Core Frontend (Upload & Preview)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| react-dropzone | latest | Drag-and-drop file upload | Most popular React file upload library (well-maintained, accessible) |
| react-pdf | ^10.3.0 | PDF preview/rendering | 1000+ npm dependents, powered by PDF.js (Mozilla) |
| docx-preview | latest | DOCX inline preview | Better rich text support than mammoth.js for rendering Word docs |
| lucide-react | ^0.564.0 | File type icons | Already in stack; provides FileText, File, Image icons |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| filetype | latest | Lightweight magic number check | Alternative to python-magic if libmagic unavailable |
| puremagic | latest | Pure Python magic number validation | Fallback if python-magic installation issues |
| @tanstack/react-query | ^5.90.21 | Upload state management | Already in stack; handles upload mutations with retry |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| python-magic | filetype | Filetype is dependency-free but less comprehensive; use if libmagic install is problematic |
| react-dropzone | react-drag-drop-files | Lighter but less feature-complete; react-dropzone has better accessibility |
| react-pdf | @pdf-viewer/react | Faster WebAssembly engine but less ecosystem support |
| docx-preview | mammoth.js | Mammoth converts to HTML but docx-preview has better formatting fidelity |

**Installation:**

Backend:
```bash
pip install python-magic python-multipart>=0.0.22 Pillow
# Note: python-magic requires libmagic system library
# macOS: brew install libmagic
# Ubuntu/Debian: apt-get install libmagic1
```

Frontend:
```bash
npm install react-dropzone react-pdf docx-preview
```

## Architecture Patterns

### Recommended Project Structure

Backend:
```
backend/
├── app/
│   ├── models/
│   │   └── file.py           # File metadata model (SQLite)
│   ├── schemas/
│   │   └── file.py           # Pydantic schemas for file operations
│   ├── api/
│   │   ├── files.py          # File upload/download endpoints
│   │   └── folders.py        # Folder management endpoints
│   ├── services/
│   │   ├── file_validator.py # Defense-in-depth validation
│   │   └── file_storage.py   # Filesystem operations
│   └── config.py             # Upload settings (size limits, allowed types)
├── uploads/                  # File storage (outside webroot in production)
│   ├── shared/               # Admin-managed shared library
│   └── projects/             # Per-project files
│       └── {project_id}/
│           └── {folder_path}/
```

Frontend:
```
frontend/src/features/files/
├── components/
│   ├── FileUploadZone.tsx    # Drag-and-drop upload area
│   ├── FileList.tsx          # Table-like file browser
│   ├── FilePreviewPanel.tsx  # Sheet with preview + actions
│   ├── FolderTree.tsx        # Folder navigation
│   └── FileTypeIcon.tsx      # Icon mapping (PDF/DOCX/image)
├── hooks/
│   ├── useFileUpload.ts      # React Query mutation with progress
│   └── useFilePreview.ts     # Preview rendering logic
└── types/
    └── file.ts               # TypeScript types
```

### Pattern 1: Defense-in-Depth File Validation

**What:** Multi-layer validation pipeline that checks file uploads through multiple independent security checks.

**When to use:** Every file upload endpoint must use this pattern (shared library, project files, wizard uploads).

**Example:**
```python
# Source: OWASP File Upload Cheat Sheet + CVE-2026-24486 mitigation
# https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html

import magic
import os
from pathlib import Path
from PIL import Image
from fastapi import UploadFile, HTTPException

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'image/png',
    'image/jpeg'
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

async def validate_file_upload(file: UploadFile) -> dict:
    """Defense-in-depth file validation.

    Layers:
    1. Extension whitelist
    2. Filename sanitization (path traversal protection)
    3. File size limit
    4. Magic number validation (content-based)
    5. Format-specific validation (images)
    """
    # Layer 1: Extension validation
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type '{ext}' not allowed")

    # Layer 2: Filename sanitization (CVE-2026-24486 mitigation)
    # Strip directory traversal sequences
    safe_filename = os.path.basename(filename)
    if safe_filename != filename:
        raise HTTPException(400, "Invalid filename (path traversal detected)")

    # Layer 3: Size limit
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, f"File exceeds {MAX_FILE_SIZE/1024/1024}MB limit")

    # Layer 4: Magic number validation (don't trust extension/MIME)
    mime = magic.from_buffer(content, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"File content type '{mime}' does not match extension")

    # Layer 5: Format-specific validation (images only)
    if mime.startswith('image/'):
        try:
            img = Image.open(io.BytesIO(content))
            img.verify()  # Detect corrupted/malicious images
        except Exception:
            raise HTTPException(400, "Invalid or corrupted image file")

    # Reset file pointer for storage
    await file.seek(0)

    return {
        'safe_filename': safe_filename,
        'mime_type': mime,
        'size': len(content)
    }
```

### Pattern 2: Filesystem Storage with Metadata in SQLite

**What:** Store actual files on filesystem, metadata in database. Avoid storing BLOBs in SQLite for files >100KB.

**When to use:** All file storage (shared library, project files).

**Example:**
```python
# Source: SQLite official docs - Internal vs External BLOBs
# https://sqlite.org/intern-v-extern-blob.html

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from datetime import datetime
from pathlib import Path
import uuid

class FileScope(str, enum.Enum):
    SHARED = "shared"
    PROJECT = "project"

class File(Base):
    """File metadata model.

    Storage strategy:
    - Files stored on filesystem at: uploads/{scope}/{project_id}/{folder}/{uuid}
    - Metadata (path, size, type) stored in SQLite
    - Benefits: Faster for files >100KB, easier backup, direct serving
    """
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    original_filename = Column(String(255), nullable=False)
    safe_filename = Column(String(255), nullable=False)  # Sanitized
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)

    scope = Column(Enum(FileScope), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)  # NULL for shared
    folder_path = Column(String(500), nullable=False, default="/")  # User-created folders

    # Filesystem storage path (relative to UPLOAD_DIR)
    storage_path = Column(String(1000), nullable=False)

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100), nullable=True)  # Future: user ID

    def get_absolute_path(self, upload_dir: str) -> Path:
        """Get absolute filesystem path."""
        return Path(upload_dir) / self.storage_path

def generate_storage_path(scope: FileScope, project_id: int | None,
                         folder_path: str, file_uuid: str, ext: str) -> str:
    """Generate organized storage path.

    Examples:
    - Shared: shared/Standards/a1b2c3d4-uuid.pdf
    - Project: projects/42/P&IDs/e5f6g7h8-uuid.png
    """
    if scope == FileScope.SHARED:
        return f"shared{folder_path}/{file_uuid}{ext}"
    else:
        return f"projects/{project_id}{folder_path}/{file_uuid}{ext}"
```

### Pattern 3: Chunked Upload with Progress Tracking

**What:** React Query mutation with progress callbacks for per-file upload state.

**When to use:** All upload zones (wizard, workspace, sidebar).

**Example:**
```typescript
// Source: React Query + FastAPI streaming upload patterns
// https://medium.com/@vishalsinghrajawat990/the-definitive-guide-to-uploading-files-in-react-ux-compression-api-best-practices-fa388fd7165c

import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'

interface UploadProgress {
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'validating' | 'done' | 'error'
  error?: string
}

export function useFileUpload(projectId?: number) {
  const [progressMap, setProgressMap] = useState<Map<string, UploadProgress>>(new Map())

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)

      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()

        // Progress tracking
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100
            setProgressMap(prev => new Map(prev).set(file.name, {
              file,
              progress: percentComplete,
              status: 'uploading'
            }))
          }
        })

        xhr.addEventListener('load', () => {
          if (xhr.status === 200) {
            setProgressMap(prev => new Map(prev).set(file.name, {
              file,
              progress: 100,
              status: 'done'
            }))
            resolve(JSON.parse(xhr.responseText))
          } else {
            const error = JSON.parse(xhr.responseText).detail || 'Upload failed'
            setProgressMap(prev => new Map(prev).set(file.name, {
              file,
              progress: 0,
              status: 'error',
              error
            }))
            reject(new Error(error))
          }
        })

        xhr.addEventListener('error', () => {
          setProgressMap(prev => new Map(prev).set(file.name, {
            file,
            progress: 0,
            status: 'error',
            error: 'Network error'
          }))
          reject(new Error('Network error'))
        })

        const endpoint = projectId
          ? `/api/projects/${projectId}/files`
          : '/api/files/shared'

        xhr.open('POST', endpoint)
        xhr.send(formData)
      })
    },
    retry: 2, // Retry failed uploads twice
    retryDelay: 1000 // Wait 1s between retries
  })

  const uploadFiles = async (files: File[]) => {
    // Initialize progress for all files
    files.forEach(file => {
      setProgressMap(prev => new Map(prev).set(file.name, {
        file,
        progress: 0,
        status: 'pending'
      }))
    })

    // Upload sequentially (avoid overwhelming server)
    for (const file of files) {
      try {
        await uploadMutation.mutateAsync(file)
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error)
      }
    }
  }

  return {
    uploadFiles,
    progressMap,
    isUploading: uploadMutation.isPending
  }
}
```

### Pattern 4: File Preview with Type-Specific Renderers

**What:** Sheet component with dynamic preview renderer based on MIME type.

**When to use:** File detail panel (clicking any file in the list).

**Example:**
```typescript
// Source: react-pdf + docx-preview official examples
// https://github.com/wojtekmaj/react-pdf
// https://www.npmjs.com/package/docx-preview

import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Document, Page } from 'react-pdf'
import { renderAsync } from 'docx-preview'
import { useEffect, useRef } from 'react'

interface FilePreviewPanelProps {
  file: FileMetadata | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function FilePreviewPanel({ file, open, onOpenChange }: FilePreviewPanelProps) {
  const docxContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (file?.mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        && docxContainerRef.current) {
      // Render DOCX in container
      fetch(`/api/files/${file.id}/download`)
        .then(res => res.blob())
        .then(blob => renderAsync(blob, docxContainerRef.current!))
    }
  }, [file])

  const renderPreview = () => {
    if (!file) return null

    const { mimeType, downloadUrl } = file

    // Image preview
    if (mimeType.startsWith('image/')) {
      return (
        <img
          src={downloadUrl}
          alt={file.filename}
          className="max-w-full h-auto"
        />
      )
    }

    // PDF preview
    if (mimeType === 'application/pdf') {
      return (
        <Document file={downloadUrl}>
          <Page pageNumber={1} />
        </Document>
      )
    }

    // DOCX preview
    if (mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      return <div ref={docxContainerRef} className="docx-preview" />
    }

    return <p>Preview not available for this file type</p>
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-3/4 sm:max-w-2xl overflow-y-auto">
        <SheetHeader>
          <SheetTitle>{file?.filename}</SheetTitle>
        </SheetHeader>

        <div className="mt-4 space-y-4">
          {/* Preview */}
          <div className="border rounded-lg p-4 bg-gray-50">
            {renderPreview()}
          </div>

          {/* Metadata */}
          <div className="space-y-2 text-sm">
            <div><strong>Type:</strong> {file?.mimeType}</div>
            <div><strong>Size:</strong> {formatBytes(file?.sizeBytes)}</div>
            <div><strong>Uploaded:</strong> {formatDate(file?.uploadedAt)}</div>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <Button onClick={() => downloadFile(file)}>Download</Button>
            <Button variant="outline" onClick={() => renameFile(file)}>Rename</Button>
            <Button variant="destructive" onClick={() => deleteFile(file)}>Delete</Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
```

### Anti-Patterns to Avoid

- **Trusting client-provided MIME types:** Always validate with magic numbers (python-magic). MIME headers are trivially spoofed.
- **Storing large files as BLOBs in SQLite:** Use filesystem storage for files >100KB. SQLite performance degrades, backups become slow.
- **Using original filenames for storage:** Generate UUIDs to prevent path traversal and filename collisions.
- **Uploading files without progress feedback:** Users need per-file progress bars, especially for large files or slow networks.
- **Missing validation error messages:** Generic "Upload failed" is frustrating. Show specific errors: "File type not allowed", "File too large (max 50MB)".

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| File type detection | Custom extension parser | python-magic | Magic numbers catch spoofed extensions; libmagic database covers 1000+ formats |
| Drag-and-drop upload | Custom HTML5 drag events | react-dropzone | Handles edge cases: multiple files, keyboard accessibility, file rejection, mobile support |
| PDF rendering | Canvas-based PDF parser | react-pdf (PDF.js) | Mozilla's PDF.js is battle-tested, handles complex PDFs, supports annotations |
| DOCX rendering | XML parser + HTML converter | docx-preview | DOCX spec is 5000+ pages; library handles styles, tables, images, headers/footers |
| Path traversal defense | Regex filename cleaning | os.path.basename() | Catches ../, ..\, and Unicode bypass techniques; OS-aware |
| Upload progress tracking | setTimeout polling | XMLHttpRequest.upload.onprogress | Native browser support, accurate byte-level progress, no polling overhead |

**Key insight:** File security is a minefield of edge cases (polyglot files, zip bombs, Unicode bypass, TOCTOU races). Use libraries maintained by security experts. Custom validation code almost always has gaps.

## Common Pitfalls

### Pitfall 1: CVE-2026-24486 - Path Traversal in python-multipart

**What goes wrong:** Uploading files with filenames like `../../../etc/passwd` writes to arbitrary filesystem locations when using `UPLOAD_KEEP_FILENAME=True`.

**Why it happens:** python-multipart <0.0.22 didn't sanitize directory traversal sequences in uploaded filenames.

**How to avoid:**
1. Require python-multipart >= 0.0.22
2. Always use `os.path.basename(filename)` before storage
3. Generate UUID-based filenames instead of keeping original names
4. Store uploads outside webroot

**Warning signs:** Files appearing in unexpected directories, security scanner alerts.

**Source:** [CVE-2026-24486](https://www.sentinelone.com/vulnerability-database/cve-2026-24486/)

### Pitfall 2: Trusting Extension Over Content

**What goes wrong:** Malicious file `virus.exe` renamed to `virus.pdf` bypasses extension whitelist, gets served to users who expect a safe PDF.

**Why it happens:** Validating only file extension or MIME header (both client-controlled).

**How to avoid:**
1. Use python-magic to validate magic numbers (file content)
2. Reject files where magic number doesn't match extension
3. For images, use Pillow.verify() to catch corrupted/malicious files
4. Consider additional scanning (antivirus, CDR) for high-security needs

**Warning signs:** Files that don't open correctly, security alerts from antivirus.

**Source:** [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)

### Pitfall 3: Large Upload Memory Exhaustion

**What goes wrong:** Uploading 1GB file crashes server because entire file is loaded into memory.

**Why it happens:** Using `file.read()` instead of streaming, or not setting size limits.

**How to avoid:**
1. Use FastAPI's `UploadFile` (streams to temp file automatically)
2. Set `MAX_FILE_SIZE` limit and validate early
3. Stream large files directly to disk in chunks
4. For very large files (>100MB), consider chunked upload with resumable transfers

**Warning signs:** Server OOM errors, slow uploads, high memory usage.

**Source:** [FastAPI File Upload Guide](https://oneuptime.com/blog/post/2026-02-02-fastapi-file-uploads/view)

### Pitfall 4: Missing Upload Validation Feedback

**What goes wrong:** User uploads 10 files, sees generic error "Upload failed", has no idea which files failed or why.

**Why it happens:** Batch upload error handling without per-file status tracking.

**How to avoid:**
1. Track per-file progress state: pending → uploading → validating → done/error
2. Show specific validation errors: "file.docx: File too large (60MB, max 50MB)"
3. Allow retry for individual failed files
4. Display validation rules upfront: "Accepted: PDF, DOCX, PNG, JPG (max 50MB)"

**Warning signs:** User confusion, repeated upload attempts, support tickets about "broken uploads".

**Source:** [React File Upload UX Guide](https://medium.com/@vishalsinghrajawat990/the-definitive-guide-to-uploading-files-in-react-ux-compression-api-best-practices-fa388fd7165c)

### Pitfall 5: Zip Bomb / Decompression Attacks

**What goes wrong:** User uploads 42KB zip file that expands to 4.5 petabytes, exhausting disk space.

**Why it happens:** Extracting archive files without size validation.

**Note:** Phase 9 doesn't extract archives (stores files as-is), but if future phases add extraction:
1. Validate uncompressed size before extraction
2. Set maximum extraction ratio (e.g., 100:1)
3. Use streaming extraction with size limits
4. Scan for nested archives (zip within zip)

**Source:** [Zip Bomb Vulnerabilities](https://hackviser.com/tactics/pentesting/web/file-upload)

### Pitfall 6: DOCX Preview Breaking on Complex Documents

**What goes wrong:** DOCX with complex tables, custom styles, or embedded objects fails to render or shows garbled output.

**Why it happens:** docx-preview supports most but not all DOCX features (macros, advanced formatting).

**How to avoid:**
1. Document limitation: "Preview may not show all formatting"
2. Always provide download option as fallback
3. Test with representative sample files from target domain
4. Consider showing raw text extraction if preview fails

**Warning signs:** Blank preview panels, layout issues, missing content.

**Source:** [docx-preview Limitations](https://codingbeast.org/upload-file-and-preview-docx-preview-in-react/)

## Code Examples

### Example 1: FastAPI File Upload Endpoint with Validation

```python
# Source: FastAPI official docs + OWASP best practices
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.file_validator import validate_file_upload
from app.services.file_storage import save_file
from app.models.file import File as FileModel, FileScope
from app.database import get_db

router = APIRouter(prefix="/api/files", tags=["files"])

@router.post("/shared")
async def upload_shared_file(
    file: UploadFile = File(...),
    folder_path: str = "/",
    db: AsyncSession = Depends(get_db)
):
    """Upload file to shared library (admin only - add auth dependency)."""

    # Defense-in-depth validation
    validation_result = await validate_file_upload(file)

    # Save to filesystem
    storage_path = await save_file(
        file=file,
        scope=FileScope.SHARED,
        project_id=None,
        folder_path=folder_path
    )

    # Store metadata in database
    file_record = FileModel(
        original_filename=file.filename,
        safe_filename=validation_result['safe_filename'],
        mime_type=validation_result['mime_type'],
        size_bytes=validation_result['size'],
        scope=FileScope.SHARED,
        folder_path=folder_path,
        storage_path=storage_path
    )

    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)

    return {
        "id": file_record.id,
        "filename": file_record.safe_filename,
        "size": file_record.size_bytes,
        "type": file_record.mime_type
    }

@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Download file (serves from filesystem)."""
    file_record = await db.get(FileModel, file_id)
    if not file_record:
        raise HTTPException(404, "File not found")

    file_path = file_record.get_absolute_path(settings.UPLOAD_DIR)
    if not file_path.exists():
        raise HTTPException(404, "File not found on disk")

    return FileResponse(
        path=file_path,
        filename=file_record.original_filename,
        media_type=file_record.mime_type
    )
```

### Example 2: React Drag-and-Drop Upload Zone

```typescript
// Source: react-dropzone official examples
import { useDropzone } from 'react-dropzone'
import { FileText, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'

interface FileUploadZoneProps {
  onFilesSelected: (files: File[]) => void
  acceptedTypes?: string[]
  maxSizeMB?: number
}

export function FileUploadZone({
  onFilesSelected,
  acceptedTypes = ['.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg'],
  maxSizeMB = 50
}: FileUploadZoneProps) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg']
    },
    maxSize: maxSizeMB * 1024 * 1024,
    onDrop: onFilesSelected,
    onDropRejected: (rejections) => {
      rejections.forEach(({ file, errors }) => {
        errors.forEach(error => {
          if (error.code === 'file-too-large') {
            alert(`${file.name} is too large (max ${maxSizeMB}MB)`)
          } else if (error.code === 'file-invalid-type') {
            alert(`${file.name} type not allowed`)
          }
        })
      })
    }
  })

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
        transition-colors
        ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
      `}
    >
      <input {...getInputProps()} />

      <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />

      <p className="text-lg font-medium mb-2">
        {isDragActive ? 'Drop bestanden hier' : 'Sleep bestanden hierheen'}
      </p>

      <Button variant="outline" className="mt-4">
        Of kies bestanden
      </Button>

      <p className="text-sm text-gray-500 mt-4">
        Toegestaan: PDF, DOCX, PNG, JPG (max {maxSizeMB}MB)
      </p>
    </div>
  )
}
```

### Example 3: File List with Type Icons

```typescript
// Source: lucide-react icons + table pattern
import { FileText, File, Image as ImageIcon } from 'lucide-react'
import { formatBytes, formatDate } from '@/lib/utils'

interface FileListProps {
  files: FileMetadata[]
  onFileClick: (file: FileMetadata) => void
}

export function FileList({ files, onFileClick }: FileListProps) {
  const getFileIcon = (mimeType: string) => {
    if (mimeType.startsWith('image/')) {
      return <ImageIcon className="h-5 w-5 text-blue-500" />
    } else if (mimeType === 'application/pdf') {
      return <FileText className="h-5 w-5 text-red-500" />
    } else if (mimeType.includes('word')) {
      return <FileText className="h-5 w-5 text-blue-600" />
    }
    return <File className="h-5 w-5 text-gray-500" />
  }

  return (
    <div className="border rounded-lg">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Bestandsnaam
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Type
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Grootte
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Geüpload
            </th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {files.map(file => (
            <tr
              key={file.id}
              onClick={() => onFileClick(file)}
              className="hover:bg-gray-50 cursor-pointer"
            >
              <td className="px-4 py-3 flex items-center gap-3">
                {getFileIcon(file.mimeType)}
                <span className="font-medium">{file.filename}</span>
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {file.mimeType.split('/')[1].toUpperCase()}
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {formatBytes(file.sizeBytes)}
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {formatDate(file.uploadedAt)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

### Example 4: Confirmation Dialog for File Deletion

```typescript
// Source: shadcn/ui AlertDialog pattern
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

interface DeleteConfirmationProps {
  file: FileMetadata | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void
}

export function DeleteConfirmation({
  file,
  open,
  onOpenChange,
  onConfirm
}: DeleteConfirmationProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Bestand verwijderen?</AlertDialogTitle>
          <AlertDialogDescription>
            Weet je zeker dat je "{file?.filename}" wilt verwijderen?
            Deze actie kan niet ongedaan worden gemaakt.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Annuleren</AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            className="bg-red-600 hover:bg-red-700"
          >
            Verwijderen
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Store BLOBs in database | Store files on filesystem, metadata in DB | Always best practice | Faster performance, easier backup, direct file serving |
| Extension-based validation | Magic number validation | Always critical | Prevents extension spoofing attacks |
| Single-threaded uploads | Chunked/resumable uploads | ~2020+ | Better UX for large files, network resilience |
| mammoth.js for DOCX | docx-preview | ~2021+ | Better formatting fidelity for complex documents |
| Custom drag-drop | react-dropzone | Mature since 2015 | Better accessibility, mobile support, edge case handling |
| Polling for progress | XHR.upload.onprogress | Native since IE10 | Accurate real-time progress without polling overhead |

**Deprecated/outdated:**
- **python-multipart <0.0.22:** CVE-2026-24486 path traversal vulnerability. Update to >=0.0.22 immediately.
- **Storing original filenames:** Security risk (path traversal). Use UUID-based storage names.
- **imghdr module:** Deprecated in Python 3.11+. Use python-magic or Pillow instead.

## Open Questions

1. **Admin authentication mechanism**
   - What we know: 5-20 user scale, simple admin panel needed for shared library management
   - What's unclear: Preference between JWT token, session-based, or simple API key
   - Recommendation: FastAPI Users library with JWT provides full auth system (login, roles, password reset) suitable for small teams. Alternative: Simple role field in user table if users already exist.

2. **Default folder names per project type**
   - What we know: Types A/B/C/D need domain-appropriate folders (e.g., P&IDs, Specificaties, Standaarden)
   - What's unclear: Exact folder structure per type from domain requirements
   - Recommendation: Reference gsd-docs-industrial/references/ for v1.0 folder patterns (Standards, Typicals). Plan should reference specific v1.0 source files for folder taxonomy.

3. **Exact file size limits**
   - What we know: Need reasonable limits for PDF, DOCX, images
   - What's unclear: Target use case file sizes (single-page PDF vs 100-page manual)
   - Recommendation: 50MB default (covers most use cases), make configurable via settings. Phase plan should specify per-type limits if needed.

4. **Image file format support**
   - What we know: PNG, JPG confirmed in decisions
   - What's unclear: Support for TIFF, BMP, WebP (common in industrial documentation)
   - Recommendation: Start with PNG/JPG, add TIFF if industrial drawings require it. WebP optional (modern browser support excellent).

5. **Folder tree UI component**
   - What we know: User-created folder structure, predefined defaults
   - What's unclear: Full tree view vs flat list with breadcrumbs
   - Recommendation: Start with flat list + breadcrumbs (simpler). Add tree view if user feedback demands it. Libraries available: react-folder-tree, SVAR React File Manager.

## Domain Context for Planning

### v1.0 Reference Structure

The planner should reference these v1.0 files for domain-specific folder organization:

```
gsd-docs-industrial/references/
├── standards/           # Shared standards (ISA-88, PackML)
│   ├── isa-88/
│   └── packml/
└── typicals/           # Reusable patterns
```

**Planning guidance:**
- Shared library default folders should map to `references/standards/` taxonomy
- Per-project folders should align with project type (A/B/C/D) deliverable structure
- Planner must reference specific v1.0 source files (path + section) when defining folder taxonomy

### Security Requirements from Domain

Industrial documentation context adds these constraints:
- **Confidentiality:** Project files may contain proprietary process designs
- **Integrity:** Reference standards must not be accidentally modified by engineers
- **Traceability:** Track who uploaded what file and when (audit trail)

**Planning guidance:**
- Shared library must be read-only for engineers (admin-only uploads)
- Project files need upload timestamp and uploader tracking
- File deletion should be soft delete (mark as deleted, don't actually remove)

## Sources

### Primary (HIGH confidence)
- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) - Security best practices
- [CVE-2026-24486: python-multipart Path Traversal](https://www.sentinelone.com/vulnerability-database/cve-2026-24486/) - Recent vulnerability mitigation
- [SQLite Internal vs External BLOBs](https://sqlite.org/intern-v-extern-blob.html) - Official storage guidance
- [FastAPI Request Files Tutorial](https://fastapi.tiangolo.com/tutorial/request-files/) - Official FastAPI docs
- [Radix UI Dialog Component](https://www.radix-ui.com/primitives/docs/components/dialog) - Official Radix docs
- [react-pdf GitHub](https://github.com/wojtekmaj/react-pdf) - Official library docs
- [react-dropzone GitHub](https://github.com/react-dropzone/react-dropzone) - Official library docs
- [python-magic PyPI](https://pypi.org/project/python-magic/) - Official package docs

### Secondary (MEDIUM confidence)
- [FastAPI File Uploads Guide (OneUpTime, 2026)](https://oneuptime.com/blog/post/2026-02-02-fastapi-file-uploads/view) - Recent practical guide
- [React File Upload UX Guide (Medium)](https://medium.com/@vishalsinghrajawat990/the-definitive-guide-to-uploading-files-in-react-ux-compression-api-best-practices-fa388fd7165c) - UX patterns
- [docx-preview npm](https://www.npmjs.com/package/docx-preview) - Package docs
- [shadcn/ui AlertDialog](https://ui.shadcn.com/docs/components/radix/alert-dialog) - Component patterns
- [Secure API file uploads with magic numbers (Transloadit)](https://transloadit.com/devtips/secure-api-file-uploads-with-magic-numbers/) - Security patterns
- [File Upload Vulnerabilities Guide (Aardwolf Security)](https://aardwolfsecurity.com/understanding-file-upload-vulnerabilities/) - Security checklist

### Tertiary (LOW confidence - marked for validation)
- Various GitHub discussions on file upload patterns - community knowledge, needs verification in production context

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Libraries well-established, versions verified via npm/PyPI, OWASP guidance authoritative
- Architecture: HIGH - Patterns verified in FastAPI/React official docs, filesystem storage confirmed by SQLite official guidance
- Pitfalls: HIGH - CVE-2026-24486 from official vulnerability database, OWASP checklist is industry standard
- File preview: MEDIUM-HIGH - react-pdf and docx-preview widely used but complex documents may have edge cases
- Admin auth: MEDIUM - Multiple valid approaches, needs user decision based on existing auth infrastructure

**Research date:** 2026-02-15
**Valid until:** 2026-03-15 (30 days - stable domain, but security landscape evolves)

**Notes for planner:**
- CVE-2026-24486 is critical and recent - MUST be addressed in validation tasks
- v1.0 folder structure reference required (HARD RULE) - planner must cite specific files
- User decisions locked in CONTEXT.md constrain many choices - prioritize those requirements
- Sheet component already exists in codebase - reuse pattern from Phase 8
- lucide-react already in package.json - use FileText, File, Image icons
