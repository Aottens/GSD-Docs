# Phase 11: Document Preview & Outline - Research

**Researched:** 2026-03-20
**Domain:** React split-pane UI, Markdown rendering, Mermaid diagrams, FastAPI filesystem API
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Outline tree & navigation
- Split view layout: left panel = outline tree, right panel = content preview, with resizable divider (using existing ResizablePanelGroup component)
- Tree nodes show section title + status icon + 1-line preview snippet when content exists
- Full depth from fds-structure.json — all levels including equipment module subsections (e.g., 4.2.3 States)
- Section numbers auto-derived from fds-structure.json (1, 1.1, 4.2.3) — matches final document output
- Clicking a node scrolls to that section in a continuous scrollable document view
- Scroll-spy highlights the currently visible section in the outline tree

#### Content rendering
- Document-style typography: generous whitespace, clear heading hierarchy, styled tables and code blocks (Notion/GitBook aesthetic)
- Mermaid code blocks render automatically as inline SVG diagrams, fallback to showing code block if rendering fails
- Subtle section headers: light divider line with section number and phase badge per section
- Auto-numbered sections matching FDS structure (1.1, 4.2.3) derived from fds-structure.json

#### Plans & wave display
- Plan info integrated directly into outline tree nodes — wave badge (W1, W2, W3) with color coding (W1=blue, W2=green, W3=orange, etc.)
- Clicking a planned-but-unwritten section shows plan details card in content panel: wave assignment, dependencies, must-haves/truths from frontmatter, plan description — formatted as readable card, not raw YAML
- Dependencies shown as tooltip on hover: "Depends on: 4.1.1, 4.1.2"

#### Empty & partial states
- Fresh projects show the full outline tree structure (derived from project type) with all nodes in 'empty' state; content panel shows friendly message with next CLI command
- Progressive status icons per node: empty circle (nothing), clipboard (plan only), document (content written), checkmark (verified) — gray for empty, colored for active states
- Clicking an empty section shows section info + next action: section title, FDS structure position, next CLI command needed
- Auto-refresh via polling every 10-30 seconds (matching PhaseTimeline pattern) — picks up new CONTENT.md or PLAN.md written by CLI

### Claude's Discretion
- Exact polling interval within the 10-30s range
- Outline tree panel default width and min/max constraints
- Mermaid rendering library choice and configuration
- Loading skeleton design for content panel
- Scroll-spy implementation approach
- Exact color palette for wave badges
- Typography scale and spacing for document-style rendering
- How to handle malformed or partial markdown files

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| WORK-03 | Engineer can view document outline tree with expandable/collapsible sections | fds-structure.json tree parsing, ResizablePanelGroup split-pane, React tree node component pattern |
| WORK-04 | Engineer can navigate to a specific section from the outline tree | Scroll-to-section with `scrollIntoView`, scroll-spy with IntersectionObserver, section IDs derived from fds-structure.json |
| OUTP-01 | Engineer can preview rendered document content with Mermaid diagram rendering | react-markdown + remark-gfm already installed, mermaid library for SVG rendering, code block renderer override |
| DOCG-01 | Engineer can view generated section plans with wave assignments in the GUI | PLAN.md frontmatter parsing (phase, plan, wave, depends_on fields), backend endpoint reads filesystem, plan card display |
</phase_requirements>

---

## Summary

Phase 11 builds a document preview cockpit: a split-pane view (resizable panels already installed) with a section outline tree on the left and rendered document content on the right. The backend reads the project filesystem to build the outline from `fds-structure.json`, detect section content status via file existence, and serve PLAN.md frontmatter for wave/dependency display. The frontend renders markdown via `react-markdown` (already installed) and Mermaid diagrams via the `mermaid` npm library (current: v11.13.0).

