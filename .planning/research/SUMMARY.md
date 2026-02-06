# Project Research Summary

**Project:** GSD-Docs Industrial
**Domain:** Claude Code plugin for industrial FDS/SDS documentation generation
**Researched:** 2026-02-06
**Confidence:** HIGH

## Executive Summary

GSD-Docs Industrial is a Claude Code plugin -- not a traditional software project. The entire deliverable consists of Markdown command files with YAML frontmatter, Markdown reference/template files, JSON configuration, and one DOCX template. There is no build step, no package.json, no transpilation. The "stack" is Claude Code's built-in plugin system: files placed in `~/.claude/commands/doc/` become `/doc:*` slash commands, and files in `~/.claude/agents/` become subagents spawned via the Task tool. The GSD reference implementation (v1.6.4) provides a proven, directly replicable architecture for command-driven orchestration with subagent delegation, wave-based parallelism, and file-based state management. GSD-Docs maps 1:1 to GSD's structure; only the payload changes from source code to technical documentation.

The recommended approach is to build GSD-Docs as a direct structural analogue of GSD, with the core value loop (discuss -> plan -> write -> verify) as the centerpiece. The framework supports 4 project types (A: new + standards, B: new flex, C: modification large, D: modification small/TWN) with dynamic ROADMAP evolution for large projects. Each write operation gets a fresh subagent context containing only the current plan, project config, phase decisions, and relevant standards -- preventing the cross-contamination that is the primary quality risk in multi-section AI-assisted documentation. Equipment module templates enforce structured output (states, parameters, interlocks, I/O with ranges and units), and goal-backward verification checks content substance, not just file existence.

The key risks are context cross-contamination between sections (which produces plausible-looking but factually wrong content -- a safety concern in industrial automation), infinite verification-fix loops (which waste tokens and erode user trust), and section numbering collapse during document assembly (which produces unprofessional output). All three are preventable with architectural discipline established in the earliest build phases: fresh context per writer, maximum 2 gap-closure iterations, and symbolic references resolved only at assembly time.

## Key Findings

### Recommended Stack

GSD-Docs has no traditional technology stack. The framework is entirely plain files that Claude Code discovers and loads at command invocation time.

**Core technologies:**
- **Claude Code custom commands** (`~/.claude/commands/doc/*.md`): The only mechanism for registering `/doc:*` slash commands. Frontmatter-driven with YAML fields for name, description, allowed-tools, argument-hint, and model.
- **Claude Code subagents** (`~/.claude/agents/*.md`): Specialized agents (doc-writer, doc-verifier, doc-planner, doc-reviewer, doc-sds-generator) spawned via the Task tool for heavy operations with fresh context.
- **Markdown + YAML frontmatter**: The command file format. Not negotiable -- this is what Claude Code parses.
- **JSON** (`config.json`, `CATALOG.json`): Structured configuration and typicals catalog.

**External dependencies (export only):**
- **Pandoc 3.x**: Markdown-to-DOCX conversion with `--reference-doc` for corporate styling.
- **mermaid-cli 11.x** (requires Node.js 18+): Renders Mermaid diagrams to PNG before Pandoc conversion.

**Critical version requirements:** None for the core framework. Pandoc 3.x for DOCX export. Node.js 18+ LTS if using mermaid-cli.

### Expected Features

**Must have (table stakes) -- the framework fails without these:**
- **TS-1: Project classification** (Type A/B/C/D) and scaffolding -- entry point for everything
- **TS-2: Discuss-plan-write-verify workflow** -- this IS the product; without it, it is just a template
- **TS-3: Equipment module documentation structure** -- states, parameters, interlocks, I/O in structured tables
- **TS-4: Goal-backward verification** -- checks substance, not just file existence (5 levels: exists, substantive, complete, consistent, standards)
- **TS-5: Gap closure loop** -- verify -> plan --gaps -> write -> re-verify, self-correcting
- **TS-6: State management** (STATE.md) -- multi-session survival across days/weeks
- **TS-7: Fresh context per write task** -- correctness guarantee against cross-contamination
- **TS-8: Document assembly** (complete-fds) -- merge phases into single FDS with section numbering and cross-refs
- **TS-9: DOCX export** -- industrial clients receive DOCX, not markdown
- **TS-10: Resume/recovery** -- forward-only, detect incomplete operations

