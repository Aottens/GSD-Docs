# Feature Research

**Domain:** Web-based industrial document generation GUI (FDS/SDS automation)
**Researched:** 2026-02-14
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Project wizard with guided setup** | Standard for complex configuration flows; reduces errors during project initialization | MEDIUM | 3-5 steps: project type (A/B/C/D), language (Dutch/English), reference files, baseline selection (Type C/D only). Must support validation before proceeding. |
| **Phase timeline/progress visualization** | Engineers need to understand where they are in multi-phase workflow | LOW | Linear timeline showing 3 FDS phases (Discuss → Plan → Write → Verify → Review) with completion status. Leverage existing STATE.md for data. |
| **Document outline tree view** | Essential for navigating hierarchical document structure (chapters/sections) | MEDIUM | Tree navigation for FDS sections, expandable/collapsible nodes. Must handle dynamic sections added during write phase. Integration with STATE.md section tracking. |
| **Real-time progress feedback for AI tasks** | Long-running LLM calls (30s-3min) feel broken without feedback | MEDIUM | Progress indicators for discuss/plan/write/verify operations with estimated time remaining. Use SSE or WebSocket for server-push updates. Phase-level granularity sufficient. |
| **Human-in-the-loop review gates** | Engineers must verify AI output before proceeding; table stakes for professional document generation | HIGH | Review UI for verify-phase and review-phase with approve/reject/request-changes workflow. Must pause automation, show diffs/changes, capture feedback in CONTEXT.md. |
| **File upload with drag-and-drop** | Modern web UI standard for reference document management | LOW | Standard dropzone.js or similar for reference files. Multi-file support required. Must handle PDF, DOCX, images. |
| **Document preview (not raw Markdown)** | Engineers need to see rendered output, not source | MEDIUM | Convert Markdown to readable preview. Basic rendering sufficient for v2.0; full DOCX preview deferred. Support Mermaid diagram rendering since v1.0 generates them. |
| **Project list/dashboard** | Multiple concurrent projects expected; need access point | LOW | List view of all projects with status, last modified, project type. Clicking opens project detail view. SQLite metadata query. |
| **Error recovery/resume capability** | Crashes happen; losing hours of AI generation is unacceptable | MEDIUM | Leverage existing v1.0 /doc:resume logic. GUI must detect incomplete state and offer resume. Forward-only strategy already proven. |
| **Export to DOCX** | Final deliverable format for clients; non-negotiable | LOW | Wrapper around existing v1.0 Pandoc + huisstijl.docx export. Download button with progress indicator. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Embedded chat panel for discussion phases** | Inline AI discussion feels natural vs switching tools; maintains context within workflow | MEDIUM | Chat UI embedded in phase view during discuss-phase. Pre-populate with v1.0 prompts from /doc:discuss-phase. Conversation history stored in CONTEXT.md. Differentiates from generic chatbot by being workflow-aware. |
| **Shared reference library + per-project overrides** | Team knowledge accumulation; new projects inherit standards but can customize | MEDIUM | Two-tier architecture: global shared library (read-only for engineers, admin-managed) + per-project uploads that override/supplement. Tagging/categorization for findability. Unique to domain-specific tools. |
| **Confidence-based SDS typicals matching** | Prevents hallucinated SDS content; shows "NEW TYPICAL NEEDED" for unknown equipment | HIGH | Surface existing v1.0 CATALOG.json matching + confidence scores in GUI. Visual indication when confidence < threshold. Shows engineer why typical was selected. Builds trust in AI output. |
| **Gap closure loop visualization** | Shows verify → write → re-verify cycles; builds trust by making AI refinement visible | MEDIUM | Visual indicator when gap detected in verification, showing re-planning and re-write cycles. Max 2 iterations per v1.0 logic. Transparency in AI iteration rare in document tools. |
| **Bilingual template system (Dutch/English)** | Single workflow, dual language output; critical for international engineering firms | LOW | Leverage existing v1.0 templates. Language selector in project wizard. Differentiates from English-only AI tools. |
| **Standards compliance overlay (PackML/ISA-88)** | Opt-in verification against industry standards; shows violations with references | HIGH | Conditional loading of standards during verify-phase if enabled. Show compliance violations in separate panel. Links to standard sections. Unique to industrial automation domain. |
| **Phase-specific context isolation** | Prevents AI cross-contamination between parallel sections; shows "what the AI knew" for each section | MEDIUM | Visualize which reference docs/baseline sections were provided to each writer. Debug view for engineers. Builds trust by showing AI's information boundaries. |
| **Project type classification with roadmap generation** | Guided questionnaire determines Type A/B/C/D and generates custom phase structure | MEDIUM | Wizard flow asking about greenfield/brownfield, single-unit/multi-unit. Auto-generates ROADMAP.md. Removes manual planning overhead. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Real-time collaborative editing (Google Docs style)** | "Multiple engineers should write simultaneously" | Document generation is single-engineer workflow per v1.0 design; AI writes in parallel sections but human reviews sequentially. Adds massive complexity (OT/CRDT, conflict resolution) for zero value. Review-phase already handles collaboration. | Use review-phase for team collaboration: one engineer drives, others review/comment. Async by design. |
| **Full auto-generation (zero human input)** | "Just generate the whole document from project name" | Equipment-specific details cannot be inferred (valve specs, safety requirements, client preferences). Results in hallucinated/unsafe content. v1.0 requires discuss-phase input for good reason. | Keep discuss-phase mandatory. Pre-populate with template questions but require engineer confirmation/edits. Trust comes from human-in-loop. |
| **Inline Markdown editing in GUI** | "Let me tweak the AI output directly" | Creates divergence between GUI and file-backed state. v1.0 files are SSOT; editing in GUI breaks CLI compatibility requirement. Also: engineers editing AI output defeats verification loop. | Show preview-only. If changes needed, use review-phase feedback → AI re-writes. Keeps workflow clean and maintains verification integrity. |
| **Database-backed document storage** | "SQLite for everything, not files" | v1.0 constraint: STATE.md must be human-readable and git-trackable. Database opaque to version control, breaks CLI compatibility, removes auditability. | SQLite only for metadata (project list, file references). Documents remain file-based. Hybrid approach gives both searchability and transparency. |
| **Live DOCX preview (Word-perfect rendering)** | "Show exactly what the export will look like" | Requires full Word rendering engine in browser (LibreOffice WASM, Office Online API, or heavy JS library). Export is Pandoc's responsibility; GUI doesn't need pixel-perfect preview. | Markdown preview with Mermaid rendering. DOCX export is download action. Engineers review exported DOCX in Word if pixel-perfection needed. |
| **AI provider selection in GUI** | "Let user choose GPT-4 vs Claude vs local model per project" | v2.0 uses Claude API exclusively per PROJECT.md. Provider abstraction exists for v3.0 local models but not multi-provider. Adds configuration complexity and prompt incompatibility risks. | Backend hardcoded to Claude API. v3.0 milestone adds local model support with provider swap, but single provider per deployment, not per project. |
| **Undo/redo for AI operations** | "Let me undo the verify step" | AI operations are forward-only per v1.0 design (SUMMARY.md as completion proof). Undo implies rollback which conflicts with crash recovery. Also: how do you undo a 3-minute LLM call? | Use review-phase feedback for corrections. Gap closure loop already handles "AI got it wrong, try again" scenario. No undo needed if workflow designed for iteration. |

