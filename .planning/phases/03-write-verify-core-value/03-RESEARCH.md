# Phase 3: Write + Verify (Core Value) - Research

**Researched:** 2026-02-10
**Domain:** Parallel document generation with subagent orchestration, goal-backward verification, and self-correcting gap closure loops
**Confidence:** HIGH

## Summary

Phase 3 implements the core value proposition of the FDS documentation system: transforming plans into substantive content through parallel writing, verifying against phase goals (not just task completion), and autonomously closing gaps through a self-correcting loop. This phase is where the GSD workflow's "verse context per task" and "gap closure loop" patterns prove their value in the documentation domain.

The research examined: (1) Claude Code's subagent system architecture including context isolation guarantees and parallel execution capabilities, (2) goal-backward verification patterns that distinguish task completion from goal achievement, (3) gap closure loop implementations with max-iteration termination, (4) cross-reference management in distributed writing contexts, and (5) state management patterns for crash recovery in multi-wave operations.

The critical architectural insight from this research: Phase 3 creates **commands that orchestrate subagents**, not commands that ARE subagents. The write-phase and verify-phase commands run in the main session and spawn specialized doc-writer and doc-verifier subagents with fresh, isolated context. This is fundamentally different from Phase 2, where commands executed directly without spawning.

**Primary recommendation:** Follow the established Phase 1/2 pattern (lean command + detailed workflow) while adding subagent orchestration logic. Use Claude Code's native subagent system for parallel execution with automatic context isolation. Implement verification as a 5-level cascade (exists → substantive → complete → consistent → standards-compliant) with gap detection feeding back into targeted fix planning. Enforce max 2 gap-closure cycles with explicit escalation to ENGINEER-TODO.md when gaps persist.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Content depth & completeness
- Best-effort with markers: writers infer reasonable values from CONTEXT.md but mark inferred content with [VERIFY] so engineer can confirm — never silently guess
- I/O tables: generate complete rows with industry-typical signal ranges (e.g., 4-20mA, 0-100%), mark inferred values with [VERIFY]
- State machines: high-level overview first (Mermaid stateDiagram-v2 + summary transition table), flag complex transitions as [DETAIL NEEDED] for engineer review
- Quality bar: all required template sections (5 for equipment modules) must have real content — optional sections can be empty if not relevant to the equipment
- [VERIFY] markers are acceptable in required sections; empty required sections are not

#### Verification feedback
- VERIFICATION.md format: summary pass/gap table at top for quick scan, detailed findings per section below
- Gap descriptions only — describe what's missing or wrong, don't suggest fixes (leave fix approach to plan-phase --gaps)
- All 5 verification levels always run: exists, substantive, complete, consistent with CONTEXT.md, standards-compliant
- Cross-references to unwritten sections in verification: Claude's discretion on whether to warn or flag as deferred gap, with reasoning documented in VERIFICATION.md

