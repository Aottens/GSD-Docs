# Stack Research

**Domain:** Docs engine rearchitecture — LLM provider abstraction, flexible document structure, docs engine visibility
**Researched:** 2026-03-31
**Confidence:** HIGH (core additions), MEDIUM (react-diff-viewer-continued React 19 peer dep)

---

## Context: What Is Already in Place

This is a SUBSEQUENT MILESTONE research file. The following are already present and should NOT be re-added:

| Layer | Already Have | Version |
|-------|-------------|---------|
| Backend framework | FastAPI, Uvicorn, SQLAlchemy async, Aiosqlite, Alembic | >=0.115, >=2.0 |
| Config | pydantic-settings, `Settings` class, `@lru_cache get_settings()` | >=2.0 |
| HTTP client | httpx | >=0.27 |
| SSE | sse-starlette | >=3.2 |
| Validation | pydantic v2 | >=2.0 |
| File handling | python-multipart, aiofiles, python-magic, Pillow | current |
| Frontend | React 19, TypeScript 5.9, Vite 7, Tailwind 4 | as in package.json |
| UI | shadcn/radix-ui, lucide-react | current |
| State | Zustand 5, TanStack Query 5 | current |
| Markdown rendering | react-markdown 10, remark-gfm | current |
| Forms | react-hook-form 7 | current |

---

## New Additions Required

### Feature 1: LLM Provider Abstraction

**Goal:** Single `completion()` call that routes to Claude, GPT-4o, or local Ollama-hosted models (DeepSeek, Llama) based on config. No provider-specific branching in business logic.

#### Core Technologies (Backend)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `litellm` | `==1.83.0` | Unified LLM provider interface | Single `litellm.completion(model=..., messages=...)` works identically for `claude-opus-4-5`, `gpt-4o`, and `ollama/deepseek-r1:14b`. Handles streaming, retries, cost tracking, fallbacks. Used by CrewAI, Giskard, and others as standard multi-provider abstraction. The `ollama/` prefix prefix routes to local Ollama without a separate integration path. |
| `anthropic` | `>=0.86.0` | Anthropic SDK (LiteLLM dependency) | LiteLLM uses it under the hood. Pin separately to lock version and have access to `anthropic.types` for type-safe config. Already required by the v1.0 CLI plugin's `.claude/` commands. |
| `openai` | `>=2.30.0` | OpenAI SDK (LiteLLM dependency + Ollama compat) | LiteLLM uses it for GPT providers. Ollama also exposes an OpenAI-compatible endpoint at `/v1`, so this handles both cloud GPT and local Ollama generation in a single SDK. |

**Security note — CRITICAL:** LiteLLM versions 1.82.7 and 1.82.8 were compromised in a supply chain attack published March 24, 2026 (TeamPCP group via Trivy CI/CD compromise). Both versions have been removed from PyPI. Version 1.83.0 was released March 31, 2026 and is confirmed clean. Pin to `==1.83.0`. Do not use `>=1.82.6` open-ended ranges without an explicit upper bound until you have independently verified a newer release.

#### Supporting Libraries (Backend)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `ollama` | `>=0.6.1` | Ollama management API client | Optional — only add if the UI needs to list available local models, check which models are running (`ollama ps`), or pull new models. LiteLLM's `ollama/` prefix handles generation without this SDK. Add it when building the "choose local model" picker in the frontend. |

#### Config Integration

The existing `Settings` class (`app/config.py`) uses pydantic-settings with `@lru_cache`. Extend it — no new config library needed:

```python
# Additions to existing app/config.py Settings class
LLM_PROVIDER: str = "anthropic"           # "anthropic" | "openai" | "ollama"
LLM_MODEL: str = "claude-opus-4-5"        # Provider-specific model string
LLM_BASE_URL: str | None = None           # Ollama: "http://localhost:11434"; None for cloud
ANTHROPIC_API_KEY: str = ""
OPENAI_API_KEY: str = ""
# Ollama needs no key — auth via base_url only
```

