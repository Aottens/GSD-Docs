# Architecture Patterns: Web GUI for FDS/SDS Document Generation

**Domain:** Industrial automation FDS/SDS document generation
**Researched:** 2026-02-14
**Confidence:** HIGH

## Recommended Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (Engineer)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ React Frontend (TypeScript)                              │   │
│  │  • Project wizard + phase timeline (Zustand/Jotai)      │   │
│  │  • Document outline + Markdown preview (react-markdown) │   │
│  │  • Chat panel (WebSocket connection)                     │   │
│  │  • Reference library manager (upload/view)              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▲ │
                   HTTPS      │ │ WebSocket
                   REST API   │ │ /ws
                              │ ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Python)                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ API Layer                                                │   │
│  │  • REST endpoints (/api/projects, /api/phases)          │   │
│  │  • WebSocket manager (/ws/{session_id})                 │   │
│  │  • File upload handler (/api/files/upload)              │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Workflow Engine (orchestrator)                           │   │
│  │  • Workflow loader (translates .md → Python)            │   │
│  │  • Step executor (wave-based parallelization)           │   │
│  │  • State manager (STATE.md checkpoint/resume)           │   │
│  │  • Background task coordinator (ARQ + Redis)            │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ LLM Provider Abstraction                                 │   │
│  │  • LLMProvider interface (abstract base)                │   │
│  │  • ClaudeProvider (Anthropic SDK)                       │   │
│  │  • LocalProvider (stub for v3.0, Ollama/llama.cpp)     │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Domain Knowledge Loader                                  │   │
│  │  • Template registry (equipment-module.md, etc.)        │   │
│  │  • Standards loader (PackML/ISA-88, opt-in)             │   │
│  │  • Prompt builder (agent context assembly)              │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Metadata Store (SQLite)                                  │   │
│  │  • Projects table (id, name, type, created, status)     │   │
│  │  • Files table (id, project_id, path, type, uploaded)   │   │
│  │  • Sessions table (id, user, started, last_activity)    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▲ │
                              │ │
                              │ ▼
┌─────────────────────────────────────────────────────────────────┐
│                      File System Storage                        │
│  • /projects/{project-id}/.planning/ (ROADMAP, STATE, etc.)    │
│  • /projects/{project-id}/.planning/phases/ (PLAN, CONTENT)    │
│  • /projects/{project-id}/output/ (FDS/SDS final docs)         │
│  • /references/shared/ (PackML, ISA-88, typicals CATALOG)      │
│  • /references/projects/{id}/ (per-project overrides)          │
└─────────────────────────────────────────────────────────────────┘
                              ▲ │
                              │ │ API calls
                              │ ▼
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                          │
│  • Anthropic Claude API (LLM provider)                         │
│  • Pandoc (DOCX export, shell subprocess)                      │
│  • Mermaid CLI (diagram rendering, mmdc)                       │
└─────────────────────────────────────────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **React Frontend** | User interface, state management, real-time updates display | FastAPI REST + WebSocket |
| **API Layer** | HTTP routing, WebSocket connection management, request validation | Workflow Engine, File Storage, SQLite |
| **Workflow Engine** | Orchestrate .md workflow execution, spawn LLM tasks, manage waves | LLM Provider, Domain Knowledge Loader, State Manager |
| **LLM Provider** | Abstract LLM API calls (Claude, future local models) | External LLM APIs (Anthropic, Ollama) |
| **Domain Knowledge Loader** | Load templates, standards, prompts from v1.0 file structure | File System (gsd-docs-industrial/) |
| **State Manager** | Read/write STATE.md, checkpoint operations, detect crashes | File System (.planning/STATE.md) |
| **SQLite Metadata** | Project list, file registry, session tracking | API Layer |
| **File Storage** | Store project files, references, generated documents | API Layer, Workflow Engine |

### Data Flow

#### 1. Project Creation Flow

```
Engineer fills wizard → React validates → POST /api/projects
                                             ↓
                                FastAPI creates project
                                             ↓
                        Workflow Engine loads new-fds.md workflow
                                             ↓
                        LLM Provider calls Claude (classify Type A/B/C/D)
                                             ↓
                        Generate ROADMAP.md, PROJECT.md, STATE.md
                                             ↓
                        File Storage writes .planning/ files
                                             ↓
                        SQLite stores project metadata
                                             ↓
                        WebSocket broadcasts "project_created" event
                                             ↓
                        React updates project list + redirects to timeline
```

#### 2. Phase Discussion Flow

```
Engineer clicks "Discuss Phase 3" → POST /api/phases/3/discuss
                                             ↓
                        Workflow Engine loads discuss-phase.md workflow
                                             ↓
                        Read ROADMAP.md for phase goals
                                             ↓
                        LLM Provider calls Claude (identify gray areas)
                                             ↓
                        WebSocket streams questions to chat panel
                                             ↓
                        Engineer answers via /ws/send_message
                                             ↓
                        Workflow accumulates decisions
                                             ↓
                        Generate CONTEXT.md with decisions
                                             ↓
                        State Manager updates STATE.md
                                             ↓
                        WebSocket broadcasts "phase_discussion_complete"
                                             ↓
                        React enables "Plan Phase 3" button
```

#### 3. Phase Writing Flow (Wave-based Parallelization)

```
Engineer clicks "Write Phase 3" → POST /api/phases/3/write
                                             ↓
                        Workflow Engine loads write-phase.md workflow
                                             ↓
                        Discover all PLAN.md files in phase-3/
                                             ↓
                        Group plans by wave number (frontmatter)
                                             ↓
                        State Manager checkpoints STATE.md (wave 1 start)
                                             ↓
                        FOR EACH WAVE (sequential):
                          ↓
                          Background Task Queue (ARQ + Redis):
                          - Spawn parallel tasks for all plans in wave
                          - Each task:
                              → Domain Knowledge Loader builds isolated context
                              → Load: PROJECT.md, CONTEXT.md, PLAN.md, standards
                              → NOT loaded: other plans, other CONTENT.md
                              → LLM Provider calls Claude (doc-writer agent)
                              → Write CONTENT.md + SUMMARY.md
                              → WebSocket streams progress per section
                          - Await all wave tasks completion
                          ↓
                          State Manager checkpoints STATE.md (wave N complete)
                          ↓
                        Aggregate CROSS-REFS.md from all writers
                                             ↓
                        WebSocket broadcasts "phase_write_complete"
                                             ↓
                        React updates phase timeline (Phase 3: Writing → Verifying)
```

