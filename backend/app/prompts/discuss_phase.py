"""
Discussion phase prompts extracted from v1.0 workflows.

Source files:
- gsd-docs-industrial/workflows/discuss-phase.md (content type detection, gray areas, scope handling)
- gsd-docs-industrial/templates/context.md (CONTEXT.md structure)
- gsd-docs-industrial/CLAUDE-CONTEXT.md (project type definitions)
"""

from typing import Optional

# Content type keywords (source: discuss-phase.md lines 128-140)
CONTENT_TYPE_KEYWORDS = {
    # Equipment Modules
    "equipment": "Equipment Modules",
    "module": "Equipment Modules",
    "em-": "Equipment Modules",
    "unit": "Equipment Modules",
    "functional unit": "Equipment Modules",

    # System Architecture
    "architecture": "System Architecture",
    "system overview": "System Architecture",
    "hierarchy": "System Architecture",
    "overview": "System Architecture",

    # Interfaces
    "interface": "Interfaces",
    "communication": "Interfaces",
    "protocol": "Interfaces",
    "bus": "Interfaces",
    "network": "Interfaces",

    # HMI
    "hmi": "HMI",
    "visualization": "HMI",
    "screen": "HMI",
    "display": "HMI",
    "operator": "HMI",

    # Safety
    "safety": "Safety",
    "interlock": "Safety",
    "sil": "Safety",
    "e-stop": "Safety",
    "emergency": "Safety",

    # Foundation
    "foundation": "Foundation",
    "scope": "Foundation",
    "terminology": "Foundation",
    "introduction": "Foundation",
    "definitions": "Foundation",

    # Appendices
    "appendix": "Appendices",
    "signal list": "Appendices",
    "parameter list": "Appendices",
    "index": "Appendices",

    # Control Philosophy
    "control": "Control Philosophy",
    "philosophy": "Control Philosophy",
    "operating mode": "Control Philosophy",
    "mode": "Control Philosophy",

    # State Machines
    "state": "State Machines",
    "state machine": "State Machines",
    "packml": "State Machines",
}

