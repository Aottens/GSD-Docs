---
phase: 06-knowledge-transfer-review
plan: 03
subsystem: fresh-eyes-review
tags: [fresh-eyes, verify-phase, multi-perspective, comprehension-gaps, completeness-gaps]
dependency_graph:
  requires:
    - rationale.md template (from 06-01)
    - fresh-eyes.md template (from 06-01)
  provides:
    - fresh-eyes.md subagent (configurable perspective reviewer)
    - verify-phase Fresh Eyes offer (post-PASS optional review)
    - Multi-perspective review capability (engineer/customer/operator/all)
  affects:
    - verify-phase.md workflow (enhanced with Fresh Eyes offer after PASS)
tech_stack:
  added: []
  patterns:
    - Subagent with configurable perspective parameter
    - Read/Write tools only (no Bash/Glob/Grep for context isolation)
    - Interactive perspective selection via AskUserQuestion
    - Optional gap closure routing via --actionable flag
    - Default informational (no auto-routing)
key_files:
  created:
    - gsd-docs-industrial/agents/fresh-eyes.md
  modified:
    - gsd-docs-industrial/workflows/verify-phase.md
decisions:
  - fresh-eyes has Read/Write tools only (no Bash/Glob/Grep) for context isolation same as doc-writer pattern
  - 3 perspectives with distinct checking criteria: engineer (technical), customer (jargon), operator (procedures)
  - Comprehension gaps (undefined/assumed) + completeness gaps (missing/logical jumps) distinction
  - 3-level severity: MUST-FIX (blocks understanding), SHOULD-FIX (helps clarity), CONSIDER (nice-to-have)
  - Evidence requirement: every finding must quote CONTENT.md with specific reference
  - RATIONALE.md integration: check for documented decisions before flagging as unclear
  - Fresh Eyes offered after PASS only (never after GAPS_FOUND) - verification complete regardless of review outcome
  - Interactive perspective selection unless --perspective flag provided
  - Default informational only - --actionable flag required to route to gap closure
  - Fresh Eyes inserted in Step 6A.5 between PASS display and ROADMAP Evolution Check
metrics:
  duration_seconds: 182
  tasks_completed: 2
  files_created: 1
  files_modified: 1
  commits: 2
  completed_date: 2026-02-14
---

# Phase 06 Plan 03: Fresh Eyes Review Subagent + Verify-Phase Enhancement

**One-liner:** Created fresh-eyes subagent with configurable perspective (engineer/customer/operator/all) for simulated reader review and enhanced verify-phase workflow to offer Fresh Eyes after PASS result with optional gap closure routing

## What Was Built

### Task 1: Fresh Eyes Subagent Definition

Created `gsd-docs-industrial/agents/fresh-eyes.md` following the established subagent pattern (YAML frontmatter + role + task steps).

**Tool configuration:**
- Tools: Read, Write
- Disallowed: Bash, Glob, Grep
- Pattern: Same as doc-writer (Read/Write/Bash but no Glob/Grep for context isolation)
- Correction during task: Initially planned Read-only, then recognized fresh-eyes needs Write to create FRESH-EYES.md output file

**Three perspective definitions with distinct checking criteria:**

1. **Engineer perspective:**
   - Who: New engineer joining project team
   - Checks: technical terms undefined, missing implementation details, ambiguous specs, inconsistent terminology
   - Assumptions HAS: general automation knowledge, PLC/HMI familiarity, control loop understanding
   - Assumptions LACKS: project-specific decisions, equipment-specific behavior, client preferences
   - Stricter on: safety-critical sections, interfaces, interlocks
   - Lighter on: overview sections, appendices

2. **Customer perspective:**
   - Who: Client reading FDS for first time
   - Checks: jargon without explanation, unexplained abbreviations, overly technical language, unclear scope, commitments not stated
   - Assumptions HAS: basic process understanding, what they asked for
   - Assumptions LACKS: technical automation background, industry standards knowledge
   - **Strict jargon policy (user decision):** Flag ALL internal jargon, ALL unexplained abbreviations, ALL overly technical language
   - Stricter on: scope boundaries, commitments, cost-impacting decisions
   - Lighter on: technical implementation details

