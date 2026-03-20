---
phase: 11
slug: document-preview-outline
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-20
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (backend), tsc --noEmit (frontend type checking) |
| **Config file** | backend/tests/conftest.py (fixtures), no pytest.ini yet — Wave 0 creates conftest |
| **Quick run command** | `cd backend && python -m pytest tests/test_documents.py -x -q` |
| **Full suite command** | `cd backend && python -m pytest tests/test_documents.py -v --tb=short` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd backend && python -m pytest tests/test_documents.py -x -q`
- **After every plan wave:** Run `cd backend && python -m pytest tests/test_documents.py -v --tb=short && cd frontend && npx tsc --noEmit`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | WORK-03, DOCG-01 | unit | `cd backend && python -c "from app.schemas.document import PlanInfoSchema; p = PlanInfoSchema(wave=1, plan_name='t', plan_file='f'); assert p.truths == []; print('OK')"` | Wave 0 creates | pending |
| 11-01-02 | 01 | 1 | WORK-03, WORK-04, DOCG-01 | unit | `cd backend && python -c "from app.api.documents import router, _parse_plan_frontmatter, _build_outline_sections; print('OK')"` | Wave 0 creates | pending |
| 11-01-03 | 01 | 1 | WORK-03, DOCG-01 | unit + integration | `cd backend && python -m pytest tests/test_documents.py -v --tb=short` | Wave 0 creates | pending |
| 11-02-01 | 02 | 2 | WORK-03, WORK-04 | typecheck | `cd frontend && npx tsc --noEmit 2>&1 \| head -30` | Plan 01 creates types | pending |
| 11-02-02 | 02 | 2 | WORK-03, OUTP-01, DOCG-01 | typecheck | `cd frontend && npx tsc --noEmit 2>&1 \| head -30` | Task creates components | pending |
| 11-02-03 | 02 | 2 | WORK-03, WORK-04 | typecheck | `cd frontend && npx tsc --noEmit 2>&1 \| head -30` | Task creates DocumentsTab | pending |
| 11-03-01 | 03 | 3 | WORK-03, WORK-04, OUTP-01, DOCG-01 | typecheck | `cd frontend && npx tsc --noEmit 2>&1 \| head -30` | Modifies existing files | pending |

*Status: pending (pre-execution) -- will be updated to green/red/flaky during execution*

---

## Wave 0 Requirements

- [x] `backend/tests/__init__.py` — package init (created in Plan 01, Task 1)
- [x] `backend/tests/conftest.py` — shared fixtures: fds_structure, tmp_project_dir (created in Plan 01, Task 1)
- [x] `backend/tests/test_documents.py` — stubs for WORK-03, WORK-04, DOCG-01 (created in Plan 01, Task 1)
- [x] `pyyaml>=6.0` added to requirements.txt (created in Plan 01, Task 1)

Plan 01 Task 1 is the Wave 0 task — it creates all test infrastructure before implementation begins.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Scroll-spy highlights correct outline node on scroll | WORK-04 | Requires browser IntersectionObserver + real DOM scroll events; cannot be automated with pytest or tsc | 1. Open project documents tab. 2. Scroll content panel. 3. Verify outline highlights track current visible section. 4. Click outline node, verify scroll-spy suppression during smooth scroll (no flicker). |
| Mermaid diagrams render as SVG in browser | OUTP-01 | Requires browser DOM rendering with mermaid.render() async API; no headless test infrastructure | 1. Open project with written content containing mermaid code blocks. 2. Verify diagrams appear as rendered SVG (not raw code). 3. Test with malformed mermaid syntax — verify fallback to code block display. |
| Plan card shows wave, dependencies, truths, description | DOCG-01 | Visual verification of card layout with real API data | 1. Open project with planned sections. 2. Click planned section in outline. 3. Verify PlanCard shows wave badge, dependencies list, "Vereisten" with truths, and description text. |
| Split-pane resize works correctly | WORK-03 | Requires mouse drag interaction on ResizableHandle | 1. Open documents tab. 2. Drag handle between panels. 3. Verify both panels resize within min/max constraints (15-40% outline, remainder content). |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (Plan 01 Task 1 creates test infra)
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-20