LiteLLM model string conventions: `"claude-opus-4-5"` → Anthropic, `"gpt-4o"` → OpenAI, `"ollama/deepseek-r1:14b"` → local Ollama instance.

---

### Feature 2: Flexible FDS Structure

**Goal:** Replace hardcoded EM-first ISA-88 decomposition with a system-first approach. Support ISA-88, functional, process-flow, and hybrid decomposition models selected at project creation based on how the engineer describes the system.

**No new Python or npm packages required.**

| What Changes | Where | New Dep? |
|-------------|-------|----------|
| Multiple decomposition model ROADMAP templates | `gsd-docs-industrial/templates/` Markdown files | No |
| System-first discovery prompt in `/doc:new-fds` | Claude Code plugin command file | No |
| Decomposition model stored per-project | Extend `Settings`/project schema — existing SQLAlchemy models | No |
| Frontend display of decomposition model | Extend existing phase timeline React component | No |
| Conditional template loading per model | `app/services/` — already has file-based template loading | No |

The existing `config_phases.py` already handles phase/section structure from filesystem. `project_service.py` already handles per-project config. This feature is a data model + prompt logic change.

---

### Feature 3: Docs Engine Visibility

**Goal:** Engineer-facing viewer for the 194 Markdown files in `gsd-docs-industrial/` — templates, prompts, workflows. Show what exists, what changed (git history), and allow inspection of raw source vs rendered output.

#### Backend

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `GitPython` | `>=3.1.46` | Read git commit history for template/prompt change tracking | Pure Python, no native binaries beyond the `git` CLI already present on the VM. `repo.iter_commits(paths=['gsd-docs-industrial/'])` gives typed access to commit history, file diffs, and blob contents. Enables a `/api/docs-engine/templates/{name}/history` endpoint. Alternative: raw `subprocess.run(['git', 'log', '--follow', ...])` — simpler but brittle and harder to parse. |

#### Frontend

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `@monaco-editor/react` | `^4.7.0` | Read-only code editor for template/prompt raw source display | v4.7.0 explicitly added React 19 as a peer dependency. Renders Markdown, YAML, prompt text with VS Code quality syntax highlighting. The existing `react-markdown` handles rendered output; Monaco handles raw source inspection. Use for the "view template source" pane in the docs engine viewer. Bundle cost ~2MB but appropriate for an engineering tool where code quality matters. |
| `react-diff-viewer-continued` | `^4.2.0` | Side-by-side diff view for template change history | Actively maintained fork of the abandoned `react-diff-viewer`. Supports inline/split diff, word-level highlighting, virtualization for large files. Use for "what changed in this template version" when navigating git history. React 19 peer dep: latest 4.x targets React 18+; verify with `npm ls react` after install and use `--legacy-peer-deps` if needed. |

---

## Installation

### Backend additions (add to `requirements.txt`)

```bash
# LLM provider abstraction
litellm==1.83.0
anthropic>=0.86.0
openai>=2.30.0

# Docs engine visibility
GitPython>=3.1.46

# Optional: local model management API
ollama>=0.6.1
```

### Frontend additions (add to `package.json`)

