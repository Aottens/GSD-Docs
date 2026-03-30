# Phase 8: Core Infrastructure & Project Management - Research

**Researched:** 2026-02-15
**Domain:** Full-stack web application (FastAPI + React)
**Confidence:** HIGH

## Summary

Phase 8 establishes the foundational architecture for GSD-Docs v2.0 GUI, implementing a modern web application with FastAPI backend and React frontend. The stack is well-proven for production use: FastAPI provides async-first Python API development with excellent type safety and developer experience, while React + Vite + Tailwind CSS + shadcn/ui delivers a modern, performant frontend with minimal configuration overhead.

The research confirms that all locked design decisions (card-based dashboard, 3-step wizard, three-panel layout, Tailwind + shadcn/ui styling) align with current 2026 best practices. Critical technical choices include using TanStack Query for server state management, react-resizable-panels for the three-panel layout, LiteLLM for LLM provider abstraction, and SQLAlchemy 2.0+ with aiosqlite for async database operations.

Key architectural patterns emphasize domain-based code organization (not file-type grouping), dependency injection for database sessions and configuration, CSS variables for theming flexibility, and proper separation of server state (TanStack Query) from client state (Zustand or Context).

**Primary recommendation:** Follow the domain-based FastAPI structure with async-first design throughout. Use shadcn/ui's resizable components for the three-panel layout, implement LiteLLM for provider abstraction, configure Vite proxy for development, and ensure proper CORS setup for production deployment.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Dashboard & project browsing:**
- Card grid layout (not table) — each card shows project name, type badge (A/B/C/D), language, current phase, progress bar, and last modified date
- Filter tabs for status slicing: Active, Completed, All
- Search bar with sort dropdown (by date, name, type) within each tab
- Recent projects section at top showing 3-4 most recently accessed projects

**Project creation flow:**
- 3-step wizard:
  - Step 1: Project name + description
  - Step 2: Type classification (A/B/C/D) presented as visual selectable cards with title, short description, and example use case per type
  - Step 3: Language selection (Dutch/English) + confirm
- After wizard completes, engineer lands directly in the project working view

**Project working view:**
- Three-panel layout: left sidebar (navigation) + center (main content) + right panel (context/chat)
- Right panel is always visible — chat and context always accessible alongside main content
- When a project is first opened, center panel shows a project overview: summary card with project name, type, language, progress, and quick actions
- Left sidebar contents: Claude's discretion based on what makes sense for the workflow

**Visual identity & design:**
- Modern & polished aesthetic — Vercel/Stripe-style with bold typography, smooth animations, dark accents
- Both light and dark mode with toggle
- Brandable design system — neutral base with a theming system so company can plug in their colors/logo later
- Tailwind CSS + shadcn/ui for styling and components

### Claude's Discretion

- Left sidebar navigation structure and contents
- Exact card layout dimensions and spacing
- Animation details and transitions
- Loading states and skeleton designs
- Error state handling and messaging
- Backend architecture details (FastAPI structure, SQLite schema, LLM abstraction layer)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope

</user_constraints>

---

## Standard Stack

### Frontend Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React | 18.x | UI framework | Industry standard for component-based UIs, excellent ecosystem |
| Vite | 5.x | Build tool | Fast HMR, modern defaults, superior DX compared to Create React App |
| TypeScript | 5.x | Type safety | Essential for large React applications, catches errors at compile time |
| React Router | 6.x | Client routing | Official routing solution with nested routes and layout support |
| TanStack Query | 5.x | Server state | De facto standard for API data fetching, caching, and synchronization |
| Zustand | 4.x | Client state | Minimal boilerplate, 1.2KB bundle, perfect for global UI state |

### Frontend UI & Styling

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Tailwind CSS | 4.x | Utility CSS | Industry standard, excellent DX, built-in dark mode support |
| shadcn/ui | Latest | Component library | Copy-paste components built on Radix UI, full code ownership |
| react-resizable-panels | Latest | Panel layouts | By Brian Vaughn (React core team), accessible, production-ready |
| React Hook Form | 7.x | Form management | Minimal re-renders, excellent validation, best-in-class performance |
| Motion | Latest | Animations | Modern rebrand of Framer Motion, 30.7k stars, most popular React animation library |

### Backend Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.115+ | API framework | Modern async Python, automatic OpenAPI docs, excellent type safety |
| SQLAlchemy | 2.0+ | ORM | Industry standard Python ORM with comprehensive async support |
| aiosqlite | Latest | Async SQLite | Official async SQLite driver for Python |
| Alembic | 1.13+ | DB migrations | Standard migration tool for SQLAlchemy |
| Pydantic | 2.x | Validation | Built into FastAPI, excellent type safety and validation |
| pydantic-settings | Latest | Config management | Official settings management with env var support |

### LLM & Integration

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| LiteLLM | Latest | LLM abstraction | Unified interface for 100+ LLM providers, OpenAI-compatible API |
| httpx | Latest | HTTP client | Async-first HTTP client for Python, recommended by FastAPI |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| react-loading-skeleton | Latest | Loading states | Automatic sizing, matches content structure |
| Zod | Latest | Schema validation | Alternative to Pydantic for React Hook Form integration |
| python-multipart | Latest | File uploads | Required for FastAPI file upload handling |
| python-dotenv | Latest | Environment vars | Load .env files in development |