3. **Operator perspective:**
   - Who: Operator running system daily
   - Checks: procedural clarity (start/stop/recover steps), alarm response instructions, state transitions, manual controls, missing operational details
   - **User decision:** Check BOTH procedural clarity AND operational completeness (states, alarms, sequences)
   - Assumptions HAS: familiarity with own process, basic HMI operation
   - Assumptions LACKS: internal system logic, PLC behavior, interlock reasoning
   - Stricter on: alarm responses, manual procedures, recovery steps, fault handling
   - Lighter on: system architecture, design rationale

**Two gap categories:**
- **Comprehension gaps:** Things reader cannot understand without asking (undefined terms, assumed knowledge)
- **Completeness gaps:** Things that should be there but are not (missing sections, logical jumps)

**Three severity levels with concrete examples per perspective:**

- **MUST-FIX:** Genuinely confusing, blocks understanding
  - Engineer: "§3.2 mentions 'settling time' without defining value or units"
  - Customer: "§7.2 uses 'Modbus TCP' without explaining what this means"
  - Operator: "§5.1 alarm AL-300-01 has no response procedure documented"

- **SHOULD-FIX:** Improvement that would help clarity
  - Engineer: "§3.3 transition conditions reference CONTEXT.md decisions not summarized in section"
  - Customer: "§4.1 says 'standard HMI layout' but doesn't specify which standard"
  - Operator: "§3.2 describes automatic sequence but not manual override procedure"

- **CONSIDER:** Nice-to-have, minor enhancement
  - Engineer: "§3.2 could benefit from Mermaid diagram showing state flow"
  - Customer: "§7.2 could clarify expected network response time"
  - Operator: "§5.1 could add typical duration for each state"

**Severity calibration rules:**
- Safety-critical sections: one level stricter
- Overview/introduction sections: one level lighter
- When in doubt: err on side of flagging (better over-report than miss)

**Evidence requirement:**
Every finding must include:
- Specific quote or reference from CONTENT.md
- Section reference (§X.Y or plan-id)
- Clear explanation of what's unclear or missing
- Why it matters to this perspective

**RATIONALE.md integration:**
- Check RATIONALE.md for documented decisions before flagging as "unclear"
- If reasoning documented in RATIONALE.md, not a gap in understanding
- However, if reasoning ONLY in RATIONALE.md and not summarized in FDS section, might be SHOULD-FIX (FDS should be self-contained)

**Output quality rules:**
- Never flag "missing" content without checking ALL CONTENT.md, ALL SUMMARY.md, and RATIONALE.md first
- Use SUMMARY.md first for token efficiency, then CONTENT.md for detail
- Every finding requires evidence (no vague "section seems incomplete")

**Task steps (5 steps):**
1. Determine perspective from spawning message
2. Read all SUMMARY.md files first (token-efficient), then CONTENT.md for detail
3. For each section, identify findings in two categories (comprehension/completeness)
4. Classify severity with examples (MUST-FIX/SHOULD-FIX/CONSIDER)
5. Write FRESH-EYES.md to phase directory using template format

**File created:** `gsd-docs-industrial/agents/fresh-eyes.md` (272 lines, 8.6KB)

### Task 2: Verify-Phase Workflow Enhancement

Enhanced `gsd-docs-industrial/workflows/verify-phase.md` with Fresh Eyes offer after PASS result.

**Integration point:**
- Inserted new Step 6A.5 between PASS display (Step 6A, line 480) and ROADMAP Evolution Check (line 490)
- After STATE.md update to "✓ Verified", before expansion check
- Preserves existing verify-phase flow - no restructuring, clean insertion only

**New Step 6A.5: Offer Fresh Eyes Review**

1. **Check for --perspective flag in arguments:**
   ```bash
   PERSPECTIVE_FLAG=$(echo "$ARGUMENTS" | grep -oE "\-\-perspective (engineer|customer|operator|all)" | cut -d' ' -f2)
   ACTIONABLE_FLAG=$(echo "$ARGUMENTS" | grep -c "\-\-actionable")
   ```

