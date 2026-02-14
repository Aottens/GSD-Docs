# Stack Research: Web GUI for FDS/SDS Document Generation

**Domain:** Web-based GUI application (FastAPI + React)
**Researched:** 2026-02-14
**Confidence:** HIGH

## Executive Summary

This stack research focuses ONLY on additions needed for the web GUI milestone. The v1.0 CLI plugin foundation (Claude Code commands, templates, domain knowledge) is validated and NOT re-researched.

**Architecture:** FastAPI backend orchestrates Claude API calls using existing templates/prompts. React frontend provides project wizard, phase timeline, document preview, chat panel, and reference library. SQLite stores metadata. SSE streams progress updates. VM deployment with Nginx + systemd (no Docker).

**Key principle:** Backend becomes the orchestrator (replacing Claude Code's role). Frontend is the interface. Domain knowledge (templates, standards, workflows) remains in files, loaded by backend.

## Backend Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| FastAPI | 0.129+ | Web framework & API orchestration | Industry standard for Python async APIs. Automatic OpenAPI docs, native Pydantic validation, excellent async performance. [FastAPI production deployment best practices](https://render.com/articles/fastapi-production-deployment-best-practices) |
| Uvicorn | 0.34+ | ASGI server | High-performance async server. Single worker for development, multi-worker via Gunicorn in production. [FastAPI Server Workers](https://fastapi.tiangolo.com/deployment/server-workers/) |
| Gunicorn | 23.0+ | Process manager (production) | Manages Uvicorn workers for multi-core utilization. Workers = CPU cores for async workloads. [Mastering Gunicorn and Uvicorn](https://medium.com/@iklobato/mastering-gunicorn-and-uvicorn-the-right-way-to-deploy-fastapi-applications-aaa06849841e) |
| Pydantic | 2.10+ | Data validation & settings | v2 is 5-50x faster (Rust core). Built into FastAPI. Use for request/response models and settings. [Pydantic v2 validation](https://oneuptime.com/blog/post/2026-01-21-python-pydantic-v2-validation/view) |
| Anthropic SDK | 0.79+ | Claude API integration | Official SDK with async, streaming, tool use, structured outputs, fast-mode. Latest: v0.79.0 (Feb 7, 2026). [Anthropic SDK releases](https://github.com/anthropics/anthropic-sdk-python/releases) |

### Database & Persistence

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| SQLite | 3.45+ | Metadata storage | No server required, single-file database, perfect for team server (5-20 users). Stores projects, phases, user sessions, generation history. [SQLAlchemy with SQLite guide](https://blog.sqlite.ai/sqlite-python-sqlalchemy) |
| SQLAlchemy | 2.1+ | ORM & query builder | Industry-standard Python ORM. v2.1+ has async support, improved typing, better performance. [SQLAlchemy 2.1 docs](https://docs.sqlalchemy.org/en/21/tutorial/orm_data_manipulation.html) |
| Alembic | 1.18+ | Database migrations | Written by SQLAlchemy author. Auto-generates migrations, handles SQLite batch operations. Latest: 1.18.4 (Feb 10, 2026). [Alembic guide](https://alembic.sqlalchemy.org/en/latest/tutorial.html) |
| aiosqlite | 0.20+ | Async SQLite driver | Enables async database operations with SQLAlchemy. Required for non-blocking DB access. |

### Real-Time Communication

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| sse-starlette | 3.2+ | Server-Sent Events | W3C-compliant SSE for FastAPI. Better than WebSockets for unidirectional server-to-client streaming (phase progress, document generation status). Simpler protocol, auto-reconnect. [Building SSE MCP Server](https://www.ragie.ai/blog/building-a-server-sent-events-sse-mcp-server-with-fastapi) |

**Why SSE over WebSockets:**
- Simpler protocol (HTTP-based, unidirectional)
- Built-in browser auto-reconnect
- No complex state management
- Perfect for progress updates: server → client
- Falls back gracefully

### File Handling

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| python-multipart | 0.0.21+ | Multipart form parsing | Required for FastAPI file uploads. Parses multipart/form-data. [FastAPI file uploads](https://fastapi.tiangolo.com/tutorial/request-files/) |
| aiofiles | 24.1+ | Async file I/O | Non-blocking file operations for uploads/downloads. Critical for async performance. [File upload best practices](https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/) |

**File upload best practices:**
- Use `UploadFile` type (streams large files)
- Validate file type and size limits
- Stream to disk, don't load into memory
- Store files outside web root
- Return download URLs, not direct file access

### Configuration & Security

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| python-dotenv | 1.0+ | Environment variables | Load .env for local dev. Use with Pydantic Settings. Production uses system env vars. [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/) |
| python-jose[cryptography] | 3.3+ | JWT handling (optional) | If implementing user authentication. Industry standard for token generation/validation. |

### CORS Configuration

CORS is CRITICAL for FastAPI + React. Production must specify exact origins.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fds.example.com"],  # NEVER "*" in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

[CORS FastAPI React setup](https://davidmuraya.com/blog/fastapi-cors-configuration/)

## Frontend Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| React | 18.3+ | UI framework | Industry standard with excellent TypeScript support, mature ecosystem. [React docs](https://react.dev/) |
| TypeScript | 5.7+ | Type safety | Catch errors at compile time, better IDE support, self-documenting code. Essential for maintainability. |
| Vite | 6.1+ | Build tool & dev server | 40x faster than Create React App. HMR in milliseconds, optimized builds, first-class TypeScript support. Node.js 20.19+ required. [Vite React TypeScript](https://medium.com/@robinviktorsson/complete-guide-to-setting-up-react-with-typescript-and-vite-2025-468f6556aaf2) |

### UI Component Library

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| shadcn/ui | Latest | Component collection | Copy-paste components built on Radix UI + Tailwind. 100k+ GitHub stars, full code ownership, WCAG accessible, no runtime dependency. Perfect for custom design systems. [shadcn/ui](https://ui.shadcn.com/) |
| Radix UI | 1.2+ | Headless UI primitives | Powers shadcn/ui. WAI-ARIA compliant, unstyled, composable. Industry-leading accessibility. |
| Tailwind CSS | 4.1+ | Utility-first CSS | v4: 5x faster builds, CSS-first config with @theme, color-mix() utilities. Requires Safari 16.4+, Chrome 111+, Firefox 128+. [Tailwind v4](https://tailwindcss.com/blog/tailwindcss-v4) |
| Lucide React | 0.468+ | Icon library | Modern icons, tree-shakeable, consistent with shadcn/ui ecosystem. |

**Why shadcn/ui over alternatives:**
- Copy-paste = full ownership, no black box
- Built on accessibility-first Radix primitives
- Works with any styling solution (Tailwind default)
- No bundle size from unused components
- 2026 trend: copy-paste beats npm-install libraries

### State Management

| Technology | Version | Purpose | When to Use |
|------------|---------|---------|-------------|
| TanStack Query | 6.1+ | Server state | PRIMARY for all API data. Automatic caching, background refetching, stale-while-revalidate. Eliminates boilerplate. [TanStack Query](https://tanstack.com/query/latest) |
| Zustand | 5.0.10+ | Client state | ONLY for UI state (sidebar open/closed, theme, selected panel). Minimal API, no boilerplate, excellent TypeScript support. Latest: Jan 2026. [Zustand](https://zustand.docs.pmnd.rs/) |
| React Hook Form | 7.54+ | Form state | Complex forms with validation. Works with shadcn/ui form components. |

**State architecture:**
- **Server data:** TanStack Query (projects, phases, documents from API)
- **Client UI state:** Zustand (sidebar collapsed, active panel, theme)
- **Local component state:** useState/useReducer
- **Form state:** React Hook Form

**DO NOT use Redux.** TanStack Query + Zustand covers all needs with less boilerplate.

### Routing & Navigation

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| React Router | 7.13+ | Client-side routing | v7 combines React Router + Remix patterns. Built-in data loaders, type-safe params. No react-router-dom package needed. Latest: 7.13.0 (Jan 2026). [React Router v7](https://reactrouter.com/home) |

### Markdown Rendering

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| react-markdown | 9.0+ | Render Markdown in React | Industry standard, CommonMark compliant. Safely renders markdown as React components, extensible with remark/rehype plugins. [react-markdown](https://remarkjs.github.io/react-markdown/) |
| remark-gfm | 4.0+ | GitHub Flavored Markdown | Tables, strikethrough, task lists. Essential for technical docs. |
| rehype-highlight | 7.0+ | Syntax highlighting | Code block highlighting. Integrates with react-markdown. |

**Alternatives considered:**
- **markdown-to-jsx:** Faster, but less extensible
- **MDXEditor:** WYSIWYG editor, too complex for read-only preview
- **markdown-it:** Not React-aware

**Use react-markdown because:** Safe by default (XSS protection), React components output, plugin ecosystem.

## Deployment Stack

### VM Infrastructure (No Docker)

| Technology | Purpose | Why Recommended |
|------------|---------|-----------------|
| systemd | Service management | Native Linux service manager. Auto-restart, logging via journalctl, dependency management. Industry standard for non-containerized deployments. [FastAPI systemd deployment](https://ashfaque.medium.com/deploy-fastapi-app-on-debian-with-nginx-uvicorn-and-systemd-2d4b9b12d724) |
| Nginx | Reverse proxy & static files | Serve React build, proxy API to Gunicorn+Uvicorn, SSL termination, rate limiting, gzip compression. [Deploy FastAPI with Nginx](https://docs.vultr.com/how-to-deploy-a-fastapi-application-with-gunicorn-and-nginx-on-ubuntu-2404) |
| Unix socket | FastAPI ↔ Nginx communication | More efficient than TCP for localhost. Security benefit (filesystem permissions). |

**Why no Docker:**
- Single-server deployment (team of 5-20)
- systemd is simpler for ops team
- No orchestration complexity needed
- Direct filesystem access for uploads

### Deployment Tools

| Technology | Purpose | Notes |
|------------|---------|-------|
| python3-venv | Virtual environment | Isolate Python dependencies |
| npm/Node.js | Frontend build | Build React to static files for Nginx |
| certbot | SSL certificates | Let's Encrypt automation (optional) |

## Installation

### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Core dependencies
pip install \
    fastapi==0.129.0 \
    uvicorn[standard]==0.34.0 \
    gunicorn==23.0.0 \
    pydantic==2.10.0 \
    pydantic-settings==2.7.0 \
    anthropic==0.79.0

# Database
pip install \
    sqlalchemy==2.1.0 \
    alembic==1.18.4 \
    aiosqlite==0.20.0

# Real-time & file handling
pip install \
    sse-starlette==3.2.0 \
    python-multipart==0.0.21 \
    aiofiles==24.1.0

# Configuration & security
pip install \
    python-dotenv==1.0.0 \
    python-jose[cryptography]==3.3.0

# Development
pip install \
    pytest==8.3.0 \
    httpx==0.28.1 \
    pytest-asyncio==0.25.0
```

### Frontend Setup

```bash
# Create Vite React TypeScript project
npm create vite@latest frontend -- --template react-ts
cd frontend

# Core dependencies
npm install \
    react-router@7.13.0 \
    @tanstack/react-query@6.1.0 \
    zustand@5.0.10 \
    react-hook-form@7.54.0

# UI components & styling
npx shadcn@latest init
npm install \
    tailwindcss@4.1.0 \
    lucide-react@0.468.0 \
    clsx@2.1.1 \
    tailwind-merge@2.6.0

# Markdown rendering
npm install \
    react-markdown@9.0.0 \
    remark-gfm@4.0.0 \
    rehype-highlight@7.0.0

# Utilities
npm install \
    axios@1.7.9

# Development
npm install -D \
    @types/node@22.12.0 \
    @typescript-eslint/eslint-plugin@8.18.0 \
    @typescript-eslint/parser@8.18.0 \
    eslint@9.18.0 \
    prettier@3.4.2
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| FastAPI | Flask | If team already invested in Flask. FastAPI preferred for async + auto-docs. |
| SQLite | PostgreSQL | If expecting >50 concurrent users or complex queries. SQLite sufficient for team server (5-20 users). |
| SSE | WebSocket | If client needs to send frequent updates to server. Our use case is server → client. |
| shadcn/ui | Material UI (MUI) | If need comprehensive pre-built components, don't mind bundle size. shadcn/ui gives ownership. |
| TanStack Query | SWR | Both excellent. TanStack Query has more features (mutations, infinite queries, dev tools). |
| Zustand | Redux Toolkit | If need time-travel debugging or very complex state. Zustand simpler for UI state. |
| Vite | Next.js | If need SSR or full-stack framework. We're building SPA with separate backend. |
| react-markdown | markdown-to-jsx | If performance critical and don't need plugins. react-markdown more extensible. |
| systemd | Docker Compose | If multi-server or complex orchestration. systemd simpler for single VM. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Create React App | Deprecated, slow builds, unmaintained | Vite (40x faster) |
| Redux (classic) | Too much boilerplate | Zustand + TanStack Query |
| Axios in React | Unnecessary with TanStack Query | TanStack Query with fetch |
| Flask-SocketIO | Complex setup, requires eventlet/gevent | sse-starlette (simpler) |
| Docker Compose | Overkill for single-server deployment | systemd (native, simpler) |
| CORS allow_origins=["*"] | Security risk, breaks credentials | Explicit origins list |
| Global state for server data | Creates stale data issues | TanStack Query (auto-refresh) |
| Embedding Markdown in database | Parsing overhead, migration pain | Files on filesystem, paths in DB |

## Integration Points

### Backend → Frontend

1. **API Communication:**
   - FastAPI serves OpenAPI schema at `/openapi.json`
   - React uses TanStack Query for `/api/*` endpoints
   - CORS configured for frontend origin

2. **Real-Time Updates:**
   - FastAPI SSE endpoint: `GET /api/stream/phase/{phase_id}`
   - React EventSource consumes stream
   - Updates phase progress, document generation status

3. **File Handling:**
   - FastAPI receives via `UploadFile` (multipart)
   - Validates type/size, streams to filesystem
   - Metadata in SQLite, returns download URL

### Backend → Claude API

1. **Orchestration Layer:**
   - FastAPI endpoint: `POST /api/phases/{id}/generate`
   - Loads v1.0 templates/prompts from filesystem
   - Calls Anthropic SDK with streaming
   - Streams progress via SSE to frontend
   - Stores results: SQLite metadata + filesystem files

2. **LLM Provider Abstraction:**
   ```python
   class LLMProvider(ABC):
       async def generate(self, prompt: str, stream: bool) -> str

   class AnthropicProvider(LLMProvider):
       # Uses official SDK

   class LocalProvider(LLMProvider):
       # Future: llama.cpp, Ollama
   ```

### Frontend State Flow

```
User Action (e.g., "Generate Phase 2")
  → React Component
    → TanStack Query mutation
      → POST /api/phases/2/generate
        → FastAPI loads templates
          → Anthropic SDK streaming call
            → SSE progress updates
              → EventSource in React
                → TanStack Query cache update
                  → Component re-render
```

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| FastAPI 0.129+ | Pydantic 2.10+ | FastAPI requires Pydantic v2 |
| SQLAlchemy 2.1+ | Alembic 1.18+ | Alembic requires SQLAlchemy 2.0+ |
| SQLAlchemy 2.1+ | aiosqlite 0.20+ | Async SQLite driver |
| React 18.3+ | React Router 7.13+ | Router v7 works with React 18-19 |
| Tailwind 4.1 | Node.js 20.19+ | v4 requires modern Node.js |
| Vite 6.1+ | Node.js 20.19+ | ESM-first, requires modern Node |
| shadcn/ui | Radix UI 1.2+ + Tailwind 3.4/4+ | Peer dependencies |
| Gunicorn 23.0+ | Uvicorn 0.34+ | Use UvicornWorker class |

## Configuration Examples

### Backend: Pydantic Settings

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # API
    anthropic_api_key: str
    api_cors_origins: list[str] = ["http://localhost:5173"]

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/fds_gui.db"

    # File storage
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 50

    # Templates (v1.0 domain knowledge)
    templates_dir: str = "./templates"
    standards_dir: str = "./references/standards"
```

### Frontend: Vite Config

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### Deployment: systemd Service

```ini
# /etc/systemd/system/fds-api.service
[Unit]
Description=FDS/SDS GUI API
After=network.target

[Service]
Type=notify
User=fds
WorkingDirectory=/opt/fds-gui/backend
Environment="PATH=/opt/fds-gui/backend/venv/bin"
ExecStart=/opt/fds-gui/backend/venv/bin/gunicorn \
    -k uvicorn.workers.UvicornWorker \
    -w 2 \
    --bind unix:/run/fds-api.sock \
    app.main:app

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Deployment: Nginx Config

```nginx
# /etc/nginx/sites-available/fds-gui
server {
    listen 80;
    server_name fds.example.com;

    # Serve React build
    location / {
        root /opt/fds-gui/frontend/dist;
        try_files $uri $uri/ /index.html;
        gzip on;
        gzip_types text/css application/javascript application/json;
    }

    # Proxy API requests
    location /api/ {
        proxy_pass http://unix:/run/fds-api.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # SSE endpoint (special handling)
    location /api/stream/ {
        proxy_pass http://unix:/run/fds-api.sock;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_buffering off;
        chunked_transfer_encoding on;
    }
}
```

## Production Checklist

### Backend

- [ ] Use Gunicorn with Uvicorn workers (workers = CPU cores)
- [ ] Set CORS to specific frontend origin (NEVER `"*"`)
- [ ] Store secrets in environment variables (not .env in production)
- [ ] Enable SQLite WAL mode for better concurrency
- [ ] Implement file upload size/type validation
- [ ] Add rate limiting (via Nginx or middleware)
- [ ] Configure logging to systemd journal
- [ ] Set up Alembic migrations for schema changes
- [ ] LLM provider abstraction for future local models

### Frontend

- [ ] Build with `npm run build` (optimized bundle)
- [ ] Verify Tailwind purges unused CSS
- [ ] TanStack Query DevTools only in development
- [ ] Configure error boundaries for graceful failures
- [ ] Add loading states for all async operations
- [ ] Implement offline detection and retry logic
- [ ] Use environment variables for API URL
- [ ] Enable React strict mode in development

### Deployment

- [ ] Create dedicated system user (`fds`)
- [ ] Set file permissions (uploads directory)
- [ ] Configure systemd with auto-restart
- [ ] Enable Nginx gzip compression
- [ ] Set up SSL with certbot (optional)
- [ ] Backup strategy for SQLite database
- [ ] Log rotation for application logs
- [ ] Test SSE with long-running connections
- [ ] Verify v1.0 templates/standards load correctly

## Domain Knowledge Integration

**CRITICAL:** The web GUI does NOT replace v1.0 domain knowledge. It orchestrates it.

### What Stays in Files

- Templates (section-equipment-module.md, etc.)
- Standards (PackML, ISA-88)
- Workflows (write-phase, verify-phase)
- Prompts for Claude API
- Typicals library (CATALOG.json)

### What Moves to Database

- Project metadata (name, type, created_at)
- Phase state (current phase, status)
- User sessions (if auth added)
- Generation history (timestamp, tokens used)
- File upload metadata (filename, path, size)

### Backend Loads Templates

```python
# app/services/template_loader.py
class TemplateLoader:
    def __init__(self, templates_dir: str):
        self.templates_dir = Path(templates_dir)

    def load_section_template(self, template_name: str) -> str:
        path = self.templates_dir / "fds" / f"{template_name}.md"
        return path.read_text()

    def load_standard(self, standard_name: str) -> str:
        path = self.templates_dir.parent / "references" / "standards" / f"{standard_name}.md"
        return path.read_text()
```

## Stack Patterns

### Pattern: API Endpoint Structure

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class PhaseGenerateRequest(BaseModel):
    phase_number: int
    options: dict = {}

@app.post("/api/phases/{project_id}/generate")
async def generate_phase(
    project_id: int,
    request: PhaseGenerateRequest,
    llm: LLMProvider = Depends(get_llm_provider),
):
    # 1. Load project from DB
    # 2. Load templates from filesystem
    # 3. Build prompt using v1.0 patterns
    # 4. Call LLM with streaming
    # 5. Stream progress via SSE
    # 6. Save results to DB + filesystem
    pass
```

### Pattern: SSE Progress Stream

```python
from sse_starlette.sse import EventSourceResponse

@app.get("/api/stream/phase/{phase_id}")
async def stream_phase_progress(phase_id: int):
    async def event_generator():
        # Simulate progress
        for i in range(0, 101, 10):
            yield {
                "event": "progress",
                "data": json.dumps({"percent": i, "message": f"Processing {i}%"})
            }
            await asyncio.sleep(0.5)

        yield {
            "event": "complete",
            "data": json.dumps({"phase_id": phase_id})
        }

    return EventSourceResponse(event_generator())
```

### Pattern: React SSE Consumption

```typescript
// hooks/usePhaseProgress.ts
import { useEffect, useState } from 'react'

export function usePhaseProgress(phaseId: number | null) {
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!phaseId) return

    const eventSource = new EventSource(`/api/stream/phase/${phaseId}`)

    eventSource.addEventListener('progress', (e) => {
      const data = JSON.parse(e.data)
      setProgress(data.percent)
      setMessage(data.message)
    })

    eventSource.addEventListener('complete', () => {
      eventSource.close()
    })

    return () => eventSource.close()
  }, [phaseId])

  return { progress, message }
}
```

## Sources

**Backend:**
- [FastAPI production deployment best practices](https://render.com/articles/fastapi-production-deployment-best-practices) — MEDIUM confidence
- [Anthropic SDK releases](https://github.com/anthropics/anthropic-sdk-python/releases) — HIGH confidence (official)
- [Building SSE MCP Server with FastAPI](https://www.ragie.ai/blog/building-a-server-sent-events-sse-mcp-server-with-fastapi) — MEDIUM confidence
- [SQLAlchemy with SQLite guide](https://blog.sqlite.ai/sqlite-python-sqlalchemy) — MEDIUM confidence
- [Alembic migrations guide](https://alembic.sqlalchemy.org/en/latest/tutorial.html) — HIGH confidence (official)
- [Pydantic v2 validation](https://oneuptime.com/blog/post/2026-01-21-python-pydantic-v2-validation/view) — MEDIUM confidence
- [FastAPI CORS configuration](https://davidmuraya.com/blog/fastapi-cors-configuration/) — MEDIUM confidence
- [FastAPI file upload best practices](https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/) — MEDIUM confidence

**Frontend:**
- [Vite React TypeScript setup](https://medium.com/@robinviktorsson/complete-guide-to-setting-up-react-with-typescript-and-vite-2025-468f6556aaf2) — MEDIUM confidence
- [shadcn/ui overview](https://ui.shadcn.com/) — HIGH confidence (official)
- [Tailwind CSS v4 guide](https://tailwindcss.com/blog/tailwindcss-v4) — HIGH confidence (official)
- [TanStack Query overview](https://tanstack.com/query/latest) — HIGH confidence (official)
- [React Router v7](https://reactrouter.com/home) — HIGH confidence (official)
- [Zustand introduction](https://zustand.docs.pmnd.rs/) — HIGH confidence (official)
- [react-markdown guide](https://remarkjs.github.io/react-markdown/) — HIGH confidence (official)
- [React component libraries 2026](https://www.builder.io/blog/react-component-libraries-2026) — MEDIUM confidence

**Deployment:**
- [Deploy FastAPI with Nginx](https://docs.vultr.com/how-to-deploy-a-fastapi-application-with-gunicorn-and-nginx-on-ubuntu-2404) — MEDIUM confidence
- [FastAPI systemd deployment](https://ashfaque.medium.com/deploy-fastapi-app-on-debian-with-nginx-uvicorn-and-systemd-2d4b9b12d724) — MEDIUM confidence
- [Mastering Gunicorn and Uvicorn](https://medium.com/@iklobato/mastering-gunicorn-and-uvicorn-the-right-way-to-deploy-fastapi-applications-aaa06849841e) — MEDIUM confidence

---
*Stack research for: Web GUI for FDS/SDS Document Generation*
*Researched: 2026-02-14*
*This research focuses ONLY on web GUI additions. v1.0 CLI foundation NOT re-researched.*
