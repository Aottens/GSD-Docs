# Feature Landscape

**Domain:** Industrial FDS/SDS documentation generation (Claude Code plugin)
**Researched:** 2026-02-06
**Confidence:** MEDIUM-HIGH (specification is detailed; domain knowledge verified against industry sources)

---

## Table Stakes

Features users expect. Missing any of these means the framework does not deliver on its core promise of "brief to verified FDS."

### TS-1: Project Classification and Scaffolding

| Aspect | Detail |
|--------|--------|
| **Feature** | Classify project (Type A/B/C/D), generate appropriate folder structure, ROADMAP, PROJECT.md |
| **Why Expected** | Engineers need the framework to understand their project type before anything else. A tool that forces one-size-fits-all structure is useless for a small TWN (Type D, 30 min) and equally useless for a 100-motor newbuild (Type A). |
| **Complexity** | Medium |
| **Spec Reference** | SPECIFICATION.md section 3, section 4.1 (`/doc:new-fds`) |
| **Dependencies** | None -- this is the entry point |
| **Notes** | Must handle the 4 types cleanly: Type A (new + standards), Type B (new flex), Type C (mod large + BASELINE.md), Type D (mod small/TWN). Classification drives everything downstream. |

### TS-2: Structured Discuss-Plan-Write-Verify Workflow

| Aspect | Detail |
|--------|--------|
| **Feature** | Phase-based workflow: discuss gray areas, plan sections, write content, verify goals |
| **Why Expected** | This IS the product. Without the discuss-plan-write-verify loop, you just have a fancy template. The GSD workflow pattern is the core value proposition -- structured AI-assisted authoring with human decisions captured at the right moments. |
| **Complexity** | High (4 distinct commands, each with specific behavior) |
| **Spec Reference** | SPECIFICATION.md sections 4.2-4.5 |
| **Dependencies** | TS-1 (project must exist) |
| **Notes** | Each step must produce specific artifacts: CONTEXT.md (discuss), PLAN.md (plan), CONTENT.md + SUMMARY.md (write), VERIFICATION.md (verify). The loop is the product. |

### TS-3: Equipment Module Documentation Structure

| Aspect | Detail |
|--------|--------|
| **Feature** | Structured EM documentation: description, operating states, parameters (with ranges/units), interlocks (with conditions/actions), I/O lists (with tags/types) |
| **Why Expected** | This is the core content of any FDS. Industry practice demands that every equipment module has states, parameters, interlocks, and I/O documented in structured tables. An FDS without these is not an FDS -- it is a narrative document. Source: IACS Engineering, RealPars, industry consensus. |
| **Complexity** | Medium (template-driven, but domain knowledge critical) |
| **Spec Reference** | SPECIFICATION.md section 5.1.1 (templates/fds/section-equipment-module.md) |
| **Dependencies** | TS-2 (written during write-phase) |
| **Notes** | Tables must include: state entry/exit conditions, parameter ranges with units, interlock priorities, I/O signal tags with types (DI/DO/AI/AO). Missing ranges or units on parameters is a verification gap -- spec already catches this. |

### TS-4: Goal-Backward Verification

| Aspect | Detail |
|--------|--------|
| **Feature** | Verification that checks whether goals are achieved (not just whether files exist). Detects stubs, missing content, inconsistencies with decisions. |
| **Why Expected** | Task completion does not equal goal achievement. A section can be written but still miss critical information. Manual FDS review is the biggest bottleneck in industrial projects -- 50% of FDS time is spent reviewing and correcting. Automated verification that catches gaps before human review is a minimum viable feature. |
| **Complexity** | High (requires understanding goal semantics, not just file presence) |
| **Spec Reference** | SPECIFICATION.md section 4.5 |
| **Dependencies** | TS-2 (must have content to verify), TS-3 (must know what complete EM documentation looks like) |
| **Notes** | Five verification levels: Exists, Substantive, Complete, Consistent (with CONTEXT.md decisions), Standards (PackML/ISA-88 compliance). All five are table stakes. |

### TS-5: Gap Closure Loop