The key complexity is the tree-data model. The `fds-structure.json` defines static sections (1–7), and section 4 (Equipment Modules) is **dynamic** — the backend must discover equipment module phases from the project's `.planning/phases/` directory and synthesize 4.x subsections at runtime. Type C/D projects insert an additional section 1.4 (Baseline) which shifts Abbreviations from 1.4 to 1.5. The status of each node (empty/plan/written/verified) is derived entirely from filesystem globs — same pattern as the existing `_derive_phase_status()` in `phases.py`.

**Primary recommendation:** Build three layers: (1) a new backend `/api/projects/{id}/documents/outline` endpoint that returns a typed outline tree, (2) a new `/api/projects/{id}/documents/sections/{section_id}/content` endpoint returning rendered status + content, and (3) a `DocumentsTab` React component tree that wires these together with polling and scroll-spy.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| react-markdown | 10.1.0 | Render markdown to React elements | Already installed; handles GFM tables, code blocks, headings |
| remark-gfm | 4.0.1 | GFM extensions (tables, strikethrough) | Already installed; FDS content uses tables heavily |
| react-resizable-panels | 4.7.3 | Resizable split-pane layout | Already installed, already wrapped in `ui/resizable.tsx` |
| mermaid | 11.13.0 | Mermaid diagram SVG rendering | Current stable; browser-side rendering; handles stateDiagram-v2 |
| @tanstack/react-query | 5.90.21 | Data fetching + polling | Already used for phase timeline; same polling pattern applies |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| rehype-raw | 7.0.0 | Allow raw HTML through rehype pipeline | If custom HTML needed in rendered output |
| lucide-react | 0.564.0 | Status icons (Circle, Clipboard, FileText, CheckCircle2) | Already used throughout project |
| shadcn/ui Badge | existing | Wave badges (W1, W2, W3) on tree nodes | Already installed — Badge component |
| shadcn/ui Skeleton | existing | Loading states for outline and content panel | Already installed |
| shadcn/ui Tooltip | existing | Dependency hover tooltips on tree nodes | Already installed |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| mermaid (browser) | mermaid-node / server-side SVG | Server-side avoids SSR issues but adds backend dep; browser-side is simpler with error fallback |
| IntersectionObserver scroll-spy | scroll event listener + getBoundingClientRect | IntersectionObserver is performant, no layout thrash; fits Claude's Discretion scope |
| polling (React Query refetchInterval) | WebSocket / SSE | Polling consistent with existing PhaseTimeline pattern; SSE overkill for file change detection |

**Installation:**
```bash
# Only mermaid needs to be added — all other dependencies are already installed
npm install mermaid
```

**Version verification:**
```bash
npm view mermaid version          # 11.13.0 (verified 2026-03-20)
npm view react-markdown version   # 10.1.0 (already in package.json)
npm view react-resizable-panels version  # 4.7.3 (already in package.json)
```

---

## Architecture Patterns

### Recommended Project Structure

```
frontend/src/features/documents/
├── components/
│   ├── DocumentsTab.tsx         # Root: ResizablePanelGroup with outline + content
│   ├── OutlinePanel.tsx         # Left panel: tree of FDS sections
│   ├── OutlineNode.tsx          # Single tree node with status icon + wave badge
│   ├── ContentPanel.tsx         # Right panel: scrollable document view
│   ├── SectionBlock.tsx         # One section rendered: header + content
│   ├── MermaidDiagram.tsx       # Mermaid SVG renderer with fallback
│   ├── PlanCard.tsx             # Plan details card for planned-but-unwritten sections
│   └── EmptySectionCard.tsx     # Empty section info + CLI command card
├── hooks/
│   ├── useDocumentOutline.ts    # React Query: GET /documents/outline, 15s polling
│   ├── useSectionContent.ts     # React Query: GET /documents/sections/:id/content
│   └── useScrollSpy.ts          # IntersectionObserver scroll-spy hook
└── types/
    └── document.ts              # OutlineNode, SectionContent, PlanInfo types

backend/app/api/documents.py     # New: outline + section content endpoints
```

### Pattern 1: Backend Outline Builder

