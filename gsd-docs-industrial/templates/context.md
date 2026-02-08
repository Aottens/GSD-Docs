<!-- TEMPLATE: Phase CONTEXT.md
     Used by: /doc:discuss-phase workflow (reads this for structure, fills with discussion content)
     Consumed by: /doc:plan-phase (reads decisions to generate section PLANs)
     Consumed by: /doc:write-phase writer subagents (reads decisions for context)

     Size guideline: CONTEXT.md should stay under 100 lines to avoid overwhelming
     writer subagents with excessive context (Pitfall 7 mitigation).

     Content priority (highest to lowest):
     1. Decisions that change implementation (concrete values, behaviors, edge cases)
     2. Specific technical values (temperatures, capacities, timing, ranges)
     3. General approach notes (only if they affect what gets written)

     Sections use XML tags for semantic grouping -- matching CLAUDE-CONTEXT.md pattern.
     The discuss-phase workflow fills {PLACEHOLDER} values from the engineer discussion. -->

# Phase {N}: {Phase Name} - Context

**Gathered:** {DATE}
**Status:** Ready for planning

<domain>
## Phase Boundary

{What this phase delivers -- extracted from ROADMAP.md phase goal.
This is the fixed boundary. Discussion clarifies implementation within it.}

{For Type C/D: "Delta from BASELINE.md -- only changes are in scope.
The existing system is treated as given. Describe only what changes."}

</domain>

<decisions>
## Implementation Decisions

### {Equipment/Section/Topic 1 from gray area discussion}

- {Specific technical decision with concrete values -- not vague requirements}
- {Failure mode or edge case handling -- what happens when things go wrong}
- {Cross-reference to other equipment if applicable -- flag for review}

### {Equipment/Section/Topic 2}

- {Decision with rationale if non-obvious}

### Claude's Discretion

- {Areas explicitly delegated to Claude -- documented so the engineer knows what was delegated}
- {These items are NOT asked during discussion -- Claude decides during planning/writing}
- {Common: exact table formatting, subsection ordering, cross-reference phrasing}

</decisions>

<specifics>
## Specific Ideas

{Technical specifics from discussion: exact values, preferred approaches,
references to existing documentation or equipment manuals.
Keep focused -- only specifics that change what gets written.}

{Examples: "Max belt speed 2.5 m/s", "Use same interlock pattern as EM-100",
"Client prefers alarm categories: Critical / Warning / Info"}

</specifics>

<deferred>
## Deferred Ideas

{Ideas that belong in other phases -- captured so they are not lost,
but explicitly out of scope for this phase.
Format: "- {Idea} -- Phase {N}". If none: "None -- discussion stayed within phase scope"}

</deferred>

---
*Phase: {NN}-{name}*
*Context gathered: {DATE}*
