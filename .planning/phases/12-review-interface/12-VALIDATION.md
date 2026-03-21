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
| **Framework** | vitest (frontend), pytest 7.x (backend) |
| **Config file** | `frontend/vitest.config.ts`, `backend/pytest.ini` |
| **Quick run command** | `cd frontend && npx vitest run --reporter=verbose 2>&1 | tail -20` |
| **Full suite command** | `cd frontend && npx vitest run && cd ../backend && python -m pytest tests/ -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npx vitest run --reporter=verbose 2>&1 | tail -20`
- **After every plan wave:** Run `cd frontend && npx vitest run && cd ../backend && python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | QUAL-03, QUAL-04 | integration | `cd backend && python -m pytest tests/test_verification_api.py -v` | ❌ W0 | ⬜ pending |
| 12-02-01 | 02 | 1 | QUAL-01, QUAL-02 | unit | `cd frontend && npx vitest run src/features/documents/components/__tests__/ReviewActionBar.test.tsx` | ❌ W0 | ⬜ pending |
| 12-02-02 | 02 | 1 | QUAL-05, QUAL-06, QUAL-07 | unit | `cd frontend && npx vitest run src/features/documents/components/__tests__/VerificationDetail.test.tsx` | ❌ W0 | ⬜ pending |
| 12-02-03 | 02 | 1 | QUAL-08 | unit | `cd frontend && npx vitest run src/features/documents/components/__tests__/StandardsBadge.test.tsx` | ❌ W0 | ⬜ pending |
| 12-03-01 | 03 | 2 | QUAL-01 | unit | `cd frontend && npx vitest run src/features/documents/hooks/__tests__/useReviewSession.test.ts` | ❌ W0 | ⬜ pending |
| 12-03-02 | 03 | 2 | QUAL-01, QUAL-02 | integration | `cd frontend && npx vitest run src/features/documents/components/__tests__/SectionBlockReview.test.tsx` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_verification_api.py` — stubs for QUAL-03, QUAL-04 verification endpoint tests
- [ ] `frontend/src/features/documents/components/__tests__/ReviewActionBar.test.tsx` — stubs for review action UI
- [ ] `frontend/src/features/documents/components/__tests__/VerificationDetail.test.tsx` — stubs for verification display
- [ ] `frontend/src/features/documents/components/__tests__/StandardsBadge.test.tsx` — stubs for standards badge
- [ ] `frontend/src/features/documents/hooks/__tests__/useReviewSession.test.ts` — stubs for review session state
- [ ] `frontend/src/features/documents/components/__tests__/SectionBlockReview.test.tsx` — stubs for integration

*Existing infrastructure covers framework setup — only test files need creation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Review controls overlay appears naturally on SectionBlock | QUAL-01 | Visual layout judgment | Open document with VERIFICATION.md present, confirm review buttons appear below section content |
| Standards badge tooltip shows full text on hover | QUAL-08 | Hover interaction | Hover ISA-88 badge, confirm tooltip renders standard requirement text |
| localStorage persists review session across page reload | QUAL-02 | Browser storage | Submit feedback, reload page, confirm feedback textarea retains content |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
