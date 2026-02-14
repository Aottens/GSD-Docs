# STATE.md — GSD-Docs Industrial

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-06)

**Core value:** Engineers can go from project brief to complete, verified FDS document through a structured, AI-assisted workflow
**Current focus:** Phase 6 verified complete. Knowledge transfer and review capabilities operational.

## Current Position

- Phase: 7 of 7 (SDS Generation + Export)
- Plan: 2 of 5 in phase (DOCX export complete)
- Status: In Progress
- Last activity: 2026-02-14 - Plan 07-02 complete (DOCX export command and workflow - Pandoc conversion with Mermaid rendering)
- Next: Continue Phase 7 Plan 3 (SDS generation scaffolding)

## Progress

Progress: ████████████████████████░░░░░░ ~86%

| Phase | Name | Plans | Status |
|-------|------|-------|--------|
| 1 | Framework Foundation + /doc:new-fds | 4/4 | ✓ Verified |
| 2 | Discuss + Plan Commands | 4/4 | ✓ Verified |
| 3 | Write + Verify (Core Value) | 5/5 | ✓ Verified |
| 4 | State Management + Recovery | 5/5 | ✓ Verified |
| 5 | Complete-FDS + Standards | 5/5 | ✓ Verified |
| 6 | Knowledge Transfer + Review | 5/5 | ✓ Verified |
| 7 | SDS Generation + Export | 2/5 | In Progress |

## Decisions

