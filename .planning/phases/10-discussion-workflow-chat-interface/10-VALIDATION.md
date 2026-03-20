---
phase: 10
slug: discussion-workflow-chat-interface
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-20
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none — no automated test infrastructure detected |
| **Config file** | none |
| **Quick run command** | `cd backend && python -m uvicorn app.main:app --reload` (manual smoke) |
| **Full suite command** | Manual smoke test: load project, verify timeline renders |
| **Estimated runtime** | ~30 seconds (manual) |

---

## Sampling Rate

- **After every task commit:** Verify backend starts without import errors: `cd backend && python -c "from app.main import app"`
- **After every plan wave:** Manual smoke test: start backend + frontend, load project
- **Before `/gsd:verify-work`:** Full manual walkthrough of success criteria
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 10-01-01 | 01 | 1 | WORK-01 | smoke | `cd backend && python -c "from app.main import app"` | N/A | pending |
| 10-02-01 | 02 | 2 | WORK-01/02 | smoke | `cd backend && python -c "from app.main import app"` | N/A | pending |
| 10-03-01 | 03 | 3 | WORK-01 | manual | Load project — verify timeline renders | N/A | pending |
| 10-04-01 | 04 | 3 | WORK-02 | manual | Click phase node — verify CLI command with copy | N/A | pending |

*Status: pending · green · red · flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements — no test framework needed. This phase is primarily deletion + rework verified by:
- Backend import check: `python -c "from app.main import app"`
- Manual smoke test of timeline UI

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Phase timeline shows filesystem-based status | WORK-01 | No test infra; visual UI check | Load project, verify phase nodes show correct status colors derived from filesystem artifacts |
| Phase popover shows CLI command | WORK-02 | No test infra; visual UI check | Click phase node, verify monospace CLI command block with copy button appears |
| Discussion code fully removed | WORK-01 | Deletion verification | Confirm `features/discussions/` directory gone, no discussion imports in backend |
| Alembic migration runs cleanly | WORK-01 | DB state dependent | Run `alembic upgrade head`, verify no errors, verify tables dropped |

---

## Validation Sign-Off

- [ ] All tasks have manual verify or import check
- [ ] Sampling continuity: backend import check after every task
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