2. **If --perspective flag provided:** Skip selection, use provided perspective (non-interactive mode)

3. **If no flag:** Present selection using AskUserQuestion:
   - header: "Optional: Fresh Eyes Review"
   - question: "Verification passed. Simulate a new reader reviewing the documentation?"
   - options:
     - "Engineer (technical clarity for new team member)"
     - "Customer (jargon, commitments, scope for client review)"
     - "Operator (procedures, alarms, recovery for daily use)"
     - "All perspectives (comprehensive review)"
     - "Skip Fresh Eyes"

4. **If "Skip" selected:** Display "Fresh Eyes review skipped." and continue to ROADMAP Evolution Check

5. **If perspective selected:** Spawn fresh-eyes subagent:
   - Build context file list: PROJECT.md, RATIONALE.md (if exists), phase CONTEXT.md, all CONTENT.md, all SUMMARY.md
   - Display spawning indicator: "DOC > Launching Fresh Eyes review ({perspective} perspective)..."
   - Spawn using Task tool with agent reference and context files
   - Wait for completion

6. **Display results summary:**
   ```bash
   MUST_FIX=$(grep -c "MUST-FIX" "${PHASE_DIR}/${PADDED_PHASE}-FRESH-EYES.md" || echo 0)
   SHOULD_FIX=$(grep -c "SHOULD-FIX" "${PHASE_DIR}/${PADDED_PHASE}-FRESH-EYES.md" || echo 0)
   CONSIDER=$(grep -c "CONSIDER" "${PHASE_DIR}/${PADDED_PHASE}-FRESH-EYES.md" || echo 0)

   echo "Fresh Eyes review complete:"
   echo "  MUST-FIX: ${MUST_FIX}"
   echo "  SHOULD-FIX: ${SHOULD_FIX}"
   echo "  CONSIDER: ${CONSIDER}"
   echo "  See: ${PHASE_DIR}/${PADDED_PHASE}-FRESH-EYES.md"
   ```

7. **Check --actionable flag:**
   - If flag present AND (MUST_FIX > 0 OR SHOULD_FIX > 0): "Routing actionable findings to gap closure pipeline... Run: /doc:plan-phase ${PHASE} --gaps --source fresh-eyes"
   - If flag present AND no actionable findings: "No actionable findings. Gap closure not needed."
   - If flag absent: "Findings are informational. Use --actionable flag to route to gap closure."

**Also updated "Also available" block in Step 6A:**
Before:
```
- `/doc:review-phase {N}` -- optional client/engineer review
- `/doc:status` -- view overall progress
```

After:
```
- `/doc:review-phase {N}` -- structured section-by-section review
- `/doc:verify-phase {N} --perspective engineer` -- Fresh Eyes with specific perspective
- `/doc:status` -- view overall progress
```

**Added Fresh Eyes workflow rule:**
```
**Fresh Eyes review:**
- Offered after PASS only (never after GAPS_FOUND)
- Engineer can accept or skip (never forced)
- Output: per-phase FRESH-EYES.md (distinct from VERIFICATION.md)
- Default: informational only (findings logged, no action)
- --actionable flag: routes MUST-FIX and SHOULD-FIX to gap closure pipeline
- --perspective flag: skip selection, use provided perspective
- Fresh Eyes does NOT change PASS result -- verification is complete regardless
```

**File modified:** `gsd-docs-industrial/workflows/verify-phase.md` (+113 lines, 1 deletion)

## Verification

All plan verification criteria met:

1. ✓ fresh-eyes.md follows established agent file pattern (frontmatter + role + steps)
2. ✓ fresh-eyes has correct tool permissions (Read, Write only -- no Bash, Glob, Grep)
3. ✓ Three perspectives have distinct checking criteria matching CONTEXT.md decisions
4. ✓ verify-phase.md offers Fresh Eyes only after PASS (not after GAPS_FOUND)
5. ✓ Interactive perspective selection uses AskUserQuestion
6. ✓ --perspective flag allows non-interactive use
7. ✓ --actionable flag enables gap closure routing
8. ✓ Default is informational only (no auto-routing)
9. ✓ PASS result is unaffected by Fresh Eyes outcome
10. ✓ No existing verify-phase behavior changed

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Task | Commit | Files |
|------|--------|-------|
| 1    | fefed44 | gsd-docs-industrial/agents/fresh-eyes.md |
| 2    | 1682db4 | gsd-docs-industrial/workflows/verify-phase.md |

