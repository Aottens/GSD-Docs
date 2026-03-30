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
| 16-01-01 | 01 | 1 | QUAL-01 | unit | `npx vitest run src/features/documents/utils/filterTruthsForSection.test.ts` | W0 | pending |
| 16-01-02 | 01 | 1 | QUAL-01, QUAL-02 | acceptance | `grep + tsc --noEmit + vitest run` | n/a | pending |

*Status: pending / green / red / flaky*

**QUAL-02 coverage note:** Empty-state rendering (QUAL-02) is verified through Task 2 acceptance criteria (grep checks for empty-state text, class, and conditional structure in SectionBlock.tsx) plus manual visual verification (see below). A dedicated VerificationDetailPanel component test is not included because it would require jsdom + @testing-library/react setup, which is out of scope for this focused plan. The filterTruthsForSection unit tests (QUAL-01) verify the filtering logic that drives the empty-state branch.

---

## Wave 0 Requirements

- [ ] `frontend/src/features/documents/utils/filterTruthsForSection.test.ts` — stubs for QUAL-01 section filtering logic

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