### Development Tools

| Tool | Purpose |
|------|---------|
| ESLint + Prettier | Code quality and formatting |
| pytest | Python testing |
| Vitest | React component testing |
| uvicorn | ASGI server for FastAPI development |

### Installation

**Frontend:**
```bash
# Create Vite + React + TypeScript project
npm create vite@latest frontend -- --template react-ts

cd frontend

# Install core dependencies
npm install react-router-dom @tanstack/react-query zustand react-hook-form

# Install UI dependencies
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install shadcn/ui (interactive CLI)
npx shadcn@latest init

# Add specific shadcn components
npx shadcn@latest add button card input label tabs resizable skeleton

# Install additional UI libraries
npm install react-resizable-panels motion react-loading-skeleton

# Install dev dependencies
npm install -D @types/node
```

**Backend:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install core dependencies
pip install fastapi[all] uvicorn[standard]
pip install sqlalchemy aiosqlite alembic
pip install pydantic pydantic-settings
pip install litellm httpx
pip install python-multipart python-dotenv

# Install dev dependencies
pip install pytest pytest-asyncio httpx black ruff
```

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Vite | Next.js | Next.js adds SSR complexity; Vite is simpler for SPA with separate backend |
| TanStack Query | SWR | SWR is lighter but less feature-rich; TanStack Query is more comprehensive |
| Zustand | Redux Toolkit | Redux has more boilerplate; Zustand is simpler for this use case |
| FastAPI | Flask, Django | FastAPI offers superior async support and automatic API docs |
| LiteLLM | LangChain | LangChain is heavier; LiteLLM focuses solely on provider abstraction |
| SQLite | PostgreSQL | PostgreSQL is overkill for 5-20 users; SQLite is sufficient and simpler |

---

## Architecture Patterns

### Recommended Project Structure

**Frontend:**
```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── ui/           # shadcn/ui components (auto-generated)
│   │   ├── layout/       # Layout components (Header, Sidebar, etc.)
│   │   └── common/       # Shared components (LoadingSkeleton, ErrorBoundary)
│   ├── features/         # Feature-based modules
│   │   ├── dashboard/    # Dashboard feature
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── queries.ts
│   │   │   └── types.ts
│   │   ├── projects/     # Project management feature
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── queries.ts
│   │   │   └── types.ts
│   │   └── wizard/       # Project creation wizard
│   ├── lib/              # Utility libraries and configs
│   │   ├── api.ts        # API client setup
│   │   ├── queryClient.ts # TanStack Query config
│   │   └── utils.ts      # Helper functions
│   ├── stores/           # Zustand stores for client state
│   │   ├── themeStore.ts
│   │   └── uiStore.ts
│   ├── hooks/            # Shared custom hooks
│   ├── types/            # TypeScript type definitions
│   ├── App.tsx           # Root component with providers
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles + Tailwind imports
├── public/               # Static assets
├── .env.development      # Development environment variables
├── .env.production       # Production environment variables
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind configuration
└── components.json       # shadcn/ui configuration
```

**Backend:**
```
backend/
├── app/
│   ├── main.py           # FastAPI app initialization
│   ├── config.py         # Global configuration (BaseSettings)
│   ├── database.py       # Database engine and session factory
│   ├── api/              # API routes organized by domain
│   │   ├── __init__.py
│   │   ├── projects.py   # Project CRUD endpoints
│   │   ├── dashboard.py  # Dashboard endpoints
│   │   └── health.py     # Health check endpoint
│   ├── models/           # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── project.py
│   │   └── base.py
│   ├── schemas/          # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── project.py
│   │   └── dashboard.py
│   ├── services/         # Business logic
│   │   ├── __init__.py
│   │   ├── project_service.py
│   │   └── llm_service.py
│   ├── llm/              # LLM abstraction layer
│   │   ├── __init__.py
│   │   ├── provider.py   # Abstract LLM provider interface
│   │   └── litellm_provider.py # LiteLLM implementation
│   └── dependencies.py   # FastAPI dependency injection
├── alembic/              # Database migrations
│   ├── versions/
│   └── env.py
├── tests/
│   ├── test_api/
│   └── test_services/
├── .env                  # Environment variables (not committed)
├── .env.example          # Example environment variables
├── alembic.ini           # Alembic configuration
└── requirements.txt      # Python dependencies
```

### Pattern 1: Domain-Based FastAPI Organization

**What:** Organize code by business domain (projects, dashboard) rather than file type (all models together, all routes together).

**When to use:** Always for FastAPI applications that will grow beyond a few endpoints.

**Example:**
```python
# app/api/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    service = ProjectService(db)
    return await service.create_project(project)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ProjectService(db)
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

### Pattern 2: Async Database Session with Dependency Injection

**What:** Use FastAPI's dependency injection to provide database sessions per request with automatic cleanup.

**When to use:** All database operations.