**Should have (differentiators) -- significant value beyond basic templates:**
- **D-1: Gray area identification** (discuss-phase) -- front-loads decisions, saves 20-30% revision cycles
- **D-2: FDS-to-SDS transformation** with typicals matching (CATALOG.json) -- saves 40-60% SDS time
- **D-3: Dynamic ROADMAP evolution** -- adapts to project complexity after System Overview
- **D-4: Cross-reference registry** (CROSS-REFS.md) -- automates the most labor-intensive quality check
- **D-5: Knowledge transfer** (RATIONALE.md, EDGE-CASES.md, Fresh Eyes) -- preserves the "why"
- **D-7: Parallel wave-based writing** -- cuts wall-clock time via parallel subagents

**Defer to post-MVP:**
- D-2 (FDS-to-SDS): Requires CATALOG.json investment; FDS alone is valuable
- D-3 (Dynamic ROADMAP): Start static; add evolution when handling real large projects
- D-6 (Standards opt-in): Bake in for Type A first; make configurable later
- D-7 (Parallel waves): Sequential writing works; parallelism is optimization
- D-9 (Version management): Simple file naming initially
- D-10 (BASELINE.md): Type C/D support after Type A/B is solid

### Architecture Approach

GSD-Docs is a command-driven orchestration system with four layers: Command Layer (thin orchestrators in `~/.claude/commands/doc/`), Reference Layer (domain knowledge, templates, standards in `~/.claude/gsd-docs-industrial/`), Project State Layer (per-project `.planning/` with STATE.md as the system's memory), and Output Layer (assembled FDS/SDS documents + DOCX exports). Commands are thin -- they load context via @-references and delegate heavy work to subagents. Subagents get fresh context with explicit boundaries (only current plan + project config + phase decisions + standards). STATE.md is read first and written last by every command.

**Major components:**
1. **Command files** (12 commands) -- entry points that define allowed tools, load execution context, and orchestrate subagent delegation
2. **Workflow files** (10 workflows) -- detailed execution logic that subagents follow, loaded via @-references
3. **Templates** (17+ files) -- scaffolding for ROADMAP, PLAN, CONTENT, VERIFICATION, organized by project type and section type
4. **References** (8+ files) -- domain knowledge: standards (PackML, ISA-88), writing guidelines, verification patterns, typicals catalog
5. **State machine** (STATE.md) -- progress tracking, decision memory, crash recovery across sessions

**Key patterns:** Orchestrator + subagent delegation, wave-based parallelization, goal-backward verification, conditional standards loading, forward-only recovery, SUMMARY.md as cross-phase bridge.

### Critical Pitfalls

1. **Context cross-contamination** (CRITICAL) -- Writer subagent for EM-400 loads or inherits content from EM-200, producing plausible but factually wrong content. **Prevention:** Each writer loads ONLY PROJECT.md + CONTEXT.md + its own PLAN.md + standards. Orchestrator never reads other plans' CONTENT.md before spawning. Verification cross-checks equipment IDs against plan scope.

2. **Infinite verification-fix loops** (CRITICAL) -- Verify finds gaps, fixes introduce new gaps, system spins without converging. **Prevention:** Maximum 2 gap-closure cycles per phase. Scoped re-verification (check only targeted gaps). Escalate to `human_needed` after limit.

3. **Section numbering collapse at assembly** (CRITICAL) -- Phase-relative section numbers collide in final document; cross-references become wrong after ROADMAP evolution. **Prevention:** Use symbolic references during writing (e.g., `{EM-200-interlocks}`). Numbering applied only at complete-fds assembly time. CROSS-REFS.md stores plan-ID + section-ID, not numbers.

4. **STATE.md corruption during parallel crashes** (CRITICAL) -- Parallel writer A crashes, writer B completes, STATE.md shows wave as done, plan A is silently lost. **Prevention:** SUMMARY.md existence is the ONLY completion proof. Resume logic scans for PLAN.md without matching SUMMARY.md. STATE.md is never the primary source of truth for plan completion.

5. **Template explosion across 4 project types** (CRITICAL) -- 4 types x 2 standards combos x N languages = copy-paste maintenance hell. **Prevention:** Template inheritance with type-specific overrides. Standards as composable modules, not conditional blocks. Language as late-binding. Test all 4 types before release.

## Implications for Roadmap

Based on combined research, the build decomposes into 7 phases following the dependency chain identified in ARCHITECTURE.md and validated against the feature dependency graph in FEATURES.md.

### Phase 1: Framework Foundation + new-fds

**Rationale:** Every subsequent command depends on the `.planning/` directory structure and PROJECT.md/ROADMAP.md that new-fds creates. The template composition architecture must be established here to prevent Pitfall 5 (template explosion). The SUMMARY.md-as-completion-proof pattern must be established here to prevent Pitfall 4 (STATE.md corruption).
**Delivers:** Working `/doc:new-fds` command that classifies projects (Type A/B/C/D), generates ROADMAP from type-specific template, scaffolds .planning/ directory, creates PROJECT.md + REQUIREMENTS.md + STATE.md + config.json. Also: framework directory structure (`~/.claude/gsd-docs-industrial/`), CLAUDE-CONTEXT.md, ui-brand.md, and the template composition pattern.
**Features addressed:** TS-1 (Project Classification), TS-6 (State Management foundation)
**Pitfalls to avoid:** Pitfall 5 (template explosion -- invest in composition architecture), Pitfall 4 (establish SUMMARY.md = completion proof)

### Phase 2: Discuss + Plan Commands

**Rationale:** Planning depends on ROADMAP + PROJECT from Phase 1. Writing (Phase 3) depends on PLAN.md files from this phase. The discuss-phase front-loads gray area identification, which is the primary differentiator (D-1) and should be available from the earliest usable version.
**Delivers:** Working `/doc:discuss-phase` producing CONTEXT.md with captured decisions. Working `/doc:plan-phase` producing PLAN.md files with wave assignments and verification criteria. FDS section templates (equipment module, state machine, interface). doc-planner subagent.
**Features addressed:** TS-2 (core workflow -- discuss + plan legs), D-1 (Gray Area Identification), TS-3 (EM documentation structure via templates)
**Pitfalls to avoid:** Pitfall 7 (CONTEXT.md overload -- enforce 1500 word limit + priority tiers), Pitfall 6 (ROADMAP evolution -- use directory names, not just numbers)

### Phase 3: Write + Verify (Core Value Delivery)

**Rationale:** This is the core value loop. Writing and verification are inseparable because gap closure ties them together. This phase produces the first real FDS content and validates it. The fresh-context-per-writer pattern (TS-7) must be correct here or the entire framework fails.
**Delivers:** Working `/doc:write-phase` with wave-based subagent execution. doc-writer subagent with fresh context isolation. CONTENT.md + SUMMARY.md generation. Working `/doc:verify-phase` with 5-level goal-backward checking. Gap closure loop (verify -> plan --gaps -> write -> re-verify, max 2 cycles). CROSS-REFS.md logging. EDGE-CASES.md logging. doc-verifier subagent. Writing guidelines and verification patterns references.
**Features addressed:** TS-2 (write + verify legs), TS-4 (Goal-Backward Verification), TS-5 (Gap Closure), TS-7 (Fresh Context), D-7 (Parallel Wave Writing), D-8 (SUMMARY.md)
**Pitfalls to avoid:** Pitfall 1 (context cross-contamination -- strict context loading rules), Pitfall 2 (infinite loops -- max 2 retries + scoped re-verification), Pitfall 9 (SUMMARY.md quality -- mandatory structure + validation)

### Phase 4: State Management + Recovery + Review

**Rationale:** Once the core write/verify cycle works, robustness features make the system production-ready. Crash recovery requires the write infrastructure to exist. Dynamic ROADMAP evolution triggers after Phase 2 (System Overview) verification, so verify-phase must exist first.
**Delivers:** Working `/doc:status` command. Working `/doc:resume` with interrupt detection and forward-only recovery. Partial write detection. Dynamic ROADMAP evolution (post-System Overview expansion). `/doc:review-phase` for client feedback. REVIEW.md template.
**Features addressed:** TS-10 (Resume/Recovery), TS-6 (State Management -- full implementation), D-3 (Dynamic ROADMAP Evolution)
**Pitfalls to avoid:** Pitfall 4 (STATE.md corruption -- SUMMARY.md as completion proof), Pitfall 6 (ROADMAP evolution -- migration of artifacts when phases renumber)

### Phase 5: Standards Integration (PackML, ISA-88)

**Rationale:** Standards are opt-in enhancements to the core workflow. The core must work without them first (Type B and D projects never use them). Building standards as an overlay on top of a working writer/verifier ensures the conditional loading pattern works correctly.
**Delivers:** PackML reference files (STATE-MODEL.md, UNIT-MODES.md). ISA-88 reference files (EQUIPMENT-HIERARCHY.md, TERMINOLOGY.md). Conditional loading mechanism in orchestrators. Standards compliance checks in doc-verifier. Standards-aware FDS section templates.
**Features addressed:** D-6 (Standards Opt-In)
**Pitfalls to avoid:** Pitfall 8 (Standards terminology drift -- composable modules, terminology enforcement post-processing, verification checks against reference lists)

### Phase 6: Complete-FDS + Knowledge Transfer

**Rationale:** Document assembly is the "end of the line" for FDS production. It requires all upstream content to exist. Knowledge transfer documents (RATIONALE, EDGE-CASES) have been accumulated during Phases 2-4 and are aggregated here. This is where symbolic cross-references resolve to actual section numbers.
**Delivers:** Working `/doc:complete-fds` with cross-phase merging, strict cross-reference validation, orphan section detection. RATIONALE.md aggregation. EDGE-CASES.md aggregation. ENGINEER-TODO.md generation (complex diagrams flagged for manual creation). Fresh Eyes review. `/doc:release` for version management. Archive workflow.
**Features addressed:** TS-8 (Document Assembly), D-4 (Cross-Reference Validation), D-5 (Knowledge Transfer), D-9 (Version Management), D-11 (ENGINEER-TODO.md)
**Pitfalls to avoid:** Pitfall 3 (section numbering collapse -- symbolic references resolved only here), Pitfall 14 (orphan content -- scan for unreferenced CONTENT.md files)

### Phase 7: SDS Generation + DOCX Export

**Rationale:** SDS depends on a complete FDS. DOCX export depends on final documents. These are downstream transformations, not core authoring. Export is the final delivery format and has the most external dependencies (Pandoc, mermaid-cli).
**Delivers:** Working `/doc:generate-sds` with typicals matching from CATALOG.json. TRACEABILITY.md linking FDS requirements to SDS implementation. Working `/doc:export` with Pandoc + huisstijl.docx. Mermaid diagram rendering with complexity fallback. Full pipeline: brief -> FDS -> SDS -> DOCX.
**Features addressed:** D-2 (FDS-to-SDS Transformation), TS-9 (DOCX Export)
**Pitfalls to avoid:** Pitfall 10 (export fragility -- pin Pandoc version, test with reference document, complexity budget per diagram), Pitfall 13 (typicals catalog staleness -- version tracking per typical)

### Phase Ordering Rationale

- **Dependency chain drives order:** Each phase produces artifacts consumed by the next. new-fds -> discuss/plan -> write/verify -> state/recovery -> standards -> assembly -> export.
- **Core value first:** Phases 1-3 are the minimum viable pipeline. After Phase 3, an engineer can run the full discuss -> plan -> write -> verify cycle and produce verified FDS sections. Everything after Phase 3 makes it better; Phases 1-3 make it work.
- **Risk mitigation front-loaded:** The three critical architectural decisions (fresh context per writer, SUMMARY.md as completion proof, symbolic references) are established in Phases 1-3 where they can be validated early.
- **Standards as overlay:** Phase 5 adds standards on top of a working system, ensuring the conditional loading pattern is correct and the core never depends on standards presence.
- **Export last:** External tool dependencies (Pandoc, mermaid-cli) are isolated in Phase 7. The framework is fully functional in Markdown without export capability.

### Research Flags

**Phases likely needing deeper research during planning:**
- **Phase 3 (Write + Verify):** The doc-writer subagent prompt and verification patterns are novel -- no direct GSD equivalent for documentation-specific content quality checks. The wave dependency analysis logic needs design work. This phase carries the most implementation risk.
- **Phase 6 (Complete-FDS):** Section numbering algorithm and cross-reference resolution at assembly time have no GSD precedent. This is a documentation-specific problem that must be designed from scratch.
- **Phase 7 (SDS Generation):** Typicals matching algorithm (FDS equipment descriptions -> CATALOG.json function blocks) is entirely new. The semantic matching logic needs research.

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (Framework Foundation):** Directly maps to GSD's `new-project.md`. Well-documented command registration pattern. Copy structure, adapt content.
- **Phase 2 (Discuss + Plan):** Maps to GSD's `discuss-phase.md` and `plan-phase.md`. Established GSD patterns. Domain-specific content (gray area catalogs) is the main work, not architecture.
- **Phase 4 (State + Recovery):** Maps to GSD's `resume-work.md` and `progress.md`. Forward-only recovery is a proven GSD pattern.
- **Phase 5 (Standards):** Content creation (writing PackML/ISA-88 reference files), not architectural work. Conditional loading pattern is already defined.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified against GSD v1.6.4 source files and official Claude Code documentation. No ambiguity -- the "stack" is Claude Code's plugin system. |
| Features | MEDIUM-HIGH | Specification v2.7.0 is detailed and internally consistent. Domain knowledge verified against IACS Engineering, RealPars, ISA-88 sources. Minor gap: real-world usage data for discuss-phase question quality is assumed, not validated. |
| Architecture | HIGH | Derived from reading actual GSD source files (24 commands, 7 references, 6 workflows). 1:1 mapping is proven by structural analysis. The component boundary rules and data flows are directly verified. |
| Pitfalls | HIGH | Critical pitfalls derived from GSD architecture analysis + domain-specific research (multi-agent failures, context rot). Prevention strategies grounded in specification sections. Phase-specific warnings are concrete and actionable. |

**Overall confidence:** HIGH

### Gaps to Address

- **doc-writer prompt quality:** The most critical unknown. How well the writer subagent produces structured FDS content (states, parameters, interlocks, I/O with ranges/units) depends entirely on the quality of the system prompt and templates. This must be iterated during Phase 3 implementation.
- **Wave dependency analysis:** The specification says plans get wave assignments, but the algorithm for determining which sections can be parallel vs. which have dependencies is not specified. This needs design during Phase 2 planning.
- **CONTEXT.md size management:** The 1500-word limit and priority tier structure are recommendations from pitfalls research, not specification mandates. The actual effective limit depends on how much context doc-writer subagents need for quality output.
- **Cross-reference resolution algorithm:** The symbolic-to-numbered reference resolution at complete-fds time is a novel requirement with no GSD precedent. The algorithm needs design during Phase 6 planning.
- **Typicals matching semantics:** How CATALOG.json entries map to FDS equipment descriptions is specified at a high level but the matching algorithm (exact vs. fuzzy, confidence thresholds, "NEW TYPICAL NEEDED" triggers) needs design during Phase 7.
- **Template composition mechanism:** The prevention for Pitfall 5 recommends template inheritance with type-specific overrides, but the exact mechanism (base + override files vs. conditional includes vs. parameterized templates) needs decision during Phase 1 planning.

## Sources

### Primary (HIGH confidence)
- GSD reference implementation v1.6.4 (`~/.claude/get-shit-done/`) -- 24 command files, 7 reference files, 6 workflow files read directly
- GSD-Docs SPECIFICATION.md v2.7.0 -- the SSOT for all GSD-Docs behavior, read directly
- [Claude Code Slash Commands Documentation](https://code.claude.com/docs/en/slash-commands)
- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)

### Secondary (MEDIUM confidence)
- [IACS Engineering - FDS](https://iacsengineering.com/functional-specifications/) -- FDS structure, time savings claims
- [RealPars - What Is an FDS](https://www.realpars.com/blog/fds) -- FDS components and purpose
- [Malisko - Essential Documentation for Controls Engineers](https://malisko.com/essential-documentation/) -- URS/FDS/HDS/SDS chain
- [PackML Overview](https://www.automationreadypanels.com/automation-and-systems/packml-the-packaging-machine-language-driving-automation/) -- state model, naming
- [Multi-Agent LLM System Failures (arXiv 2025)](https://arxiv.org/html/2503.13657v1) -- inter-agent misalignment
- [Context Rot research by Chroma (2025)](https://tilburg.ai/2025/03/context-window-management/) -- context degradation

### Tertiary (LOW confidence)
- [Stack Overflow 2025 Developer Survey](https://simonwillison.net/2025/Dec/31/the-year-in-llms/) -- 46% distrust AI accuracy (cited indirectly)
- [PLCtalk - FDS Discussion](https://www.plctalk.net/forums/threads/functional-design-specification.63433/) -- practitioner perspectives (access limited)

---
*Research completed: 2026-02-06*
*Ready for roadmap: yes*