```bash
# Docs engine visibility
npm install @monaco-editor/react@^4.7.0
npm install react-diff-viewer-continued@^4.2.0
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `litellm` for provider abstraction | Hand-rolled provider adapter (abstract base class per provider) | Only if you need zero runtime dependencies and are willing to maintain adapters for each provider update. The LiteLLM supply chain incident (now resolved) was the strongest argument for rolling your own — but 1.83.0 is clean and the library remains the industry standard. |
| `litellm` Ollama routing | Direct `ollama` Python SDK for all generation | Only if committing to Ollama-only (no cloud providers). The `ollama` SDK is simpler in that scenario but cannot route to Claude or GPT. |
| `GitPython` for change tracking | `subprocess.run(['git', 'log', ...])` + manual parsing | Use subprocess if you want zero new dependencies. It works but requires parsing raw git output; error handling is messier. GitPython gives typed objects (`Commit`, `Diff`, `Blob`). |
| `@monaco-editor/react` for template source viewer | `<pre>` + highlight.js / Prism | Use the lighter approach if you only need syntax highlighting without the editor chrome (line numbers, folding, minimap). Monaco is heavier but gives VS Code parity — appropriate for an engineering tool. |
| `react-diff-viewer-continued` | Build manually with the `diff` npm package | Use manual diff rendering only if you need highly custom diff UI. The component handles the common split/inline cases out of the box. |

---

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| LangChain | 50+ transitive dependencies, most features unused. This project runs LLM ops in the CLI, not in FastAPI. The backend is a file/project management API, not an agent runtime. | `litellm` for provider routing; raw prompt strings |
| `langchain-litellm` | Adds LangChain as a dependency just to call LiteLLM — circular overhead | `litellm` directly |
| LiteLLM Proxy Server (Docker mode) | Separate infrastructure component requiring Docker or a second service. Overkill for a single-server deployment where LiteLLM is embedded in FastAPI. | LiteLLM Python SDK embedded in `llm_service.py` |
| `instructor` (structured JSON outputs) | Useful for JSON-mode responses but no structured output requirement exists in the current prompt pattern. Adds a dependency for a problem not yet present. | Standard `litellm.completion()` with prompt-level JSON instructions |
| `dulwich` | Pure-Python Git reimplementation; correct but slower for repo traversal than GitPython. Not needed since `git` binary is available on the VM. | `GitPython` |
| Vector DB (Chroma, Weaviate, pgvector) | No semantic search requirement. Templates are accessed by filename/path, not by similarity. | Filesystem traversal + GitPython |
| `litellm==1.82.7` or `==1.82.8` | Supply chain compromise — malicious payload in `proxy_server.py`. Removed from PyPI. | `litellm==1.83.0` |

---

## Stack Patterns by Variant

**Fully local deployment (IP-sensitive client project):**
- Set `LLM_PROVIDER=ollama`, `LLM_MODEL=ollama/deepseek-r1:14b`, `LLM_BASE_URL=http://localhost:11434`
- No API key needed — Ollama runs locally
- LiteLLM routes all `completion()` calls to local Ollama daemon
- Add `ollama>=0.6.1` to requirements if the frontend needs a model picker that lists `ollama.list()` results

**Cloud deployment (standard project):**
- Set `LLM_PROVIDER=anthropic`, `LLM_MODEL=claude-opus-4-5`, `ANTHROPIC_API_KEY=...`
- No `LLM_BASE_URL` needed
- LiteLLM routes to Anthropic API using `anthropic` SDK under the hood

**Hybrid (per-project provider choice):**
- Store `llm_provider` and `llm_model` per-project in SQLite (extend existing project model)
- Pass provider/model as call-time arguments to `litellm.completion(model=project.llm_model, ...)`
- LiteLLM's `model` parameter is call-time overrideable — no global state

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| `litellm==1.83.0` | `anthropic>=0.86.0`, `openai>=2.30.0` | LiteLLM installs these as transitive deps; pin them separately to prevent unexpected upgrades |
| `GitPython>=3.1.46` | Python 3.9+, `git` CLI on PATH | VM already has git; v3.1.46 released January 2026 |
| `@monaco-editor/react@^4.7.0` | React 19.x | v4.7.0 explicitly added React 19 peer dep; versions below 4.7.0 only list React 16-18 |
| `react-diff-viewer-continued@^4.2.0` | React 18.x confirmed; React 19 unconfirmed | Check `npm ls react` after install. If peer warning appears, use `--legacy-peer-deps` or wait for confirmed React 19 support in a newer 4.x release |

---

## Integration Points with Existing Stack