#### 4. Document Preview Flow

```
Engineer clicks section in outline → GET /api/phases/3/content/03-02
                                             ↓
                        File Storage reads 03-02-CONTENT.md
                                             ↓
                        Return raw Markdown to React
                                             ↓
                        react-markdown renders with syntax highlighting
                                             ↓
                        Mermaid diagrams rendered client-side
```

#### 5. Reference Upload Flow

```
Engineer uploads PackML guide PDF → POST /api/files/upload
                                             ↓
                        FastAPI UploadFile handler
                                             ↓
                        Validate file type + size
                                             ↓
                        File Storage writes to /references/projects/{id}/
                                             ↓
                        SQLite stores file metadata
                                             ↓
                        WebSocket broadcasts "file_uploaded"
                                             ↓
                        React updates reference library list
```

---

## Integration Points: v1.0 → v2.0

### New Components (Built from Scratch)

| Component | What | Technology |
|-----------|------|------------|
| **Frontend UI** | Visual interface for all workflows | React + TypeScript, Zustand/Jotai state, react-markdown |
| **FastAPI Backend** | Replaces Claude Code as orchestrator | FastAPI 2026, Pydantic v2, async/await |
| **WebSocket Manager** | Real-time progress streaming | FastAPI WebSockets, Redis pub/sub for multi-instance |
| **LLM Provider Abstraction** | Model-agnostic interface | Abstract base class, ClaudeProvider (Anthropic SDK) |
| **Background Task Queue** | Wave-based parallel execution | ARQ (Async Redis Queue) |
| **SQLite Metadata Store** | Project/file/session registry | SQLite with SQLAlchemy async |
| **API Routes** | REST endpoints for all operations | FastAPI routers (projects, phases, files, export) |

### Modified Components (Adapted from v1.0)

| Component | v1.0 Implementation | v2.0 Change | Reason |
|-----------|---------------------|-------------|--------|
| **Workflow Logic** | .md files with embedded bash/prompts | Python orchestrator reads .md, executes steps | Web backend can't execute bash directly; translate logic to Python |
| **Context Loading** | Claude Code @file syntax | Python file reader + prompt builder | Explicit context assembly for API calls |
| **State Management** | STATE.md read/write via bash | Python STATE.md parser/writer | Programmatic checkpoint/resume logic |
| **File Discovery** | Glob/Grep tools | Python pathlib.glob() + regex | Native Python file operations |
| **Progress Feedback** | Terminal output (echo, boxes) | WebSocket JSON events | Real-time browser updates |

### Unchanged Components (Reused Exactly)

| Component | What | Why Unchanged |
|-----------|------|---------------|
| **Domain Knowledge Files** | Templates (equipment-module.md), standards (PackML, ISA-88), section structures | These ARE the SSOT for document structure; backend loads as prompt context |
| **Workflow .md Files** | 14 workflow files (new-fds.md, write-phase.md, etc.) | Step descriptions, validation logic, success criteria remain authoritative; Python reads them |
| **Agent Prompts** | doc-writer.md, doc-verifier.md, fresh-eyes.md | Agent role definitions and instructions reused verbatim as LLM system prompts |
| **Project File Format** | .planning/, ROADMAP.md, PLAN.md frontmatter, STATE.md structure | CLI compatibility requirement; GUI and CLI produce identical files |
| **SPECIFICATION.md** | v2.7.0 SSOT for workflow semantics | Reference document for implementing Python orchestration logic |

---

## Pattern 1: Workflow Translation (.md → Python)

### v1.0 Pattern (CLI)

Workflows are .md files with embedded bash and Claude Code directives:

```markdown
## Step 3: Discover Plans

**Discover plans:**
```bash
PHASE_DIR=$(find .planning/phases -type d -name "${PHASE}-*" | head -1)
PLAN_FILES=$(find ${PHASE_DIR} -name "${PHASE}-[0-9][0-9]-PLAN.md" | sort)
```

**For each plan file, read YAML frontmatter:**
```bash
WAVE=$(grep "^wave:" ${PLAN_FILE} | cut -d: -f2 | tr -d ' ')
```
```

### v2.0 Pattern (Web Backend)

Python orchestrator reads the .md workflow and executes equivalent logic:

```python
# backend/workflows/engine.py

class WorkflowEngine:
    def __init__(self, workflow_path: Path):
        """Load workflow .md file and parse steps."""
        self.workflow_md = workflow_path.read_text()
        self.steps = self._parse_workflow_steps()

    def _parse_workflow_steps(self) -> List[WorkflowStep]:
        """Extract ## Step N: sections from markdown."""
        # Parse markdown, extract step headers + content
        # Each step becomes a callable Python function
        pass

    async def execute_step(self, step_name: str, context: dict):
        """Execute a workflow step with given context."""
        step = self.steps[step_name]

        # Example: "Discover Plans" step
        if step_name == "discover_plans":
            return await self._discover_plans(context)

    async def _discover_plans(self, context: dict) -> List[PlanFile]:
        """Python equivalent of bash plan discovery."""
        phase_num = context["phase"]

        # Find phase directory
        phase_dirs = list(Path(".planning/phases").glob(f"{phase_num:02d}-*"))
        if not phase_dirs:
            raise WorkflowError(f"Phase {phase_num} directory not found")

        phase_dir = phase_dirs[0]

        # Find all PLAN.md files
        plan_files = sorted(phase_dir.glob(f"{phase_num:02d}-[0-9][0-9]-PLAN.md"))

        # Parse frontmatter from each plan
        plans = []
        for plan_path in plan_files:
            frontmatter = self._parse_yaml_frontmatter(plan_path)
            plans.append(PlanFile(
                path=plan_path,
                plan_id=frontmatter["plan"],
                wave=frontmatter["wave"],
                name=frontmatter["name"],
                depends_on=frontmatter.get("depends_on", [])
            ))

        return plans
```