| Aspect | Detail |
|--------|--------|
| **Feature** | When verification finds gaps: generate fix plans, write fixes, re-verify. Automatic cycle until PASS. |
| **Why Expected** | Without gap closure, verification is just reporting -- it finds problems but does not fix them. The engineer is back to manual correction. The loop (verify -> plan --gaps -> write -> re-verify) is what makes the framework self-correcting. |
| **Complexity** | Medium (reuses existing plan/write/verify commands with --gaps flag) |
| **Spec Reference** | SPECIFICATION.md section 4.5 (GAPS_FOUND flow) |
| **Dependencies** | TS-4 (gaps must be detected first) |
| **Notes** | Fix plans should be minimal and targeted -- only addressing the specific gap, not rewriting entire sections. |

### TS-6: State Management and Progress Tracking

| Aspect | Detail |
|--------|--------|
| **Feature** | STATE.md tracking current position, completed phases, decisions, blockers. Survives /clear and session changes. |
| **Why Expected** | Industrial FDS projects span days to weeks. Claude Code sessions are ephemeral. Without persistent state, every session requires the engineer to manually re-orient the AI. STATE.md is what makes multi-session work possible. |
| **Complexity** | Low-Medium |
| **Spec Reference** | SPECIFICATION.md section 2.2, section 9.7 |
| **Dependencies** | TS-1 (STATE.md created at project init) |
| **Notes** | Must include: current phase, current plan, status, list of completed items, decisions log, blockers. Updated before and after each operation for crash recovery. |

### TS-7: Fresh Context Per Write Task

| Aspect | Detail |
|--------|--------|
| **Feature** | Each section write task loads only: PROJECT.md + CONTEXT.md + current PLAN.md + standards. No cross-contamination from other sections. |
| **Why Expected** | Context pollution is the primary failure mode of AI-assisted multi-section writing. If the AI carries information from EM-100 while writing EM-200, it will inadvertently mix parameters, states, or interlocks. Fresh context is essential for correctness in a domain where incorrect cross-talk between equipment modules is a safety concern. |
| **Complexity** | Medium (requires subagent spawning pattern from GSD) |
| **Spec Reference** | SPECIFICATION.md section 4.4 |
| **Dependencies** | TS-2 (write-phase command) |
| **Notes** | This is a constraint, not a feature in the user-visible sense. But it is table stakes for correctness. The subagent pattern from GSD handles this naturally. |

### TS-8: Document Assembly (complete-fds)

| Aspect | Detail |
|--------|--------|
| **Feature** | Merge all phase CONTENT.md files into a single FDS document with proper section numbering, cross-references, and table of contents. |
| **Why Expected** | The FDS must be delivered as a single coherent document, not a folder of markdown fragments. Engineers deliver one FDS document to clients. Assembly with proper numbering and cross-references is the minimum expected output. |
| **Complexity** | Medium-High (section numbering, cross-ref resolution, orphan detection) |
| **Spec Reference** | SPECIFICATION.md section 4.7 |
| **Dependencies** | All phases must be verified (TS-4) |
| **Notes** | Must handle: section renumbering (phase-based sections -> document sections), cross-reference resolution, broken reference detection, orphan section warning. |

### TS-9: DOCX Export with Corporate Styling

| Aspect | Detail |
|--------|--------|
| **Feature** | Export final FDS/SDS as .docx with corporate template (heading styles, headers/footers, logo, page numbering, table formatting). |
| **Why Expected** | Industrial clients receive DOCX documents. Nobody delivers an FDS as a markdown file or PDF-from-browser. Corporate styling is non-negotiable -- the document must look professional with the integrator's branding. Source: industry standard practice, every industrial integrator. |
| **Complexity** | Medium (Pandoc + reference docx template) |
| **Spec Reference** | SPECIFICATION.md section 8 |
| **Dependencies** | TS-8 (document must be assembled first), external: Pandoc + mermaid-cli installed |
| **Notes** | Pandoc with --reference-doc is the proven approach. Mermaid diagrams must be pre-rendered to PNG before Pandoc conversion. huisstijl.docx template must be provided by the integrator. |

### TS-10: Resume/Recovery

| Aspect | Detail |
|--------|--------|
| **Feature** | Resume work after session interruption, crash, or /clear. Detect incomplete operations, offer continuation options. |
| **Why Expected** | LLM sessions crash. Networks timeout. Engineers close laptops. A tool that loses progress is not a professional tool. Forward-only recovery (what is written stays written, retry only incomplete items) is the minimum. |
| **Complexity** | Medium |
| **Spec Reference** | SPECIFICATION.md section 4.11, section 9.7 |
| **Dependencies** | TS-6 (STATE.md must track operation checkpoints) |
| **Notes** | Partial write detection: CONTENT.md < 200 chars or [TO BE COMPLETED] marker or abrupt ending. Recovery is forward-only -- never rollback completed work. |

