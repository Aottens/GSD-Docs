---
phase: 16
slug: per-section-verification-display
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-30
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest |
| **Config file** | `frontend/vite.config.ts` |
| **Quick run command** | `cd frontend && npx vitest run --reporter=verbose` |
| **Full suite command** | `cd frontend && npx vitest run` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npx vitest run --reporter=verbose`
- **After every plan wave:** Run `cd frontend && npx vitest run`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 16-01-01 | 01 | 1 | QUAL-01 | unit | `npx vitest run src/features/documents/utils/filterTruthsForSection.test.ts` | ❌ W0 | ⬜ pending |
| 16-01-02 | 01 | 1 | QUAL-01 | unit | same file | ❌ W0 | ⬜ pending |
| 16-01-03 | 01 | 1 | QUAL-02 | unit | `npx vitest run src/features/documents/components/VerificationDetailPanel.test.tsx` | ❌ W0 | ⬜ pending |
| 16-01-04 | 01 | 1 | QUAL-02 | unit | same file | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `frontend/src/features/documents/utils/filterTruthsForSection.test.ts` — stubs for QUAL-01 section filtering logic
- [ ] `frontend/src/features/documents/components/VerificationDetailPanel.test.tsx` — stubs for QUAL-02 empty-state rendering

*Existing infrastructure covers framework setup — only test files need creation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual confirmation: sections with no truths show "geen bevindingen" text | QUAL-02 | Visual rendering check | Open a document with verification, navigate to a section without truths, confirm message appears |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
