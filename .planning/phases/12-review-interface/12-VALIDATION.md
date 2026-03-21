---
phase: 12
slug: review-interface
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — project uses structural verification (TypeScript compilation + Python import checks) |
| **Config file** | `frontend/tsconfig.json` (TypeScript), no pytest.ini |
| **Quick run command** | `cd frontend && npx tsc --noEmit 2>&1 \| head -30` |
| **Full suite command** | `cd frontend && npx tsc --noEmit && cd ../backend && source venv/bin/activate && python -c "from app.schemas.verification import VerificationDetailResponse; from app.api.phases import get_phase_verification_detail; print('OK')"` |
| **Estimated runtime** | ~15 seconds |

**Note:** No vitest or pytest infrastructure exists in this project. RESEARCH.md confirms "No test framework detected." All automated verification uses TypeScript compilation checks (`tsc --noEmit`) for frontend and Python import checks for backend. This is a known project-level decision, not a Phase 12 gap.

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npx tsc --noEmit 2>&1 | head -30`
- **After every plan wave:** Run full suite command above
- **Before `/gsd:verify-work`:** Full suite must pass (tsc + imports)
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 12-01-01 | 01 | 1 | QUAL-01, QUAL-02, QUAL-03 | structural | `cd backend && source venv/bin/activate && python -c "from app.schemas.verification import VerificationDetailResponse, TruthResult; from app.api.phases import get_phase_verification_detail; print('OK')"` | pending |
| 12-01-02 | 01 | 1 | QUAL-06 | structural | `cd frontend && npx tsc --noEmit 2>&1 \| head -30` | pending |
| 12-02-01 | 02 | 2 | QUAL-04, QUAL-05, QUAL-07, QUAL-08 | structural | `cd frontend && npx tsc --noEmit 2>&1 \| head -30` | pending |
| 12-02-02 | 02 | 2 | QUAL-02, QUAL-04 | structural | `cd frontend && npx tsc --noEmit 2>&1 \| head -30` | pending |
| 12-03-01 | 03 | 3 | QUAL-01, QUAL-03, QUAL-04, QUAL-05, QUAL-06 | structural | `cd frontend && npx tsc --noEmit 2>&1 \| head -30` | pending |
| 12-03-02 | 03 | 3 | ALL | manual | Human checkpoint — end-to-end review flow | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

None — no test framework to scaffold. Automated verification uses TypeScript compilation and Python import checks which require no additional setup.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Review controls overlay appears naturally on SectionBlock | QUAL-01 | Visual layout judgment | Open document with VERIFICATION.md present, confirm review buttons appear below section content |
| Standards badge tooltip shows full text on hover | QUAL-08 | Hover interaction | Hover ISA-88 badge, confirm tooltip renders standard requirement text |
| localStorage persists review session across page reload | QUAL-02 | Browser storage | Submit feedback, reload page, confirm feedback textarea retains content |
| End-to-end flow from ProjectWorkspace through DocumentsTab | QUAL-01 | Integration flow | Navigate to Documents tab, verify review controls appear without manual prop injection |

---

## Nyquist Compliance Note

`nyquist_compliant: false` — This project uses structural verification (TypeScript compilation + Python import checks) rather than unit tests. No vitest or pytest infrastructure exists. All `<automated>` commands in plans use `tsc --noEmit` and `python -c "import ..."` checks, which verify structural correctness (types compile, imports resolve) but not behavioral correctness. Behavioral verification is covered by the Plan 12-03 human checkpoint.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify commands
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter (cannot be set — no test framework)

**Approval:** pending