**What:** Backend synthesizes the full FDS outline tree by merging fds-structure.json (static) with dynamic equipment modules discovered from the project's `.planning/phases/` directory.

**When to use:** Any time the outline tree is requested — single source of truth for section IDs, numbering, and hierarchy.

**How the dynamic section 4 works:**
- Scan `.planning/phases/` for directories matching equipment module naming patterns from `config_phases.py`
- For Type A: phase 3 ("Equipment Modules") contains equipment modules; their subsections are synthesized as 4.1.x, 4.2.x, etc. per `fds-structure.json`'s `dynamic_sections.equipment_modules`
- Each discovered equipment module becomes section 4.N with 9 subsections (4.N.1 Function through 4.N.9 Maintenance)

**Type C/D baseline insertion:**
- Insert section 1.4 (Baseline System) before standard Abbreviations
- Shift original section 1.4 (Abbreviations) → 1.5

**Example outline API response:**
```typescript
// Source: fds-structure.json + filesystem discovery
interface OutlineNode {
  id: string               // "1", "1.1", "4.2.3" — matches final document numbering
  title: { en: string; nl: string }
  depth: number            // 1, 2, 3
  required: boolean
  source_type: string      // "system-overview", "dynamic", "auto-generated"
  status: 'empty' | 'planned' | 'written' | 'verified'
  has_content: boolean
  has_plan: boolean
  plan_info?: PlanInfo     // wave, depends_on, plan name — from PLAN.md frontmatter
  preview_snippet?: string // first ~80 chars of CONTENT.md (if written)
  children: OutlineNode[]
}

interface PlanInfo {
  wave: number
  depends_on: string[]     // e.g., ["01-01", "01-02"]
  plan_name: string
  plan_file: string
}

interface DocumentOutlineResponse {
  project_id: number
  project_language: 'nl' | 'en'
  sections: OutlineNode[]
}
```

### Pattern 2: Section Status Detection (Backend)

**What:** Same filesystem-glob approach as `_derive_phase_status()` in `phases.py`, applied to per-section content files.

**When to use:** For each outline node, to determine whether it has content, a plan, or is empty.

**How PLAN.md files map to FDS sections:**
- PLAN.md files live at `.planning/phases/NN-*/NN-MM-PLAN.md`
- PLAN.md frontmatter contains: `phase`, `plan`, `name`, `type`, `wave`, `depends_on`
- The plan's `## Sections` list identifies which FDS sections it covers
- Backend parses frontmatter YAML + extracts wave/depends_on for the plan card

**Content files (CONTENT.md / SUMMARY.md):**
- Written content lives at `.planning/phases/NN-*/NN-MM-SUMMARY.md` (post-write)
- Or at `projects/{id}/content/{section_id}.md` if the project uses per-section content files
- **Important:** The actual FDS content structure depends on how `write-phase` stores output — research the project's `.planning/phases/` structure for project ID 2 to verify actual file names

**Status derivation per section:**
```python
# Pseudocode — mirrors _derive_phase_status() pattern
def _derive_section_status(project_dir, phase_number, section_id):
    phase_dir = find_phase_dir(project_dir, phase_number)
    has_plan = any plan file whose ## Sections references this section_id
    has_content = SUMMARY.md exists for this phase/plan
    has_verification = VERIFICATION.md exists for this phase

    if has_verification: return 'verified'
    if has_content: return 'written'
    if has_plan: return 'planned'
    return 'empty'
```

### Pattern 3: Mermaid Rendering in React

**What:** Custom code block renderer in `react-markdown` that intercepts `mermaid` language fences and renders them as SVG using the `mermaid` library.

**When to use:** Any code block with language identifier `mermaid` in FDS content.