**Key principle:** The .md file is the SOURCE OF TRUTH for workflow logic. Python code IMPLEMENTS what the .md describes, not vice versa. If workflow changes, update the .md; Python reads and executes it.

---

## Pattern 2: FastAPI Backend Structure

### Recommended Directory Layout

```
backend/
├── main.py                      # FastAPI app entry, lifespan, CORS
├── config.py                    # Settings (Pydantic BaseSettings)
├── database.py                  # SQLite/SQLAlchemy async session
│
├── api/                         # REST API routes
│   ├── __init__.py
│   ├── projects.py              # /api/projects CRUD
│   ├── phases.py                # /api/phases/{phase}/discuss|plan|write|verify
│   ├── files.py                 # /api/files/upload, /api/files/{file_id}
│   ├── export.py                # /api/export/fds|sds|docx
│   └── websocket.py             # /ws/{session_id} WebSocket endpoint
│
├── workflows/                   # Workflow orchestration
│   ├── __init__.py
│   ├── engine.py                # WorkflowEngine (loads .md, executes steps)
│   ├── loaders.py               # Load workflow .md files from gsd-docs-industrial/
│   ├── state_manager.py         # STATE.md read/write, checkpoint/resume
│   └── steps/                   # Python implementations of workflow steps
│       ├── new_fds.py           # new-fds.md step implementations
│       ├── discuss_phase.py
│       ├── plan_phase.py
│       ├── write_phase.py
│       └── verify_phase.py
│
├── llm/                         # LLM provider abstraction
│   ├── __init__.py
│   ├── provider.py              # LLMProvider abstract base class
│   ├── claude.py                # ClaudeProvider (Anthropic SDK)
│   ├── local.py                 # LocalProvider (stub for v3.0)
│   └── context_builder.py       # Build agent prompts with domain knowledge
│
├── domain/                      # Domain knowledge loading
│   ├── __init__.py
│   ├── templates.py             # Load templates from gsd-docs-industrial/templates/
│   ├── standards.py             # Load PackML/ISA-88 if enabled in PROJECT.md
│   ├── agents.py                # Load agent prompts (doc-writer.md, etc.)
│   └── prompts.py               # Assemble full prompts for LLM calls
│
├── tasks/                       # Background task definitions (ARQ)
│   ├── __init__.py
│   ├── write_tasks.py           # Parallel section writing tasks
│   └── export_tasks.py          # DOCX generation tasks
│
├── models/                      # Pydantic models + SQLAlchemy schemas
│   ├── __init__.py
│   ├── project.py               # Project SQLAlchemy + Pydantic models
│   ├── phase.py                 # Phase state models
│   ├── plan.py                  # PLAN.md frontmatter schema
│   └── session.py               # WebSocket session tracking
│
└── utils/                       # Utilities
    ├── __init__.py
    ├── file_ops.py              # File read/write helpers
    ├── frontmatter.py           # YAML frontmatter parser
    └── markdown.py              # Markdown utilities
```

### Core FastAPI Application

```python
# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api import projects, phases, files, export, websocket
from database import init_db
from tasks import setup_arq

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    await init_db()
    await setup_arq()
    yield
    # Shutdown
    # Close connections, cleanup

app = FastAPI(
    title="GSD-Docs Industrial API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(phases.router, prefix="/api/phases", tags=["phases"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root():
    return {"message": "GSD-Docs Industrial API v2.0"}
```

---

## Pattern 3: LLM Provider Abstraction

### Interface Design (Model-Agnostic)

```python
# backend/llm/provider.py

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional
from pydantic import BaseModel

class LLMMessage(BaseModel):
    """Single message in conversation."""
    role: str  # "system" | "user" | "assistant"
    content: str

class LLMResponse(BaseModel):
    """Response from LLM."""
    content: str
    model: str
    usage: dict  # tokens, cost, etc.
    finish_reason: str

class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    async def complete(
        self,
        messages: list[LLMMessage],
        model: str,
        max_tokens: int = 4000,
        temperature: float = 1.0,
        **kwargs
    ) -> LLMResponse:
        """Single completion (non-streaming)."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[LLMMessage],
        model: str,
        max_tokens: int = 4000,
        temperature: float = 1.0,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streaming completion (yields text chunks)."""
        pass

    @abstractmethod
    async def count_tokens(self, text: str, model: str) -> int:
        """Estimate token count for text."""
        pass
```

### Claude Implementation (v2.0)

```python
# backend/llm/claude.py

from anthropic import AsyncAnthropic
from llm.provider import LLMProvider, LLMMessage, LLMResponse

class ClaudeProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
        self.default_model = "claude-opus-4-6"

    async def complete(
        self,
        messages: list[LLMMessage],
        model: str = None,
        max_tokens: int = 4000,
        temperature: float = 1.0,
        **kwargs
    ) -> LLMResponse:
        """Call Claude API (non-streaming)."""
        model = model or self.default_model

        # Convert LLMMessage to Anthropic format
        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role != "system"  # system goes in separate param
        ]

        system_msg = next((m.content for m in messages if m.role == "system"), None)

        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_msg,
            messages=anthropic_messages,
            **kwargs
        )

        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            finish_reason=response.stop_reason
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        model: str = None,
        max_tokens: int = 4000,
        temperature: float = 1.0,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Call Claude API (streaming)."""
        model = model or self.default_model

        # Same message conversion as above
        anthropic_messages = [...]
        system_msg = ...

        async with self.client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_msg,
            messages=anthropic_messages,
            **kwargs
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def count_tokens(self, text: str, model: str) -> int:
        """Estimate tokens (Anthropic SDK provides count_tokens)."""
        return await self.client.count_tokens(text)
```

### Local Model Stub (v3.0 Preparation)