| New Addition | Integrates With | How |
|-------------|-----------------|-----|
| `litellm` | `app/config.py` `Settings` class | Add `LLM_PROVIDER`, `LLM_MODEL`, `LLM_BASE_URL`, key fields to existing Settings. Create new `app/services/llm_service.py` that wraps `litellm.completion()`. Inject via existing `get_settings_dependency()` pattern in `dependencies.py`. |
| `anthropic` / `openai` | `litellm` | LiteLLM uses these SDKs under the hood. No direct import needed in application code unless accessing provider-specific type hints. |
| `ollama` SDK | New API endpoint `/api/docs-engine/models` | Call `ollama.list()` to return available local models for the frontend model picker. Only needed if building that UI feature. |
| `GitPython` | `app/config.py` `V1_DOCS_PATH` | Use `V1_DOCS_PATH = "./gsd-docs-industrial"` as the repo root for `git.Repo(settings.V1_DOCS_PATH)`. New `app/services/docs_engine_service.py` reads template metadata, commit history, and file contents. |
| `@monaco-editor/react` | Existing `react-markdown` rendering | `react-markdown` stays for rendered Markdown preview. Monaco replaces `<pre>` blocks for raw source inspection. Two-pane layout: rendered (react-markdown) left, source (Monaco read-only) right. |
| `react-diff-viewer-continued` | TanStack Query data fetching | Diff view component fetches two file versions via new `/api/docs-engine/templates/{name}/diff?from={sha}&to={sha}` endpoint. TanStack Query caches version pairs. Old/new strings passed as props to `<ReactDiffViewer>`. |

---

## Sources

- [LiteLLM Docs](https://docs.litellm.ai/docs/) — provider support, routing conventions, install (HIGH confidence — official)
- [LiteLLM PyPI](https://pypi.org/project/litellm/) — version 1.83.0 confirmed current as of 2026-03-31 (HIGH confidence)
- [LiteLLM Supply Chain Incident Report](https://docs.litellm.ai/blog/security-update-march-2026) — versions 1.82.7/1.82.8 compromised, 1.83.0 clean (HIGH confidence — official)
- [The Hacker News: TeamPCP Backdoors LiteLLM](https://thehackernews.com/2026/03/teampcp-backdoors-litellm-versions.html) — corroborating source for supply chain incident (HIGH confidence)
- [ollama-python GitHub](https://github.com/ollama/ollama-python) — v0.6.1, AsyncClient, streaming support (HIGH confidence — official)
- [Anthropic Python SDK PyPI](https://pypi.org/project/anthropic/) — v0.86.0 current as of March 2026 (HIGH confidence — official)
- [OpenAI Python SDK PyPI](https://pypi.org/project/openai/) — v2.30.0 released March 25, 2026 (HIGH confidence — official)
- [GitPython PyPI](https://pypi.org/project/GitPython/) — v3.1.46 released January 2026 (HIGH confidence — official)
- [@monaco-editor/react npm](https://www.npmjs.com/package/@monaco-editor/react) — v4.7.0, React 19 peer dep added in this release (HIGH confidence — official)
- [monaco-react GitHub releases](https://github.com/suren-atoyan/monaco-react/releases) — React 19 peer dep confirmed in v4.7.0-rc.0 → v4.7.0 (HIGH confidence — official)
- [react-diff-viewer-continued npm](https://www.npmjs.com/package/react-diff-viewer-continued) — v4.2.0 current, actively maintained (MEDIUM confidence — React 19 compat unconfirmed)
- [FastAPI Settings docs](https://fastapi.tiangolo.com/advanced/settings/) — pydantic-settings pattern (HIGH confidence — official, already in use)

---
*Stack research for: GSD-Docs v3.0 Docs Engine Rearchitecture*
*Researched: 2026-03-31*
*Scope: NEW additions only. v1.0 CLI plugin and v2.0 FastAPI/React stack NOT re-researched.*
