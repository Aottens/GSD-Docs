# Phase 2: Discuss + Plan Commands - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Commands that let an engineer front-load implementation decisions (`/doc:discuss-phase N`) and generate section-level plans with wave assignments (`/doc:plan-phase N`) for FDS documentation. Produces CONTEXT.md from discussion and NN-MM-PLAN.md files from planning. Writing, verification, and assembly are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Gray area identification
- Auto-detect gray areas from phase goal/description dynamically — no predefined categories in ROADMAP templates
- Probe at full functional spec depth: operational parameters AND interlocks, failure modes, manual overrides, startup/shutdown sequences
- For Type C/D projects (modification/extension), always reference BASELINE.md to focus discussion on deltas — "the existing system does X, are you changing this?"
- Cross-references to not-yet-documented equipment: capture the decision, flag it for review checklist ("verify when [target module] is documented")

### Plan structure + waves
- Plan granularity: Claude's discretion based on phase complexity and section count
- Wave assignment strategy: Claude's discretion based on phase content and dependencies
- Verification checklists at full FDS quality level: content completeness + consistency with CONTEXT.md + standards compliance (PackML states, ISA-88 terms if enabled), signal naming conventions, table completeness
- Standards references: reference the standards module by name in plans, not inline — writer loads the standards file when needed

### FDS section templates
- Equipment module subsections: configurable — define a full list of possible subsections, plan command selects which apply based on equipment type
  - Possible subsections include: Description, Operating States, Parameters/Setpoints, Interlocks, I/O Table, Manual Controls, Alarm List, Maintenance Mode, Startup/Shutdown Sequence
- State machines: Mermaid stateDiagram-v2 for visual representation + structured transition table (from, to, condition, action) for precision
- I/O tables: full I/O spec columns — Tag, Description, Type (DI/DO/AI/AO), Signal Range, Engineering Unit, PLC Address, Fail-safe State, Alarm Limits, Scaling
- Interface templates: Claude's discretion to structure based on interface type (fieldbus, Ethernet, hardwired)

### Language + domain tone
- Language split: Claude's discretion on what's most efficient — no rigid rule on what's Dutch vs. English in internal artifacts
- Technical terms: mixed convention — PackML/ISA states in English (industry standard), descriptive text in configured language, signal types in English abbreviations (DI, DO, AI, AO)
- Tone: formal technical — third person, passive voice, precise ("The pump shall be started when the inlet valve is confirmed open")
- Tag naming conventions: project-defined in PROJECT.md during setup, templates reference that definition — not enforced by templates themselves

### Claude's Discretion
- Plan granularity (one per section vs. per functional group)
- Wave assignment strategy (top-down hierarchy vs. dependency-driven)
- Interface template structure (varies by interface type)
- Language distribution across internal artifacts (efficiency-driven)

</decisions>

<specifics>
## Specific Ideas

- Equipment modules should be configurable because different equipment types genuinely need different subsections — a valve doesn't need a startup sequence, a conveyor does
- I/O tables should be detailed enough for PLC programming, not just functional overview
- State diagrams always paired with transition tables — the diagram for quick understanding, the table for precision
- BASELINE.md integration for C/D projects is about focusing engineer time on what's changing, not re-specifying what already works

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-discuss-plan-commands*
*Context gathered: 2026-02-07*