# Gray area patterns (source: discuss-phase.md lines 164-214)
GRAY_AREA_PATTERNS = {
    "Equipment Modules": [
        {
            "topic": "Operating parameters",
            "description": "Ranges, tolerances, timing constraints, capacities",
            "probe_questions": [
                "What are the process limits for each parameter?",
                "What triggers alarms vs trips?",
                "What are the acceptable operating ranges?"
            ]
        },
        {
            "topic": "Operating states",
            "description": "State model, entry/exit conditions, transitions",
            "probe_questions": [
                "Which states does this equipment use?",
                "What are the entry and exit conditions for each state?",
                "How do state transitions occur (automatic/manual)?"
            ]
        },
        {
            "topic": "Interlocks",
            "description": "Conditions, actions, priorities, cross-EM dependencies",
            "probe_questions": [
                "What are the interlock conditions?",
                "Are there cross-equipment interlocks?",
                "What are the sequence dependencies?"
            ]
        },
        {
            "topic": "Failure modes",
            "description": "Sensor failure behavior, actuator failure, recovery approach",
            "probe_questions": [
                "How does the system behave when sensors fail?",
                "What is the recovery procedure (automatic vs manual)?",
                "What is the safe state for each failure mode?"
            ]
        },
        {
            "topic": "Manual overrides",
            "description": "Which operations allow manual override and under what conditions",
            "probe_questions": [
                "Which operations can be manually overridden?",
                "Under what conditions are overrides allowed?",
                "What are the safety constraints on overrides?"
            ]
        },
        {
            "topic": "Startup/shutdown sequences",
            "description": "Step order, timing, conditions, abort behavior",
            "probe_questions": [
                "What is the step order for startup/shutdown?",
                "What are the timing requirements between steps?",
                "What happens if the sequence is aborted?"
            ]
        },
        {
            "topic": "Maintenance mode",
            "description": "What is accessible and restricted during maintenance",
            "probe_questions": [
                "What operations are accessible in maintenance mode?",
                "What is restricted during maintenance?",
                "How does equipment behavior change in maintenance mode?"
            ]
        }
    ],

    "Interfaces": [
        {
            "topic": "Protocol selection",
            "description": "Which protocol, data format, message structure",
            "probe_questions": [
                "Which communication protocol is used and why?",
                "What is the data format and message structure?",
                "What are the update rates for data exchange?"
            ]
        },
        {
            "topic": "Signal list",
            "description": "Direction, data types, update rates, engineering units",
            "probe_questions": [
                "What signals are exchanged (input/output)?",
                "What are the data types and engineering units?",
                "What are the required update rates?"
            ]
        },
        {
            "topic": "Error handling",
            "description": "Timeout behavior, retry logic, fallback values",
            "probe_questions": [
                "How are communication timeouts handled?",
                "What is the retry logic for failed transmissions?",
                "What are the fallback values for stale data?"
            ]
        },
        {
            "topic": "Handshake patterns",
            "description": "Acknowledgment, validation, sequence management",
            "probe_questions": [
                "What acknowledgment patterns are used?",
                "How is data validated?",
                "How are message sequences managed?"
            ]
        },
        {
            "topic": "Connection failure",
            "description": "Detection, alarm generation, recovery, impact",
            "probe_questions": [
                "How is connection failure detected?",
                "What alarms are generated on failure?",
                "What is the impact on dependent equipment?"
            ]
        }
    ],

    "HMI": [
        {
            "topic": "Screen hierarchy",
            "description": "Navigation structure, access levels, screen count",
            "probe_questions": [
                "What is the screen navigation structure?",
                "What access levels are required (operator/supervisor/engineer)?",
                "How many screens are needed?"
            ]
        },
        {
            "topic": "Alarm presentation",
            "description": "Grouping strategy, priority levels, acknowledgment rules",
            "probe_questions": [
                "How are alarms grouped and displayed?",
                "What priority levels are used?",
                "What are the acknowledgment and shelving rules?"
            ]
        },
        {
            "topic": "Trend displays",
            "description": "Which signals to trend, retention period, scales",
            "probe_questions": [
                "Which signals should be trended?",
                "What is the data retention period?",
                "What are the Y-axis scales and comparison views?"
            ]
        },
        {
            "topic": "Manual controls",
            "description": "Which operations from HMI, confirmations, constraints",
            "probe_questions": [
                "Which operations can be performed from the HMI?",
                "What confirmation dialogs are required?",
                "What are the safety constraints and authorization requirements?"
            ]
        }
    ],

    "Safety": [
        {
            "topic": "Risk categories",
            "description": "Safety-critical vs process interlocks",
            "probe_questions": [
                "Which interlocks are safety-critical?",
                "What distinguishes safety interlocks from process interlocks?",
                "What are the different risk categories?"
            ]
        },
        {
            "topic": "E-stop behavior",
            "description": "Scope, recovery sequence, reset requirements",
            "probe_questions": [
                "What is the E-stop scope (local/zone/plant-wide)?",
                "What is the recovery sequence after E-stop?",
                "What are the reset requirements?"
            ]
        },
        {
            "topic": "SIL levels",
            "description": "Safety functions and required SIL levels",
            "probe_questions": [
                "Which safety functions are implemented?",
                "What SIL levels are required?",
                "How does this impact the architecture?"
            ]
        },
        {
            "topic": "Fail-safe states",
            "description": "Fail-safe state per equipment module",
            "probe_questions": [
                "What is the fail-safe state for each equipment module?",
                "What are the valve positions in fail-safe mode?",
                "How are motors and heating elements handled?"
            ]
        }
    ],

    "Foundation": [
        {
            "topic": "Scope boundaries",
            "description": "What is in scope and explicitly out of scope",
            "probe_questions": [
                "What is documented in this FDS?",
                "What is explicitly out of scope?",
                "What are the system boundaries?"
            ]
        },
        {
            "topic": "Equipment grouping",
            "description": "How equipment modules are organized",
            "probe_questions": [
                "How are equipment modules organized (by area/function)?",
                "What is the grouping strategy?",
                "How does this align with the physical layout?"
            ]
        },
        {
            "topic": "Operating modes",
            "description": "Plant-level modes and their effect on equipment",
            "probe_questions": [
                "What plant-level operating modes exist?",
                "How do modes affect equipment behavior?",
                "Are mode transitions automatic or manual?"
            ]
        },
        {
            "topic": "Terminology",
            "description": "Project-specific terms and abbreviations",
            "probe_questions": [
                "What project-specific terms are used?",
                "What abbreviation conventions apply?",
                "What reference standards are followed?"
            ]
        }
    ],

    "Control Philosophy": [
        {
            "topic": "Control strategy",
            "description": "Regulatory control, sequence control, batch control",
            "probe_questions": [
                "What control strategy is used (PID/sequence/batch)?",
                "How are these strategies combined?",
                "What are the control objectives?"
            ]
        },
        {
            "topic": "Mode transitions",
            "description": "How plant modes affect equipment",
            "probe_questions": [
                "How do plant modes affect equipment behavior?",
                "Are mode transitions automatic or operator-initiated?",
                "What are the transition conditions?"
            ]
        },
        {
            "topic": "Alarm philosophy",
            "description": "Priority levels, rationalization, flood management",
            "probe_questions": [
                "How many alarm priority levels are used?",
                "What is the alarm rationalization approach?",
                "How is alarm flooding managed?"
            ]
        }
    ],

    "Appendices": [
        {
            "topic": "Signal list scope",
            "description": "What signals are included",
            "probe_questions": [
                "Should all I/O be included or only external signals?",
                "Should virtual signals be included?",
                "What level of detail is required?"
            ]
        },
        {
            "topic": "Parameter list",
            "description": "Which parameters and access levels",
            "probe_questions": [
                "Which parameters are operator-adjustable?",
                "What access levels apply to each parameter?",
                "How should parameters be organized?"
            ]
        },
        {
            "topic": "Document cross-references",
            "description": "P&ID references, wiring diagrams, vendor documents",
            "probe_questions": [
                "What P&ID references are needed?",
                "Should wiring diagrams be referenced?",
                "What vendor documentation should be listed?"
            ]
        }
    ]
}

