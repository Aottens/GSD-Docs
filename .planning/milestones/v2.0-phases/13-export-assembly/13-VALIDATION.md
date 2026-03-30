---
phase: 13
slug: export-assembly
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.0+ with pytest-asyncio 0.23+ |
| **Config file** | none — Wave 0 creates `backend/pytest.ini` if needed |
| **Quick run command** | `cd backend && python -m pytest tests/ -x -q` |
| **Full suite command** | `cd backend && python -m pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd backend && python -m pytest tests/ -x -q`
- **After every plan wave:** Run `cd backend && python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 1 | OUTP-02 | unit | `pytest tests/test_assembly_service.py -x` | ❌ W0 | ⬜ pending |
| 13-01-02 | 01 | 1 | OUTP-07 | unit | `pytest tests/test_assembly_service.py::test_language_param -x` | ❌ W0 | ⬜ pending |
| 13-02-01 | 02 | 1 | OUTP-03 | unit (mock Pandoc) | `pytest tests/test_export_service.py -x` | ❌ W0 | ⬜ pending |
| 13-02-02 | 02 | 1 | OUTP-04 | integration | `pytest tests/test_export_api.py::test_sse_stream -x` | ❌ W0 | ⬜ pending |
| 13-03-01 | 03 | 2 | OUTP-05 | unit | `pytest tests/test_sds_service.py -x` | ❌ W0 | ⬜ pending |
| 13-03-02 | 03 | 2 | OUTP-06 | unit | `pytest tests/test_sds_service.py::test_confidence_scoring -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_assembly_service.py` — stubs for OUTP-02, OUTP-07
- [ ] `backend/tests/test_export_service.py` — stubs for OUTP-03
- [ ] `backend/tests/test_export_api.py` — stubs for OUTP-04
- [ ] `backend/tests/test_sds_service.py` — stubs for OUTP-05, OUTP-06

*Existing infrastructure covers pytest config.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| DOCX corporate styling correct | OUTP-03 | Visual inspection of font, headers, layout | Open exported .docx, verify heading styles match huisstijl spec |
| Pipeline UX layout renders correctly | OUTP-04 | Visual layout check | Open Export tab, verify 3-stage pipeline renders left-to-right |
| SDS tab renders matching confidence | OUTP-05 | Visual check of scores | Open SDS tab, verify HIGH/MEDIUM/LOW badges visible |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