**Example:**
```typescript
// Source: mermaid npm docs + react-markdown custom renderer pattern
import mermaid from 'mermaid'
import { useEffect, useRef, useState } from 'react'

// Initialize once at app level (or component level with useEffect)
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',  // or 'dark' matching app theme
  securityLevel: 'loose'  // required for stateDiagram-v2 click events
})

function MermaidDiagram({ chart }: { chart: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [svg, setSvg] = useState<string | null>(null)

  useEffect(() => {
    const id = `mermaid-${Math.random().toString(36).slice(2)}`
    mermaid.render(id, chart)
      .then(({ svg }) => setSvg(svg))
      .catch((err) => setError(String(err)))
  }, [chart])

  if (error) {
    // Fallback: show raw code block
    return <pre><code>{chart}</code></pre>
  }
  if (!svg) return <Skeleton className="h-48 w-full" />
  return <div dangerouslySetInnerHTML={{ __html: svg }} />
}

// Custom code block in react-markdown
const components = {
  code({ node, inline, className, children, ...props }) {
    const language = /language-(\w+)/.exec(className || '')?.[1]
    if (language === 'mermaid') {
      return <MermaidDiagram chart={String(children).replace(/\n$/, '')} />
    }
    return <code className={className} {...props}>{children}</code>
  }
}
```

### Pattern 4: Scroll-Spy with IntersectionObserver

**What:** IntersectionObserver watches section heading elements; when a heading enters the viewport, the corresponding outline node is highlighted.

**When to use:** Continuous scroll of the content panel — highlights current section in outline tree.

**Example:**
```typescript
// Source: IntersectionObserver API pattern for scroll-spy
function useScrollSpy(sectionIds: string[]) {
  const [activeId, setActiveId] = useState<string | null>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        // Find the topmost visible section
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (visible.length > 0) {
          setActiveId(visible[0].target.id)
        }
      },
      { rootMargin: '-20% 0px -70% 0px', threshold: 0 }
    )

    sectionIds.forEach(id => {
      const el = document.getElementById(`section-${id}`)
      if (el) observer.observe(el)
    })
    return () => observer.disconnect()
  }, [sectionIds])

  return activeId
}
```

### Pattern 5: react-resizable-panels Integration

**What:** Use existing `ResizablePanelGroup` from `ui/resizable.tsx` (wrapping `react-resizable-panels`) for the outline/content split.

**Configuration:**
```tsx
// Source: react-resizable-panels docs + existing ui/resizable.tsx
<ResizablePanelGroup direction="horizontal" className="h-full">
  <ResizablePanel
    defaultSize={25}   // 25% width default
    minSize={15}       // ~200px at 1280px viewport
    maxSize={40}       // 40% maximum
  >
    <OutlinePanel sections={outline.sections} activeId={activeId} onSelect={scrollToSection} />
  </ResizablePanel>
  <ResizableHandle withHandle />
  <ResizablePanel defaultSize={75}>
    <ContentPanel sections={outline.sections} language={project.language} />
  </ResizablePanel>
</ResizablePanelGroup>
```

### Pattern 6: API Endpoints (Backend)

**New endpoints to add in `backend/app/api/documents.py`:**

```python
# Endpoint 1: Full outline tree
GET /api/projects/{project_id}/documents/outline
→ DocumentOutlineResponse

# Endpoint 2: Rendered content for a section (optional — could be served as part of outline)
GET /api/projects/{project_id}/documents/sections/{section_id}/content
→ { section_id, markdown_content, plan_info }

# No endpoint needed for full document render — frontend assembles from section content
```

**Backend file reading pattern (mirrors phases.py):**
```python
# Re-use _get_project_dir() from phases.py
# Re-use _derive_phase_status() pattern — just apply it per-section instead of per-phase
```

### Anti-Patterns to Avoid

