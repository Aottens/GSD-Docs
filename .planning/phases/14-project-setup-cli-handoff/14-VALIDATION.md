---
phase: 14
slug: project-setup-cli-handoff
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (backend) — no config file detected; Wave 0 installs |
| **Config file** | none — Wave 0 creates `backend/tests/conftest.py` |
| **Quick run command** | `cd backend && python -m pytest tests/ -x -q` |
| **Full suite command** | `cd backend && python -m pytest tests/ -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd backend && python -m pytest tests/ -x -q`
- **After every plan wave:** Run `cd backend && python -m pytest tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 1 | PROJ-01 | unit | `pytest tests/test_setup_state.py::test_doc_type_config -x` | ❌ W0 | ⬜ pending |
| 14-01-02 | 01 | 1 | PROJ-01 | unit | `pytest tests/test_files.py::test_upload_with_doc_type -x` | ❌ W0 | ⬜ pending |
| 14-02-01 | 02 | 1 | PROJ-01 | unit | `pytest tests/test_setup_state.py::test_setup_state_endpoint -x` | ❌ W0 | ⬜ pending |
| 14-03-01 | 03 | 2 | PROJ-01 | manual | — (wizard UI interaction) | N/A | ⬜ pending |
| 14-04-01 | 04 | 2 | PROJ-04 | manual | — (ProjectOverview visual) | N/A | ⬜ pending |
| 14-04-02 | 04 | 2 | PROJ-01 | unit | `pytest tests/test_setup_state.py::test_coverage_computation -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/conftest.py` — shared fixtures (async DB session, test client)
- [ ] `backend/tests/test_setup_state.py` — stubs for setup-state endpoint and doc-type config
- [ ] `backend/tests/test_files.py` — extend with doc_type upload tests
- [ ] Verify `pytest` + `httpx` in `backend/requirements.txt`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Wizard Step 4 renders doc-type checklist | PROJ-01 | UI interaction / visual layout | 1. Create new project, reach Step 4. 2. Verify doc-type rows appear per project type. 3. Toggle "Niet beschikbaar" — verify row grays out. |
| SetupStatusSection shows coverage | PROJ-04 | Requires CLI filesystem changes + polling | 1. Open project overview. 2. Verify setup status section shows doc-type coverage. 3. Run CLI setup. 4. Verify GUI updates within 5s. |
| Referenties tab doc-type assignment | PROJ-01 | UI interaction / dropdown | 1. Go to Referenties tab. 2. Upload a file. 3. Verify doc-type dropdown appears. 4. Select type and upload. 5. Verify file shows correct doc_type. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