## Feature Dependencies

```
Project Wizard
    └──creates──> Project State (STATE.md, ROADMAP.md)
                      └──enables──> Phase Timeline View
                                       ├──enables──> Discuss Phase (Chat Panel)
                                       ├──enables──> Plan Phase (Section Planning)
                                       ├──enables──> Write Phase (Progress Feedback)
                                       ├──enables──> Verify Phase (Gap Visualization)
                                       └──enables──> Review Phase (Human-in-Loop UI)

Reference Library Management
    ├──feeds──> Discuss Phase (context for AI)
    ├──feeds──> Write Phase (content source)
    └──feeds──> SDS Generation (typicals matching)

Document Preview
    ├──requires──> Write Phase completion (CONTENT.md exists)
    └──enhanced-by──> Mermaid Rendering (diagrams in preview)

Export to DOCX
    ├──requires──> Complete-FDS or Generate-SDS completion
    └──requires──> Pandoc backend integration

Error Recovery
    ├──requires──> STATE.md parsing
    └──enables──> Resume from any phase

Standards Compliance
    ├──requires──> Verify Phase enabled
    ├──requires──> Standards files loaded (opt-in)
    └──conflicts-with──> Projects without standards requirement (Type A/B often skip)
```

### Dependency Notes

- **Project Wizard creates Project State:** Wizard must generate STATE.md and ROADMAP.md before any phase operations. Timeline view is read-only visualization of this state.
- **Phase Timeline enables phase operations:** Each phase button in timeline triggers corresponding workflow (discuss/plan/write/verify/review). Timeline is navigation hub.
- **Reference Library feeds AI phases:** Upload must complete before discuss-phase. Files stored in per-project directory, referenced in CONTEXT.md for AI prompt context.
- **Document Preview requires Write completion:** Cannot preview non-existent content. Preview disabled until at least one section has CONTENT.md.
- **Export requires completion:** FDS export needs complete-fds completion (STATE.md status check). SDS export needs generate-sds completion.
- **Error Recovery requires STATE parsing:** Resume functionality depends on parsing STATE.md to detect incomplete phases. Must handle corrupted/partial STATE.md gracefully.
- **Standards Compliance conflicts with non-standards projects:** PackML/ISA-88 overhead inappropriate for simple projects. Must be opt-in during wizard, disabled by default.