- **Embedding mermaid initialization inside React render loop:** Initialize once with `mermaid.initialize()` outside of components or in a single `useEffect` with empty deps array. Multiple `initialize()` calls cause rendering conflicts.
- **Fetching all section content on mount:** Fetch outline first (lightweight), then fetch content only when rendered in viewport or selected. The outline with status flags is cheap; raw content can be large.
- **Hardcoding section IDs in frontend:** Section IDs must come from the backend outline response, which derives them from fds-structure.json. The frontend must not assume "1", "1.1", etc.
- **Blocking outline on dynamic section discovery:** If a project has no content yet (empty), the outline must still show all sections from fds-structure.json. The dynamic equipment module sections may be empty (showing 0 modules) until write-phase creates content.
- **Using `dangerouslySetInnerHTML` for markdown:** Use react-markdown with a custom components map, not raw innerHTML injection.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown to HTML | Custom regex/HTML converter | react-markdown + remark-gfm | Handles GFM tables, code fences, nested lists, edge cases; already installed |
| Mermaid SVG | Manual SVG generation for state diagrams | mermaid library (v11) | Handles stateDiagram-v2, flowchart, sequence — all used in FDS templates |
| Resizable panels | CSS flex with JS drag handlers | react-resizable-panels (existing) | Handles resize state persistence, keyboard accessibility, min/max constraints |
| Section tree collapse/expand | Manual DOM manipulation | React controlled state (isExpanded per node) | Simple useState map; no library needed for a 3-level tree |
| Scroll-spy | setInterval polling getBoundingClientRect | IntersectionObserver | Browser-native, performant, no layout thrash |

**Key insight:** All core libraries are already installed. Phase 11 is primarily integration work — wiring together existing tools, not installing new ones (only `mermaid` is new).

---

## Common Pitfalls

### Pitfall 1: Mermaid `initialize()` Called Multiple Times
**What goes wrong:** Each `MermaidDiagram` component calls `mermaid.initialize()`, causing "already initialized" warnings and inconsistent rendering in React StrictMode (double-render).
**Why it happens:** Treating Mermaid like a stateless render function; it maintains global state.
**How to avoid:** Call `mermaid.initialize()` once in a module-level side effect or in the root `DocumentsTab` `useEffect` with `[]` dependency. Use `mermaid.render()` per diagram, never `mermaid.initialize()` per diagram.
**Warning signs:** Console warnings "Mermaid is already loaded", diagrams render twice on StrictMode, race conditions on multiple diagrams.

### Pitfall 2: Dynamic Section 4 Shows Empty Without Equipment Module Data
**What goes wrong:** On a fresh project, section 4 (Equipment Modules) has no subsections because no writing has occurred. The outline tree shows "4. Equipment Modules" with no children.
**Why it happens:** The backend only discovers equipment modules from actual PLAN.md or SUMMARY.md files, but for a fresh project those don't exist.
**How to avoid:** For the outline tree, derive expected equipment modules from the project's ROADMAP.md (if it exists) or from `config_phases.py` phase descriptions. If no ROADMAP.md yet, show section 4 as a single "dynamic" placeholder node with a note: "Equipment modules verschijnen na `/doc:plan-phase 3`."
**Warning signs:** Section 4 disappears entirely from outline on fresh projects.

### Pitfall 3: Scroll-Spy Highlights Wrong Section After Navigation
**What goes wrong:** Clicking an outline node scrolls to a section, but scroll-spy immediately fires and highlights a different section (the one at the top of viewport during scroll animation).
**Why it happens:** `scrollIntoView` is asynchronous; IntersectionObserver fires during the scroll animation.
**How to avoid:** After a programmatic scroll, suppress scroll-spy updates for ~500ms using a `isScrolling` ref:
```typescript
const isScrolling = useRef(false)
function scrollToSection(id: string) {
  isScrolling.current = true
  document.getElementById(`section-${id}`)?.scrollIntoView({ behavior: 'smooth' })
  setTimeout(() => { isScrolling.current = false }, 600)
}
// In IntersectionObserver callback: if (isScrolling.current) return
```
**Warning signs:** Outline highlight "jumps" when clicking a tree node.

