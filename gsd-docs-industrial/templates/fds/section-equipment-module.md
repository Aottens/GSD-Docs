---
type: equipment-module
language: "{LANGUAGE}"
standards: [packml, isa88]
subsections:
  required: [description, operating-states, parameters, interlocks, io-table]
  optional: [manual-controls, alarm-list, maintenance-mode, startup-shutdown]
---

<!-- TEMPLATE: Equipment Module Section
     Used by: /doc:plan-phase (referenced via @-path in PLAN.md)
     Filled by: /doc:write-phase writer subagent
     Subsections marked OPTIONAL are included/excluded per PLAN.md instructions.
     All {PLACEHOLDER} values are replaced with actual content by the writer.
     Bilingual headers: writer selects language based on PROJECT.md output.language setting. -->

### [N.M] {EM_ID}: {EM_NAME}

#### [N.M.1] {Description / Beschrijving}

{Function and operation of this equipment module. Include purpose within the process,
physical characteristics relevant to control, and operational context.}

#### [N.M.2] Operating States

> PackML state names (IDLE, STARTING, EXECUTE, etc.) are always in English per industry convention.

| State | ID | {Description / Beschrijving} | {Entry Condition / Startconditie} | {Exit Condition / Stopconditie} |
|-------|-----|------|------|------|
| IDLE | {ID} | {DESC} | {ENTRY} | {EXIT} |
| STARTING | {ID} | {DESC} | {ENTRY} | {EXIT} |
| EXECUTE | {ID} | {DESC} | {ENTRY} | {EXIT} |
| {STATE} | {ID} | {DESC} | {ENTRY} | {EXIT} |

#### [N.M.3] {Parameters / Parameters}

| Parameter | {Range / Bereik} | {Unit / Eenheid} | Default | {Description / Beschrijving} |
|-----------|-------|---------|---------|------|
| {PARAM} | {MIN}-{MAX} | {UNIT} | {DEF} | {DESC} |

#### [N.M.4] Interlocks

| ID | {Condition / Conditie} | {Action / Actie} | {Priority / Prioriteit} |
|----|----------|-------|------------|
| IL-{EM}-01 | {CONDITION} | {ACTION} | {PRIO} |

#### [N.M.5] I/O

| Tag | {Description / Beschrijving} | Type | {Signal Range / Signaalbereik} | {Eng. Unit / Eenheid} | {PLC Address / PLC Adres} | {Fail-safe State / Veilige Stand} | {Alarm Limits / Alarmgrenzen} | {Scaling / Schaling} |
|-----|------|------|------|------|------|------|------|------|
| {TAG} | {DESC} | DI | {RANGE} | {UNIT} | {ADDR} | {SAFE} | {LIMITS} | {SCALE} |
| {TAG} | {DESC} | DO | {RANGE} | {UNIT} | {ADDR} | {SAFE} | {LIMITS} | {SCALE} |
| {TAG} | {DESC} | AI | {RANGE} | {UNIT} | {ADDR} | {SAFE} | {LIMITS} | {SCALE} |
| {TAG} | {DESC} | AO | {RANGE} | {UNIT} | {ADDR} | {SAFE} | {LIMITS} | {SCALE} |

<!-- OPTIONAL: include if equipment has manual operation -->

#### [N.M.6] {Manual Controls / Handmatige Bediening}

| {Control / Bediening} | {Function / Functie} | {Condition / Voorwaarde} |
|---------|----------|-----------|
| {CTRL} | {FUNC} | {COND} |

<!-- OPTIONAL: include if equipment has alarms -->

#### [N.M.7] {Alarm List / Alarmlijst}

| ID | {Description / Beschrijving} | {Category / Categorie} | {Action / Actie} |
|----|------|----------|-------|
| AL-{EM}-01 | {DESC} | {CAT} | {ACTION} |

<!-- OPTIONAL: include if equipment has maintenance procedures -->

#### [N.M.8] {Maintenance Mode / Onderhoudsmodus}

{Description of maintenance mode behavior: entry conditions, available operations,
safety restrictions, and return-to-normal procedure.}

<!-- OPTIONAL: include if equipment has complex startup/shutdown -->

#### [N.M.9] {Startup/Shutdown Sequence / Opstart/Afsluitprocedure}

{Step-by-step sequence description:
1. {STEP_1}
2. {STEP_2}
3. {STEP_N}

Include timing requirements, confirmation points, and abort conditions.}