## MVP Definition

### Launch With (v2.0)

Minimum viable GUI — what's needed to replace CLI for single-engineer workflow.

- [ ] **Project Wizard** — Guided setup for Type A/B/C/D, language, reference upload. Generates STATE.md + ROADMAP.md. Critical path: no wizard = no projects.
- [ ] **Project List Dashboard** — Browse existing projects, see status, open project. Engineers need to find their work.
- [ ] **Phase Timeline View** — Visual representation of ROADMAP phases with completion status. Primary navigation for workflow.
- [ ] **Embedded Chat Panel** — AI discussion interface for discuss-phase. Core differentiator; enables gray area resolution.
- [ ] **Basic Document Preview** — Markdown rendering of CONTENT.md with Mermaid diagrams. Engineers need to see output without exporting.
- [ ] **Progress Feedback for Long Tasks** — SSE/polling for write/verify operations with "Generating Section 3.2..." messages. Prevents "is it frozen?" anxiety.
- [ ] **Human-in-Loop Review UI** — Approve/reject for verify-phase and review-phase. Non-negotiable for professional use.
- [ ] **Reference File Upload** — Drag-and-drop for per-project files. Discuss-phase useless without reference context.
- [ ] **DOCX Export** — Download button wrapping Pandoc export. Final deliverable format.
- [ ] **Error Recovery** — Resume button when STATE.md shows incomplete phase. Crash resilience required for 3-hour generation runs.

### Add After Validation (v2.x)

Features to add once core workflow proven in production.