# Scope creep template (source: discuss-phase.md Step 5.3)
SCOPE_CREEP_TEMPLATE = """{feature} sounds like it belongs in Phase {phase_number}: {phase_name}.
I will note it as a deferred idea so it is not lost.

Back to {current_topic}: {return_question}"""

# Phase boundary template (source: discuss-phase.md Step 4.1)
PHASE_BOUNDARY_TEMPLATE = """Phase {phase_number}: {phase_name}
Domain: {phase_goal}

We will clarify HOW to implement this phase.
(New capabilities belong in other phases.)"""

# CONTEXT.md template (source: templates/context.md)
CONTEXT_MD_TEMPLATE = """# Phase {phase_number}: {phase_name} - Context

**Gathered:** {date}
**Status:** Ready for planning

<domain>
## Phase Boundary

{phase_goal}

{delta_scope}
</domain>

<decisions>
## Implementation Decisions

{decisions}

### Claude's Discretion

{discretion_items}
</decisions>

<specifics>
## Specific Ideas

{specifics}
</specifics>

<deferred>
## Deferred Ideas

{deferred_ideas}
</deferred>

---
*Phase: {phase_slug}*
*Context gathered: {date}*
"""

# Project type phases (source: CLAUDE-CONTEXT.md section "project-types")
PROJECT_TYPE_PHASES = {
    "A": [
        {"number": 1, "name": "Foundation", "description": "Intro, definitions, standards scope"},
        {"number": 2, "name": "System Architecture", "description": "Overview, equipment hierarchy, operating modes"},
        {"number": 3, "name": "Equipment Modules", "description": "Per EM: description, states, parameters, interlocks"},
        {"number": 4, "name": "Control and HMI", "description": "Control philosophy, HMI requirements, screen descriptions"},
        {"number": 5, "name": "Interfaces and Safety", "description": "External interfaces, safety, interlocks overview"},
        {"number": 6, "name": "Appendices", "description": "Signal list, parameter list, state transition tables"}
    ],
    "B": [
        {"number": 1, "name": "Foundation", "description": "Intro, definitions, scope"},
        {"number": 2, "name": "System Overview", "description": "Description, functional blocks, process flow"},
        {"number": 3, "name": "Functional Units", "description": "Per unit: description, operation, parameters, interlocks"},
        {"number": 4, "name": "HMI and Interfaces", "description": "Operation, external connections, communication"},
        {"number": 5, "name": "Appendices", "description": "Optional"}
    ],
    "C": [
        {"number": 1, "name": "Scope and Baseline", "description": "Change description, BASELINE.md reference, change/no-change scope"},
        {"number": 2, "name": "Delta Functional", "description": "Modified functionality, new equipment, impact on existing"},
        {"number": 3, "name": "Delta HMI and Interfaces", "description": "Modified/new screens, interface changes"},
        {"number": 4, "name": "Verification and Appendices", "description": "Test criteria, regression check, delta signal list"}
    ],
    "D": [
        {"number": 1, "name": "Change Description", "description": "Description, reason, scope in/out"},
        {"number": 2, "name": "Implementation", "description": "Technical changes, impact analysis, test criteria"}
    ]
}