## Key Decisions

1. **Tool configuration correction:** Plan initially specified Read-only for fresh-eyes, but recognized during execution that fresh-eyes needs Write tool to create FRESH-EYES.md output. Updated to Read/Write (same pattern as doc-writer: context isolation via Glob/Grep disallowed, not all tools disabled).

2. **Strict customer jargon policy:** Customer perspective strictly flags ALL jargon, unexplained abbreviations, and overly technical language per user decision in CONTEXT.md.

3. **Operator completeness scope:** Operator perspective checks BOTH procedural clarity (how to do things) AND operational completeness (states, alarms, sequences) per user decision.

4. **Evidence requirement enforced:** Every finding must quote CONTENT.md with specific reference - prevents vague "seems incomplete" findings.

5. **RATIONALE.md integration:** fresh-eyes checks RATIONALE.md before flagging content as "unclear" - if reasoning is documented, it's not a comprehension gap. However, if reasoning is ONLY in RATIONALE.md and not in FDS, that's a different issue (FDS self-containment).

6. **Default informational only:** Fresh Eyes findings are logged in FRESH-EYES.md but do NOT auto-route to gap closure. Engineer must explicitly use --actionable flag. This matches user decision: "Default informational only".

7. **PASS result unaffected:** Fresh Eyes review happens AFTER verification PASS and does NOT change the PASS status. Verification is complete regardless of Fresh Eyes outcome. This is explicit in workflow rules.

8. **Integration point:** Fresh Eyes inserted as Step 6A.5 between PASS display and ROADMAP Evolution Check - preserves existing flow, no restructuring.

## Dependencies

**Requires from upstream:**
- Plan 06-01: fresh-eyes.md template (defines FRESH-EYES.md output format)
- Plan 06-01: rationale.md template (fresh-eyes reads RATIONALE.md for decision context)

**Provides for downstream:**
- Plan 06-05: fresh-eyes subagent ready for integration testing
- Gap closure pipeline: --source fresh-eyes support (findings can route to plan-phase --gaps)

**Affects:**
- verify-phase workflow: enhanced with Fresh Eyes offer (backward-compatible - engineer can skip)

## Cross-References

- gsd-docs-industrial/agents/fresh-eyes.md references gsd-docs-industrial/templates/fresh-eyes.md (output template)
- gsd-docs-industrial/workflows/verify-phase.md references gsd-docs-industrial/agents/fresh-eyes.md (subagent spawning)
- fresh-eyes reads .planning/RATIONALE.md for decision context (integration with Plan 06-01 output)

---

## Self-Check: PASSED

Verified all claims in SUMMARY.md:

**Created files:**
- FOUND: gsd-docs-industrial/agents/fresh-eyes.md (272 lines)

**Modified files:**
- FOUND: gsd-docs-industrial/workflows/verify-phase.md (+113 lines)

**Commits:**
- FOUND: fefed44 (feat(06-03): create fresh-eyes subagent definition)
- FOUND: 1682db4 (feat(06-03): enhance verify-phase with Fresh Eyes offer)

**Verification checks:**
- FOUND: "tools: Read, Write" in fresh-eyes.md
- FOUND: "disallowedTools: Bash, Glob, Grep" in fresh-eyes.md
- FOUND: 3 perspective definitions (Engineer, Customer, Operator)
- FOUND: Step 6A.5 in verify-phase.md
- FOUND: AskUserQuestion reference in Step 6A.5
- FOUND: --perspective flag handling
- FOUND: --actionable flag handling
- FOUND: Fresh Eyes workflow rule

All files created, all commits exist, all claims verified.

---

*Plan type: execute*
*Completed: 2026-02-14*
*Duration: 182 seconds (3 minutes)*