---

## Differentiators

Features that set this framework apart from manual documentation or basic template-filling. Not expected by default, but significantly valuable.

### D-1: Gray Area Identification (discuss-phase)

| Aspect | Detail |
|--------|--------|
| **Feature** | AI identifies domain-specific gray areas for each phase type (e.g., "What is the settling time for the weigh cell?" for equipment phases, "What protocol for external interface?" for interface phases) before writing begins. |
| **Value Proposition** | Manual FDS writing discovers gray areas mid-writing, causing rework. discuss-phase front-loads these decisions. This alone can save 20-30% of revision cycles. The AI brings domain knowledge to ask questions the engineer might not think to ask until later. |
| **Complexity** | Medium-High (requires domain knowledge embedded in prompts per phase type) |
| **Spec Reference** | SPECIFICATION.md section 4.2 |
| **Dependencies** | TS-1 (must know project type), phase-specific gray area catalogs |
| **Notes** | Gray areas differ by content type: Equipment (capacities, tolerances, failure modes, timing), Interfaces (protocols, polling rates, error handling), HMI (layout, navigation, alarm presentation), Safety (risk categories, interlock priorities). The quality of discuss-phase questions determines the quality of the entire FDS. |

### D-2: FDS-to-SDS Transformation with Typicals Matching

| Aspect | Detail |
|--------|--------|
| **Feature** | Automatically transform FDS equipment descriptions into SDS software design, matching against a typicals library (CATALOG.json) of reusable function blocks. |
| **Value Proposition** | SDS creation is highly repetitive -- most equipment modules map to known function block patterns. Automating this mapping saves 40-60% of SDS writing time (source: Rockwell reusable process object libraries claim 40% reduction). When no match exists, the system flags "NEW TYPICAL NEEDED" rather than hallucinating. |
| **Complexity** | High (semantic matching, catalog maintenance, traceability) |
| **Spec Reference** | SPECIFICATION.md section 4.8, section 7 |
| **Dependencies** | TS-8 (FDS must be complete), CATALOG.json must be populated |
| **Notes** | Generates TRACEABILITY.md linking each FDS requirement to SDS implementation. The typicals catalog is a long-term investment that grows with each project. Initial catalog will be small -- flag unmatched equipment explicitly. |

### D-3: Dynamic ROADMAP Evolution

| Aspect | Detail |
|--------|--------|
| **Feature** | After System Overview phase, automatically analyze identified units and propose expanded ROADMAP with logically grouped phases (3-5 units per phase). |
| **Value Proposition** | Large projects (20+ units) are unworkable with static phase structure. A discuss-phase with 60+ gray area questions is chaos. Dynamic grouping keeps each phase manageable while adapting to project complexity. No manual planning tool does this automatically. |
| **Complexity** | Medium-High |
| **Spec Reference** | SPECIFICATION.md section 3.5 |
| **Dependencies** | TS-2 (System Overview phase must be complete), TS-4 (verification triggers evolution) |
| **Notes** | Grouping criteria: functional area (primary), process sequence (secondary), max 7 units per phase (target 3-5). Engineer can accept, adjust, or reject proposed grouping. Also applies to Type C modifications (group by change area). |

### D-4: Cross-Reference Registry and Validation

| Aspect | Detail |
|--------|--------|
| **Feature** | Automatically track all cross-references between sections (CROSS-REFS.md), validate at verify-phase (warn) and complete-fds (block on broken refs), detect orphan sections. |
| **Value Proposition** | Cross-reference consistency is the single most labor-intensive quality check in FDS review. Manual cross-ref validation in a 100-page FDS takes hours and still misses issues. Automated tracking and validation eliminates an entire category of review effort. |
| **Complexity** | Medium-High |
| **Spec Reference** | SPECIFICATION.md section 9.6 |
| **Dependencies** | TS-2 (refs created during writing), TS-8 (final validation at assembly) |
| **Notes** | Two validation levels: warn-only during phases (targets may not exist yet), strict-block at complete-fds. The --force flag allows generation with [BROKEN REF] placeholders and DRAFT suffix. Orphan detection catches sections nobody references (possible dead content). |