### Pitfall 4: fds-structure.json Section Numbering Off for Type C/D
**What goes wrong:** For Type C/D projects, the backend inserts section 1.4 (Baseline) but doesn't shift Abbreviations to 1.5, causing section ID conflicts.
**Why it happens:** `fds-structure.json` documents this shift in `type_conditional.baseline_section.note`, but it's easy to miss when building the outline builder.
**How to avoid:** Backend outline builder must apply the type_conditional rules from `fds-structure.json`:
- If project type is C or D: insert baseline section at 1.4, shift abbreviations from 1.4 → 1.5
- All section IDs in the API response must reflect the shifted numbering
**Warning signs:** Type C/D outline shows "1.4 Abbreviations" without "1.4 Baseline System"; wrong section IDs in scroll targets.

### Pitfall 5: PLAN.md Frontmatter Wave Field Not Present
**What goes wrong:** Trying to display wave badges on outline nodes fails because PLAN.md files don't have a `wave` frontmatter field or it's embedded in the markdown body, not YAML frontmatter.
**Why it happens:** Looking at the `/doc:plan-phase` workflow: plan files use YAML frontmatter (`---` delimited) with `wave:` field — but only if generated by the CLI. Manually created or older plan files may not have this.
**How to avoid:** Backend PLAN.md parser must be defensive: parse frontmatter if present, fall back to regex-searching the markdown body for `wave:` or `Wave {N}` pattern if frontmatter is absent. Never crash; return null wave instead.
**Warning signs:** All wave badges show "?" or nothing for CLI-generated plans.

### Pitfall 6: react-markdown + Tailwind CSS Class Conflicts
**What goes wrong:** Tailwind's CSS reset (`prose` class from `@tailwindcss/typography`) is not available in this project (only `tailwindcss` base is used). Default `react-markdown` output has no styling — all headings look the same size.
**Why it happens:** This project uses Tailwind v4 without `@tailwindcss/typography` plugin. `react-markdown` renders semantic HTML, not styled HTML.
**How to avoid:** Apply custom className overrides via the `components` prop of `react-markdown`. Define a `markdownComponents` object that applies Tailwind utility classes to `h1`, `h2`, `h3`, `p`, `table`, `code`, etc. This is the "document-style typography" work.
**Warning signs:** All rendered markdown looks like unstyled HTML; tables have no borders; headings are same size as body text.

---

## Code Examples

Verified patterns from official sources and existing codebase:

### React Query with Polling (existing pattern from usePhaseStatus.ts)
```typescript
// Source: frontend/src/features/timeline/hooks/usePhaseStatus.ts
export function useDocumentOutline(projectId: number) {
  return useQuery({
    queryKey: ['projects', projectId, 'documents', 'outline'],
    queryFn: () => api.get<DocumentOutlineResponse>(`/projects/${projectId}/documents/outline`),
    refetchInterval: 15000,  // 15s — within 10-30s window from CONTEXT.md
    staleTime: 10000,
  })
}
```

### Backend Outline Endpoint (following phases.py pattern)
```python
# Source: backend/app/api/phases.py pattern (_get_project_dir, _derive_phase_status)
# In new backend/app/api/documents.py

router = APIRouter(prefix="/api/projects/{project_id}/documents", tags=["documents"])

@router.get("/outline", response_model=DocumentOutlineResponse)
async def get_document_outline(
    project_id: int,
    db: AsyncSession = Depends(get_db)
) -> DocumentOutlineResponse:
    project = await _get_project(project_id, db)
    project_dir = _get_project_dir(project_id)

    # Load fds-structure.json from V1_DOCS_PATH
    settings = get_settings()
    fds_structure_path = Path(settings.V1_DOCS_PATH) / "templates" / "fds-structure.json"
    fds_structure = json.loads(fds_structure_path.read_text())

    # Build sections with type_conditional for C/D
    sections = _build_outline_sections(
        fds_structure,
        project.type.value,
        project_dir
    )

    return DocumentOutlineResponse(
        project_id=project_id,
        project_language=project.language.value,
        sections=sections
    )
```