- [ ] **Shared Reference Library** — Global library with admin management. Wait for team feedback on per-project file pain points. Trigger: "We're uploading the same standards PDF 50 times."
- [ ] **Gap Closure Loop Visualization** — Show verify → re-plan → re-write cycles. Nice transparency but not critical for operation. Trigger: Engineers ask "Why did it take 3 verify cycles?"
- [ ] **Phase-Specific Context Visualization** — Debug view showing which files/baseline sections fed each writer. Builds trust but not MVP. Trigger: "Why didn't the AI include X?"
- [ ] **Standards Compliance Panel** — PackML/ISA-88 verification overlay. Deferred until standards-requiring projects demand it. Trigger: Client requires PackML compliance report.
- [ ] **SDS Typicals Confidence Display** — Show matching scores for CATALOG.json hits. Useful but SDS generation itself is post-FDS. Trigger: Engineers question typical selections.
- [ ] **Document Outline Tree with Jump-to-Section** — Enhanced navigation for large FDS. MVP preview is linear scroll; tree adds polish. Trigger: "FDS too long to scroll."
- [ ] **Batch Export** — Export multiple versions (draft, final, with/without diagrams). Single export covers MVP. Trigger: Engineers manually exporting 4 variants.

### Future Consideration (v3.0+)

Features to defer until product-market fit established and architecture ready.

- [ ] **Local LLM Support** — Provider abstraction ready but requires v3.0 milestone per PROJECT.md. Deferred: API costs manageable, model quality unproven for technical docs.
- [ ] **Multi-user Team Features** — Role-based access, project sharing, activity logs. v2.0 is single-engineer per project. Deferred: Complexity not justified until team workflow clarifies.
- [ ] **Client Portal** — Read-only review access for clients outside engineering team. Scope creep risk. Deferred: Email PDF works for now.
- [ ] **Version Comparison UI** — Diff view between FDS v1.0 and v1.1. Useful but v1.0 /doc:release handles versioning. Deferred: Engineers use Word's compare feature.
- [ ] **Mobile/Tablet UI** — Responsive design for field access. Engineering work is desktop-based. Deferred: No field use cases identified.
- [ ] **API for External Integration** — REST API for CI/CD or third-party tools. Over-engineering for MVP. Deferred: No integration requests yet.
- [ ] **Advanced Search** — Full-text search across all projects. SQLite metadata search sufficient for v2.0. Deferred: Team size doesn't warrant Elasticsearch.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority | Notes |
|---------|------------|---------------------|----------|-------|
| Project Wizard | HIGH | MEDIUM | P1 | Blocking: No projects without wizard |
| Phase Timeline View | HIGH | LOW | P1 | Core navigation; reads STATE.md |
| Chat Panel (Discuss) | HIGH | MEDIUM | P1 | Differentiator; critical for discuss-phase |
| Progress Feedback | HIGH | MEDIUM | P1 | UX disaster without it for 3min LLM calls |
| Human-in-Loop Review | HIGH | HIGH | P1 | Professional requirement; approve/reject workflow |
| Document Preview | HIGH | MEDIUM | P1 | Must see output; Markdown + Mermaid sufficient |
| Reference Upload | HIGH | LOW | P1 | Discuss/write phases need context |
| DOCX Export | HIGH | LOW | P1 | Final deliverable; wraps existing Pandoc |
| Error Recovery | HIGH | MEDIUM | P1 | 3-hour runs can crash; resume essential |
| Project List | HIGH | LOW | P1 | Engineers need project access |
| Shared Library | MEDIUM | MEDIUM | P2 | Nice-to-have; per-project works for MVP |
| Gap Loop Viz | MEDIUM | LOW | P2 | Transparency; not operational need |
| Context Viz | MEDIUM | MEDIUM | P2 | Debug/trust feature; defer to v2.x |
| Standards Panel | MEDIUM | HIGH | P2 | Opt-in; subset of projects need it |
| SDS Confidence Display | MEDIUM | LOW | P2 | SDS post-FDS; can add after FDS proven |
| Document Tree Nav | MEDIUM | MEDIUM | P2 | Polish; linear scroll works for MVP |
| Batch Export | LOW | LOW | P2 | Single export sufficient initially |
| Local LLM | HIGH | HIGH | P3 | v3.0 milestone; architecture ready but deferred |
| Multi-User Features | MEDIUM | HIGH | P3 | v2.0 single-engineer; wait for team workflow clarity |
| Client Portal | LOW | MEDIUM | P3 | Scope creep; email PDF works |
| Version Comparison | LOW | MEDIUM | P3 | Word handles this; low ROI |
| Mobile UI | LOW | HIGH | P3 | Desktop-only workflow; no field use |
| External API | LOW | MEDIUM | P3 | No integrations identified |
| Advanced Search | LOW | HIGH | P3 | Team size doesn't need it |