### D-5: Knowledge Transfer Documents

| Aspect | Detail |
|--------|--------|
| **Feature** | Automatically generate RATIONALE.md (why decisions were made), EDGE-CASES.md (failure modes and recovery), and Fresh Eyes review (simulated new-engineer read). |
| **Value Proposition** | FDS documents tell you WHAT the system does. RATIONALE.md tells you WHY. This is the information that is always lost -- six months later, nobody remembers why the settling time is 3 seconds. EDGE-CASES.md captures failure modes that are often missing from traditional FDS. Fresh Eyes catches ambiguities before the client does. |
| **Complexity** | Medium |
| **Spec Reference** | SPECIFICATION.md section 9.1-9.4 |
| **Dependencies** | TS-2 (generated during discuss/write/verify phases) |
| **Notes** | Timing is critical: RATIONALE at discuss (when decisions are made), EDGE-CASES at write (when failure modes surface), Fresh Eyes after verify PASS (when content is complete). These are triggered automatically at the right moments, not manual afterthoughts. |

### D-6: Standards-as-Opt-In (PackML, ISA-88)

| Aspect | Detail |
|--------|--------|
| **Feature** | PackML state model and ISA-88 equipment hierarchy loaded conditionally based on PROJECT.md settings. Never pushed -- only applied when explicitly enabled. Verification checks compliance when enabled. |
| **Value Proposition** | Many integrators work with clients who require PackML/ISA-88 compliance, but many do not. A tool that forces standards alienates half the market. Opt-in standards with automatic compliance checking when enabled serves both audiences. |
| **Complexity** | Medium |
| **Spec Reference** | SPECIFICATION.md section 6 |
| **Dependencies** | TS-1 (standards config in PROJECT.md), TS-4 (compliance checked at verify) |
| **Notes** | When PackML enabled: exact state names enforced (IDLE, STARTING, EXECUTE, etc.), state transitions validated, modes checked. When ISA-88 enabled: terminology enforced (Unit, Equipment Module, Control Module), hierarchy depth validated. When disabled: engineer uses their own structure freely. |

### D-7: Parallel Wave-Based Writing

| Aspect | Detail |
|--------|--------|
| **Feature** | Group independent sections into waves and write them in parallel using subagents, each with fresh context. |
| **Value Proposition** | A phase with 6 equipment modules takes 6x as long sequentially. Wave-based parallelism (from GSD) cuts wall-clock time significantly. With 4 parallel agents, a 6-section phase drops from ~30 min to ~10 min. |
| **Complexity** | Medium (reuses GSD subagent pattern) |
| **Spec Reference** | SPECIFICATION.md section 4.4 |
| **Dependencies** | TS-7 (fresh context enables safe parallelism) |
| **Notes** | Wave ordering respects dependencies: foundation sections first, dependent sections in later waves. Each subagent produces CONTENT.md + SUMMARY.md. Dependency analysis determines wave assignments during plan-phase. |

### D-8: SUMMARY.md for AI Context Efficiency

| Aspect | Detail |
|--------|--------|
| **Feature** | Per-section 150-word summaries (facts only, no prose) that allow AI agents to understand section content without loading full CONTENT.md. |
| **Value Proposition** | Cross-reference checking and verification need to understand what is in each section. Loading all CONTENT.md files would blow the context window. SUMMARY.md provides a compact representation that enables multi-section awareness without context pollution. This is an AI-native feature that has no manual equivalent. |
| **Complexity** | Low |
| **Spec Reference** | SPECIFICATION.md section 4.4 (SUMMARY.md format) |
| **Dependencies** | TS-2 (generated alongside CONTENT.md during write-phase) |
| **Notes** | Must include: factual counts (states, parameters, interlocks, I/O), key decisions, dependencies on other sections, cross-refs. Format is strictly structured -- not a paragraph summary but a structured data block. |

### D-9: Version Management

