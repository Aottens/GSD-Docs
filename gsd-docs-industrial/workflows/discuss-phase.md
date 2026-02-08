<workflow>

# /doc:discuss-phase Workflow

Complete execution logic for phase discussion and decision capture. The command file (`~/.claude/commands/doc/discuss-phase.md`) delegates here. Follow each step in order.

**Purpose:** Front-load implementation decisions so that `/doc:plan-phase` and `/doc:write-phase` can act without re-asking the engineer. Adapt the GSD discuss-phase pattern to the FDS domain, where gray areas are technical specifications (capacities, tolerances, failure modes, protocols, operating states) rather than software design decisions.

**Downstream consumers:**
- `/doc:plan-phase` reads CONTEXT.md to generate section PLANs with locked decisions
- `/doc:write-phase` writer subagents read CONTEXT.md for technical specifics
- Neither should need to re-ask the engineer about captured decisions

**Philosophy:** Engineer = domain expert with process knowledge. Claude = documentation builder. The engineer knows operating parameters, failure modes, equipment behavior, and client requirements. Claude structures this into FDS-ready content. Ask about specifications and implementation choices -- never about document formatting or section structure.

---

## Step 1: Validate Phase

Parse `$ARGUMENTS` to get the phase number. This is required -- abort if missing.

```bash
PHASE=$ARGUMENTS
PADDED_PHASE=$(printf "%02d" ${PHASE})
```

### 1.1 Read ROADMAP.md

Read `.planning/ROADMAP.md` to find the phase entry.

Extract:
- Phase number and name
- Phase goal / description
- Phase dependencies (prior phases that must be complete)
- Phase requirements or deliverables list

**If phase not found in ROADMAP.md:**

```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

Phase {N} not found in ROADMAP.md.

**To fix:** Use `/doc:status` to see available phases,
or check .planning/ROADMAP.md for the phase list.
```

Stop execution. Do not continue.

### 1.2 Check Dependencies

For each dependency listed in the phase entry, verify completion by checking for SUMMARY.md files in the dependent phase directories. SUMMARY.md existence is the completion proof -- not STATE.md status.

```bash
# Example: if phase 3 depends on phase 2
ls .planning/phases/02-*/SUMMARY.md 2>/dev/null
ls .planning/phases/02-*/*-SUMMARY.md 2>/dev/null
```

**If dependencies are unmet (no SUMMARY.md found):**

```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

Phase {N} depends on Phase {D} which is not yet complete.
No SUMMARY.md found in .planning/phases/{DD}-{name}/.

**To fix:** Complete Phase {D} first, then return to Phase {N}.
```

Stop execution. Do not continue.

### 1.3 Check Existing CONTEXT.md

```bash
ls .planning/phases/${PADDED_PHASE}-*/${PADDED_PHASE}-CONTEXT.md 2>/dev/null
ls .planning/phases/${PADDED_PHASE}-*/CONTEXT.md 2>/dev/null
```

**If CONTEXT.md already exists:**

Use AskUserQuestion:
- header: "Existing Context"
- question: "Phase {N} already has a CONTEXT.md. What do you want to do?"
- options:
  - "Update it" -- review and revise existing context
  - "View it" -- show current content, then choose
  - "Skip" -- use existing context as-is

If "Update": load existing content, continue to Step 2
If "View": display CONTEXT.md, then offer update/skip
If "Skip": exit workflow

**If CONTEXT.md does not exist:** Continue to Step 2.