# Chat-optimized system prompt (extracted from v1.0 patterns)
DISCUSSION_SYSTEM_PROMPT = """You are conducting a discussion phase for an FDS (Functional Design Specification) project.

**Your role:**
- Guide the engineer through implementation decisions for Phase {phase_number}: {phase_name}
- Focus on FULL functional specification depth (exact values, behaviors, edge cases)
- Probe gray areas where assumptions would change the written output
- Keep discussion within the phase boundary from ROADMAP.md
- Redirect scope creep to deferred ideas

**Phase boundary:**
{phase_goal}

**Content types detected:** {content_types}

**Gray areas to explore:**
{gray_areas}

**Discussion rules:**
1. Ask specific, functional-spec-depth questions (NOT generic questions)
   - GOOD: "When sensor TT-101 reads above 85C, should the system: (a) generate alarm and continue, (b) automatically reduce power, or (c) trip to safe state?"
   - BAD: "Tell me about the interlocks."

2. Use project language ({project_language}) for all questions
3. After each topic, summarize decisions and confirm before moving on
4. If engineer mentions functionality outside phase scope, use scope creep template
5. If engineer delegates a decision ("you decide"), add to Claude's Discretion
6. Cross-references to undocumented equipment: capture and flag, do not block

**Scope creep handling:**
If engineer mentions out-of-scope features, respond:
"[feature] sounds like it belongs in Phase [N]. I will note it as a deferred idea."

**Goal:** Capture 100-line CONTEXT.md with concrete decisions that prevent re-asking during planning/writing.

{delta_framing}
"""

# Delta framing for Type C/D (source: discuss-phase.md Step 3.3)
DELTA_FRAMING_TEMPLATE = """
**CRITICAL: This is a Type {project_type} modification project.**

All questions must be framed as DELTAS from the baseline:
- BASELINE.md describes the existing system (treat as given)
- Focus on what is NEW or DIFFERENT
- Do not re-specify unchanged functionality

**Baseline summary:**
{baseline_summary}

**Pattern for questions:**
- GOOD: "EM-100 currently has 3 operating states (Idle, Running, Faulted). Are you adding new states or changing transitions?"
- BAD: "What operating states should EM-100 have?" (re-specifies existing)
"""


def build_system_prompt(
    phase_goal: str,
    phase_number: int,
    phase_name: str,
    content_types: list[str],
    project_type: str,
    project_language: str,
    gray_areas: list[dict],
    baseline_summary: Optional[str] = None,
) -> str:
    """
    Build chat-optimized system prompt from v1.0 patterns.

    Args:
        phase_goal: Phase goal/description from ROADMAP.md
        phase_number: Phase number
        phase_name: Phase name
        content_types: Detected content types for this phase
        project_type: Project type (A, B, C, or D)
        project_language: Project language (nl or en)
        gray_areas: Gray area topics with probe questions
        baseline_summary: Baseline summary for Type C/D projects

    Returns:
        Formatted system prompt for discussion
    """
    # Format gray areas
    gray_areas_text = "\n".join([
        f"- {area['topic']}: {area['description']}"
        for area in gray_areas
    ])

    # Build delta framing for Type C/D
    delta_framing = ""
    if project_type in ["C", "D"] and baseline_summary:
        delta_framing = DELTA_FRAMING_TEMPLATE.format(
            project_type=project_type,
            baseline_summary=baseline_summary
        )

    # Build full prompt
    return DISCUSSION_SYSTEM_PROMPT.format(
        phase_number=phase_number,
        phase_name=phase_name,
        phase_goal=phase_goal,
        content_types=", ".join(content_types),
        gray_areas=gray_areas_text,
        project_language=project_language,
        delta_framing=delta_framing
    )


def detect_content_types(phase_goal: str) -> list[str]:
    """
    Detect content types from phase goal text using v1.0 keyword mapping.

    Args:
        phase_goal: Phase goal/description text

    Returns:
        List of detected content type names
    """
    phase_goal_lower = phase_goal.lower()
    detected = set()

    for keyword, content_type in CONTENT_TYPE_KEYWORDS.items():
        if keyword.lower() in phase_goal_lower:
            detected.add(content_type)

    return sorted(list(detected))


def get_gray_areas(content_types: list[str]) -> list[dict]:
    """
    Get gray area topics with probe questions for detected content types.

    Args:
        content_types: List of content type names

    Returns:
        List of gray area topic dictionaries
    """
    gray_areas = []

    for content_type in content_types:
        if content_type in GRAY_AREA_PATTERNS:
            # Select top 3-5 gray areas per content type (manageable discussion)
            areas = GRAY_AREA_PATTERNS[content_type][:5]
            gray_areas.extend(areas)

    return gray_areas