### PLAN.md Frontmatter Parser (Python)
```python
# PLAN.md files start with YAML frontmatter: ---\nphase: 1\nwave: 2\n---
import yaml

def _parse_plan_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from PLAN.md file. Returns {} if not present."""
    if not content.startswith('---'):
        return {}
    end = content.find('---', 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(content[3:end]) or {}
    except yaml.YAMLError:
        return {}
```

### Enabling Documents Nav in ProjectNavigation.tsx
```typescript
// Source: frontend/src/features/projects/components/ProjectNavigation.tsx
// Change isEnabled for 'documents':
const isEnabled =
  section.id === 'overview' ||
  section.id === 'references' ||
  section.id === 'fasering' ||
  section.id === 'documents'  // ADD THIS
```

### ProjectWorkspace.tsx DocumentsTab slot
```typescript
// Source: frontend/src/features/projects/ProjectWorkspace.tsx
// Add after existing activeSection === 'fasering' check:
import { DocumentsTab } from '../documents/components/DocumentsTab'

{activeSection === 'documents' && <DocumentsTab projectId={project.id} language={project.language} />}
```

### Mermaid Dark Mode Theming
```typescript
// mermaid supports 'default', 'dark', 'forest', 'base', 'neutral'
// Match app theme from document.documentElement.classList
const isDark = document.documentElement.classList.contains('dark')
mermaid.initialize({
  startOnLoad: false,
  theme: isDark ? 'dark' : 'default',
  securityLevel: 'loose',
})
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| mermaid v8/v9 synchronous `mermaid.init()` | mermaid v10+ async `mermaid.render()` Promise API | v10 (2023) | Must use async render; `mermaid.init()` still works but is deprecated for programmatic use |
| react-markdown v6/v7 `renderers` prop | react-markdown v8+ `components` prop | v8 (2022) | `renderers` no longer exists — use `components` |
| Prose styling via `@tailwindcss/typography` | Custom component-level Tailwind classes | Always an option | This project lacks typography plugin — must style via `components` prop overrides |
| `react-resizable-panels` v1 `Panel` API | v2+ `Panel` with `defaultSize` as percentage | v2 (2023) | `defaultSize` is a % 0-100, not pixels |

**Deprecated/outdated:**
- `mermaid.init()` with DOM selectors: replaced by `mermaid.render(id, text)` Promise API in v10+
- `react-markdown` `renderers` prop: removed in v8, replaced by `components`

---

## Open Questions

1. **How does write-phase store per-section content?**
   - What we know: `_derive_phase_status()` checks for `NN-MM-SUMMARY.md` to determine `has_content` status. PLAN.md files are `NN-MM-PLAN.md`.
   - What's unclear: The exact structure of SUMMARY.md — does it contain the full FDS section markdown, or just a summary? Does each PLAN.md produce one SUMMARY.md with the full section content?
   - Recommendation: Read `gsd-docs-industrial/workflows/write-phase.md` before implementing the content endpoint. The backend must parse whatever format write-phase actually produces.

2. **Equipment Module discovery from ROADMAP.md vs phases directory**
   - What we know: Section 4 subsections are "dynamic" — one subsection group per equipment module. The `fds-structure.json` explains they come from "roadmap_phases". For project type A, phase 3 is the Equipment Modules phase.
   - What's unclear: How to enumerate specific equipment modules (e.g., "EM-01: Conveyor", "EM-02: Filler") for a given project. The project's `.planning/ROADMAP.md` may enumerate them, or they may only appear after planning.
   - Recommendation: Backend should check for `.planning/ROADMAP.md` in the project directory; if it exists, parse equipment module phase entries. If not, show section 4 as a placeholder with no subsections.

3. **Project language for section titles in outline tree**
   - What we know: `fds-structure.json` has bilingual titles `{ en: "...", nl: "..." }`. The project has a `language` field (`nl` or `en`).
   - What's unclear: Should the outline show Dutch or English titles? CONTEXT.md says "all UI in Dutch" but section titles in FDS documents may be in the project's configured language.
   - Recommendation: Use project language for section titles in the outline tree (matches the document content); use Dutch for all UI chrome (panel labels, status messages, CLI command hints).

---

## Validation Architecture

No test infrastructure detected for this project (no `pytest.ini`, no `tests/` directory, no `*.test.ts` files). The `nyquist_validation` key is absent from `.planning/config.json`, which means validation is treated as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (listed in requirements.txt, not yet configured) |
| Config file | None — Wave 0 must create `pytest.ini` or `pyproject.toml [tool.pytest]` |
| Quick run command | `pytest backend/tests/ -x -q` |
| Full suite command | `pytest backend/tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| WORK-03 | Outline tree returns correct section hierarchy from fds-structure.json | unit | `pytest backend/tests/test_documents.py::test_outline_static_sections -x` | ❌ Wave 0 |
| WORK-03 | Type C/D inserts baseline section and shifts abbreviations | unit | `pytest backend/tests/test_documents.py::test_outline_type_c_baseline_shift -x` | ❌ Wave 0 |
| WORK-04 | Section IDs in outline match scroll targets in rendered document | manual | Manual browser test — scroll spy cannot be automated without browser | manual-only |
| OUTP-01 | Mermaid code blocks render as SVG in content panel | manual | Manual browser test — requires DOM rendering | manual-only |
| OUTP-01 | Malformed mermaid falls back to code block display | manual | Manual browser test | manual-only |
| DOCG-01 | PLAN.md frontmatter parsed: wave, depends_on, name extracted | unit | `pytest backend/tests/test_documents.py::test_plan_frontmatter_parsing -x` | ❌ Wave 0 |
| DOCG-01 | Plan card shows correct wave badge and dependencies | manual | Manual browser test | manual-only |