```python
# backend/llm/local.py

from llm.provider import LLMProvider, LLMMessage, LLMResponse

class LocalProvider(LLMProvider):
    """Local model provider (Ollama, llama.cpp, etc.)."""

    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint  # e.g., "http://localhost:11434" for Ollama
        self.model = model        # e.g., "llama3.3-405b"

    async def complete(
        self,
        messages: list[LLMMessage],
        model: str = None,
        max_tokens: int = 4000,
        temperature: float = 1.0,
        **kwargs
    ) -> LLMResponse:
        """Call local model endpoint (stub for v3.0)."""
        # TODO v3.0: Implement Ollama/llama.cpp API call
        raise NotImplementedError("Local model support coming in v3.0")

    async def stream(self, messages, model, max_tokens, temperature, **kwargs):
        raise NotImplementedError("Local model support coming in v3.0")

    async def count_tokens(self, text: str, model: str) -> int:
        # TODO v3.0: Implement local tokenizer
        return len(text) // 4  # Rough estimate
```

### Provider Factory

```python
# backend/llm/__init__.py

from llm.provider import LLMProvider
from llm.claude import ClaudeProvider
from llm.local import LocalProvider
from config import settings

def get_llm_provider() -> LLMProvider:
    """Factory: return configured LLM provider."""
    if settings.LLM_PROVIDER == "claude":
        return ClaudeProvider(api_key=settings.ANTHROPIC_API_KEY)
    elif settings.LLM_PROVIDER == "local":
        return LocalProvider(
            endpoint=settings.LOCAL_LLM_ENDPOINT,
            model=settings.LOCAL_LLM_MODEL
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")
```

**Key benefit:** Entire codebase calls `get_llm_provider().complete()`. Swapping Claude → local model is a config change, not a code rewrite.

---

## Pattern 4: React Frontend Structure

### Recommended Directory Layout

```
frontend/
├── src/
│   ├── main.tsx                 # React entry point
│   ├── App.tsx                  # Root component, routing
│   │
│   ├── components/              # Reusable UI components
│   │   ├── ProjectWizard.tsx    # Multi-step project creation
│   │   ├── PhaseTimeline.tsx    # Phase progress visualization
│   │   ├── DocumentOutline.tsx  # Collapsible phase/section tree
│   │   ├── ChatPanel.tsx        # WebSocket-connected chat
│   │   ├── MarkdownPreview.tsx  # react-markdown + Mermaid
│   │   ├── ReferenceLibrary.tsx # File upload + listing
│   │   └── ProgressIndicator.tsx # Wave/section progress bars
│   │
│   ├── pages/                   # Route pages
│   │   ├── Home.tsx             # Project list dashboard
│   │   ├── ProjectView.tsx      # Main working view (timeline + outline + preview)
│   │   ├── PhaseDiscuss.tsx     # Discussion UI for gray areas
│   │   ├── PhaseVerify.tsx      # Verification results display
│   │   └── Export.tsx           # DOCX export options
│   │
│   ├── state/                   # State management
│   │   ├── projectStore.ts      # Zustand store for projects
│   │   ├── phaseStore.ts        # Zustand store for current phase state
│   │   ├── chatStore.ts         # WebSocket message history
│   │   └── referenceStore.ts    # Reference library state
│   │
│   ├── api/                     # API client
│   │   ├── client.ts            # Axios instance with auth
│   │   ├── projects.ts          # Project CRUD endpoints
│   │   ├── phases.ts            # Phase operation endpoints
│   │   ├── files.ts             # File upload endpoints
│   │   └── websocket.ts         # WebSocket connection manager
│   │
│   ├── hooks/                   # Custom React hooks
│   │   ├── useWebSocket.ts      # WebSocket connection hook
│   │   ├── useProject.ts        # Load project data
│   │   ├── usePhaseState.ts     # Track phase progress
│   │   └── useFileUpload.ts     # File upload with progress
│   │
│   └── types/                   # TypeScript types
│       ├── project.ts           # Project, ROADMAP types
│       ├── phase.ts             # Phase, Plan types
│       ├── message.ts           # WebSocket message types
│       └── api.ts               # API request/response types
│
├── public/
│   └── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts               # Vite bundler config
```

### State Management: Zustand (Lightweight, Recommended)

```typescript
// frontend/src/state/projectStore.ts

import create from 'zustand';

interface Project {
  id: string;
  name: string;
  type: 'A' | 'B' | 'C' | 'D';
  status: 'planning' | 'writing' | 'verifying' | 'complete';
  currentPhase: number;
  createdAt: string;
}

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;

  // Actions
  loadProjects: () => Promise<void>;
  selectProject: (id: string) => void;
  createProject: (data: CreateProjectRequest) => Promise<string>;
  updateProjectStatus: (id: string, status: Project['status']) => void;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  currentProject: null,

  loadProjects: async () => {
    const response = await fetch('/api/projects');
    const projects = await response.json();
    set({ projects });
  },

  selectProject: (id: string) => {
    const project = get().projects.find(p => p.id === id);
    set({ currentProject: project || null });
  },

  createProject: async (data) => {
    const response = await fetch('/api/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    const newProject = await response.json();
    set(state => ({
      projects: [...state.projects, newProject],
      currentProject: newProject,
    }));
    return newProject.id;
  },

  updateProjectStatus: (id, status) => {
    set(state => ({
      projects: state.projects.map(p =>
        p.id === id ? { ...p, status } : p
      ),
    }));
  },
}));
```

### WebSocket Hook (Real-Time Updates)

```typescript
// frontend/src/hooks/useWebSocket.ts

import { useEffect, useRef, useState } from 'react';
import { useChatStore } from '../state/chatStore';

export interface WebSocketMessage {
  type: string;
  data: any;
}

export function useWebSocket(sessionId: string) {
  const [connected, setConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const addMessage = useChatStore(state => state.addMessage);

  useEffect(() => {
    // Connect to WebSocket
    const socket = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
    ws.current = socket;

    socket.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    socket.onmessage = (event) => {
      const message: WebSocketMessage = JSON.parse(event.data);

      // Route message based on type
      switch (message.type) {
        case 'chat_message':
          addMessage(message.data);
          break;
        case 'progress_update':
          // Handle progress update (e.g., wave completion)
          break;
        case 'phase_complete':
          // Handle phase completion
          break;
        default:
          console.warn('Unknown message type:', message.type);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    return () => {
      socket.close();
    };
  }, [sessionId]);

  const sendMessage = (type: string, data: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type, data }));
    }
  };

  return { connected, sendMessage };
}
```