**Example:**
```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./gsd_docs.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# app/dependencies.py
from app.database import AsyncSessionLocal

async def get_db():
    """Dependency that provides database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Pattern 3: LLM Provider Abstraction

**What:** Abstract LLM providers behind a unified interface to enable future provider swapping.

**When to use:** All LLM interactions.

**Example:**
```python
# app/llm/provider.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate completion from messages."""
        pass

    @abstractmethod
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ):
        """Stream completion from messages."""
        pass

# app/llm/litellm_provider.py
from litellm import acompletion
from app.llm.provider import LLMProvider

class LiteLLMProvider(LLMProvider):
    """LiteLLM implementation supporting multiple providers."""

    def __init__(self, model: str):
        self.model = model

    async def complete(self, messages, **kwargs):
        response = await acompletion(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

    async def stream_complete(self, messages, **kwargs):
        response = await acompletion(
            model=self.model,
            messages=messages,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

# app/services/llm_service.py
from app.llm.litellm_provider import LiteLLMProvider
from app.config import settings

def get_llm_provider() -> LLMProvider:
    """Factory function to get configured LLM provider."""
    return LiteLLMProvider(model=settings.LLM_MODEL)
```

### Pattern 4: TanStack Query for Server State

**What:** Use TanStack Query hooks for all API data fetching, caching, and synchronization.

**When to use:** Any data from the backend API.

**Example:**
```typescript
// src/features/projects/queries.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { Project, ProjectCreate } from './types';

export const useProjects = () => {
  return useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await api.get<Project[]>('/api/projects');
      return response.data;
    },
  });
};