#### Gap closure autonomy
- Gap closure trigger: Claude decides whether to auto-fix or ask based on gap severity (Claude's discretion)
- Escalation after max 2 cycles: remaining gaps added to ENGINEER-TODO.md AND phase completion blocked — gaps are both tracked and blocking
- Re-verification scope: Claude decides based on whether fixes touched cross-references (full phase) or isolated content (fixed sections only)
- Gap preview: before generating fix plans, show engineer the list of gaps that will be addressed and let them confirm

#### Cross-reference handling
- Reference format in CONTENT.md: Claude's discretion — picks format that works best for downstream assembly resolution
- Reference creation: Claude's discretion — decides based on how obvious the relationship is between sections
- CROSS-REFS.md captures full context per reference: source section, target section, status (resolved/pending), context sentence, and reference type (depends-on, related-to, see-also)
- Undocumented equipment references: Claude's discretion based on available info from CONTEXT.md about the target

### Claude's Discretion

- Cross-reference format (symbolic tags vs descriptive placeholders) — choose what works best for assembly
- Whether to proactively create cross-references beyond what PLAN.md specifies — based on obviousness of relationship
- Verification treatment of references to unwritten sections (warn vs deferred gap) — document reasoning
- Gap closure: auto-fix vs ask engineer — based on gap severity
- Re-verification scope after fixes — based on whether fixes affect cross-references
- How much to capture about undocumented referenced equipment — based on available info

### Specific Implementation Ideas

- Writers load ONLY PROJECT.md + phase CONTEXT.md + own PLAN.md + standards (if enabled) — strict isolation, no cross-contamination from other sections' content
- Each section produces both CONTENT.md (substantive) and SUMMARY.md (max 150 words, facts only: counts, key decisions, dependencies, cross-references)
- Writers in the same wave execute in parallel
- The gap closure loop is: verify → preview gaps → engineer confirms → plan-phase --gaps → write-phase → re-verify (max 2 cycles)
- STATE.md checkpoint before and after each wave

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope
</user_constraints>

## Standard Stack

Phase 3 creates markdown command files that orchestrate Claude Code subagents. The "stack" is the established patterns from Phases 1-2 plus Claude Code's native subagent system.

### Core

| Component | Location | Purpose | Why Standard |
|-----------|----------|---------|--------------|
| Command file | `commands/doc/write-phase.md` | Orchestrates parallel writing | Established Phase 1/2 pattern: frontmatter + @-references |
| Command file | `commands/doc/verify-phase.md` | Goal-backward verification orchestrator | Same pattern as write-phase |
| Workflow file | `gsd-docs-industrial/workflows/write-phase.md` | Wave-based execution logic | Phase 1/2 pattern: detailed workflow in separate file |
| Workflow file | `gsd-docs-industrial/workflows/verify-phase.md` | 5-level verification cascade | Same separation as write-phase |
| Subagent definition | `gsd-docs-industrial/agents/doc-writer.md` | Writer with strict context isolation | Claude Code native subagent format (YAML frontmatter + markdown prompt) |
| Subagent definition | `gsd-docs-industrial/agents/doc-verifier.md` | Verifier with read-only access | Same format as doc-writer |

### Supporting

| Component | Location | Purpose | When Used |
|-----------|----------|---------|-----------|
| SUMMARY.md template | `gsd-docs-industrial/templates/summary.md` | 150-word summary format | Template for writer output validation |
| VERIFICATION.md template | `gsd-docs-industrial/templates/verification.md` | Pass/gap summary format | Template for verifier output |
| CROSS-REFS.md template | `gsd-docs-industrial/templates/cross-refs.md` | Cross-reference registry format | Created/updated during write-phase |
| STATE.md checkpoint logic | (inline in workflows) | Wave completion tracking | Before/after each wave in write-phase |
| gsd-tools.js | `~/.claude/get-shit-done/bin/gsd-tools.js` | Phase operations helper | Already exists; provides `init phase-op`, `commit` commands |

### Claude Code Subagent System

| Feature | Version | Purpose | Source |
|---------|---------|---------|--------|
| Subagent definitions | Claude Code 2026 | YAML frontmatter + markdown prompt files | [Official docs](https://code.claude.com/docs/en/sub-agents) |
| Context isolation | Built-in | Each subagent gets fresh context with only specified files | Guaranteed by Claude Code architecture |
| Parallel execution | Built-in | Multiple subagents can run concurrently | Native capability when tasks touch different files |
| Tool restrictions | Built-in via `tools` field | Limit doc-verifier to read-only tools | YAML frontmatter configuration |
| Model selection | Built-in via `model` field | Use `sonnet` for writers, `haiku` for verifiers | Cost optimization via model field |

**Installation:**
No external dependencies. Claude Code subagent system is built-in. The gsd-tools.js utility is already installed from Phase 1.

## Architecture Patterns

### Recommended File Structure

```
commands/doc/
├── write-phase.md              # Orchestrator command (~80-100 lines)
├── verify-phase.md             # Verification orchestrator (~80-100 lines)
└── plan-phase.md               # (Already exists from Phase 2)

gsd-docs-industrial/
├── workflows/
│   ├── write-phase.md          # Wave execution logic (~500-700 lines)
│   └── verify-phase.md         # 5-level verification logic (~400-600 lines)
├── agents/
│   ├── doc-writer.md           # Writer subagent definition (~100-150 lines)
│   └── doc-verifier.md         # Verifier subagent definition (~80-120 lines)
└── templates/
    ├── summary.md              # SUMMARY.md format spec
    ├── verification.md         # VERIFICATION.md format spec
    └── cross-refs.md           # CROSS-REFS.md format spec
```

### Pattern 1: Orchestrator Command + Subagent Spawning

**What:** The command file runs in the main session and spawns subagents with isolated context. This is fundamentally different from Phase 2 commands that executed directly.

**When to use:** write-phase and verify-phase commands that need parallel execution with context isolation.

**Architecture:**
```
Main Session (write-phase command)
    │
    ├─ Load: ROADMAP.md, STATE.md, all NN-MM-PLAN.md files
    ├─ Build: dependency graph, wave assignments
    ├─ For each wave:
    │   ├─ Spawn: doc-writer subagent for each plan in wave
    │   │   └─ Isolated context: PROJECT.md + phase CONTEXT.md + own PLAN.md + standards
    │   ├─ Wait: all writers in wave complete
    │   └─ Checkpoint: update STATE.md
    └─ Return: completion summary to engineer

Main Session (verify-phase command)
    │
    ├─ Load: ROADMAP.md, STATE.md, phase CONTEXT.md
    ├─ Derive: must-have truths from phase goal
    ├─ Spawn: doc-verifier subagent
    │   └─ Isolated context: ROADMAP.md + all CONTENT.md + all SUMMARY.md + CONTEXT.md
    └─ Return: VERIFICATION.md with pass/gap status
```

**Critical distinction:** The orchestrator (write-phase command) reads ALL plans to build the dependency graph but NEVER passes other plans' content to writers. Each writer subagent receives only its own PLAN.md via strict context loading rules.

**Example subagent spawn pattern (from workflow):**

```markdown
## Step 4: Execute Wave 1 (Parallel)

For each plan in Wave 1, spawn a doc-writer subagent with isolated context:

```bash
# For plan 03-01-PLAN.md
claude --agent doc-writer \
  --context "PROJECT.md,phases/03-*/03-CONTEXT.md,phases/03-*/03-01-PLAN.md" \
  --message "Write section 03-01 following the plan. Produce CONTENT.md and SUMMARY.md."
```

The subagent receives:
- PROJECT.md (project context)
- 03-CONTEXT.md (phase decisions)
- 03-01-PLAN.md (what to write)
- Standards files (if enabled in PROJECT.md)

The subagent does NOT receive:
- Other PLAN.md files
- Other CONTENT.md files
- Main session conversation history
```

**Source:** [Claude Code Subagent Documentation](https://code.claude.com/docs/en/sub-agents) - verified 2026-02-10

### Pattern 2: Wave-Based Parallel Execution

**What:** Plans are grouped into waves based on dependencies. All plans in a wave execute in parallel via simultaneous subagent spawns. Waves execute sequentially.

**When to use:** write-phase execution after dependency analysis.

**Wave assignment algorithm:**
```
1. Build dependency graph from all PLAN.md files
   - Each plan lists depends_on: [other-plans]
   - Create directed acyclic graph (DAG)

2. Topological sort with level assignment:
   Wave 1: All plans with no dependencies
   Wave 2: All plans whose dependencies are in Wave 1
   Wave 3: All plans whose dependencies are in Waves 1-2
   Wave N: Continue until all plans assigned

3. Special rules:
   - Overview sections always last wave (no dependencies)
   - Summary sections always last wave
   - Cross-reference intensive sections placed late
```

**Example wave structure:**
```
Phase 3: Equipment Modules (6 plans)

Wave 1 (parallel):
  03-01 EM-100 Waterbad          (no deps)
  03-02 EM-200 Bovenloopkraan    (no deps)

Wave 2 (parallel):
  03-03 EM-300 Vulunit           (depends on 03-01)
  03-04 EM-400 Losunit           (depends on 03-02)

Wave 3:
  03-05 EM-500 Kettingbaan       (depends on 03-03, 03-04)
  03-06 EM-600 General Interlocks (overview, always last)
```

**STATE.md checkpoint pattern:**
```markdown
Before wave:
## Current Operation
- command: write-phase
- phase: 3
- wave: 2
- wave_total: 3
- plans_done: [03-01, 03-02]
- plans_pending: [03-03, 03-04, 03-05, 03-06]
- status: IN_PROGRESS

After wave:
## Current Operation
- command: write-phase
- phase: 3
- wave: 3
- wave_total: 3
- plans_done: [03-01, 03-02, 03-03, 03-04]
- plans_pending: [03-05, 03-06]
- status: IN_PROGRESS
```

**Source:** SPECIFICATION.md section 4.4 defines wave-based execution pattern.

### Pattern 3: Goal-Backward Verification (5-Level Cascade)

**What:** Verification checks whether phase goals are achieved, not just whether tasks completed. The 5 levels form a cascade where each level assumes previous levels passed.

**When to use:** Every verify-phase execution.

**The 5 verification levels:**

| Level | Question | Pass Criteria | Gap Example |
|-------|----------|---------------|-------------|
| 1. Exists | Is the artifact present? | File exists with non-zero size | CONTENT.md missing |
| 2. Substantive | Is it real content or a stub? | Contains structured tables, technical content, >200 words | Only placeholders like "TODO: describe EM-200" |
| 3. Complete | Are all required sections present? | All template sections filled (5 required for EM) | Missing I/O table or interlocks section |
| 4. Consistent | Does it match CONTEXT.md decisions? | Uses specified signal ranges, follows decisions | Uses 0-10V when CONTEXT.md specifies 4-20mA |
| 5. Standards | Does it comply with enabled standards? | PackML state names, ISA-88 hierarchy | Custom state names when PackML enabled |

**Verification workflow:**
```
For each must-have truth derived from phase goal:
  1. Check Level 1 (Exists)
     └─ FAIL → Gap: "03-02-CONTENT.md not found", STOP cascade for this truth
     └─ PASS → Continue to Level 2

  2. Check Level 2 (Substantive)
     └─ FAIL → Gap: "03-02-CONTENT.md is stub (only 45 words)", STOP cascade
     └─ PASS → Continue to Level 3

  3. Check Level 3 (Complete)
     └─ FAIL → Gap: "03-02 missing required section: I/O table", STOP cascade
     └─ PASS → Continue to Level 4

  4. Check Level 4 (Consistent)
     └─ FAIL → Gap: "03-02 uses 0-100% but CONTEXT.md specifies 4-20mA", STOP cascade
     └─ PASS → Continue to Level 5

  5. Check Level 5 (Standards)
     └─ FAIL → Gap: "03-02 uses custom state 'RUNNING' but PackML requires 'EXECUTE'"
     └─ PASS → Truth verified
```

**VERIFICATION.md structure:**
```markdown
# Phase 3: Equipment Modules - Verification

**Verified:** 2026-02-10
**Status:** GAPS_FOUND

## Summary

| Truth | Exists | Substantive | Complete | Consistent | Standards | Status |
|-------|--------|-------------|----------|------------|-----------|--------|
| All 6 EMs documented | ✓ | ✓ | ✓ | ⚠ | ✓ | GAP |
| All EMs have state tables | ✓ | ✓ | ✓ | ✓ | ⚠ | GAP |
| All EMs have I/O tables | ✓ | ✓ | ⚠ | - | - | GAP |
| All interlocks documented | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |

**Quick scan:** 3 gaps found across 4 truths. 1 truth passed all levels.

## Detailed Findings

### Truth 1: All 6 equipment modules fully documented

**Status:** GAP (Level 4 - Consistency)

**Verification trail:**
- Level 1 (Exists): ✓ PASS - All 6 CONTENT.md files present
- Level 2 (Substantive): ✓ PASS - All files >500 words with technical content
- Level 3 (Complete): ✓ PASS - All required sections present in all files
- Level 4 (Consistent): ⚠ GAP - 03-02 signal ranges don't match CONTEXT.md
- Level 5 (Standards): Not checked (stopped at Level 4)

**Gap description:**
Section 03-02 (EM-200 Bovenloopkraan) specifies analog inputs as 0-100% range. CONTEXT.md decision "Standard Ranges" section specifies "All analog inputs use 4-20mA industrial standard unless explicitly exceptional." No exception documented for EM-200 inputs.

**Evidence:**
- File: phases/03-*/03-02-CONTENT.md, line 78
- Context: phases/03-*/03-CONTEXT.md, "Standard Ranges" section

### Truth 2: All equipment modules have PackML-compliant state tables

**Status:** GAP (Level 5 - Standards)

[... detailed findings for each truth ...]
```

**Source:** GSD verify-phase pattern documented in SPECIFICATION.md section 4.5. The 5-level cascade is adapted from GSD's artifact verification approach.

### Pattern 4: Gap Closure Loop with Max Iteration Termination

**What:** When verification finds gaps, engineer runs plan-phase --gaps to generate targeted fix plans, then write-phase to execute fixes, then verify-phase to re-check. Loop terminates after max 2 cycles.

**When to use:** Whenever verify-phase returns GAPS_FOUND status.

**Loop structure:**
```
Iteration 1:
  verify-phase N → GAPS_FOUND
    → VERIFICATION.md created with 3 gaps
    → Engineer reviews gaps

  plan-phase N --gaps
    → Reads VERIFICATION.md
    → Generates 03-02-fix-PLAN.md, 03-04-fix-PLAN.md (targeted fixes)
    → Assigns as Wave 1 (all fix plans parallel)

  write-phase N
    → Discovers 2 fix plans
    → Executes Wave 1 (parallel)
    → Updates 03-02-CONTENT.md, 03-04-CONTENT.md

  verify-phase N (re-verify)
    → Engineer decides: full phase or fixed sections only
    → If fixes touched cross-refs: re-verify entire phase
    → If isolated content: re-verify only 03-02, 03-04

Iteration 2 (if still gaps):
  verify-phase N → GAPS_FOUND (1 gap remains)
    → VERIFICATION.md updated

  plan-phase N --gaps
    → Generates 03-02-fix-PLAN.md

  write-phase N
    → Executes fix

  verify-phase N (re-verify)
    → PASS or GAPS_FOUND

Iteration 3 attempt:
  verify-phase N → GAPS_FOUND
    → MAX_ITERATIONS_REACHED (2 cycles completed)
    → Remaining gaps added to ENGINEER-TODO.md
    → Phase marked BLOCKED
    → Engineer must manually resolve gaps
```

**Escalation format (ENGINEER-TODO.md):**
```markdown
# Phase 3: Equipment Modules - Manual Intervention Required

**Date:** 2026-02-10
**Reason:** Gap closure loop terminated after max 2 cycles

## Remaining Gaps

### Gap 1: 03-02 I/O table incomplete
**Severity:** High
**Description:** Digital output DO-200-03 (brake release) missing from I/O table.
**Context:** Equipment has 8 documented I/Os but mechanical drawing shows 9.
**Attempts:** 2 automated fixes tried, both failed to add the missing I/O.
**Next steps:**
1. Confirm DO-200-03 existence with mechanical engineer
2. If confirmed, manually add row to I/O table in 03-02-CONTENT.md
3. Re-run verify-phase 3

### Gap 2: [...]
```

**Phase blocking behavior:**
When gaps remain after max iterations:
- STATE.md phase status: `BLOCKED`
- VERIFICATION.md status: `GAPS_FOUND (ESCALATED)`
- ENGINEER-TODO.md: created with gap details
- Next command attempts: show blocking message with TODO reference
- Override: Engineer can mark gaps as "accepted" to unblock

**Source:** User decision in CONTEXT.md specifies max 2 cycles with escalation to ENGINEER-TODO.md AND phase completion blocked.

### Pattern 5: Strict Context Isolation for Writers

**What:** Each doc-writer subagent receives ONLY the files specified in its context loading rules. The orchestrator enforces this by explicit file passing, not directory access.

**When to use:** Every doc-writer spawn in write-phase.

**Context loading rules for doc-writer:**
```yaml
ALWAYS LOADED:
  - PROJECT.md (project metadata and configuration)
  - phases/{phase}/*-CONTEXT.md (phase decisions and gray area resolutions)
  - phases/{phase}/{plan-id}-PLAN.md (this writer's specific plan)
  - standards files (if PROJECT.md enables PackML/ISA-88)
    - gsd-docs-industrial/references/packml-states.md
    - gsd-docs-industrial/references/isa88-hierarchy.md

NEVER LOADED:
  - Other PLAN.md files in same phase
  - Other CONTENT.md files in same phase
  - Other SUMMARY.md files in same phase
  - Previous phase content
  - Main session conversation history
```

**Enforcement mechanism:**
The orchestrator (write-phase command) uses explicit file paths when spawning subagents, NOT directory globs:

```bash
# CORRECT: Explicit file list
claude --agent doc-writer \
  --context ".planning/PROJECT.md,.planning/phases/03-*/03-CONTEXT.md,.planning/phases/03-*/03-02-PLAN.md" \
  --message "Write section per plan"

# INCORRECT: Directory glob (would leak other plans)
claude --agent doc-writer \
  --context ".planning/phases/03-*/*.md" \
  --message "Write section per plan"
```

**Subagent definition enforces read-only for non-writing:**
```yaml
---
name: doc-writer
description: Writes FDS section content following a PLAN.md
tools: Read, Write, Bash
disallowedTools: Glob, Grep
---
```

The `disallowedTools: Glob, Grep` prevents the writer from discovering other files beyond what was explicitly loaded. It can only write its output files and read what was passed in context.

**Source:** [Claude Code Subagent Context Isolation](https://code.claude.com/docs/en/sub-agents) - "Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions."

### Pattern 6: SUMMARY.md as Facts-Only Abstract

**What:** Each CONTENT.md is paired with a SUMMARY.md that provides a token-efficient overview for cross-section reference checking and verification. SUMMARY.md is structured facts, never prose.

**When to use:** Generated by every doc-writer alongside CONTENT.md.

**Format (from SPECIFICATION.md section 4.4):**
```markdown
# SUMMARY: 03-02 EM-200 Bovenloopkraan

## Facts
- Type: Equipment Module
- States: 6 (PackML compliant)
- Parameters: 4
- Interlocks: 3
- I/O: 8 DI, 4 DO, 2 AI

## Key Decisions
- Geen collision detection (klant keuze)
- E-stop = controlled stop, positie behouden
- Max last 500 kg

## Dependencies
- Interlock met EM-100 (waterbad niveau)
- Interface naar SCADA via Modbus TCP

## Cross-refs
- Interlock IL-200-01 → zie §6.3
- HMI scherm → zie phase-4/04-02
```

**Validation rules:**
- Max 150 words
- Must have all 4 sections (Facts, Key Decisions, Dependencies, Cross-refs)
- Facts section: bullet list with counts (states: N, parameters: N, etc.)
- No prose paragraphs
- Cross-refs use standardized format: `IL-200-01 → zie §6.3`

**Usage by verifier:**
The doc-verifier loads ALL SUMMARY.md files (token-efficient) to check cross-references and dependencies without loading full CONTENT.md files. Full CONTENT.md only loaded when detailed verification needed.

**Source:** SPECIFICATION.md section 4.4 defines SUMMARY.md purpose and format.

### Anti-Patterns to Avoid

- **Don't pass all context to all writers:** This defeats the verse-context-per-task principle and causes context contamination. Each writer should only see its own plan.
- **Don't verify task completion instead of goal achievement:** Checking "CONTENT.md exists" is not enough. Must verify substantive content, completeness, consistency, and standards compliance.
- **Don't allow infinite gap closure loops:** Max 2 cycles is a hard limit. Escalate to human, don't retry forever.
- **Don't embed fix suggestions in VERIFICATION.md:** Verification describes gaps only. Fix approach is determined later by plan-phase --gaps based on gap description.
- **Don't skip STATE.md checkpoints:** Before/after each wave, update STATE.md. This enables crash recovery.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Subagent context isolation | Custom file filtering logic, temporary directories | Claude Code's native --context flag | Claude Code guarantees isolation; custom solutions risk leaks |
| Parallel execution | Manual thread/process management, async/await patterns | Claude Code's native parallel subagent spawning | Built-in handles concurrency, errors, and aggregation |
| Model selection per task | API switching logic, cost calculation | Subagent `model` field (sonnet/haiku/opus) | Declarative configuration, no runtime overhead |
| Dependency graph topological sort | Recursive graph traversal | Standard topological sort algorithm with visited tracking | Well-studied algorithm, many edge cases (cycles, disconnected graphs) |
| Gap severity assessment | Rule-based scoring, keyword matching | Claude's judgment based on gap context | Gap severity depends on domain knowledge (e.g., missing interlock vs missing description) |
| Cross-reference resolution | String parsing, regex matching | Structured CROSS-REFS.md format parsed by verifier | Symbolic references (§6.3) resolve during assembly, not during writing |

**Key insight:** Claude Code's subagent system already solves the hardest problems (context isolation, parallel execution, error aggregation). Don't rebuild what the platform provides. Focus on orchestration logic and domain-specific patterns (wave assignment, verification levels, gap escalation).

## Common Pitfalls

### Pitfall 1: Context Contamination from Orchestrator

**What goes wrong:** The orchestrator command loads ALL plans to build the dependency graph. If it accidentally passes this context to subagents, writers see other sections' plans and content.

**Why it happens:** Natural to pass entire directory when spawning subagents. `--context ".planning/phases/03-*/"` would load everything.

**How to avoid:**
- Orchestrator builds dependency graph from plan frontmatter only (phase, plan, depends_on fields)
- Orchestrator explicitly lists files when spawning: `--context "PROJECT.md,03-CONTEXT.md,03-02-PLAN.md"`
- Subagent definition uses `disallowedTools: Glob, Grep` to prevent file discovery
- Test isolation: spawn a writer and ask it "What other plans exist?" - it should not know.

**Warning signs:** Writers referencing content from other sections they haven't written yet. Writers asking questions like "Should I coordinate with the EM-300 section?"

### Pitfall 2: Infinite Verification Loops

**What goes wrong:** Gap closure loop never terminates because verification keeps finding new gaps or fixes introduce new problems.

**Why it happens:** No hard limit on iterations. Complex interdependencies where fixing A breaks B.

**How to avoid:**
- Enforce max 2 cycles in workflow logic (iteration counter in STATE.md)
- On iteration 3 attempt: immediately escalate to ENGINEER-TODO.md
- Mark phase as BLOCKED, prevent further automated attempts
- Log each iteration's gaps to detect regression (fixing A shouldn't break previously passing B)

**Warning signs:** STATE.md shows gap_closure_iteration: 4 or higher. VERIFICATION.md shows gaps that were previously marked PASS.

### Pitfall 3: Verification Suggests Fixes

**What goes wrong:** VERIFICATION.md contains "Fix by changing line 45 to use 4-20mA" instead of describing the gap.

**Why it happens:** Natural for verifier to want to be helpful. Combining diagnosis and prescription.

**How to avoid:**
- Verifier system prompt explicitly: "Describe what's wrong, not how to fix it"
- VERIFICATION.md template shows gap description format: "Signal range is X but should match CONTEXT.md"
- Separation of concerns: verify-phase finds gaps, plan-phase --gaps determines fixes
- Validation: check VERIFICATION.md for imperative language ("change", "update", "fix") vs descriptive ("uses X instead of Y")

**Warning signs:** VERIFICATION.md contains code snippets or specific edit instructions. Gap descriptions use imperative verbs.

### Pitfall 4: Empty vs Stub vs Substantive Content

**What goes wrong:** Verification Level 2 (substantive) flags real content as stub or accepts stubs as real.

**Why it happens:** Ambiguous threshold between "too short" and "concise technical content". Equipment modules vary in complexity.

**How to avoid:**
- Quantitative checks: word count >200, has structured tables, section headers present
- Qualitative checks: contains technical values (numbers with units), decision documentation, no placeholder text
- Template section matching: all 5 required sections for EM present (description, states, parameters, interlocks, I/O)
- Stub markers: any occurrence of [TODO], [TBD], [PLACEHOLDER] triggers substantive fail

**Warning signs:** Verification passes content with "To be documented later". Verification fails legitimately concise sections like simple interfaces.

### Pitfall 5: Re-verification Scope Explosion

**What goes wrong:** After fixing 1 gap in section 03-02, re-verification checks entire phase (all 6 sections), wasting tokens and time.

**Why it happens:** Conservative approach - "might have affected cross-references, better check everything."

**How to avoid:**
- Decision logic based on fix type:
  - Isolated content fix (parameter value changed): re-verify only that section
  - Cross-reference touched (interlock added): re-verify entire phase
  - Template structure changed (new I/O table row): re-verify only that section
- Track what changed: git diff between before-fix and after-fix commits
- Engineer decides scope via flag: `verify-phase 3 --scope sections:03-02,03-04` or `--scope full`

**Warning signs:** Re-verification taking 5x longer than initial verification. Token usage spike on iteration 2 verify.

### Pitfall 6: Cross-Reference Deadlock

**What goes wrong:** Section A references section B which references section A. Dependency graph has cycle, wave assignment fails.

**Why it happens:** Bidirectional relationships (EM-200 interlocks with EM-300, EM-300 interlocks with EM-200).

**How to avoid:**
- Dependency graph cycle detection before wave assignment
- Treat cross-references separately from write dependencies:
  - Write dependencies: A must exist before B can write (topological sort, no cycles allowed)
  - Cross-references: A mentions B (bidirectional OK, logged in CROSS-REFS.md)
- Break cycles by marking one as "will use placeholder": A writes with "EM-300 interlock (see §X)" placeholder, B writes concrete content, assembly resolves references
- Validation: run cycle detection on dependency graph, error if cycles found

**Warning signs:** Wave assignment fails with "Cycle detected: 03-02 → 03-03 → 03-02". PLAN.md files with circular depends_on.

### Pitfall 7: STATE.md Checkpoint Missed

**What goes wrong:** Write-phase crashes during Wave 2. On resume, Wave 1 work is lost or redone.

**Why it happens:** Forgot to update STATE.md after Wave 1 completed.

**How to avoid:**
- Checkpoint pattern: before wave (status IN_PROGRESS), after wave (update plans_done)
- Atomic checkpoint: write STATE.md only after all writers in wave complete
- Resume detection: on write-phase start, check if status==IN_PROGRESS with non-empty plans_done
- Test recovery: manually stop process mid-wave, restart, verify resume from correct point

**Warning signs:** Resume always starts from Wave 1. STATE.md shows wave:1 but CONTENT.md files from Wave 1 exist.

### Pitfall 8: Standards-Compliant Check Without Standards Knowledge

**What goes wrong:** Verification Level 5 checks PackML compliance but doesn't know PackML state names.

**Why it happens:** Verifier doesn't load standards reference files.

**How to avoid:**
- Load standards files when PROJECT.md enables them:
  - packml.enabled: true → load packml-states.md
  - isa88.enabled: true → load isa88-hierarchy.md
- Standards files contain canonical reference (PackML states: IDLE, STARTING, EXECUTE, COMPLETING, COMPLETE, ABORTING, ABORTED, STOPPING, STOPPED)
- Verification checks: state names in CONTENT.md match canonical list exactly
- Skip Level 5 if no standards enabled (mark as N/A in VERIFICATION.md)

**Warning signs:** Verification Level 5 always passes regardless of content. Verification fails legitimate PackML state names.

### Pitfall 9: SUMMARY.md Quality Variation

**What goes wrong:** Some SUMMARY.md files are 500 words of prose, others are 20 words of stub.

**Why it happens:** No validation of SUMMARY.md format during writing.

**How to avoid:**
- Template with mandatory structure (4 sections: Facts, Key Decisions, Dependencies, Cross-refs)
- Validation in writer's self-check before returning:
  - Word count 100-150 (hard limit)
  - All 4 section headers present
  - Facts section has bullet list with counts
  - Cross-refs use standardized format
- Reject and retry if validation fails
- Example SUMMARY.md in writer's system prompt

**Warning signs:** SUMMARY.md files vary wildly in length. Missing sections. Prose paragraphs instead of bullet lists.

## Code Examples

Verified patterns from Claude Code documentation and SPECIFICATION.md:

### Subagent Definition for doc-writer

```yaml
---
name: doc-writer
description: Writes FDS section content following a PLAN.md. Use for all /doc:write-phase section writing tasks.
tools: Read, Write, Bash
disallowedTools: Glob, Grep
model: sonnet
permissionMode: acceptEdits
---

You are a technical documentation writer specializing in Functional Design Specifications for industrial automation systems.

## Context You Receive

When spawned, you have access to:
- PROJECT.md: project metadata, enabled standards, output language
- {phase}-CONTEXT.md: phase-specific decisions and gray area resolutions
- {plan-id}-PLAN.md: your specific writing plan (sections, context, template reference, verification checklist)
- Standards files (if enabled): packml-states.md, isa88-hierarchy.md

You do NOT have access to other plans or content from this phase. This isolation prevents cross-contamination.

## Your Task

1. Read your PLAN.md completely - it contains:
   - Goal: what this section achieves
   - Sections: what to document
   - Context: relevant background from CONTEXT.md
   - Template: structural reference (@path to template)
   - Standards: which apply (PackML, ISA-88)
   - Verification: how success is measured

2. Load the template referenced in PLAN.md to understand structure

3. Write CONTENT.md:
   - Follow template structure exactly
   - Fill all required sections (5 for equipment modules)
   - Use technical detail: specific values, units, ranges
   - Mark inferred content with [VERIFY] - never silently guess
   - For I/O tables: generate complete rows with industry-typical ranges (4-20mA, 0-100%), mark inferred with [VERIFY]
   - For state machines: high-level overview (Mermaid stateDiagram-v2 + summary table), flag complex transitions as [DETAIL NEEDED]
   - Create cross-references where obvious (interlocks, interfaces, HMI)
   - Use output language from PROJECT.md for headers and descriptions

4. Write SUMMARY.md:
   - Max 150 words
   - 4 mandatory sections: Facts, Key Decisions, Dependencies, Cross-refs
   - Facts: bullet list with counts (states: N, parameters: N, I/O: N DI, N DO, N AI)
   - Key Decisions: critical choices documented in this section
   - Dependencies: what this section depends on or provides to others
   - Cross-refs: standardized format (ID → zie §X.Y)

5. Log cross-references:
   - Append to CROSS-REFS.md (or create if first writer)
   - Format: | source | target | type | context |
   - Types: depends-on, related-to, see-also

6. Self-verify before completing:
   - [ ] CONTENT.md has all required sections
   - [ ] Technical content is substantive (>500 words for EM, >200 for others)
   - [ ] All tables are complete (no empty rows)
   - [ ] Inferred content marked with [VERIFY]
   - [ ] SUMMARY.md is 100-150 words
   - [ ] SUMMARY.md has all 4 sections
   - [ ] Cross-references logged in CROSS-REFS.md

7. Return completion message:
   - File: {plan-id}-CONTENT.md ({size})
   - File: {plan-id}-SUMMARY.md ({word-count} words)
   - Cross-refs: {count} logged
   - [VERIFY] markers: {count} (locations listed)
```

**Source:** Adapted from [Claude Code Subagent Examples](https://code.claude.com/docs/en/sub-agents#example-subagents), structured for doc-writing domain.

### Wave Execution with Parallel Spawning

```markdown
## Step 4: Execute Wave N (Parallel)

For wave {N} with {count} plans, spawn all writers simultaneously:

```bash
# Build spawn commands for all plans in wave
WAVE_PLANS=$(jq -r '.[] | select(.wave == '$WAVE_NUM') | .plan_id' wave-assignments.json)

for PLAN_ID in $WAVE_PLANS; do
  # Launch subagent in background
  claude --agent doc-writer \
    --context ".planning/PROJECT.md,.planning/phases/${PHASE}/*-CONTEXT.md,.planning/phases/${PHASE}/${PLAN_ID}-PLAN.md" \
    --message "Write section ${PLAN_ID} per plan. Produce CONTENT.md and SUMMARY.md." \
    --background &

  echo "Spawned writer for ${PLAN_ID}"
done

# Wait for all background subagents to complete
wait

echo "Wave ${WAVE_NUM} complete: ${count} sections written"
```

Update STATE.md checkpoint:
```bash
node ~/.claude/get-shit-done/bin/gsd-tools.js state patch \
  --field "current_operation.wave" "${WAVE_NUM}" \
  --field "current_operation.plans_done" "${COMPLETED_PLANS[@]}" \
  --field "current_operation.plans_pending" "${REMAINING_PLANS[@]}"
```
```

**Source:** Parallel execution pattern from [Claude Code Background Tasks](https://code.claude.com/docs/en/sub-agents#run-subagents-in-foreground-or-background).

### 5-Level Verification Cascade

```typescript
// Pseudocode for verification cascade
interface Truth {
  description: string;
  artifact: string;  // File path
  required_content: string[];
  context_requirements: Record<string, string>;
  standard_requirements: string[];
}

interface VerificationResult {
  level_1_exists: boolean;
  level_2_substantive: boolean;
  level_3_complete: boolean;
  level_4_consistent: boolean;
  level_5_standards: boolean;
  first_failure_level: number | null;
  gap_description: string | null;
}

function verifyCascade(truth: Truth): VerificationResult {
  const result: VerificationResult = {
    level_1_exists: false,
    level_2_substantive: false,
    level_3_complete: false,
    level_4_consistent: false,
    level_5_standards: false,
    first_failure_level: null,
    gap_description: null,
  };

  // Level 1: Exists
  if (!fileExists(truth.artifact)) {
    result.first_failure_level = 1;
    result.gap_description = `File ${truth.artifact} not found`;
    return result;  // STOP cascade
  }
  result.level_1_exists = true;

  const content = readFile(truth.artifact);

  // Level 2: Substantive
  const wordCount = content.split(/\s+/).length;
  const hasPlaceholders = /\[TODO\]|\[TBD\]|\[PLACEHOLDER\]/i.test(content);
  const hasStructure = /^#{1,4} /m.test(content);  // Has headers

  if (wordCount < 200 || hasPlaceholders || !hasStructure) {
    result.first_failure_level = 2;
    result.gap_description = `${truth.artifact} is not substantive (${wordCount} words, ${hasPlaceholders ? 'has placeholders' : 'no placeholders'}, ${hasStructure ? 'has structure' : 'no structure'})`;
    return result;  // STOP cascade
  }
  result.level_2_substantive = true;

  // Level 3: Complete
  const missingSections = truth.required_content.filter(section =>
    !content.includes(section)
  );

  if (missingSections.length > 0) {
    result.first_failure_level = 3;
    result.gap_description = `${truth.artifact} missing required sections: ${missingSections.join(', ')}`;
    return result;  // STOP cascade
  }
  result.level_3_complete = true;

  // Level 4: Consistent with CONTEXT.md
  const contextMismatches: string[] = [];
  for (const [requirement, expectedValue] of Object.entries(truth.context_requirements)) {
    if (!content.includes(expectedValue)) {
      contextMismatches.push(`${requirement} should be ${expectedValue}`);
    }
  }

  if (contextMismatches.length > 0) {
    result.first_failure_level = 4;
    result.gap_description = `${truth.artifact} inconsistent with CONTEXT.md: ${contextMismatches.join('; ')}`;
    return result;  // STOP cascade
  }
  result.level_4_consistent = true;

  // Level 5: Standards-compliant
  const standardViolations: string[] = [];
  for (const standard of truth.standard_requirements) {
    // Load standard reference and check compliance
    const violation = checkStandardCompliance(content, standard);
    if (violation) {
      standardViolations.push(violation);
    }
  }

  if (standardViolations.length > 0) {
    result.first_failure_level = 5;
    result.gap_description = `${truth.artifact} standards violations: ${standardViolations.join('; ')}`;
    return result;  // STOP cascade (but all levels checked)
  }
  result.level_5_standards = true;

  // All levels passed
  return result;
}
```

**Source:** Adapted from GSD verify-phase pattern in SPECIFICATION.md section 4.5.

### Gap Closure Loop with Iteration Counter

```bash
#!/bin/bash
# Workflow logic for gap closure loop

MAX_ITERATIONS=2
ITERATION=0

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
  echo "DOC > Verification Iteration $((ITERATION + 1)) of $MAX_ITERATIONS"

  # Run verification
  /doc:verify-phase ${PHASE}
  STATUS=$(jq -r '.status' .planning/phases/${PHASE}/VERIFICATION.md)

  if [ "$STATUS" == "PASS" ]; then
    echo "DOC > ✓ All verifications passed"
    exit 0
  fi

  if [ "$STATUS" == "GAPS_FOUND" ]; then
    ITERATION=$((ITERATION + 1))

    if [ $ITERATION -ge $MAX_ITERATIONS ]; then
      echo "DOC > ⚠ Max iterations reached, escalating to ENGINEER-TODO.md"

      # Extract remaining gaps and write to ENGINEER-TODO.md
      jq -r '.gaps[] | "### Gap: \(.description)\n**Severity:** \(.severity)\n**Context:** \(.evidence)\n"' \
        .planning/phases/${PHASE}/VERIFICATION.md > \
        .planning/ENGINEER-TODO.md

      # Mark phase as blocked
      node ~/.claude/get-shit-done/bin/gsd-tools.js state patch \
        --field "phases.${PHASE}.status" "BLOCKED" \
        --field "phases.${PHASE}.blocked_reason" "Gap closure failed after ${MAX_ITERATIONS} iterations"

      echo "DOC > Phase ${PHASE} BLOCKED. See ENGINEER-TODO.md for manual resolution."
      exit 1
    fi

    # Preview gaps and get confirmation
    echo "DOC > Gaps found, generating fix plans..."
    jq -r '.gaps[] | "- \(.description)"' .planning/phases/${PHASE}/VERIFICATION.md

    read -p "Generate fix plans for these gaps? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo "DOC > Gap closure cancelled by engineer"
      exit 1
    fi

    # Generate fix plans
    /doc:plan-phase ${PHASE} --gaps

    # Execute fixes
    /doc:write-phase ${PHASE}

    # Loop back to verify again
  fi
done
```

**Source:** User decision in CONTEXT.md specifies max 2 cycles with engineer confirmation before fix generation.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Sequential section writing with shared context | Parallel wave-based writing with isolated context per writer | Claude Code subagents 2024-2025 | Prevents cross-contamination, enables true parallelism |
| Task completion verification (file exists?) | Goal-backward 5-level cascade verification | GSD framework 2025 | Catches substantive vs stub content, inconsistencies |
| Unlimited retry loops on gaps | Max 2 iterations with human escalation | This project 2026 | Prevents infinite loops, forces human judgment on persistent gaps |
| Single model for all tasks | Per-task model selection (sonnet for writing, haiku for verification) | Claude Code subagent model field 2025 | Cost optimization without quality loss |
| Manual cross-reference tracking | Automated CROSS-REFS.md registry during writing | This project 2026 | Enables assembly-time resolution, reduces broken references |

**Deprecated/outdated:**
- Manual context passing to subagents: Claude Code --context flag replaces DIY file injection
- Custom parallel execution: Claude Code --background replaces manual thread management
- Inline fix suggestions in verification: Separation of verification (describe gap) and planning (determine fix) is now standard

## Open Questions

1. **Optimal wave size for parallel execution**
   - What we know: Claude Code can spawn unlimited subagents, but system resources limit practical parallelism
   - What's unclear: What's the sweet spot between parallelism (minimize wall-clock time) and resource usage (disk I/O, API rate limits)?
   - Recommendation: Start with max 4 parallel writers per wave (conservative), make configurable in config.json, document performance testing results in Phase 3 verification

2. **Re-verification scope heuristics**
   - What we know: Isolated content fixes don't need full-phase re-verification; cross-reference changes do
   - What's unclear: What's the reliable heuristic to detect "cross-reference touched"? Git diff keyword matching? Explicit marker in fix plan?
   - Recommendation: Let engineer decide via flag (--scope full|sections:id,id) for Phase 3, gather data on false positives/negatives, automate in later phase if pattern emerges

3. **[VERIFY] marker resolution timing**
   - What we know: Writers mark inferred content with [VERIFY], engineer must confirm
   - What's unclear: When does engineer review these? During gap closure? After phase complete? Separate command?
   - Recommendation: Out of Phase 3 scope (no command to resolve [VERIFY] markers), document in ENGINEER-TODO.md with markers, address in Phase 4 (review-phase) or later

4. **Standards file versioning**
   - What we know: PackML and ISA-88 references are loaded from gsd-docs-industrial/references/
   - What's unclear: What if standards evolve? How to track which version was used for this FDS?
   - Recommendation: Log standards file git hashes in PROJECT.md when first loaded, include in FDS metadata section, enables reproducible verification

## Sources

### Primary (HIGH confidence)

- [Claude Code Subagent Documentation](https://code.claude.com/docs/en/sub-agents) - Complete subagent system reference, verified 2026-02-10
- SPECIFICATION.md sections 4.4 (write-phase), 4.5 (verify-phase), 9.7 (error recovery) - Project-specific patterns
- CONTEXT.md Phase 3 - User decisions on content depth, verification format, gap closure
- Phase 1 RESEARCH.md - Established command + workflow separation pattern
- Phase 2 RESEARCH.md - FDS-domain adaptation of GSD patterns

### Secondary (MEDIUM confidence)

- [Claude Code Parallel Subagents Guide](https://timdietrich.me/blog/claude-code-parallel-subagents/) - Practical patterns for parallel execution
- [Agent Teams Multi-Session Orchestration](https://claudefa.st/blog/guide/agents/agent-teams) - Context on when to use teams vs subagents
- [How to Use Claude Code Subagents to Parallelize Development](https://zachwills.net/how-to-use-claude-code-subagents-to-parallelize-development/) - Parallel execution best practices
- [Session Management - Claude API Docs](https://platform.claude.com/docs/en/agent-sdk/sessions) - Session isolation and state preservation

### Tertiary (LOW confidence)

- [Goal Achievement in AI Planning](https://arxiv.org/html/2503.09545v2) - Academic research on goal persistence verification, not specific to Claude Code
- Web search results on "goal-backward verification" - General concept, needs verification in Claude context

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Claude Code subagent system is official, well-documented, verified with direct source reading
- Architecture patterns: HIGH - Based on established Phase 1/2 patterns plus official Claude Code documentation
- Pitfalls: MEDIUM-HIGH - Derived from SPECIFICATION.md and general distributed systems experience; some require validation during Phase 3 execution
- Code examples: HIGH - Adapted from official Claude Code documentation and verified SPECIFICATION.md patterns

**Research date:** 2026-02-10
**Valid until:** 2026-03-10 (30 days - relatively stable domain, Claude Code subagent system is mature)

**Critical verification needs:**
- Wave size performance testing (open question 1)
- Re-verification scope heuristics accuracy (open question 2)
- [VERIFY] marker workflow (open question 3)