### Markdown Preview Component

```typescript
// frontend/src/components/MarkdownPreview.tsx

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import mermaid from 'mermaid';

interface MarkdownPreviewProps {
  content: string;
}

export const MarkdownPreview: React.FC<MarkdownPreviewProps> = ({ content }) => {
  // Initialize Mermaid
  React.useEffect(() => {
    mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
    mermaid.contentLoaded();
  }, [content]);

  return (
    <div className="markdown-preview">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';

            // Mermaid diagrams
            if (language === 'mermaid') {
              return (
                <div className="mermaid">
                  {String(children).replace(/\n$/, '')}
                </div>
              );
            }

            // Code blocks with syntax highlighting
            if (!inline && match) {
              return (
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={language}
                  PreTag="div"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              );
            }

            // Inline code
            return <code className={className} {...props}>{children}</code>;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
```

---

## Pattern 5: File Storage Architecture

### Storage Layout

```
/opt/gsd-docs-data/              # Base data directory (VM deployment)
│
├── references/                  # Reference library
│   ├── shared/                  # Global references (all projects)
│   │   ├── standards/
│   │   │   ├── packml/
│   │   │   │   ├── STATE-MODEL.md
│   │   │   │   └── UNIT-MODES.md
│   │   │   └── isa-88/
│   │   │       ├── EQUIPMENT-HIERARCHY.md
│   │   │       └── TERMINOLOGY.md
│   │   ├── typicals/
│   │   │   ├── CATALOG.json
│   │   │   └── library/
│   │   │       ├── FB_AnalogIn.scl
│   │   │       └── FB_DosingStation.scl
│   │   └── vendor-docs/
│   │       ├── siemens-packml-guide.pdf
│   │       └── rockwell-isa88-overview.pdf
│   │
│   └── projects/                # Per-project reference overrides
│       ├── {project-id}/
│       │   ├── client-standards/
│       │   ├── baseline-fds/   # For modification projects (Type C/D)
│       │   └── vendor-docs/
│       └── ...
│
├── projects/                    # Project working directories
│   ├── {project-id}/
│   │   ├── .planning/           # Planning artifacts
│   │   │   ├── PROJECT.md
│   │   │   ├── REQUIREMENTS.md
│   │   │   ├── ROADMAP.md
│   │   │   ├── STATE.md
│   │   │   ├── BASELINE.md      # Type C/D only
│   │   │   ├── config.json
│   │   │   │
│   │   │   ├── phases/
│   │   │   │   ├── 01-foundation/
│   │   │   │   │   ├── CONTEXT.md
│   │   │   │   │   ├── 01-01-PLAN.md
│   │   │   │   │   ├── 01-01-CONTENT.md
│   │   │   │   │   ├── 01-01-SUMMARY.md
│   │   │   │   │   └── VERIFICATION.md
│   │   │   │   ├── 02-architecture/
│   │   │   │   │   └── ...
│   │   │   │   └── 03-equipment/
│   │   │   │       ├── CONTEXT.md
│   │   │   │       ├── CROSS-REFS.md
│   │   │   │       ├── 03-01-PLAN.md
│   │   │   │       ├── 03-01-CONTENT.md
│   │   │   │       ├── 03-01-SUMMARY.md
│   │   │   │       ├── 03-02-PLAN.md
│   │   │   │       └── ...
│   │   │   │
│   │   │   └── archive/
│   │   │       └── v1.0/
│   │   │
│   │   ├── output/              # Final documents
│   │   │   ├── FDS-{Project}-v1.0.md
│   │   │   ├── SDS-{Project}-v1.0.md
│   │   │   ├── RATIONALE.md
│   │   │   ├── EDGE-CASES.md
│   │   │   └── TRACEABILITY.md
│   │   │
│   │   ├── diagrams/            # Generated diagrams
│   │   │   ├── mermaid/
│   │   │   │   ├── phase-3-state-em-200.mmd
│   │   │   │   └── ...
│   │   │   └── rendered/
│   │   │       ├── phase-3-state-em-200.png
│   │   │       └── ...
│   │   │
│   │   └── export/              # DOCX exports
│   │       ├── FDS-{Project}-v1.0.docx
│   │       └── SDS-{Project}-v1.0.docx
│   │
│   └── ...
│
└── metadata/                    # SQLite database
    └── gsd-docs.db
```

### File Upload Endpoint

```python
# backend/api/files.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from typing import List
import aiofiles
import mimetypes

router = APIRouter()

UPLOAD_DIR = Path("/opt/gsd-docs-data/references/projects")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "text/markdown",
    "text/plain",
}

@router.post("/upload")
async def upload_file(
    project_id: str,
    category: str,  # "client-standards" | "baseline-fds" | "vendor-docs"
    file: UploadFile = File(...)
):
    """Upload reference file for a project."""

    # Validate file type
    content_type = file.content_type
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {content_type} not allowed"
        )

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)     # Reset to start

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {MAX_FILE_SIZE // 1024 // 1024}MB)"
        )

    # Save file
    project_dir = UPLOAD_DIR / project_id / category
    project_dir.mkdir(parents=True, exist_ok=True)

    file_path = project_dir / file.filename

    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Store metadata in SQLite
    file_metadata = {
        "project_id": project_id,
        "filename": file.filename,
        "category": category,
        "path": str(file_path),
        "size": size,
        "mime_type": content_type,
        "uploaded_at": datetime.now().isoformat(),
    }
    # ... save to database

    return {
        "success": True,
        "file_id": file_metadata["id"],
        "path": str(file_path)
    }
```