export const useProject = (id: number) => {
  return useQuery({
    queryKey: ['projects', id],
    queryFn: async () => {
      const response = await api.get<Project>(`/api/projects/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (project: ProjectCreate) => {
      const response = await api.post<Project>('/api/projects', project);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate projects list to trigger refetch
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
};

// src/features/projects/components/ProjectList.tsx
import { useProjects } from '../queries';

export function ProjectList() {
  const { data: projects, isLoading, error } = useProjects();

  if (isLoading) return <ProjectListSkeleton />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {projects?.map(project => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  );
}
```

### Pattern 5: Multi-Step Form Wizard with React Hook Form

**What:** Use React Hook Form with step-based state management for the project creation wizard.

**When to use:** Multi-step forms with validation.

**Example:**
```typescript
// src/features/wizard/components/ProjectWizard.tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useCreateProject } from '@/features/projects/queries';

type WizardStep = 1 | 2 | 3;

interface WizardFormData {
  name: string;
  description: string;
  type: 'A' | 'B' | 'C' | 'D';
  language: 'nl' | 'en';
}

export function ProjectWizard() {
  const [step, setStep] = useState<WizardStep>(1);
  const navigate = useNavigate();
  const createProject = useCreateProject();

  const { register, handleSubmit, watch, formState: { errors } } = useForm<WizardFormData>();

  const onSubmit = async (data: WizardFormData) => {
    const project = await createProject.mutateAsync(data);
    navigate(`/projects/${project.id}`);
  };

  const nextStep = () => setStep((prev) => Math.min(prev + 1, 3) as WizardStep);
  const prevStep = () => setStep((prev) => Math.max(prev - 1, 1) as WizardStep);

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {step === 1 && (
        <Step1_NameDescription register={register} errors={errors} />
      )}
      {step === 2 && (
        <Step2_TypeClassification register={register} errors={errors} />
      )}
      {step === 3 && (
        <Step3_Language register={register} errors={errors} />
      )}

      <div className="flex justify-between mt-6">
        {step > 1 && <Button onClick={prevStep}>Back</Button>}
        {step < 3 ? (
          <Button onClick={nextStep}>Next</Button>
        ) : (
          <Button type="submit" disabled={createProject.isPending}>
            Create Project
          </Button>
        )}
      </div>
    </form>
  );
}
```

### Pattern 6: Three-Panel Layout with react-resizable-panels

**What:** Use shadcn/ui's Resizable components for the three-panel working view.

**When to use:** Project working view layout.

**Example:**
```typescript
// src/features/projects/components/ProjectWorkspace.tsx
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from '@/components/ui/resizable';

export function ProjectWorkspace({ projectId }: { projectId: number }) {
  return (
    <ResizablePanelGroup direction="horizontal" className="h-screen">
      {/* Left Sidebar */}
      <ResizablePanel defaultSize={20} minSize={15} maxSize={30}>
        <ProjectNavigation projectId={projectId} />
      </ResizablePanel>

      <ResizableHandle withHandle />

      {/* Center Content */}
      <ResizablePanel defaultSize={55} minSize={40}>
        <ProjectContent projectId={projectId} />
      </ResizablePanel>

      <ResizableHandle withHandle />

      {/* Right Panel (Chat/Context) - Always Visible */}
      <ResizablePanel defaultSize={25} minSize={20} maxSize={40}>
        <ChatContextPanel projectId={projectId} />
      </ResizablePanel>
    </ResizablePanelGroup>
  );
}
```

### Pattern 7: Dark Mode with Tailwind CSS Variables

**What:** Use Tailwind's class-based dark mode with CSS variables for theming.

**When to use:** All styling that needs dark mode support.

**Example:**
```css
/* src/index.css */
@import "tailwindcss";

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    /* ... other variables */
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    /* ... other variables */
  }
}
```

```typescript
// src/stores/themeStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeStore {
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      theme: 'system',
      setTheme: (theme) => {
        set({ theme });

        const root = document.documentElement;
        root.classList.remove('light', 'dark');

        if (theme === 'system') {
          const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light';
          root.classList.add(systemTheme);
        } else {
          root.classList.add(theme);
        }
      },
    }),
    { name: 'theme-storage' }
  )
);
```

### Pattern 8: Configuration Management with Pydantic Settings

**What:** Use Pydantic BaseSettings for type-safe environment variable configuration.

**When to use:** All application configuration.

**Example:**
```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Application
    APP_NAME: str = "GSD-Docs Industrial"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./gsd_docs.db"

    # LLM
    LLM_PROVIDER: str = "anthropic"  # or "openai"
    LLM_MODEL: str = "anthropic/claude-opus-4-20250514"
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str | None = None

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

@lru_cache
def get_settings() -> Settings:
    """Cached settings instance (loaded once per app lifecycle)."""
    return Settings()

# Usage in endpoints
from fastapi import Depends
from app.config import get_settings, Settings

@router.get("/config")
def get_config(settings: Settings = Depends(get_settings)):
    return {"app_name": settings.APP_NAME, "debug": settings.DEBUG}
```

### Pattern 9: CORS Configuration for Development and Production

**What:** Configure CORS middleware to allow frontend access from different origins.

**When to use:** Always when frontend and backend are on different ports/domains.

**Example:**
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# CORS must be added FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Then register routers
from app.api import projects, dashboard, health

app.include_router(projects.router)
app.include_router(dashboard.router)
app.include_router(health.router)
```

### Pattern 10: Vite Development Proxy

**What:** Use Vite's proxy to forward API requests to FastAPI during development.

**When to use:** Development environment (avoids CORS issues).

**Example:**
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### Anti-Patterns to Avoid

- **Mixing sync and async in FastAPI routes:** Use `async def` consistently and await all database operations
- **Global database sessions:** Always use dependency injection for per-request sessions
- **Storing secrets in code:** Use environment variables via Pydantic Settings
- **Using Context for server state:** Use TanStack Query; Context is for UI state only
- **Hardcoding API URLs:** Use environment variables (VITE_API_URL) and Vite proxy
- **Manual theme management:** Use CSS variables and Tailwind's built-in dark mode
- **Hand-rolling form state:** Use React Hook Form for complex forms
- **Creating custom panel resizing:** Use react-resizable-panels (battle-tested, accessible)
- **Blocking operations in async routes:** Offload CPU-bound tasks to thread pools or Celery

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Form state management | Custom useState form handlers | React Hook Form | Handles validation, errors, dirty state, touched fields - complex state machine |
| API data caching | Custom fetch wrappers with useState | TanStack Query | Background refetching, cache invalidation, optimistic updates, retry logic |
| Panel resizing | Custom drag handlers | react-resizable-panels | Keyboard accessibility, touch support, nested panels, edge cases |
| Dark mode toggle | Custom CSS class management | Tailwind dark mode + CSS variables | System preference detection, persistent storage, SSR considerations |
| Component library | Custom styled components | shadcn/ui | Accessibility (ARIA), keyboard navigation, focus management |
| LLM provider switching | Custom provider wrappers | LiteLLM | Handles 100+ providers, streaming, error handling, retries |
| Database migrations | Manual SQL scripts | Alembic | Tracks versions, rollback support, team synchronization |
| Loading skeletons | Custom placeholder divs | react-loading-skeleton | Auto-sizing, theme integration, shimmer animations |
| Multi-step wizards | Custom step state logic | React Hook Form + step state | Form persistence across steps, validation per step, back/forward logic |

**Key insight:** Modern web development has mature solutions for common UI/UX patterns. Custom implementations miss edge cases (keyboard nav, screen readers, mobile touch, browser inconsistencies) that take years to handle properly. Use battle-tested libraries unless there's a specific limitation.

---

## Common Pitfalls

### Pitfall 1: Mixing Sync and Async in FastAPI Routes

**What goes wrong:** Using synchronous database operations in `async def` route handlers blocks the event loop, preventing FastAPI from handling other requests.

**Why it happens:** SQLAlchemy's default Session is synchronous; developers forget to use AsyncSession and await operations.

**How to avoid:**
- Always use `AsyncSession` from SQLAlchemy
- Always `await` database operations
- Use `async def` for all route handlers that touch I/O
- Configure database engine with `create_async_engine`

**Warning signs:**
- Application becomes unresponsive under load
- Concurrent requests processed sequentially instead of in parallel
- High latency on simple database queries

**Example:**
```python
# BAD - blocks event loop
@router.get("/projects")
async def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()  # Synchronous - blocks!
    return projects

# GOOD - async throughout
@router.get("/projects")
async def get_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project))  # Async - non-blocking
    projects = result.scalars().all()
    return projects
```

### Pitfall 2: SQLite check_same_thread Configuration

**What goes wrong:** SQLite raises "SQLite objects created in a thread can only be used in that same thread" errors with FastAPI.

**Why it happens:** SQLite's default thread-safety check conflicts with FastAPI's async request handling across multiple threads.

**How to avoid:**
- Add `connect_args={"check_same_thread": False}` to SQLAlchemy engine
- This is safe with FastAPI's request-scoped sessions
- Only applies to SQLite (not PostgreSQL)

**Warning signs:**
- Random "same thread" errors under concurrent load
- Errors that don't reproduce in single-request testing

**Example:**
```python
# Required for SQLite with FastAPI
engine = create_async_engine(
    "sqlite+aiosqlite:///./app.db",
    connect_args={"check_same_thread": False}  # Critical for SQLite
)
```

### Pitfall 3: TanStack Query Cache Invalidation

**What goes wrong:** After creating/updating data, the UI doesn't reflect changes because cached queries aren't invalidated.

**Why it happens:** TanStack Query caches responses aggressively; mutations must explicitly invalidate related queries.

**How to avoid:**
- Use `queryClient.invalidateQueries()` in mutation `onSuccess` callbacks
- Invalidate by query key (e.g., `['projects']` invalidates all project queries)
- Use optimistic updates for instant UI feedback

**Warning signs:**
- Creating a project doesn't add it to the list
- Updates require manual page refresh to appear
- Stale data shown after mutations

**Example:**
```typescript
// BAD - no invalidation
const createProject = useMutation({
  mutationFn: (data) => api.post('/projects', data),
});

// GOOD - invalidates cache
const createProject = useMutation({
  mutationFn: (data) => api.post('/projects', data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['projects'] });
  },
});
```

### Pitfall 4: Vite Environment Variables Not Prefixed

**What goes wrong:** Environment variables don't appear in `import.meta.env` despite being defined in `.env`.

**Why it happens:** Vite only exposes variables prefixed with `VITE_` to prevent accidental secret leakage to the client.

**How to avoid:**
- Prefix all client-side env vars with `VITE_` (e.g., `VITE_API_URL`)
- Use unprefixed vars only in `vite.config.ts` (server-side)
- Document this clearly for team members

**Warning signs:**
- `import.meta.env.API_URL` is undefined
- Environment variables work in build but not in dev

**Example:**
```bash
# .env
VITE_API_URL=http://localhost:8000  # ✓ Exposed to client
API_SECRET=xyz123                   # ✗ Not exposed (correct for secrets)
```

### Pitfall 5: Dark Mode Theme Flashing (FOUC)

**What goes wrong:** Page loads in light mode then flashes to dark mode when theme is applied.

**Why it happens:** Theme is applied after JavaScript loads, causing a flash of unstyled content (FOUC).

**How to avoid:**
- Add inline script in `index.html` before React loads
- Read theme from localStorage synchronously
- Apply class to `<html>` before first paint

**Warning signs:**
- Visible theme flash on page load
- User sees light mode briefly before switching to saved dark mode

**Example:**
```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <script>
    // Runs BEFORE React loads - prevents flash
    const theme = localStorage.getItem('theme-storage');
    if (theme) {
      const { state } = JSON.parse(theme);
      if (state.theme === 'dark' ||
          (state.theme === 'system' &&
           window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
      }
    }
  </script>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>
```

### Pitfall 6: React Hook Form Controlled vs Uncontrolled Inputs

**What goes wrong:** Input values don't update or form doesn't submit with correct data.

**Why it happens:** Mixing controlled (value prop) and uncontrolled (register) patterns in React Hook Form.

**How to avoid:**
- Use `{...register('fieldName')}` for native inputs (uncontrolled)
- Use `Controller` component for custom UI library components
- Don't mix `value` prop with `register` on the same input

**Warning signs:**
- Input shows stale values
- Form submits empty data despite visible input values
- Console warnings about controlled/uncontrolled components

**Example:**
```typescript
// BAD - mixing patterns
<Input
  value={watch('name')}
  {...register('name')}  // Conflict!
/>

// GOOD - uncontrolled
<Input {...register('name')} />

// GOOD - controlled (for shadcn/ui components)
<Controller
  name="type"
  control={control}
  render={({ field }) => (
    <Select onValueChange={field.onChange} value={field.value}>
      {/* ... */}
    </Select>
  )}
/>
```

### Pitfall 7: LiteLLM max_tokens for Anthropic

**What goes wrong:** Anthropic API calls fail with "max_tokens is required" error.

**Why it happens:** Anthropic requires `max_tokens` parameter; LiteLLM auto-fills it to 4096 if omitted, but this might not match your needs.

**How to avoid:**
- Always explicitly set `max_tokens` for Anthropic calls
- Be aware LiteLLM defaults to 4096 if you don't specify
- Different models have different max token limits

**Warning signs:**
- API calls fail with missing parameter errors
- Responses are cut off unexpectedly
- Billing doesn't match expectations

**Example:**
```python
# Explicit max_tokens
response = await completion(
    model="anthropic/claude-opus-4-20250514",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=2048  # Explicit is better
)
```

### Pitfall 8: Alembic Migration Conflicts in Teams

**What goes wrong:** Multiple developers create migrations simultaneously, causing version conflicts.

**Why it happens:** Alembic creates sequential migration versions; parallel branches create conflicts.

**How to avoid:**
- Coordinate migrations in team (one person at a time)
- Pull latest migrations before creating new ones
- Use Alembic's `merge` command to resolve conflicts
- Review migration files before committing

**Warning signs:**
- "Multiple head revisions" error
- Migrations fail to apply in CI/CD
- Database schema doesn't match models

**Example:**
```bash
# Check for conflicts before creating migration
alembic heads  # Should show only one head

# If multiple heads, merge them
alembic merge -m "merge migration branches" <head1> <head2>

# Always review generated migrations
cat alembic/versions/<timestamp>_<description>.py
```

### Pitfall 9: FastAPI Dependency Scope Confusion

**What goes wrong:** Database sessions or other resources are shared across requests, causing data leakage or race conditions.

**Why it happens:** Using global variables instead of dependency injection.

**How to avoid:**
- Always use `Depends()` for per-request resources
- Use `yield` in dependencies for cleanup (session.close())
- Avoid global state for request-specific data

**Warning signs:**
- Data from one request appears in another
- Database session errors about uncommitted transactions
- Memory leaks (connections not closed)

**Example:**
```python
# BAD - global session (shared across requests!)
db_session = AsyncSessionLocal()

@router.get("/projects")
async def get_projects():
    return await db_session.execute(select(Project))

# GOOD - dependency injection (per-request session)
@router.get("/projects")
async def get_projects(db: AsyncSession = Depends(get_db)):
    return await db.execute(select(Project))
```

### Pitfall 10: Resizable Panel Layout Shifts

**What goes wrong:** Panel layout shifts/jumps when navigating between pages or on initial load.

**Why it happens:** Not persisting panel sizes or not setting proper default sizes.

**How to avoid:**
- Set `defaultSize` on all panels (must sum to 100)
- Persist layout using `onLayout` callback + localStorage
- Set reasonable `minSize` and `maxSize` constraints

**Warning signs:**
- Layout resets on page refresh
- Panels jump to different sizes when navigating
- Panels disappear or become too small

**Example:**
```typescript
// Store layout in localStorage
const [layout, setLayout] = useState<number[]>([20, 55, 25]);

useEffect(() => {
  const saved = localStorage.getItem('panel-layout');
  if (saved) setLayout(JSON.parse(saved));
}, []);

<ResizablePanelGroup
  direction="horizontal"
  onLayout={(sizes) => {
    setLayout(sizes);
    localStorage.setItem('panel-layout', JSON.stringify(sizes));
  }}
>
  <ResizablePanel defaultSize={layout[0]} minSize={15} maxSize={30}>
    {/* Left sidebar */}
  </ResizablePanel>
  {/* ... */}
</ResizablePanelGroup>
```

---

## Code Examples

Verified patterns from official sources and research.

### FastAPI Application Initialization

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import engine, Base
from app.api import projects, dashboard, health

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown: close connections
    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS middleware (must be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(projects.router)
app.include_router(dashboard.router)
app.include_router(health.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

### SQLAlchemy Model Definition

```python
# app/models/project.py
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum

class ProjectType(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class Language(str, enum.Enum):
    DUTCH = "nl"
    ENGLISH = "en"

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    type = Column(SQLEnum(ProjectType), nullable=False)
    language = Column(SQLEnum(Language), nullable=False)
    status = Column(String, default="active", index=True)
    current_phase = Column(String, default="setup")
    progress = Column(Integer, default=0)  # 0-100

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, type={self.type})>"
```

### Pydantic Schemas

```python
# app/schemas/project.py
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.project import ProjectType, Language

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    type: ProjectType
    language: Language

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    current_phase: str | None = None
    progress: int | None = Field(None, ge=0, le=100)

class ProjectResponse(ProjectBase):
    id: int
    status: str
    current_phase: str
    progress: int
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
```

### Service Layer with Business Logic

```python
# app/services/project_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, project_data: ProjectCreate) -> Project:
        """Create a new project."""
        project = Project(**project_data.model_dump())
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_project(self, project_id: int) -> Project | None:
        """Get project by ID."""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def list_projects(
        self,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Project]:
        """List projects with optional filtering."""
        query = select(Project)
        if status:
            query = query.where(Project.status == status)
        query = query.offset(skip).limit(limit).order_by(Project.updated_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate
    ) -> Project | None:
        """Update project."""
        # Only update fields that are set
        update_data = project_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_project(project_id)

        await self.db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(**update_data)
        )
        await self.db.commit()

        return await self.get_project(project_id)

    async def delete_project(self, project_id: int) -> bool:
        """Delete project (soft delete by setting status)."""
        project = await self.get_project(project_id)
        if not project:
            return False

        await self.db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(status="deleted")
        )
        await self.db.commit()
        return True