**Priority key:**
- P1 (Must have for launch): 10 features — Project Wizard, Timeline, Chat, Progress, Review UI, Preview, Upload, Export, Recovery, Project List
- P2 (Should have, add when possible): 7 features — Shared Library, Gap Viz, Context Viz, Standards Panel, SDS Confidence, Tree Nav, Batch Export
- P3 (Nice to have, future consideration): 7 features — Local LLM, Multi-User, Client Portal, Version Diff, Mobile, API, Search

## Existing v1.0 Workflow Integration

The GUI wraps proven v1.0 CLI workflows. Feature dependencies on existing logic:

| v1.0 Command | GUI Feature | Integration Point |
|--------------|-------------|-------------------|
| `/doc:new-fds` | Project Wizard | Backend calls v1.0 classification logic, generates STATE.md + ROADMAP.md |
| `/doc:discuss-phase N` | Chat Panel | Chat messages become discussion prompts; output stored in CONTEXT.md |
| `/doc:plan-phase N` | Timeline "Plan" button | Backend orchestrates wave planning; GUI shows progress |
| `/doc:write-phase N` | Timeline "Write" button + Progress | Backend runs parallel writers; SSE streams section completion |
| `/doc:verify-phase N` | Timeline "Verify" button + Review UI | Backend runs 5-level verification; GUI shows gaps for human review |
| `/doc:review-phase N` | Review UI with feedback | Human provides approve/reject/feedback; stored in CONTEXT.md |
| `/doc:complete-fds` | Timeline final step | Backend assembles FDS; enables export |
| `/doc:generate-sds` | SDS generation button | Backend scaffolds SDS with typicals matching |
| `/doc:export` | Export to DOCX button | Backend calls Pandoc; GUI streams file download |
| `/doc:status` | Project List + Timeline | Backend parses STATE.md; GUI visualizes status |
| `/doc:resume` | Recovery/Resume button | Backend detects incomplete phase; resumes forward-only |
| `/doc:release` | Version management UI | Backend handles internal/client versioning |
| `/doc:check-standards` | Standards compliance panel | Backend runs PackML/ISA-88 checks if enabled |

**Key constraint:** GUI does not reimplement v1.0 logic. Backend wraps existing workflows. Frontend provides visual interface and captures human input.

## Competitor Feature Analysis

Web-based document generation tools comparison (as of 2026):

| Feature Category | Generic Doc Gen (Templafy, Docupilot) | AI Writing (Jasper, Copy.ai) | Engineering DMS (eQuorum, OpenText) | Our Approach (GSD-Docs GUI) |
|------------------|--------------------------------------|------------------------------|--------------------------------------|------------------------------|
| **Template-based generation** | Heavy template libraries, drag-drop builders | Prompt-based, minimal templates | CAD integration, drawing mgmt | Domain-specific templates (FDS/SDS section structures) |
| **AI integration** | Limited: autocomplete, suggestions | Core feature: full AI writing | Emerging: AI search, GenAI assist | Core: AI writes with human-in-loop verification |
| **Workflow automation** | Linear approval flows | No structured workflow | Complex approval chains, revision control | Phase-based with discuss→plan→write→verify→review cycle |
| **Collaboration** | Real-time editing, comments | Share/export only | Multi-user with locking, markup | Async review-phase, single engineer per project |
| **Preview/Export** | Live preview, multi-format export | Plain text, basic export | Native CAD viewers, PDF | Markdown preview + DOCX export via Pandoc |
| **Reference Management** | Central asset library | No reference system | Document vaults, version control | Two-tier: shared library + per-project uploads |
| **Domain Specificity** | Industry-agnostic | Generic business writing | Engineering-aware but CAD-focused | Industrial automation (FDS/SDS) specialist |
| **Human-in-Loop** | Manual review steps | No verification | Approval workflows | Structured verify/review phases with gap detection |
| **Standards Compliance** | Template enforcement only | None | Audit trails, compliance reporting | Opt-in PackML/ISA-88 verification |
| **Pricing Model** | Per-user SaaS subscription | Usage-based (API calls) | Enterprise licensing | Team server (self-hosted), Claude API costs |