| Aspect | Detail |
|--------|--------|
| **Feature** | vMAJOR.MINOR versioning with clear semantics: internal drafts (v0.x), client releases (v1.0, v2.0), post-feedback iterations (v1.x). FDS and SDS versioned independently. |
| **Value Proposition** | Industrial projects have formal release cycles to clients. Mixing internal drafts with client versions causes confusion and contractual issues. Clear version semantics with `/doc:release` commands prevent accidental client exposure of drafts. |
| **Complexity** | Low |
| **Spec Reference** | SPECIFICATION.md section 9.5 |
| **Dependencies** | TS-6 (versions tracked in STATE.md) |
| **Notes** | SDS references its source FDS version on the frontpage. SDS can version independently (typicals update, SCL refactor) without FDS change. Release history maintained in STATE.md. |

### D-10: Modification Project Support (BASELINE.md)

| Aspect | Detail |
|--------|--------|
| **Feature** | For Type C/D modification projects: capture existing system as BASELINE.md, generate only delta documentation. AI instructed to treat baseline as given and describe only changes. |
| **Value Proposition** | Modification projects are the majority of industrial automation work (roughly 60-70% of projects are modifications, not greenfield). A tool that only handles new builds misses the primary use case. Delta documentation prevents the AI from suggesting rewrites of working systems. |
| **Complexity** | Medium |
| **Spec Reference** | SPECIFICATION.md section 3.4 |
| **Dependencies** | TS-1 (BASELINE.md generated during new-fds for Type C/D) |
| **Notes** | BASELINE.md has explicit instructions: "AI MUST treat this as given. ONLY describe the DELTA." This prevents the most common AI failure mode in modification projects -- suggesting improvements to systems that are working and contractually unchanged. |

### D-11: ENGINEER-TODO.md for Complex Diagrams

| Aspect | Detail |
|--------|--------|
| **Feature** | When diagrams exceed Mermaid complexity limits (>15 nodes, >10 states, >4 sequence participants), automatically add to ENGINEER-TODO.md with description, section reference, and priority. |
| **Value Proposition** | Honest about AI limitations. Rather than generating broken or unreadable diagrams, the system flags them for human creation in proper tools (Visio, Draw.io). This prevents the quality trap of "AI-generated but unreadable" diagrams. |
| **Complexity** | Low |
| **Spec Reference** | SPECIFICATION.md section 8.2.3 |
| **Dependencies** | TS-8 (generated at complete-fds) |
| **Notes** | Triggers: Mermaid syntax error at >15 nodes, state diagram >10 states, sequence >4 participants, nested subgraphs >2 levels. Each TODO item includes: section reference, diagram type, description, priority. |

---

## Anti-Features

Features to explicitly NOT build. Common mistakes in this domain that would reduce value or create false confidence.

### AF-1: PLC Code Generation

| Anti-Feature | Why Avoid | What to Do Instead |
|---|---|---|
| Generating actual PLC code (SCL, Ladder, Structured Text) from the SDS | SDS describes software DESIGN, not executable code. PLC code generation from natural language descriptions is unreliable and potentially unsafe in industrial contexts. A valve that opens when it should close because of a code generation error is a safety incident. Engineers must write and test code themselves. | SDS describes function block structure, interfaces, parameters, and behavior. The engineer uses this as a specification for manual coding. CATALOG.json provides typicals as reference, not as deployed code. |

### AF-2: Real-Time Collaboration / Multi-User Editing

| Anti-Feature | Why Avoid | What to Do Instead |
|---|---|---|
| Google Docs-style real-time multi-user editing of FDS sections | Adds massive complexity (conflict resolution, locking, merge) for a use case that rarely exists. FDS writing is typically done by one engineer or a small team taking turns. The review cycle (review-phase) is the collaboration mechanism. | Use `/doc:review-phase` for structured client/engineer review. Use git for version history. The framework is single-user at write time, multi-stakeholder at review time. This matches actual industrial workflows. |

### AF-3: Automated P&ID / Electrical Diagram Generation

| Anti-Feature | Why Avoid | What to Do Instead |
|---|---|---|
| Generating P&ID (Process & Instrumentation Diagrams) or electrical schematics | These are engineering drawings governed by strict standards (ISA-5.1 for P&ID, IEC 61082 for electrical). They require CAD tools (AutoCAD, EPLAN, Visio) and professional engineering review. AI-generated P&IDs would be at best decorative and at worst dangerously misleading. | Reference external Engineering Package as attachments. Optionally embed pre-existing diagrams as images. P&IDs are INPUT to the FDS process, not OUTPUT. |

### AF-4: Natural Language Requirements Extraction from Meetings