```

### React App Setup with Providers

```typescript
// src/App.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import { useThemeStore } from '@/stores/themeStore';
import Dashboard from '@/features/dashboard/Dashboard';
import ProjectWizard from '@/features/wizard/ProjectWizard';
import ProjectWorkspace from '@/features/projects/ProjectWorkspace';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  const { theme, setTheme } = useThemeStore();

  // Initialize theme on app load
  useEffect(() => {
    setTheme(theme);
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects/new" element={<ProjectWizard />} />
          <Route path="/projects/:id" element={<ProjectWorkspace />} />
        </Routes>
      </BrowserRouter>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
```

### shadcn/ui Component Usage

```typescript
// src/features/dashboard/components/ProjectCard.tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import type { Project } from '../types';

interface ProjectCardProps {
  project: Project;
  onOpen: (id: number) => void;
}

export function ProjectCard({ project, onOpen }: ProjectCardProps) {
  const typeColors = {
    A: 'bg-blue-500',
    B: 'bg-green-500',
    C: 'bg-yellow-500',
    D: 'bg-red-500',
  };

  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => onOpen(project.id)}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-bold">{project.name}</CardTitle>
          <Badge className={typeColors[project.type]} variant="default">
            Type {project.type}
          </Badge>
        </div>
        <CardDescription className="line-clamp-2">
          {project.description || 'No description'}
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Language:</span>
            <Badge variant="outline">{project.language.toUpperCase()}</Badge>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Phase:</span>
            <span className="font-medium">{project.current_phase}</span>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress:</span>
              <span className="font-medium">{project.progress}%</span>
            </div>
            <Progress value={project.progress} className="h-2" />
          </div>

          <div className="text-xs text-muted-foreground">
            Last updated: {new Date(project.updated_at).toLocaleDateString()}
          </div>

          <Button className="w-full" onClick={(e) => {
            e.stopPropagation();
            onOpen(project.id);
          }}>
            Open Project
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

### Loading Skeleton Component

```typescript
// src/features/dashboard/components/ProjectListSkeleton.tsx
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';
import { Card, CardHeader, CardContent } from '@/components/ui/card';

export function ProjectListSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <Card key={i}>
          <CardHeader>
            <Skeleton height={24} width="70%" />
            <Skeleton height={16} width="90%" count={2} />
          </CardHeader>
          <CardContent>
            <Skeleton height={20} count={4} />
            <Skeleton height={40} />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Create React App | Vite | 2021-2022 | 10-100x faster HMR, simpler config, better DX |
| React Query | TanStack Query | 2023 (rebranding) | Same library, broader ecosystem (Vue, Svelte, Solid) |
| Framer Motion | Motion | 2026 | Rebranding only, same powerful library |
| Redux | Zustand/Jotai | 2020-2023 | 90% less boilerplate, smaller bundles |
| Styled Components | Tailwind CSS | 2019-2022 | Faster development, smaller bundles, better DX |
| Manual components | shadcn/ui | 2023-2024 | Pre-built accessible components with code ownership |
| Flask/Django | FastAPI | 2018-2023 | Async-first, automatic docs, better type safety |
| SQLAlchemy 1.x | SQLAlchemy 2.0 | 2023 | Full async support, better typing, modern API |
| Pydantic v1 | Pydantic v2 | 2023 | 5-50x faster validation, better error messages |
| LangChain for abstraction | LiteLLM | 2024-2025 | Lighter weight, focused on provider abstraction only |

**Deprecated/outdated:**
- **Create React App**: Officially deprecated, Vite is the modern replacement
- **Class components in React**: Hooks are the standard since React 16.8 (2019)
- **SQLAlchemy 1.x**: Still supported but 2.0 is the current standard
- **Pydantic v1**: v2 released June 2023, v1 maintenance mode only
- **Tailwind v2/v3**: v4 is current with improved theming and better performance
- **React Query (name)**: Now TanStack Query (same library, broader ecosystem)

---

## Open Questions

### 1. VM Deployment Configuration

**What we know:**
- Requirement: Deploy on VM with Nginx reverse proxy and systemd services (SYST-02)
- No Docker per company policy
- FastAPI runs via uvicorn ASGI server
- React builds to static files

**What's unclear:**
- Specific Nginx configuration for WebSocket support (needed for SSE/real-time features)
- systemd service configuration for auto-restart and logging
- Process manager (systemd vs. supervisord vs. gunicorn+uvicorn workers)
- SSL/TLS certificate management approach

**Recommendation:**
- Plan Phase 17 (deployment) should research Nginx + uvicorn configurations
- Use systemd for service management (simplest, built into Linux)
- Use uvicorn workers for production (multiple processes for concurrency)
- Document Nginx reverse proxy config with WebSocket upgrade headers

### 2. SQLite vs PostgreSQL for Production

**What we know:**
- Requirement specifies SQLite for 5-20 users (sufficient)
- SQLite with WAL mode supports concurrent reads
- User decision: SQLite for metadata only

**What's unclear:**
- Concurrent write performance under 20 users
- SQLite limitations for SSE/WebSocket real-time features
- Backup strategy for SQLite file
- Migration path to PostgreSQL if needed later

**Recommendation:**
- Start with SQLite as specified (simpler deployment)
- Use WAL mode for better concurrency: `?mode=wal` in connection string
- Design schema with PostgreSQL compatibility in mind (Alembic makes migration easy)
- Monitor write concurrency in testing; switch to PostgreSQL if issues arise

### 3. LLM Provider Configuration

**What we know:**
- Requirement: LLM provider abstracted (SYST-04)
- LiteLLM supports 100+ providers with unified interface
- User needs Anthropic and OpenAI support

**What's unclear:**
- Default provider selection strategy
- API key management for multiple providers
- Fallback behavior if primary provider fails
- Cost tracking across providers

**Recommendation:**
- Use environment variable `LLM_PROVIDER` to select default (anthropic/openai)
- Store API keys in .env (not committed to git)
- Implement simple retry logic in LLM service layer
- Defer cost tracking to Phase 17 or later (out of Phase 8 scope)

### 4. Real-Time Communication Strategy

**What we know:**
- Future phases need real-time updates (progress, chat)
- FastAPI supports WebSockets and SSE
- SSE is simpler than WebSockets for server-to-client streaming

**What's unclear:**
- Which approach to use (WebSockets vs SSE)
- Connection management for multiple clients
- How to integrate with TanStack Query on frontend

**Recommendation:**
- Use SSE for Phase 8 (simpler, unidirectional)
- Plan for WebSockets in Phase 10 (chat) if bidirectional needed
- Use EventSource API on frontend with TanStack Query integration
- Document pattern in Phase 10 research (discussion workflow)

### 5. File Storage Strategy

**What we know:**
- Future Phase 9 handles file uploads (references, documents)
- Requirement: Defense-in-depth security validation

**What's unclear:**
- File storage location (filesystem vs S3-compatible storage)
- File naming and organization strategy
- Virus scanning requirements
- Maximum file sizes per project

**Recommendation:**
- Defer to Phase 9 research
- Phase 8 should create `uploads/` directory structure in project filesystem
- Use filesystem storage for simplicity (S3 adds complexity for 5-20 users)
- Document upload directory in configuration (Settings class)

---

## Sources

### Primary (HIGH confidence)

#### Official Documentation
- [FastAPI Official Docs](https://fastapi.tiangolo.com/) - Framework reference
- [shadcn/ui Installation](https://ui.shadcn.com/docs/installation) - Component library setup
- [Tailwind CSS Dark Mode](https://tailwindcss.com/docs/dark-mode) - Dark mode configuration
- [Vite Environment Variables](https://vite.dev/guide/env-and-mode) - Env var handling
- [TanStack Query Overview](https://tanstack.com/query/latest/docs/framework/react/overview) - Server state management
- [React Router Routing](https://reactrouter.com/start/declarative/routing) - Client-side routing
- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/) - Configuration management
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/) - CORS middleware setup

#### GitHub Repositories
- [react-resizable-panels](https://github.com/bvaughn/react-resizable-panels) - Panel layout library
- [LiteLLM](https://github.com/BerriAI/litellm) - LLM provider abstraction
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices) - Production patterns

### Secondary (MEDIUM confidence)

#### Technical Articles & Guides
- [FastAPI Best Practices for Production 2026](https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026) - Production patterns
- [FastAPI Project Structure for Large Applications](https://medium.com/@devsumitg/the-perfect-structure-for-a-large-production-ready-fastapi-app-78c55271d15c) - Architecture guidance
- [How to Use Async Database Connections in FastAPI](https://oneuptime.com/blog/post/2026-02-02-fastapi-async-database/view) - Database setup
- [React Hook Form Advanced Usage](https://www.react-hook-form.com/advanced-usage/) - Form patterns
- [Implementing SSE with FastAPI](https://mahdijafaridev.medium.com/implementing-server-sent-events-sse-with-fastapi-real-time-updates-made-simple-6492f8bfc154) - Real-time patterns
- [React TypeScript Project Structure Best Practices](https://medium.com/@tusharupadhyay691/effective-react-typescript-project-structure-best-practices-for-scalability-and-maintainability-bcbcf0e09bd5) - Frontend architecture
- [shadcn/ui Theming](https://ui.shadcn.com/docs/theming) - CSS variable theming
- [Vite Proxy Configuration](https://medium.com/@eric_abell/simplifying-api-proxies-in-vite-a-guide-to-vite-config-js-a5cc3a091a2f) - Development setup

#### Library Comparisons
- [Zustand vs Jotai Comparison](https://betterstack.com/community/guides/scaling-nodejs/zustand-vs-redux-toolkit-vs-jotai/) - State management options
- [Top 5 React State Management Tools 2026](https://www.syncfusion.com/blogs/post/react-state-management-libraries) - Ecosystem overview
- [Beyond Eye Candy: Top 7 React Animation Libraries 2026](https://www.syncfusion.com/blogs/post/top-react-animation-libraries) - Animation options

### Tertiary (LOW confidence - marked for validation)

- WebSearch results on LiteLLM alternatives (verify features with official docs)
- Medium articles on React skeleton patterns (best practices validated across multiple sources)
- Blog posts on multi-step form wizards (concepts valid, verify specific implementations)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All recommendations from official docs and verified 2026 sources
- Architecture patterns: HIGH - Patterns verified across official docs and production use cases
- Pitfalls: MEDIUM-HIGH - Based on community experience and official documentation warnings
- Code examples: HIGH - Adapted from official documentation and verified repositories

**Research date:** 2026-02-15
**Valid until:** 2026-03-15 (30 days - stable ecosystem, minor updates expected)

**Note:** Fast-moving areas (Tailwind v4, shadcn/ui components) may see updates. Verify latest documentation during implementation.
