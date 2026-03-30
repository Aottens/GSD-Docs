# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — CLI

**Shipped:** 2026-02-14
**Phases:** 7 | **Plans:** 33

### What Was Built
- Complete Claude Code plugin for FDS/SDS document generation
- 14 commands under `/doc:*` namespace covering full lifecycle
- 194 files, 50,263 lines of Markdown (templates, workflows, references)
- 89/89 requirements satisfied

### What Worked
- Frontmatter-driven command architecture — clean separation of concerns
- Forward-only recovery strategy — simpler than rollback, reliable crash recovery
- Goal-backward verification — catches gaps that task-based QA misses

### What Was Inefficient
- Early-phase SUMMARY.md files lacked structured frontmatter (requirements_completed field missing)
- REQUIREMENTS.md traceability table not maintained during execution (resolved by archival)

### Patterns Established
- SUMMARY.md as completion proof (atomic file existence)
- Context isolation for parallel writers
- 5-level verification cascade
- Standards as opt-in verification level

### Key Lessons
1. File existence is a more reliable completion signal than state file fields
2. Domain knowledge (templates, section structures) should live in dedicated files, not inline in commands

---

## Milestone: v2.0 — GUI

**Shipped:** 2026-03-30
**Phases:** 11 | **Plans:** 26 | **Tasks:** 56

### What Was Built
- FastAPI backend (37 files, 5,563 LOC) — project CRUD, file management, document outline, verification detail, export/assembly, SDS scaffolding
- React frontend (118 files, 9,089 LOC) — dashboard, wizard, workspace, document preview, review interface, export pipeline, SDS tab, reference library
- 31/33 requirements satisfied (deployment deferred)

### What Worked
- Cockpit pivot (Phase 10) was the right call — embedded chat felt forced vs CLI. Dropping 7 DISC/DOCG requirements simplified everything
- Gap closure cycle worked well: audit → plan gaps → execute → re-audit closed all integration issues
- Phase 16 (per-section truth filtering) is a good example of a surgical fix that dramatically improved UX
- v1.0 fidelity rule ensured domain content was faithfully reproduced, not paraphrased

### What Was Inefficient
- Phase 10/10.1 built a discussion engine that was entirely scrapped in the cockpit pivot — significant rework
- Phase 12 shipped with React Rules of Hooks violations that required Phase 15.2 to fix
- Phase 8/9 summaries lacked requirements_completed field — made audit cross-referencing harder
- SYST-04 (LLM abstraction) was built in Phase 8, then deleted in Phase 10 cleanup — wasted effort from premature architecture

### Patterns Established
- GUI as cockpit pattern: visual tasks in GUI, AI in CLI
- SSE for long-running operations (export progress)
- localStorage for review state persistence
- useRef-based polling fingerprint change detection for cross-tool notifications
- Regex-based section matching with strict equality (prevents false positives like "2.1" matching "2.10")

### Key Lessons
1. Don't build embedded chat UIs for CLI tools — the conversation experience is always worse than the native CLI
2. LLM abstraction in a GUI that doesn't need LLM is waste — build what you need now, not what you might need
3. Gap closure phases (decimal phases) are an efficient way to surgically fix audit findings without replanning
4. Per-section filtering of phase-level data should be the default, not an afterthought
5. React Rules of Hooks violations are easy to introduce and hard to catch without ESLint — enforce linting early

### Cost Observations
- Model mix: primarily sonnet for executors/verifiers, opus for orchestration
- 236 commits over 43 days
- Notable: gap closure phases (15.1-16) were very efficient — small, surgical, fast

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 CLI | 7 | 33 | Established GSD workflow with forward-only recovery |
| v2.0 GUI | 11 | 26 | Added gap closure cycle, cockpit pivot mid-milestone |

### Cumulative Quality

| Milestone | Requirements | Satisfaction | Key Metric |
|-----------|-------------|-------------|------------|
| v1.0 CLI | 89 | 100% | All requirements met |
| v2.0 GUI | 33 | 94% | 2 deferred (deployment) |

### Top Lessons (Verified Across Milestones)

1. File existence as completion proof works better than state fields (v1.0 SUMMARY.md pattern, validated in v2.0)
2. Goal-backward verification catches gaps that task-based QA misses (v1.0 verification cascade, v2.0 audit cycle)
3. Forward-only is almost always the right recovery strategy (v1.0 crash recovery, v2.0 gap closure)