---

## Pattern 6: Real-Time Communication Layer

### WebSocket Message Protocol

```python
# backend/api/websocket.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
import asyncio

router = APIRouter()

# Active connections registry
connections: Dict[str, WebSocket] = {}

@router.websocket("/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket connection for real-time updates."""

    await websocket.accept()
    connections[session_id] = websocket

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "data": {"session_id": session_id}
        })

        # Listen for client messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Route message based on type
            await handle_client_message(session_id, message)

    except WebSocketDisconnect:
        del connections[session_id]
        print(f"Client {session_id} disconnected")

async def handle_client_message(session_id: str, message: dict):
    """Handle incoming message from client."""
    msg_type = message.get("type")

    if msg_type == "chat_message":
        # User answered a discussion question
        # ... process answer
        pass

    elif msg_type == "ping":
        # Heartbeat
        await send_to_client(session_id, {
            "type": "pong",
            "data": {}
        })

async def send_to_client(session_id: str, message: dict):
    """Send message to specific client."""
    ws = connections.get(session_id)
    if ws:
        await ws.send_json(message)

async def broadcast_progress(session_id: str, event: str, data: dict):
    """Broadcast progress update to client."""
    await send_to_client(session_id, {
        "type": "progress_update",
        "data": {
            "event": event,
            "timestamp": datetime.now().isoformat(),
            **data
        }
    })
```

### Progress Broadcasting (from Background Tasks)

```python
# backend/tasks/write_tasks.py

from arq import create_pool
from arq.connections import RedisSettings
from api.websocket import broadcast_progress

async def write_section_task(
    ctx: dict,
    session_id: str,
    project_id: str,
    phase: int,
    plan_id: str
):
    """Background task: write single section (runs in wave)."""

    # Load context
    context = await load_section_context(project_id, phase, plan_id)

    # Broadcast start
    await broadcast_progress(session_id, "section_write_start", {
        "plan_id": plan_id,
        "plan_name": context["plan"]["name"]
    })

    # Call LLM provider
    llm = get_llm_provider()
    messages = build_writer_prompt(context)

    # Stream response and broadcast chunks
    content_chunks = []
    async for chunk in llm.stream(messages, model="claude-opus-4-6"):
        content_chunks.append(chunk)

        # Broadcast progress every N chunks
        if len(content_chunks) % 10 == 0:
            await broadcast_progress(session_id, "section_write_progress", {
                "plan_id": plan_id,
                "chars_written": len("".join(content_chunks))
            })

    # Write files
    content = "".join(content_chunks)
    await write_content_file(project_id, phase, plan_id, content)

    # Generate SUMMARY.md
    summary = await generate_summary(llm, content)
    await write_summary_file(project_id, phase, plan_id, summary)

    # Broadcast completion
    await broadcast_progress(session_id, "section_write_complete", {
        "plan_id": plan_id,
        "content_length": len(content),
        "summary_length": len(summary)
    })

    return {"success": True, "plan_id": plan_id}
```

### React Component (Receiving Updates)

```typescript
// frontend/src/components/ProgressIndicator.tsx

import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface SectionProgress {
  plan_id: string;
  plan_name: string;
  status: 'pending' | 'writing' | 'complete';
  chars_written: number;
}

export const ProgressIndicator: React.FC<{ sessionId: string }> = ({ sessionId }) => {
  const { connected } = useWebSocket(sessionId);
  const [sections, setSections] = useState<Record<string, SectionProgress>>({});

  useEffect(() => {
    // Listen for progress updates
    const handleMessage = (event: MessageEvent) => {
      const message = JSON.parse(event.data);

      if (message.type === 'progress_update') {
        const { event: eventName, data } = message.data;

        if (eventName === 'section_write_start') {
          setSections(prev => ({
            ...prev,
            [data.plan_id]: {
              plan_id: data.plan_id,
              plan_name: data.plan_name,
              status: 'writing',
              chars_written: 0,
            }
          }));
        }

        if (eventName === 'section_write_progress') {
          setSections(prev => ({
            ...prev,
            [data.plan_id]: {
              ...prev[data.plan_id],
              chars_written: data.chars_written,
            }
          }));
        }

        if (eventName === 'section_write_complete') {
          setSections(prev => ({
            ...prev,
            [data.plan_id]: {
              ...prev[data.plan_id],
              status: 'complete',
            }
          }));
        }
      }
    };

    // ... attach listener
  }, []);

  return (
    <div className="progress-indicator">
      <h3>Writing Progress</h3>
      {Object.values(sections).map(section => (
        <div key={section.plan_id} className="section-progress">
          <span>{section.plan_name}</span>
          <span className={`status ${section.status}`}>
            {section.status === 'writing'
              ? `${section.chars_written} chars...`
              : section.status
            }
          </span>
        </div>
      ))}
    </div>
  );
};
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Hardcoding Workflow Logic in API Routes

**What:** Embedding workflow steps directly in FastAPI route handlers.

```python
# BAD: Workflow logic in route
@router.post("/phases/{phase}/write")
async def write_phase(phase: int):
    # Find plans
    plans = glob(f".planning/phases/{phase:02d}-*/*-PLAN.md")
    # Group by wave
    waves = {}
    for plan in plans:
        wave = parse_frontmatter(plan)["wave"]
        waves.setdefault(wave, []).append(plan)
    # Execute waves
    for wave_num, wave_plans in waves.items():
        # ... spawn tasks
    # This is fragile and doesn't follow v1.0 workflow definitions
```

**Why bad:** Duplicates workflow logic from .md files. Changes to workflows require code edits, not .md edits. Violates SSOT principle.

**Instead:** Route handlers trigger WorkflowEngine, which reads .md and executes steps.

```python
# GOOD: Workflow engine reads .md
@router.post("/phases/{phase}/write")
async def write_phase(phase: int, session_id: str):
    engine = WorkflowEngine.load("write-phase.md")
    await engine.execute(context={"phase": phase, "session_id": session_id})
