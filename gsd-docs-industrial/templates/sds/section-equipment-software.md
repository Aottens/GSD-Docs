---
type: equipment-software
language: "{LANGUAGE}"
standards: [tia-portal, packml]
subsections:
  required: [typical-assignment, fb-composition, instantiation, parameter-configuration, data-flow, state-machine]
  optional: []
---

<!-- TEMPLATE: SDS Equipment Module Section
     Used by: /doc:plan-phase (referenced via @-path in PLAN.md for SDS phases)
     Filled by: /doc:write-phase writer subagent during SDS generation
     All {PLACEHOLDER} values are replaced with actual content by the writer.
     Bilingual headers: writer selects language based on PROJECT.md output.language setting.
     Cross-references FDS section 4.x for traceability. -->

### [N.M] {EM_ID}: {EM_NAME}

#### [N.M.1] {Typical Assignment / Typical Toewijzing}

{Brief description of which typical(s) were matched to this equipment module, or why no match was found.}

| {Equipment Module ID / Apparatuurmodule ID} | {Matched Typical / Gematched Typical} | {Confidence / Betrouwbaarheid} | Status | {Library Reference / Bibliotheek Referentie} |
|-----|-----|-----|-----|-----|
| {EM_ID} | {FB_NAME or "—"} | {HIGH/MEDIUM/LOW or "—"} | {Matched / NEW TYPICAL NEEDED} | {CATALOG.json ID or "—"} |

**{Typical Summary / Typical Samenvatting}:**

{If matched: Brief description of the typical's purpose and key interfaces. Summary only - see library documentation for full details. Include: what it does, primary inputs/outputs, key parameters.}

{If NEW TYPICAL NEEDED: Explain why no existing typical matched (unique requirements, missing library coverage, special control logic). This section becomes the starting point for custom FB development.}

**{Library Reference / Bibliotheek Referentie}:** {Path to library documentation if available, or "—"}

#### [N.M.2] {FB Composition / FB Compositie}

{Description of which function blocks compose this equipment module and how they relate to each other. Focus on SOFTWARE STRUCTURE: calling hierarchy, parent-child relationships, control flow.}

| {FB Name / FB Naam} | {Type / Type} | {Purpose / Doel} | {Parent FB / Ouder FB} |
|-----|-----|-----|-----|
| {FB_NAME_1} | {from library / custom} | {DESC} | {PARENT or "—"} |
| {FB_NAME_2} | {from library / custom} | {DESC} | {PARENT or "—"} |

**{FB Hierarchy Diagram / FB Hiërarchie Diagram}:**

```mermaid
graph TD
    {Replace with actual FB hierarchy diagram showing calling relationships}
    Example:
    OB1[OB1 Main Cycle] --> EM[FB_EquipmentModule]
    EM --> AI1[FB_AnalogIn]
    EM --> VC1[FB_ValveCtrl]
    EM --> AL1[FB_AlarmHandler]
```

#### [N.M.3] {Instantiation / Instantiatie}

{Description of how FBs are instantiated: instance names, data block assignments, PLC/CPU mapping. Follows project naming conventions.}

| {Instance Name / Instantienaam} | {FB Type / FB Type} | {DB Number / DB Nummer} | {PLC/CPU} | {Comment / Opmerking} |
|-----|-----|-----|-----|-----|
| {INSTANCE_NAME} | {FB_TYPE} | DB{NUMBER} | {PLC_NAME/CPU_NUMBER} | {COMMENT} |

**{Naming Convention / Naamgevingsconventie}:** {Explain instance naming pattern, e.g., "EM_{EquipmentID}_{Suffix}" or project-specific convention}

#### [N.M.4] {Parameter Configuration / Parameter Configuratie}

{Description of parameter values: how they're derived from FDS requirements, typical defaults, engineering overrides. Cross-references FDS section 4.x.3.}

| Parameter | {Value / Waarde} | {Source / Bron} | {Unit / Eenheid} | {Description / Beschrijving} |
|-----|-----|-----|-----|-----|
| {PARAM_NAME} | {VALUE} | {FDS / Typical Default / Engineer} | {UNIT} | {DESC} |

**{FDS Cross-Reference / FDS Kruisverwijzing}:** {Reference to FDS section 4.x.3 where these parameters were originally specified}

#### [N.M.5] {Data Flow / Data Flow}

{Description of signal flow between FBs within this module and data exchange with other modules. Shows interconnections at software level.}

| Signal | {Source FB.Output / Bron FB.Output} | {Destination FB.Input / Bestemming FB.Input} | {Data Type / Datatype} | {Description / Beschrijving} |
|-----|-----|-----|-----|-----|
| {SIGNAL_NAME} | {SOURCE_FB}.{OUTPUT} | {DEST_FB}.{INPUT} | {TYPE} | {DESC} |

**{Data Flow Diagram / Data Flow Diagram}:**

```mermaid
flowchart LR
    {Replace with actual data flow diagram showing signal connections}
    Example:
    AI[FB_AnalogIn] -->|Value| VC[FB_ValveCtrl]
    VC -->|Status| EM[Main Equipment FB]
    EM -->|Command| VC
```

#### [N.M.6] {State Machine Implementation / Toestandsmachine Implementatie}

{Description of how FDS operating states map to FB state variables. Shows transition logic and state synchronization between FDS specification and PLC implementation.}

| {FDS State / FDS Toestand} | {FB State / FB Toestand} | Trigger | {Action / Actie} | {Notes / Opmerkingen} |
|-----|-----|-----|-----|-----|
| {FDS_STATE_NAME} | {FB_STATE_VAR} = {VALUE} | {TRIGGER_CONDITION} | {ACTION_DESCRIPTION} | {NOTES} |

**{FDS Cross-Reference / FDS Kruisverwijzing}:** {Reference to FDS section 4.x.2 where operating states were originally defined}

**{State Synchronization / Toestand Synchronisatie}:** {Explain how states are kept synchronized between equipment module and parent system state machine, if applicable}