### 1.4 Display Banner

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > DISCUSSING PHASE {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Dutch (if `LANGUAGE = "nl"`): `DOC > FASE {N} BESPREKEN`

---

## Step 2: Detect Content Type

### 2.1 Read Project Configuration

Read `.planning/PROJECT.md` for:
- Project type (A, B, C, or D)
- Language setting (nl or en)
- Standards configuration (PackML enabled, ISA-88 enabled)

Store as `PROJECT_TYPE`, `LANGUAGE`, `PACKML_ENABLED`, `ISA88_ENABLED`.

### 2.2 Analyze Phase Goal for Content Types

Read the phase goal text from ROADMAP.md and determine the content type(s) this phase covers. A phase can have multiple content types.

**Content type detection (keyword mapping):**

| Keywords in phase goal | Content type |
|---|---|
| "equipment", "module", "EM-", "unit", "functional unit" | Equipment Modules |
| "architecture", "system overview", "hierarchy", "overview" | System Architecture |
| "interface", "communication", "protocol", "bus", "network" | Interfaces |
| "HMI", "visualization", "screen", "display", "operator" | HMI |
| "safety", "interlock", "SIL", "E-stop", "emergency" | Safety |
| "foundation", "scope", "terminology", "introduction", "definitions" | Foundation |
| "appendix", "signal list", "parameter list", "index" | Appendices |
| "control", "philosophy", "operating mode", "mode" | Control Philosophy |
| "state", "state machine", "PackML" | State Machines |

A phase can match multiple types. For example, an Equipment Modules phase typically includes both Equipment Modules AND State Machines content.

### 2.3 Type C/D: Load Baseline

**Only if `PROJECT_TYPE` is C or D:**

Read `.planning/BASELINE.md` to understand the existing system scope. Extract:
- Which equipment exists and is UNCHANGED
- Which equipment is MODIFIED
- What is NEW

This informs the delta-focused discussion in Steps 3-5.

---

## Step 3: Identify Gray Areas

This is the core adaptation from GSD to FDS. The GSD discuss-phase analyzes what kind of software is being built. The FDS version analyzes what kind of technical documentation content is being written and probes at FULL functional spec depth.

### 3.1 Generate Gray Area Topics

For each detected content type, generate gray area topics. Do NOT use a fixed list -- derive topics from the specific phase goal and content type. Use these probing patterns as guidance for the depth expected.

**Equipment Modules gray areas (probe FULL depth):**

- **Operating parameters** -- Ranges, tolerances, timing constraints, capacities. What are the process limits? What triggers alarms vs trips?
- **Operating states** -- State model (PackML if enabled), entry/exit conditions, transitions. Which states does this equipment actually use?
- **Interlocks** -- Conditions, actions, priorities. Cross-EM interlocks? Sequence dependencies?
- **Failure modes** -- Sensor failure behavior (hold last value? go to safe state?), actuator failure, recovery approach (automatic vs manual intervention)
- **Manual overrides** -- Which operations allow manual override? Under what conditions? Safety constraints on overrides?
- **Startup/shutdown sequences** -- Step order, timing between steps, conditions for advancing, abort behavior
- **Maintenance mode** -- What is accessible? What is restricted? How does the equipment behave?

**Interfaces gray areas:**

- **Protocol selection** -- Which protocol, why? Data format? Message structure?
- **Signal list** -- Direction (in/out), data types, update rates, engineering units
- **Error handling** -- Timeout behavior, retry logic, fallback values, stale data detection
- **Handshake patterns** -- Acknowledgment, data validation, sequence management
- **Connection failure** -- Detection method, alarm generation, recovery procedure, impact on dependent equipment

**HMI gray areas:**

- **Screen hierarchy** -- Navigation structure, access levels (operator/supervisor/engineer), screen count
- **Alarm presentation** -- Grouping strategy, priority levels, acknowledgment rules, alarm shelving
- **Trend displays** -- Which signals to trend, retention period, Y-axis scales, comparison views
- **Manual controls** -- Which operations from HMI, confirmation dialogs, safety constraints, authorization requirements

**Safety gray areas:**

- **Risk categories** -- Which interlocks are safety-critical vs process interlocks?
- **E-stop behavior** -- Scope (local/zone/plant-wide), recovery sequence, reset requirements
- **SIL levels** -- If applicable: which safety functions, required SIL level, impact on architecture
- **Fail-safe states** -- Per equipment module, what is the fail-safe state? Valve positions, motor states, heating off?

**Foundation/Architecture gray areas:**

- **Scope boundaries** -- What is documented in this FDS, what is explicitly out of scope?
- **Equipment grouping** -- How are equipment modules organized? By process area? By function?
- **Operating modes** -- Plant-level modes (Production, Manual, Maintenance, Cleaning) and their effect on equipment behavior
- **Terminology** -- Project-specific terms, abbreviation conventions, reference standards

**Control Philosophy gray areas:**

- **Control strategy** -- Regulatory control (PID), sequence control, batch control? Combination?
- **Mode transitions** -- How do plant modes affect equipment? Automatic transitions or operator-initiated?
- **Alarm philosophy** -- How many priority levels? Rationalization approach? Alarm flood management?

**Appendices gray areas:**

- **Signal list scope** -- All I/O or only external? Include virtual signals?
- **Parameter list** -- Which parameters are operator-adjustable? Access levels?
- **Document cross-references** -- P&ID references, wiring diagram references, vendor document list

### 3.2 Topic Selection and Count

Present 3-5 gray area topics per content type. Keep the discussion manageable -- do not overwhelm with 8-10 topics (Pitfall 7 mitigation).

If the phase has many potential areas:
1. Present the 3-5 most impactful topics (ones where a wrong assumption changes the written output)
2. After the list, offer: "Any other areas you want to discuss?"

### 3.3 Type C/D: Delta Framing

**For Type C/D projects:** Frame ALL gray areas as deltas from the baseline.

**Pattern:** "The existing system does X (from BASELINE.md). Are you changing this? If so, how?"

Focus questions on what is NEW or DIFFERENT. Do not re-specify the existing system. Examples:

- GOOD: "EM-100 currently has 3 operating states (Idle, Running, Faulted). Are you adding new states or changing transitions?"
- BAD: "What operating states should EM-100 have?" (re-specifies existing)

- GOOD: "The current HMI has 12 screens. Which screens are being modified, and are any new screens needed?"
- BAD: "How many HMI screens do you need?" (ignores baseline)

---

## Step 4: Present Gray Areas

### 4.1 State the Phase Boundary

Display the domain boundary clearly -- this is the scope anchor for the entire discussion.

```
Phase {N}: {Phase Name}
Domain: {What this phase delivers -- from ROADMAP.md goal}

We will clarify HOW to implement this phase.
(New capabilities belong in other phases.)
```

For Type C/D, add:
```
Delta scope: Changes to the existing system as described in BASELINE.md.
Unchanged functionality is not in scope for this discussion.
```

### 4.2 Present Topics for Selection

Use AskUserQuestion (multiSelect: true):
- header: "Discussion Topics"
- question: "Which areas do you want to discuss for Phase {N}: {Phase Name}?"
- options: Generated gray area topics (3-5 per content type), each formatted as:
  - "[Topic name]" -- 1-line description of what this covers

**Include a "Claude's Discretion" option** for topics the engineer wants to delegate:
- "Mark any remaining topics as Claude's Discretion" -- Claude will make reasonable decisions and document them

**Example for an Equipment Modules phase:**
```
Which areas do you want to discuss for Phase 3: Equipment Modules?

[ ] Operating parameters -- Ranges, tolerances, capacities for each EM
[ ] Operating states -- State model, transitions, entry/exit conditions
[ ] Interlocks and failure modes -- Trip conditions, sensor failure behavior, recovery
[ ] Startup/shutdown sequences -- Step order, timing, abort conditions
[ ] Mark remaining as Claude's Discretion -- reasonable defaults, documented
```

### 4.3 Record Selections

Store:
- `SELECTED_TOPICS` -- Topics the engineer wants to discuss
- `DISCRETION_TOPICS` -- Topics delegated to Claude (from unselected topics or explicit delegation)

---

## Step 5: Deep-Dive Discussion

For each selected gray area topic, conduct a focused, specification-depth discussion.

### 5.1 Discussion Flow Per Topic

For each topic in `SELECTED_TOPICS`:

1. **Announce the topic:**
   ```
   Let's discuss: {Topic Name}
   ```

2. **Ask 3-5 targeted questions at functional spec depth.** These are NOT generic questions. Each question must be specific enough that the answer directly maps to FDS content.

   **CRITICAL: Probe at FULL functional spec depth.**

   - BAD: "What parameters does this pump have?"
   - GOOD: "What is the flow rate range for pump P-101? What happens when flow drops below minimum -- automatic shutdown or alarm only? Is there a startup ramp time?"

   - BAD: "Tell me about the interlocks."
   - GOOD: "When sensor TT-101 reads above 85C, should the system: (a) generate an alarm and continue, (b) automatically reduce power, or (c) trip to safe state? What is the safe state for the heating element?"

   - BAD: "How does the HMI work?"
   - GOOD: "For the main overview screen: should operators see all equipment modules at once, or navigate per process area? What status information per EM -- running/stopped only, or full state + key parameters?"

3. **Use inline conversation for technical deep-dives** -- more natural for specification discussions than AskUserQuestion for every detail. Use AskUserQuestion for structured choices (e.g., selecting from options).

4. **After each question batch, summarize decisions:**
   ```
   Captured for {Topic}:
   - {Decision 1}
   - {Decision 2}
   - {Decision 3}

   Anything else for this topic, or move on?
   ```

5. **Move to next topic when engineer confirms.**

### 5.2 Cross-Reference Handling

When discussion references equipment, interfaces, or systems not yet documented in a previous phase:

- Capture the decision as-is
- Add a cross-reference flag: "Verify when {target module} is documented in Phase {X}"
- Do NOT block the discussion -- capture and flag

### 5.3 Scope Creep Handling

If the engineer mentions functionality outside the phase domain:

```
"{Feature/capability} sounds like it belongs in Phase {X}: {Phase Name}.
I will note it as a deferred idea so it is not lost.

Back to {current topic}: {return to current question}"
```

Track deferred ideas internally for CONTEXT.md.

### 5.4 Discussion Rules

- All user-facing text matches the project language (from PROJECT.md)
- Use DOC prefix on all banners (the doc namespace, not the gsd namespace)
- Use AskUserQuestion for structured choices (topic selection, confirmation, either/or decisions)
- Use inline conversation for technical deep-dives (specifications, parameters, sequences)
- Never ask about items marked "Claude's Discretion" -- document them with reasonable defaults
- Cross-references to undocumented equipment: capture and flag, do not block
- If the engineer says "you decide" or "your call" for a specific question: add it to Claude's Discretion, confirm, move on

---

## Step 6: Capture in CONTEXT.md

### 6.1 Read Template

Read the CONTEXT.md template from `@~/.claude/gsd-docs-industrial/templates/context.md` for structure reference. The template defines the XML-tagged section pattern.

### 6.2 Find or Create Phase Directory

```bash
PADDED_PHASE=$(printf "%02d" ${PHASE})
PHASE_DIR=$(ls -d .planning/phases/${PADDED_PHASE}-* 2>/dev/null | head -1)
if [ -z "$PHASE_DIR" ]; then
  # Create from ROADMAP name (lowercase, hyphens)
  PHASE_NAME=$(grep -i "Phase ${PHASE}" .planning/ROADMAP.md | head -1 | sed 's/.*: //' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
  mkdir -p ".planning/phases/${PADDED_PHASE}-${PHASE_NAME}"
  PHASE_DIR=".planning/phases/${PADDED_PHASE}-${PHASE_NAME}"
fi
```

### 6.3 Generate CONTEXT.md

Write to `${PHASE_DIR}/${PADDED_PHASE}-CONTEXT.md` using the template structure.

**`<domain>` section:**
- Phase boundary from ROADMAP.md goal
- For Type C/D: include delta scope statement referencing BASELINE.md

**`<decisions>` section:**
- Organized by topic (matching the gray area topics from Steps 4-5)
- Each decision is a concrete, actionable statement -- not a vague requirement
- Include `### Claude's Discretion` subsection for all delegated areas
- Each discretion item notes what Claude will decide and the general approach

**`<specifics>` section:**
- Exact technical values gathered (temperatures, capacities, timing, ranges)
- Preferred approaches or patterns ("same interlock pattern as EM-100")
- References to existing documentation (P&IDs, vendor manuals, client standards)

**`<deferred>` section:**
- Ideas that belong in other phases
- Format: "- {Idea} -- Phase {N}"
- If none: "None -- discussion stayed within phase scope"

### 6.4 Size Control (Pitfall 7 Mitigation)

**CONTEXT.md MUST stay under 100 lines.** Priority if over budget:
1. Decisions that change what gets written (keep)
2. Specific technical values -- temperatures, capacities, timing (keep)
3. General approach notes (compress or omit)

Compression: combine related decisions, use tables for parameter values, compress Claude's Discretion to a single bullet list.

### 6.5 Write and Verify

Write the CONTEXT.md file. Verify line count. If over 100 lines: compress using priority tiers above.

---

## Step 7: Completion

### 7.1 Git Commit

Stage and commit the CONTEXT.md file:

```bash
git add "${PHASE_DIR}/${PADDED_PHASE}-CONTEXT.md"
git commit -m "docs(${PADDED_PHASE}): capture phase ${PHASE} context

Phase ${PHASE}: ${PHASE_NAME}
- Implementation decisions documented
- Phase boundary established
- Ready for /doc:plan-phase ${PHASE}"
```

### 7.2 Display Completion Banner

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > PHASE {N} DISCUSSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Dutch (if `LANGUAGE = "nl"`): `DOC > FASE {N} BESPROKEN`

### 7.3 Display Summary

Show what was captured:

```
Topics discussed: {count}
Decisions captured: {count}
Items delegated to Claude's Discretion: {count}
Deferred items: {count}

CONTEXT.md: {path to file}
```

### 7.4 Next Up Block

```
───────────────────────────────────────────────────────────────

## > Next Up

**Phase {N}: {Phase Name}** -- {Goal from ROADMAP}

`/doc:plan-phase {N}`

<sub>`/clear` first -- fresh context window</sub>

───────────────────────────────────────────────────────────────

**Also available:**
- `/doc:status` -- view project progress
- Review/edit CONTEXT.md before continuing

───────────────────────────────────────────────────────────────
```

Dutch (if `LANGUAGE = "nl"`): translate "Next Up" to "Volgende Stap", "Also available" to "Ook beschikbaar", phase description.

---

## Workflow Rules

1. **Language consistency:** All user-facing text matches the project language (from PROJECT.md). Internal variable names remain English.
2. **Functional spec depth:** Every question must map directly to FDS content. Never ask generic questions -- probe for exact values and concrete alternatives.
3. **CONTEXT.md size limit:** Under 100 lines. Compress using priority tiers if needed (Pitfall 7).
4. **DOC > prefix:** All banners use the `DOC >` namespace prefix. Never use the gsd namespace.
5. **SUMMARY.md = completion proof:** Dependency checks use SUMMARY.md existence, not STATE.md status.
6. **Scope anchor:** Phase boundary from ROADMAP.md is FIXED. Discussion clarifies HOW, never adds new capabilities. Scope creep goes to deferred ideas.
7. **Claude's Discretion:** Delegated items are documented in CONTEXT.md but never asked to the engineer.
8. **Cross-reference flagging:** References to undocumented equipment: capture and flag, do not block.
9. **Type C/D delta focus:** All questions framed as deltas from BASELINE.md. Do not re-specify existing system.
10. **Interactive conversation:** AskUserQuestion for structured selections. Inline conversation for technical deep-dives.
11. **No emoji in text:** Only use status symbols defined in ui-brand.md.
12. **Error handling:** Show error box and stop if ROADMAP.md missing, phase not found, or dependencies unmet.

</workflow>