```

---

### Anti-Pattern 2: Tight Coupling to Claude API

**What:** Calling Anthropic SDK directly throughout codebase.

```python
# BAD: Direct Claude calls everywhere
from anthropic import AsyncAnthropic

async def write_section(plan):
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = await client.messages.create(
        model="claude-opus-4-6",
        messages=[...]
    )
    return response.content[0].text
```

**Why bad:** Cannot swap LLM providers without rewriting all LLM calls. Vendor lock-in.

**Instead:** Use LLMProvider abstraction.

```python
# GOOD: Provider-agnostic
async def write_section(plan):
    llm = get_llm_provider()  # Returns ClaudeProvider or LocalProvider
    response = await llm.complete(messages=[...])
    return response.content
```

---

### Anti-Pattern 3: Storing Generated Content in Database

**What:** Saving CONTENT.md, SUMMARY.md in SQLite/Postgres BLOBs.

**Why bad:**
- Breaks CLI compatibility (CLI expects .md files on disk)
- Loses human-readable git-trackable project structure
- Complicates debugging (can't inspect files directly)

**Instead:** Store files on disk exactly as v1.0 does. SQLite stores only METADATA (project ID, file path, upload time).

---

### Anti-Pattern 4: Frontend Calling LLM APIs Directly

**What:** React components making direct API calls to Anthropic.

**Why bad:**
- Exposes API keys in browser
- No orchestration control (can't checkpoint, resume)
- Can't implement wave-based parallelization

**Instead:** Frontend calls FastAPI endpoints. Backend orchestrates LLM calls.

---

## Scalability Considerations

| Concern | At 1 Engineer | At 5 Engineers | At 20 Engineers |
|---------|---------------|----------------|-----------------|
| **Concurrent Projects** | Single VM handles easily | Same VM, separate project dirs | Consider load balancer + multiple VM instances |
| **WebSocket Connections** | Direct connection to FastAPI | Redis pub/sub for multi-instance | Dedicated WebSocket gateway (e.g., Socket.IO cluster) |
| **Background Tasks** | ARQ worker on same VM | Dedicated worker VM with Redis | Worker pool with autoscaling |
| **File Storage** | Local disk (/opt/gsd-docs-data) | NFS mount for shared access | Object storage (S3-compatible, MinIO) |
| **LLM API Rate Limits** | Anthropic tier sufficient | Monitor usage, upgrade tier | Queue requests, implement retry + backoff |
| **Database** | SQLite on disk | Migrate to PostgreSQL for concurrent writes | PostgreSQL with connection pooling |

---

## Build Order (Dependency-Aware)

### Phase 1: Foundation (Week 1)

**Backend:**
1. FastAPI skeleton (main.py, config, CORS)
2. SQLite setup (database.py, models)
3. File storage structure (/opt/gsd-docs-data/)
4. Basic project CRUD API (/api/projects)

**Frontend:**
1. React + Vite setup
2. Routing (React Router)
3. Zustand stores (projectStore)
4. Project list page (Home.tsx)

**Integration:**
- Frontend can create/list projects
- Backend writes PROJECT.md, ROADMAP.md to disk

---

### Phase 2: Workflow Engine Core (Week 2)

**Backend:**
1. WorkflowEngine (load .md, parse steps)
2. State Manager (STATE.md read/write, checkpoint)
3. Domain Knowledge Loader (templates, standards)
4. LLM Provider abstraction + ClaudeProvider

**Testing:**
- Implement /doc:new-fds workflow in Python
- Verify PROJECT.md, ROADMAP.md generation matches v1.0

---

### Phase 3: Discussion + Planning Workflows (Week 3)

**Backend:**
1. /api/phases/{phase}/discuss endpoint
2. discuss-phase.md workflow implementation
3. /api/phases/{phase}/plan endpoint
4. plan-phase.md workflow implementation

**Frontend:**
1. PhaseTimeline component
2. ChatPanel component (WebSocket connection)
3. PhaseDiscuss page

**Integration:**
- Engineer can discuss phase, see questions in chat
- Engineer answers, backend generates CONTEXT.md
- Engineer plans phase, backend generates PLAN.md files

---

### Phase 4: Writing Workflow + Real-Time (Week 4)

**Backend:**
1. ARQ + Redis setup
2. Background task queue (write_tasks.py)
3. /api/phases/{phase}/write endpoint
4. write-phase.md workflow (wave-based parallel)
5. WebSocket broadcasting (progress updates)

**Frontend:**
1. ProgressIndicator component
2. DocumentOutline component
3. MarkdownPreview component

**Integration:**
- Engineer clicks "Write Phase 3"
- Backend spawns parallel writers per wave
- Frontend shows real-time progress
- Engineer sees CONTENT.md in preview panel

---

### Phase 5: Verification + Review (Week 5)

**Backend:**
1. /api/phases/{phase}/verify endpoint
2. verify-phase.md workflow (goal-backward checks)
3. /api/phases/{phase}/review endpoint
4. review-phase.md workflow

**Frontend:**
1. PhaseVerify page (gap display, fix trigger)
2. Review UI (client feedback capture)

**Integration:**
- Engineer verifies phase, sees gaps
- Engineer triggers gap closure (re-plan, re-write)
- Engineer reviews with client, logs feedback

---

### Phase 6: FDS Assembly + Export (Week 6)

**Backend:**
1. /api/export/fds endpoint
2. complete-fds.md workflow (cross-ref resolution)
3. /api/export/docx endpoint
4. Pandoc subprocess integration
5. Mermaid CLI integration (mmdc)

**Frontend:**
1. Export page (format options, download)

**Integration:**
- Engineer completes all phases
- Backend assembles FDS.md
- Engineer exports DOCX with diagrams

---

### Phase 7: Reference Library + SDS (Week 7)

**Backend:**
1. /api/files/upload endpoint
2. Reference library API
3. /api/export/sds endpoint
4. generate-sds.md workflow (typicals matching)

**Frontend:**
1. ReferenceLibrary component
2. File upload UI

**Integration:**
- Engineer uploads client standards
- Backend makes them available to workflows
- Engineer generates SDS from FDS

---

### Phase 8: VM Deployment + Production Hardening (Week 8)

**Infrastructure:**
1. Nginx reverse proxy config
2. systemd service files (FastAPI, ARQ worker)
3. Redis setup
4. SSL certificate (Let's Encrypt)
5. Backup scripts (project files, SQLite)

**Testing:**
- Full end-to-end workflow (new-fds → export)
- Multi-user concurrent access
- Crash recovery (STATE.md resume)

---

## Deployment Architecture (VM, No Docker)

### System Services

```ini
# /etc/systemd/system/gsd-docs-api.service

