---
name: doc:review-phase
description: Present completed phase content section-by-section for engineer or client review with feedback capture
argument-hint: "<phase> [--route-gaps] [--resume]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>

Present phase N documentation section-by-section for structured review. For each section: show SUMMARY.md key facts + cross-references + CONTENT.md (paginated if long). Collect feedback via interactive prompts: Approved / Comment / Flag / Skip. Capture all feedback in REVIEW.md. Optionally route flagged issues to gap closure pipeline.

**Output:** phase-N/REVIEW.md with structured feedback per section

**Use cases:**
- Engineer handover (present to colleague taking over project)
- Client walkthrough (section-by-section FDS review)
- Internal review (structured quality check)

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/review-phase.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md

</execution_context>

<context>

Phase number: $ARGUMENTS (required)
Flags: --route-gaps (optional), --resume (optional)

@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/PROJECT.md

</context>

<process>

Follow the workflow in `review-phase.md` exactly. It contains all steps: phase validation, section loading, interactive presentation with AskUserQuestion, feedback capture in REVIEW.md, and optional gap closure routing.

</process>

<success_criteria>

- [ ] Phase validated and has completed content (VERIFICATION.md PASS or written content exists)
- [ ] All sections loaded with CONTENT.md + SUMMARY.md + cross-refs
- [ ] Each section presented sequentially with interactive feedback collection
- [ ] Feedback captured in REVIEW.md with section reference, status, finding, suggested action
- [ ] Review summary displayed: N sections reviewed, X approved, Y comments, Z flagged
- [ ] If --route-gaps: flagged issues previewed then routed to plan-phase --gaps
- [ ] Engineer knows next steps (manual resolution or automatic gap closure)

</success_criteria>
