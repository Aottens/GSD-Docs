<!-- TEMPLATE: ENGINEER-TODO.md
     Created by: /doc:verify-phase when gap closure loop exceeds max 2 cycles
     Purpose: Tracks remaining gaps that require manual engineer intervention
     Effect: Phase is BLOCKED until gaps are resolved or explicitly accepted

     This file is created automatically. Engineer resolves gaps manually,
     then re-runs /doc:verify-phase to re-check.
     To unblock without fixing: mark gaps as "accepted" with rationale.

     Validation rules:
     - Severity must be High, Medium, or Low
     - Level references the 5-level cascade (1-Exists, 2-Substantive, 3-Complete, 4-Consistent, 5-Standards)
     - Description copied verbatim from VERIFICATION.md
     - "Accepted" marker pattern for unblocking: **Accepted:** {rationale} -->

# Phase {N}: {Phase Name} - Manual Intervention Required

**Date:** {YYYY-MM-DD}
**Reason:** Gap closure loop terminated after max 2 cycles
**Phase status:** BLOCKED

## Instructions

The automated gap closure loop has run {cycle_count} times without resolving all gaps.
Remaining gaps require manual engineer review and action.

**To resolve:**
1. Review each gap below
2. Fix the content file directly or provide missing information
3. Run `/doc:verify-phase {N}` to re-verify

**To accept gaps (unblock without fixing):**
1. Add `**Accepted:** {rationale}` under the gap
2. Run `/doc:verify-phase {N}` -- accepted gaps are skipped

## Remaining Gaps

### Gap {N}: {Truth description}

**Severity:** {High | Medium | Low}
**Level:** {Level N - Level Name} (where verification cascade stopped)
**Description:** {Gap description from VERIFICATION.md}
**Evidence:**
- File: {path}
- Context: {CONTEXT.md reference or standards reference}
**Attempted fixes:** {count} automated cycles
**Suggested action:**
1. {Actionable step for engineer}
2. Run `/doc:verify-phase {N}` to re-check

---

{Repeat "Remaining Gaps" section for each unresolved gap}

---

## Next Steps

After resolving gaps manually:
- Run `/doc:verify-phase {N}` to verify fixes
- If verification passes: proceed with next phase
- If verification still finds gaps: additional manual intervention required

After accepting gaps without fixing:
- Add `**Accepted:** {rationale}` marker under each accepted gap above
- Run `/doc:verify-phase {N}` -- accepted gaps will be skipped
- Verify-phase will show PASS if all remaining gaps are accepted
