# {PROJECT_NAME}

## Project Config

```yaml
project_name: "{PROJECT_NAME}"
project_type: {TYPE}           # A, B, C, or D
client: "{CLIENT}"
location: "{LOCATION}"
date_created: "{DATE}"
modification:
  is_modification: {IS_MODIFICATION}  # true for Type C/D, false for A/B
  baseline_system: "{BASELINE_SYSTEM}"
  baseline_version: "{BASELINE_VERSION}"
standards:
  packml:
    enabled: {PACKML_ENABLED}  # true/false
  isa88:
    enabled: {ISA88_ENABLED}   # true/false
output:
  language: "{LANGUAGE}"       # "nl" or "en"
  include_diagrams: true
  diagram_format: "mermaid"
git_integration: true
```

## What This Is

{PROJECT_DESCRIPTION}

## Core Value

{CORE_VALUE}

## Scope

### In Scope

- {SCOPE_IN_1}
- {SCOPE_IN_2}

### Out of Scope

- {SCOPE_OUT_1}
- {SCOPE_OUT_2}

## Constraints

- **Standards:** {STANDARDS_CONSTRAINT}
- **Timeline:** {TIMELINE_CONSTRAINT}
- **Technical:** {TECHNICAL_CONSTRAINT}

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Project type: {TYPE} | {TYPE_RATIONALE} | -- Pending |
| Language: {LANGUAGE} | {LANGUAGE_RATIONALE} | -- Pending |

---
*Last updated: {DATE} after initialization*