[Unit]
Description=GSD-Docs FastAPI Backend
After=network.target

[Service]
Type=notify
User=gsd-docs
Group=gsd-docs
WorkingDirectory=/opt/gsd-docs-backend
Environment="PATH=/opt/gsd-docs-backend/venv/bin"
ExecStart=/opt/gsd-docs-backend/venv/bin/uvicorn main:app \
  --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/gsd-docs-worker.service

[Unit]
Description=GSD-Docs ARQ Background Worker
After=network.target redis.service

[Service]
Type=simple
User=gsd-docs
Group=gsd-docs
WorkingDirectory=/opt/gsd-docs-backend
Environment="PATH=/opt/gsd-docs-backend/venv/bin"
ExecStart=/opt/gsd-docs-backend/venv/bin/arq tasks.WorkerSettings
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/gsd-docs

upstream fastapi_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name docs.company.local;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name docs.company.local;

    ssl_certificate /etc/letsencrypt/live/docs.company.local/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docs.company.local/privkey.pem;

    # React frontend (static files)
    root /opt/gsd-docs-frontend/dist;
    index index.html;

    # API requests to FastAPI
    location /api/ {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket connections
    location /ws/ {
        proxy_pass http://fastapi_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;  # 24h for long-running operations
    }

    # React routing (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## Sources

### Architecture Patterns
- [Elevating LLM Deployment with FastAPI and React: A Step-By-Step Guide](https://medium.com/@georgewen7/elevating-llm-deployment-with-fastapi-and-react-a-step-by-step-guide-885d8f08f4f1)
- [Architecting Scalable FastAPI Systems for Large Language Model (LLM) Applications](https://medium.com/@moradikor296/architecting-scalable-fastapi-systems-for-large-language-model-llm-applications-and-external-cf72f76ad849)
- [How to build production-ready AI agents with RAG and FastAPI](https://thenewstack.io/how-to-build-production-ready-ai-agents-with-rag-and-fastapi/)
- [Building LLM apps with FastAPI — best practices](https://agentsarcade.com/blog/building-llm-apps-with-fastapi-best-practices)

### WebSocket Real-Time Communication
- [WebSockets - FastAPI](https://fastapi.tiangolo.com/advanced/websockets/)
- [How to Implement WebSockets in FastAPI](https://oneuptime.com/blog/post/2026-02-02-fastapi-websockets/view)
- [FastAPI + WebSockets + React: Real-Time Features for Your Modern Apps](https://medium.com/@suganthi2496/fastapi-websockets-react-real-time-features-for-your-modern-apps-b8042a10fd90)
- [Real-Time Features in FastAPI: WebSockets, Event Streaming, and Push Notifications](https://python.plainenglish.io/real-time-features-in-fastapi-websockets-event-streaming-and-push-notifications-fec79a0a6812)

### LLM Provider Abstraction
- [Implementing an LLM Agnostic Architecture](https://www.entrio.io/blog/implementing-llm-agnostic-architecture-generative-ai-module)
- [LLM & AI Agent Applications with LangChain and LangGraph — Part 29: Model Agnostic Pattern and LLM API Gateway](https://towardsai.net/p/machine-learning/llm-ai-agent-applications-with-langchain-and-langgraph-part-29-model-agnostic-pattern-and-llm-api-gateway)
- [Introducing Any-Agent: An abstraction layer between your code and the many agentic frameworks](https://blog.mozilla.ai/introducing-any-agent-an-abstraction-layer-between-your-code-and-the-many-agentic-frameworks/)

### React State Management
- [18 Best React State Management Libraries in 2026](https://fe-tool.com/awesome-react-state-management)
- [Top 5 React State Management Tools Developers Actually Use in 2026 and Why](https://www.syncfusion.com/blogs/post/react-state-management-libraries)
- [React State Management in 2025: What You Actually Need](https://www.developerway.com/posts/react-state-management-2025)
- [Editor State Management | docmost/docmost](https://deepwiki.com/docmost/docmost/3.4-editor-state-management)

### FastAPI File Upload
- [How to Implement File Uploads in FastAPI](https://oneuptime.com/blog/post/2026-01-26-fastapi-file-uploads/view)
- [Uploading Files Using FastAPI: A Complete Guide to Secure File Handling](https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/)
- [Static File & Upload Management | fastapi-practices/fastapi_best_architecture](https://deepwiki.com/fastapi-practices/fastapi_best_architecture/11.5-static-file-and-upload-management)

### Background Tasks
- [How to Implement Background Tasks in FastAPI](https://oneuptime.com/blog/post/2026-02-02-fastapi-background-tasks/view)
- [Managing Background Tasks in FastAPI: BackgroundTasks vs ARQ + Redis](https://davidmuraya.com/blog/fastapi-background-tasks-arq-vs-built-in/)
- [How I Handled 100K Daily Jobs in FastAPI Using Task Queues and Async Retries](https://medium.com/@connect.hashblock/how-i-handled-100k-daily-jobs-in-fastapi-using-task-queues-and-async-retries-62bbcdd8240d)

### React Markdown Rendering
- [react-markdown - npm](https://www.npmjs.com/package/react-markdown)
- [How to render and edit Markdown in React with react-markdown](https://www.contentful.com/blog/react-markdown/)
- [Creating Polished Content with React Markdown](https://refine.dev/blog/react-markdown/)
- [5 Best Markdown Editors for React Compared](https://strapi.io/blog/top-5-markdown-editors-for-react)