| Anti-Feature | Why Avoid | What to Do Instead |
|---|---|---|
| Automatically extracting requirements from meeting transcripts or emails | Requirements in industrial automation must be explicit, validated, and traceable. Automatically extracted requirements are by definition unvalidated. False requirements are worse than missing requirements -- they cause builds that don't match needs. | The discuss-phase IS the structured requirements capture mechanism. The engineer drives the conversation, the AI asks clarifying questions, decisions are explicitly captured in CONTEXT.md. Human-in-the-loop is not a limitation -- it is the quality mechanism. |

### AF-5: Full-Auto Mode (No Human Decisions)

| Anti-Feature | Why Avoid | What to Do Instead |
|---|---|---|
| "Generate entire FDS from project brief with zero human input" | This would produce a technically plausible but factually wrong document. Equipment capacities, failure modes, safety requirements, and client-specific decisions CANNOT be inferred from a brief. The 2025 Stack Overflow survey found 46% of developers do not trust AI accuracy -- in industrial automation, the stakes are higher. | The discuss-plan-write-verify workflow is deliberately human-in-the-loop. The AI structures the work and drafts content. The engineer makes decisions and validates output. This produces documents that are both efficient AND trustworthy. |

### AF-6: Database-Backed State Management

| Anti-Feature | Why Avoid | What to Do Instead |
|---|---|---|
| Using SQLite/PostgreSQL for state tracking instead of STATE.md | Adds deployment complexity, requires database setup, makes state opaque (not human-readable), and breaks the "everything is markdown" principle. Engineers need to be able to read and fix STATE.md manually when things go wrong. | STATE.md as flat file. Human-readable, git-trackable, manually editable. Complexity budget should go into document quality, not infrastructure. |

### AF-7: Integrated Review/Approval Workflow (BPM)

| Anti-Feature | Why Avoid | What to Do Instead |
|---|---|---|
| Built-in approval chains, digital signatures, routing to reviewers | This is a document management system feature, not a document generation feature. Building this duplicates SharePoint/Documentum/etc. and diverts effort from the core value proposition. | Generate the FDS document. Hand it off to whatever approval system the client uses. review-phase captures feedback, but the formal approval process is outside scope. |

### AF-8: Client-Specific Knowledge Base / RAG System

| Anti-Feature | Why Avoid | What to Do Instead |
|---|---|---|
| Building a retrieval-augmented generation system that indexes previous FDS documents for the same client | Massive infrastructure investment (vector DB, embedding pipeline, retrieval tuning) for marginal benefit. Previous FDS documents may be outdated, may reference decommissioned equipment, and may contain errors that would propagate. The typicals library (CATALOG.json) handles the "reuse" case cleanly. | CATALOG.json for reusable function block patterns. BASELINE.md for modification context. These are curated, version-controlled knowledge sources -- not a dump of old documents. |

---

## Feature Dependencies

```
TS-1: Project Classification
  |
  +---> TS-6: State Management
  |       |
  |       +---> TS-10: Resume/Recovery
  |
  +---> TS-2: Discuss-Plan-Write-Verify Workflow
  |       |
  |       +---> TS-3: EM Documentation Structure
  |       |
  |       +---> TS-7: Fresh Context Per Task
  |       |       |
  |       |       +---> D-7: Parallel Wave Writing
  |       |
  |       +---> TS-4: Goal-Backward Verification
  |       |       |
  |       |       +---> TS-5: Gap Closure Loop
  |       |       |
  |       |       +---> D-3: Dynamic ROADMAP Evolution
  |       |
  |       +---> D-1: Gray Area Identification
  |       |
  |       +---> D-5: Knowledge Transfer (RATIONALE, EDGE-CASES, Fresh Eyes)
  |       |
  |       +---> D-8: SUMMARY.md (generated alongside CONTENT.md)
  |
  +---> D-6: Standards Opt-In (PackML/ISA-88)
  |
  +---> D-10: Modification Support (BASELINE.md)
  |
  +---> TS-8: Document Assembly (complete-fds)
          |
          +---> D-4: Cross-Reference Validation
          |
          +---> D-11: ENGINEER-TODO.md
          |
          +---> TS-9: DOCX Export
          |
          +---> D-2: FDS-to-SDS Transformation
          |
          +---> D-9: Version Management
```