### Sampling Rate
- **Per task commit:** `pytest backend/tests/ -x -q`
- **Per wave merge:** `pytest backend/tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/__init__.py` — package init
- [ ] `backend/tests/test_documents.py` — covers WORK-03 (outline structure), DOCG-01 (plan parsing)
- [ ] `backend/tests/conftest.py` — shared fixtures (test project dir, mock fds-structure.json)
- [ ] Framework config: add `[tool.pytest.ini_options]` to `backend/pyproject.toml` or create `backend/pytest.ini`

---

## Sources

### Primary (HIGH confidence)
- Codebase direct read: `fds-structure.json` — exact section hierarchy, dynamic section rules, type_conditional logic
- Codebase direct read: `backend/app/api/phases.py` — `_derive_phase_status()`, `_get_project_dir()` patterns to replicate
- Codebase direct read: `frontend/src/features/projects/ProjectWorkspace.tsx` — integration point for `documents` case
- Codebase direct read: `frontend/src/features/projects/components/ProjectNavigation.tsx` — enable `documents` nav item
- Codebase direct read: `frontend/src/components/ui/resizable.tsx` — ResizablePanelGroup API surface
- Codebase direct read: `frontend/package.json` — confirmed react-markdown@10.1.0, remark-gfm@4.0.1, react-resizable-panels@4.7.3 installed
- npm registry (2026-03-20): `npm view mermaid version` → 11.13.0

### Secondary (MEDIUM confidence)
- mermaid v10+ async render API: mermaid.js.org docs — `mermaid.render()` returns Promise<{svg}>; confirmed by checking npm version 11.13.0
- react-resizable-panels v2 `defaultSize` as percentage: confirmed by existing `ui/resizable.tsx` wrapper

### Tertiary (LOW confidence)
- IntersectionObserver scroll-spy `rootMargin` values: common community pattern; exact thresholds are Claude's Discretion per CONTEXT.md

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified in package.json or npm registry
- Architecture: HIGH — patterns directly mirror existing phases.py and usePhaseStatus.ts code
- Pitfalls: HIGH — derived from reading actual source code and fds-structure.json documentation
- Mermaid API: MEDIUM — verified library version, API patterns based on mermaid v10+ docs knowledge

**Research date:** 2026-03-20
**Valid until:** 2026-04-20 (mermaid API is stable; react-markdown API is stable)