**Competitive positioning:**
- **vs Generic Doc Gen:** We have AI writing, they have broader template variety. Win: Domain expertise (FDS/SDS structures).
- **vs AI Writing:** We have structured workflow + verification, they have simplicity. Win: Professional quality gates.
- **vs Engineering DMS:** We have AI generation, they have mature collaboration. Win: Document creation speed (hours not weeks).

**Feature gaps we accept:**
- No real-time collaboration (engineering DMS have this) — Our workflow is single-engineer by design
- No broad template marketplace (generic doc gen have this) — Deep not wide: FDS/SDS only
- No CAD integration (engineering DMS have this) — Documents only, not drawings per PROJECT.md scope

**Features we uniquely offer:**
- Confidence-scored SDS typicals matching (prevents hallucination)
- Gap closure loop with re-verification (quality iteration)
- Bilingual template system (Dutch/English from same workflow)
- Phase-specific context isolation (shows "what AI knew")
- Standards compliance as workflow step not post-hoc audit

## Sources

**Web-Based Document Generation Best Practices:**
- [Best Enterprise Document Assembly Tools: Top 12 Picks for 2026](https://www.edocgen.com/blogs/top12-document-assembly-tools-2026)
- [What is document generation? (The 5 best tools in 2026)](https://www.templafy.com/what-is-document-generation/)
- [18 Best Document Generation Software Reviewed in 2026](https://thedigitalprojectmanager.com/tools/best-document-generation-software/)

**AI Document Assistant Interface Patterns:**
- [13 Best AI Document Generation Tools for 2026](https://venngage.com/blog/best-ai-document-generator/)
- [31 Chatbot UI Examples from Product Designers](https://www.eleken.co/blog-posts/chatbot-ui-examples)
- [AI chat interfaces could become the primary user interface to read documentation](https://idratherbewriting.com/blog/ai-chat-interfaces-are-the-new-user-interface-for-docs)

**Project Wizard UX Design:**
- [The Ultimate Guide to Web Wizard Design](https://lab.interface-design.co.uk/the-ultimate-guide-to-web-wizard-design-5b6fb4201f94)
- [Wizards: Definition and Design Recommendations - NN/G](https://www.nngroup.com/articles/wizards/)
- [Wizard Design Pattern by Nick Babich](https://uxplanet.org/wizard-design-pattern-8c86e14f2a38)
- [Creating a setup wizard (and when you shouldn't) - LogRocket](https://blog.logrocket.com/ux-design/creating-setup-wizard-when-you-shouldnt/)

**Real-Time Progress Feedback:**
- [Building Progress Bars for the Web with Django and Celery](https://www.saaspegasus.com/guides/django-celery-progress-bars/)
- [Providing Real-Time Feedback About Long-Running Task with SignalR](https://blog.stevanfreeborn.com/providing-real-time-feedback-about-long-running-task-with-signal-r)
- [How to create progress indicator UI for better usability?](https://cieden.com/book/atoms/progress-indicator/progress-indicator-ui)

**Document Preview/Rendering:**
- [How to Preview Document or File in Browser for SaaS](https://ardas-it.com/how-to-preview-document-or-file-in-a-browser-for-saas)
- [Word Document Online Preview Demo](https://develop365.gitlab.io/word-preview/)
- [How To Preview Doc And PDF Files In Browser](https://selleo.com/blog/how-to-preview-doc-and-pdf-files-in-browser)

**File Upload/Drag-Drop:**
- [Dropzone.js](https://www.dropzone.dev/)
- [File drag and drop - Web APIs | MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API/File_drag_and_drop)
- [How to Implement Drag and Drop in Document Upload UI](https://blog.filestack.com/implement-drag-drop-document-upload-ui/)

**Workflow Dashboards:**
- [What is a Timeline Workflow and How to Manage it? – Businessmap](https://knowledgebase.businessmap.io/hc/en-us/articles/360028419032-What-is-a-Timeline-Workflow-and-How-to-Manage-it)
- [Tree view - Carbon Design System](https://carbondesignsystem.com/components/tree-view/usage/)
- [Interaction Design for Trees](https://medium.com/@hagan.rivers/interaction-design-for-trees-5e915b408ed2)

**Team Collaboration Patterns:**
- [Document Collaboration: Maximize Team Efficiency | Zoom](https://www.zoom.com/en/products/collaborative-docs/features/document-collaboration/)
- [Enhancing Collaboration and Productivity with Multi-User Document Management](https://www.docmoto.com/blog/enhancing-collaboration-and-productivity-with-multi-user-document-management/)

**Engineering Document Management:**
- [EDMS Guide: Engineering Document Management Systems | Accruent](https://www.accruent.com/resources/knowledge-hub/what-is-an-engineering-document-management-system)
- [Understanding an Engineering Workflow | eQuorum](https://www.equorum.com/blog/understanding-an-engineering-workflow/)
- [Document Approval Workflow: Steps to Create](https://www.cflowapps.com/document-approval-workflow/)

**Technical Documentation Automation:**
- [12 AI Tools for Technical Writers](https://clickhelp.com/clickhelp-technical-writing-blog/ai-tools-for-technical-writers/)
- [AI in technical writing: complete guide for 2026](https://instrktiv.com/en/ai-in-technical-writing/)

**Document Tagging/Reference Management:**
- [Document Tagging for Technical Writing: Best Practices | Docsie](https://www.docsie.io/blog/glossary/document-tagging/)
- [How content tagging enables better content management | Contentful](https://www.contentful.com/blog/content-tagging/)

**Human-in-the-Loop AI Patterns:**
- [Human-in-the-loop in AI workflows: Meaning and patterns | Zapier](https://zapier.com/blog/human-in-the-loop/)
- [Human-in-the-Loop for AI Agents: Best Practices | Permit.io](https://www.permit.io/blog/human-in-the-loop-for-ai-agents-best-practices-frameworks-use-cases-and-demo)
- [Human-in-the-Loop AI Review Queues: Workflow Patterns That Scale (2025)](https://alldaystech.com/guides/artificial-intelligence/human-in-the-loop-ai-review-queue-workflows)
- [Human-in-the-Loop AI in Document Workflows - Best Practices | Parseur](https://parseur.com/blog/hitl-best-practices)

**Real-Time Communication Architecture:**
- [Polling vs. Long Polling vs. SSE vs. WebSockets vs. Webhooks](https://blog.algomaster.io/p/polling-vs-long-polling-vs-sse-vs-websockets-webhooks)
- [How to set up WebSockets, Server-Sent Events, and Long Polling for Real-Time Features in SaaS Products](https://venturenox.com/blog/websockets-server-sent-events-and-long-polling-for-real-time-features-in-saas-products/)
- [WebSockets vs Server-Sent Events (SSE) | Ably](https://ably.com/blog/websockets-vs-sse)

---
*Feature research for: GSD-Docs Industrial v2.0 GUI*
*Researched: 2026-02-14*
*Confidence: HIGH — grounded in web UI patterns, AI document tools, engineering workflows, and existing v1.0 constraints*
