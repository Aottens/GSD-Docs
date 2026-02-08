---
type: interface
language: "{LANGUAGE}"
---

<!-- TEMPLATE: Interface Section
     Used by: /doc:plan-phase (referenced via @-path in PLAN.md)
     Filled by: /doc:write-phase writer subagent
     Protocol Details section structure varies by interface type -- Claude adapts
     based on the protocol (fieldbus, Ethernet, hardwired) per CONTEXT.md decision.
     All {PLACEHOLDER} values are replaced with actual content by the writer.
     Bilingual headers: writer selects language based on PROJECT.md output.language setting. -->

### [N.M] Interface: {INTERFACE_NAME}

#### [N.M.1] {Overview / Overzicht}

| {Property / Eigenschap} | {Value / Waarde} |
|------------|--------|
| Type | {Modbus TCP / Profinet / OPC-UA / Hardwired / ...} |
| {Direction / Richting} | {Incoming / Inkomend / Outgoing / Uitgaand / Bidirectional / Bidirectioneel} |
| {Counterpart / Tegenpartij} | {SYSTEM_NAME} |
| {Update Rate / Verversingssnelheid} | {X} ms |
| {Physical Layer / Fysieke Laag} | {Ethernet / RS-485 / 4-20mA / 24VDC / ...} |
| {Redundancy / Redundantie} | {None / Hot standby / Ring / ...} |

#### [N.M.2] {Signals / Signalen}

| # | {Name / Naam} | Type | {Description / Beschrijving} | {Direction / Richting} | {Range / Bereik} |
|---|------|------|------|----------|-------|
| 1 | {SIGNAL} | BOOL | {DESC} | IN | {RANGE} |
| 2 | {SIGNAL} | INT | {DESC} | OUT | {RANGE} |
| 3 | {SIGNAL} | REAL | {DESC} | IN | {RANGE} |

#### [N.M.3] {Protocol Details / Protocoldetails}

> Structure varies by interface type. Claude adapts this section based on the protocol:
> fieldbus interfaces emphasize register mapping and polling; Ethernet interfaces
> emphasize connection management and error recovery; hardwired interfaces
> emphasize signal conditioning and wiring references.

**{Connection / Verbinding}:**
- {Polling interval / Polling interval}: {X} ms
- Timeout: {Y} ms
- {Retry strategy / Herstelprocedure}: {DESCRIPTION}
- {Connection monitoring / Verbindingsbewaking}: {DESCRIPTION}

**{Data Exchange / Data-uitwisseling}:**
- {Data format / Dataformaat}: {DESCRIPTION}
- {Byte order / Byte-volgorde}: {Big-endian / Little-endian}
- {Handshake / Handshake}: {DESCRIPTION}

**{Error Handling / Foutafhandeling}:**
- {Communication loss / Communicatieverlies}: {DESCRIPTION}
- {Data validation / Datavalidatie}: {DESCRIPTION}
- {Fail-safe behavior / Veilig gedrag}: {DESCRIPTION}