### Dependency Ordering Rationale

1. **TS-1 must come first** -- everything depends on project classification
2. **TS-2 is the core loop** -- discuss/plan/write/verify is the backbone
3. **TS-3 + TS-7 enable TS-4** -- you need structured content and isolation before verification makes sense
4. **TS-4 enables TS-5 and D-3** -- gap closure and roadmap evolution trigger from verification
5. **TS-8 is the assembly gate** -- cross-refs, export, SDS all depend on assembled FDS
6. **D-2 (SDS) comes last** -- requires complete, verified FDS plus populated CATALOG.json

---

## MVP Recommendation

For MVP (first usable version), prioritize in this order:

### Must Have for MVP

1. **TS-1** -- Project Classification and Scaffolding
2. **TS-2** -- Discuss-Plan-Write-Verify Workflow (core loop)
3. **TS-3** -- Equipment Module Documentation Structure (templates)
4. **TS-6** -- State Management (multi-session survival)
5. **TS-7** -- Fresh Context Per Task (correctness guarantee)
6. **TS-4** -- Goal-Backward Verification (quality gate)
7. **TS-5** -- Gap Closure Loop (self-correction)
8. **D-1** -- Gray Area Identification (differentiates from "just a template")

### Should Have for MVP

9. **TS-10** -- Resume/Recovery (professional reliability)
10. **TS-8** -- Document Assembly (usable output)
11. **TS-9** -- DOCX Export (deliverable format)
12. **D-8** -- SUMMARY.md (enables efficient verification)

### Defer to Post-MVP

- **D-2** (FDS-to-SDS): Requires CATALOG.json investment; FDS alone is valuable
- **D-3** (Dynamic ROADMAP): Start with static roadmaps; add evolution when handling real large projects
- **D-4** (Cross-Reference Validation): Valuable but complex; manual cross-ref checking is tolerable for v1
- **D-5** (Knowledge Transfer): Nice-to-have; RATIONALE and EDGE-CASES can be manually maintained initially
- **D-6** (Standards Opt-In): Start with PackML/ISA-88 content baked in for Type A; make opt-in configurable later
- **D-7** (Parallel Waves): Sequential writing works; parallelism is an optimization
- **D-9** (Version Management): Simple file naming works initially; formal versioning adds complexity
- **D-10** (BASELINE.md): Type C/D support can come after Type A/B is solid
- **D-11** (ENGINEER-TODO.md): Manual tracking suffices initially

### MVP Rationale

The MVP must demonstrate the full discuss-plan-write-verify loop for a Type A or Type B project, producing a single assembled FDS in DOCX format. This proves the core value proposition: structured AI-assisted FDS authoring that captures decisions, generates quality content, verifies completeness, and delivers a professional document.

Everything else makes it better. Nothing else makes it work.

---

## Sources

- [IACS Engineering - FDS](https://iacsengineering.com/functional-specifications/) -- FDS structure, 50% time savings claim
- [Positive Engineering - FDS for Industrial Control Systems](https://positiveengineering.com/functional-design-specification-fds-for-industrial-control-system-software/) -- 9-section FDS structure, reusable object libraries
- [RealPars - What Is an FDS](https://www.realpars.com/blog/fds) -- FDS components and purpose
- [Malisko - Essential Documentation for Controls Engineers](https://malisko.com/essential-documentation/) -- URS/FDS/HDS/SDS documentation chain
- [ISA-88 Phases & Equipment Modules](https://sgsystemsglobal.com/glossary/isa-88-phases-equipment-modules/) -- EM interface patterns
- [PackML Overview](https://www.automationreadypanels.com/automation-and-systems/packml-the-packaging-machine-language-driving-automation/) -- State model, naming conventions
- [PLCtalk - FDS Discussion](https://www.plctalk.net/forums/threads/functional-design-specification.63433/) -- Practitioner perspectives (access limited)
- [IDC Online - Design of Industrial Automation Functional Specifications](https://www.idc-online.com/downloads/FC_IDCBookextract.pdf) -- Common mistakes, consistency requirements
- [Stack Overflow 2025 Developer Survey](https://simonwillison.net/2025/Dec/31/the-year-in-llms/) -- 46% distrust AI accuracy (cited indirectly)
- SPECIFICATION.md v2.7.0 -- GSD-Docs specification (primary source, local)