- Standalone plugin, not GSD fork (2026-02-06)
- Commands under /doc:* prefix (2026-02-06)
- Defer standards content to later milestone (2026-02-06)
- Configurable language Dutch/English (2026-02-06)
- Mode: yolo, Depth: comprehensive, Parallelization: enabled (2026-02-06)
- CLAUDE-CONTEXT.md uses XML section tags for semantic grouping (2026-02-07)
- DOC > prefix for all stage banners, never GSD > (2026-02-07)
- writing-guidelines.md kept minimal for Phase 3 expansion (2026-02-07)
- Standalone templates per type, not base+overlay -- each type has genuinely different phase structures (2026-02-07)
- BASELINE.md INSTRUCTIE bilingual Dutch+English as safety-critical directive (2026-02-07)
- Templates define structure only (44-109 lines), command fills content (2026-02-07)
- Lean command file (62 lines) + detailed workflow file (544 lines) separation pattern (2026-02-07)
- Language selection always first, no default assumed (2026-02-07)
- Classification: 2-stage process (type determination then metadata gathering) with override warning (2026-02-07)
- SUMMARY.md existence is completion proof, not STATE.md status (2026-02-07)
- Command files tracked in plugin repo under commands/ for version control (2026-02-07)
- Phase 1 verified complete through automated checks + human approval (2026-02-07)
- Plugin files live in project repo, installed via directory junctions (install.ps1) — no admin required (2026-02-07)
- GitHub remote: https://github.com/Aottens/GSD-Docs.git — push after each phase (2026-02-07)
- Equipment module template: 9 subsections (5 required, 4 optional) with HTML comment markers (2026-02-08)
- I/O table: 9 columns (Tag, Description, Type, Signal Range, Eng. Unit, PLC Address, Fail-safe State, Alarm Limits, Scaling) (2026-02-08)
- CONTEXT.md template: XML-tagged sections matching CLAUDE-CONTEXT.md pattern (2026-02-08)
- discuss-phase is interactive (AskUserQuestion), not a subagent spawner -- no Task tool needed (2026-02-08)
- Gray areas derive from phase goal, not fixed list -- probing patterns as depth guidance (2026-02-08)
- Cross-references to undocumented equipment: capture and flag, never block (2026-02-08)
- plan-phase is non-interactive (no AskUserQuestion) -- reads CONTEXT.md autonomously (2026-02-08)
- Doc PLAN.md format: ## Goal/Sections/Context/Template/Standards/Writing Rules/Verification (not GSD XML) (2026-02-08)
- Wave assignment: topological sort on dependency graph, independent to Wave 1, overview/summary last (2026-02-08)
- Self-verification: 7 inline checks before completing, fix-and-retry pattern (2026-02-08)
- Gap closure (--gaps): requires VERIFICATION.md, generates targeted fix plans as Wave 1 (2026-02-08)
- EM subsection selection: 5 required always + 4 optional per CONTEXT.md mentions (2026-02-08)
- Phase 2 verified complete through 8-category automated checks + human approval (2026-02-08)
- doc-writer subagent: sonnet model, Read/Write/Bash tools, Glob/Grep disallowed for context isolation (2026-02-10)
- doc-verifier subagent: sonnet model, Read/Bash/Glob/Grep tools, Write disallowed for read-only verification (2026-02-10)
- SUMMARY.md: 150-word hard limit, 4 mandatory sections (Facts, Key Decisions, Dependencies, Cross-refs) (2026-02-10)
- VERIFICATION.md: 5-level cascade (Exists→Substantive→Complete→Consistent→Standards), cycle tracking (max 2) (2026-02-10)
- CROSS-REFS.md: full context per reference (source/target/type/context/status), types: depends-on/related-to/see-also (2026-02-10)
- write-phase orchestrator: wave-based parallel execution, max 4 concurrent writers, STATE.md checkpointing before/after waves (2026-02-10)
- Context isolation: explicit file lists (no directory globs), writers never receive other plans' content (2026-02-10)
- [Phase 03]: verify-phase is lean orchestrator (70 lines) delegating to comprehensive workflow (650 lines)
- [Phase 03]: Goal-backward verification: derive 3-7 observable truths from phase goal before verification cascade
- [Phase 03]: Gap closure: max 2 cycles, escalate to ENGINEER-TODO.md + phase BLOCKED when exceeded
- [Phase 03]: Re-verification scope: Claude's discretion based on cross-reference impact (full phase vs fixed sections)
- [Phase 03]: Gap preview is informational only (non-interactive mode) - engineers can delete unwanted plans before write-phase
- [Phase 03]: Gap grouping: same artifact + related levels = one plan, different artifacts = separate plans
- [Phase 03]: Fix plans include gap_closure:true flag and original_plan field for traceability
- [Phase 03]: Phase 3 verified complete through 10-category automated checks (78 checks) + human approval (2026-02-10)
- [Phase 03]: Write-verify-gap-closure loop operational and ready for engineer use (2026-02-10)
- [Phase 04]: STATE.md Current Operation section has 8 fields for crash recovery (command, phase, wave, wave_total, plans_done, plans_pending, status, started) (2026-02-13)
- [Phase 04]: Partial write detection uses 4 heuristics (missing SUMMARY, < 200 chars, [TO BE COMPLETED], abrupt ending) with confidence levels (2026-02-13)
- [Phase 04]: Verify-phase blocks on HIGH-confidence partials, warns on MEDIUM-confidence (2026-02-13)
- [Phase 04]: Status command is read-only (Read/Bash/Glob/Grep tools only, no Task/Write) (2026-02-13)
- [Phase 04]: Filesystem verification takes precedence over STATE.md status field (2026-02-13)
- [Phase 04]: Next action logic has 9 branches covering all project states (crash recovery to completion) (2026-02-13)
- [Phase 04]: Status command is read-only (Read/Bash/Glob/Grep tools only, no Task/Write)
- [Phase 04]: Filesystem verification takes precedence over STATE.md status field
- [Phase 04]: Next action logic has 9 branches covering all project states (crash recovery to completion)
- [Phase 04]: /doc:resume command uses Task tool for re-spawning write-phase or verify-phase subagents (2026-02-13)
- [Phase 04]: Auto-detect resume in write-phase Step 3b with Y/n confirmation (default: Y) (2026-02-13)
- [Phase 04]: Command-conflict warnings in write-phase (Step 3a) and verify-phase (Step 1a) when different command running during IN_PROGRESS status (2026-02-13)
- [Phase 04]: Decimal phase numbering format {parent}.{sequence} (e.g., 4.1, 4.2) preserves existing phase numbers (2026-02-13)
- [Phase 04]: ROADMAP expansion grouping: 3-5 units per phase, maximum 7 new phases, Claude's discretion on strategy (2026-02-13)
- [Phase 04]: Interactive approval: one group at a time with approve/modify/skip options (2026-02-13)
- [Phase 04]: Auto-trigger threshold: >5 units in System Overview triggers expansion proposal via verify-phase Step 6A (2026-02-13)
- [Phase 04]: Phase 4 verified complete through 11-category automated checks + human approval (2026-02-13)
- [Phase 05]: FDS structure follows IEC-style hierarchical numbering (1, 1.1, 1.2, 2, 2.1, etc.) - locked in fds-structure.json (2026-02-14)
- [Phase 05]: Section ordering predefined in template, not ROADMAP phase order - assembly reorders content (2026-02-14)
- [Phase 05]: Unwritten sections appear as '[TO BE COMPLETED]' placeholder stubs (2026-02-14)
- [Phase 05]: Equipment modules (section 4) expand dynamically - one 4.x subsection per ROADMAP equipment module (2026-02-14)
- [Phase 05]: Type-conditional baseline section (1.4) only for Type C/D projects (2026-02-14)
- [Phase 05]: Bilingual template pattern: dual language blocks with lang attributes, assembly selects based on PROJECT.md (2026-02-14)
- [Phase 05]: Revision history hybrid approach: auto-generated from git as draft, engineer edits before release (2026-02-14)
- [Phase 05]: Abbreviations auto-extraction from document content plus manual additions (2026-02-14)
- [Phase 05]: PackML state validation uses exact match enforcement with common synonyms mapped to remediation hints (2026-02-14)
- [Phase 05]: ISA-88 terminology context-aware - enforced in hierarchy sections, relaxed in I/O tables (2026-02-14)
- [Phase 05]: Standards severity configurable per standard (error blocks assembly, warning is non-blocking) (2026-02-14)
- [Phase 05]: Version scheme: v0.x internal drafts, v1.0 first client release, v1.1 internal revisions, v2.0 next client (2026-02-14)
- [Phase 05]: Client release gate: all phases must pass verification, but --force allows release with warnings (2026-02-14)
- [Phase 05]: Previous version files archived to .planning/archive/vX.Y/ on new release (2026-02-14)
- [Phase 05]: FDS and SDS versioned independently, SDS references source FDS version (2026-02-14)
- [Phase 05]: Section ordering happens BEFORE numbering to avoid reorder-after-number pitfall (2026-02-14)
- [Phase 05]: Symbol table built AFTER numbering finalized for cross-reference resolution (2026-02-14)
- [Phase 05]: Orphan severity: equipment modules HIGH, intro/safety MEDIUM, appendices LOW (Claude's discretion) (2026-02-14)
- [Phase 05]: --force flag allows DRAFT assembly with broken references, DRAFT suffix prevents accidental client delivery (2026-02-14)
- [Phase 05]: Archive is COPY not MOVE - original phase files remain for continued work (2026-02-14)
- [Phase 05]: Phase 5 verified complete through 11-category automated checks (103 checks) + human approval (2026-02-14)
- [Phase 06]: Edge case capture is non-blocking - zero edge cases per section is acceptable (2026-02-14)
- [Phase 06]: Design Reason field is REQUIRED for all edge cases - explains WHY system behaves this way (2026-02-14)
- [Phase 06]: CRITICAL edge cases get dual format: table row + blockquote warning box for visual distinction (2026-02-14)
- [Phase 06]: Temporary file pattern ({plan-id}-edge-cases.tmp) prevents race conditions between parallel writers (2026-02-14)
- [Phase 06]: EDGE-CASES.md is per-phase (in phase directory, not project-wide) (2026-02-14)
- [Phase 06]: RATIONALE.md is project-wide single file organized by FDS section reference
- [Phase 06]: Edge cases have required Design Reason column - incomplete without it
- [Phase 06]: Incremental RATIONALE.md capture after each discussion topic (not batch at end)
- [Phase 06]: Review is supplementary to verify-phase (human judgment vs automated checks), both exist independently (2026-02-14)
- [Phase 06]: Multi-session review support via --resume flag and Review Progress tracking in REVIEW.md (2026-02-14)
- [Phase 06]: Fresh Eyes review offered after verify-phase PASS only, never after GAPS_FOUND (2026-02-14)
- [Phase 06]: Fresh Eyes has 3 perspectives (engineer/customer/operator) with distinct checking criteria and severity calibration (2026-02-14)
- [Phase 06]: Customer perspective is strict on jargon - flags ALL internal jargon, unexplained abbreviations, overly technical language (2026-02-14)
- [Phase 06]: Fresh Eyes default is informational only - --actionable flag required to route MUST-FIX/SHOULD-FIX to gap closure (2026-02-14)
- [Phase 06]: Fresh Eyes does NOT change PASS result - verification complete regardless of review outcome (2026-02-14)
- [Phase 06]: Review fatigue mitigation with pause option every 10 sections (2026-02-14)
- [Phase 06]: Gap closure routing optional via --route-gaps with preview-before-routing pattern (2026-02-14)
- [Phase 06]: Phase 6 verified complete through 11-category automated checks (96 checks) + human approval (2026-02-14)
- [Phase 07]: Pandoc 3.9+ as DOCX conversion tool with --reference-doc for corporate styling (2026-02-14)
- [Phase 07]: mermaid-cli for server-side PNG rendering with complexity budgets (40-node soft limit, 100-node hard limit) (2026-02-14)
- [Phase 07]: Deferred diagrams routed to ENGINEER-TODO.md (not blocking errors) with timeout (60s per diagram) (2026-02-14)
- [Phase 07]: huisstijl.docx optional reference document (warning if missing, Pandoc defaults as fallback) (2026-02-14)
- [Phase 07]: --draft and --skip-diagrams flags for graceful degradation during export (2026-02-14)

## Blockers

(None)

## Future: v2.0 — Web Frontend

Browser-based UI so non-technical colleagues can run GSD-Docs from a server without touching the CLI. Scope after v1.0 is complete.

- **UX:** Dashboard home screen + wizard mode per command (classify → discuss → plan → write → verify)
- **Auth:** Login from day one (single-user initially, scalable when lighter models allow concurrency)
- **Concurrency:** One project at a time (local LLM constraint); auth built in for future multi-user scaling
- **Feedback:** Progress bar + expandable live terminal output + notifications on completion
- **Backend:** Local LLM (not Claude API) — model selection TBD
- **Depends on:** v1.0 CLI pipeline complete and stable

## Session Continuity

Last session: 2026-02-14
Stopped at: Completed 07-02-PLAN.md — DOCX export command and workflow (Pandoc conversion with Mermaid rendering)
Resume file: N/A

---
*Last updated: 2026-02-14*
