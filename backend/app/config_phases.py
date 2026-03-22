"""Phase configuration extracted from v1.0 project type definitions."""

from typing import Optional

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

DOC_TYPE_CONFIG: dict[str, list[dict]] = {
    "A": [
        {"id": "fds_old",      "label": "Oude FDS / bestaande FDS",       "required": True},
        {"id": "pid",          "label": "P&ID tekeningen",                "required": True},
        {"id": "machine_spec", "label": "Machinespecificatie / PLC-spec", "required": True},
        {"id": "risk_assess",  "label": "Risicobeoordeling / RA",         "required": False},
        {"id": "standards",    "label": "Standaarden scope documenten",   "required": True},
    ],
    "B": [
        {"id": "fds_old",      "label": "Oude FDS / bestaande FDS",       "required": False},
        {"id": "pid",          "label": "P&ID tekeningen",                "required": True},
        {"id": "machine_spec", "label": "Machinespecificatie / PLC-spec", "required": True},
        {"id": "risk_assess",  "label": "Risicobeoordeling / RA",         "required": False},
    ],
    "C": [
        {"id": "baseline",     "label": "BASELINE.md / bestaand FDS",     "required": True},
        {"id": "pid",          "label": "P&ID tekeningen (bestaand + delta)", "required": True},
        {"id": "machine_spec", "label": "Machinespecificatie / PLC-spec", "required": True},
        {"id": "risk_assess",  "label": "Risicobeoordeling / RA",         "required": False},
        {"id": "change_order", "label": "Wijzigingsopdracht / TWN",       "required": False},
    ],
    "D": [
        {"id": "pid",          "label": "P&ID tekening (gewijzigd)",      "required": False},
        {"id": "change_order", "label": "Wijzigingsopdracht / TWN",       "required": True},
        {"id": "machine_spec", "label": "Machinespecificatie fragment",   "required": False},
    ],
}

STATUS_CLI_COMMANDS: dict[str, Optional[str]] = {
    "not_started": "/doc:discuss-phase {n}",
    "discussed":   "/doc:plan-phase {n}",
    "planned":     "/doc:write-phase {n}",
    "written":     "/doc:verify-phase {n}",
    "verified":    "/doc:review-phase {n}",
    "reviewed":    None,
    "completed":   None,
}


def get_cli_command(status: str, phase_number: int) -> Optional[str]:
    """Get the recommended CLI command for a phase based on its current status."""
    template = STATUS_CLI_COMMANDS.get(status)
    if template is None:
        return None
    return template.format(n=phase_number)
