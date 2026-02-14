<!--
ABBREVIATIONS LIST TEMPLATE
Created by: /doc:new-fds command during project initialization
Consumed by: /doc:complete-fds workflow during document assembly
Validation: Auto-extracted from document content + manual engineer additions
Language: Bilingual - definitions in project language (Dutch or English)
-->

<!-- ENGLISH VERSION -->
<div class="abbreviations" lang="en">

## Abbreviations and Acronyms

<!-- AUTO-EXTRACTED SECTION -->
### Auto-Detected Abbreviations

The following abbreviations were automatically extracted from the FDS document content. **Engineers should review for accuracy and add definitions where missing.**

{AUTO_ABBREVIATIONS}

<!-- MANUAL SECTION -->
### Pre-Populated Industrial Abbreviations

Common industrial automation abbreviations. Engineers may delete unused entries before final release.

| Abbreviation | Full Term | Description |
|--------------|-----------|-------------|
| AI | Analog Input | Continuous measurement signal input to PLC |
| AO | Analog Output | Continuous control signal output from PLC |
| CM | Control Module | ISA-88 control module (coordinated equipment modules) |
| DCS | Distributed Control System | Industrial process control system |
| DI | Digital Input | Binary state input to PLC (on/off) |
| DO | Digital Output | Binary state output from PLC (on/off) |
| EM | Equipment Module | ISA-88 basic control unit (valves, motors, etc.) |
| FDS | Functional Design Specification | This document |
| HMI | Human-Machine Interface | Operator control and visualization interface |
| I/O | Input/Output | Signals between field devices and control system |
| IEC | International Electrotechnical Commission | International standards organization |
| ISA | International Society of Automation | Automation industry standards body |
| ISA-88 | Batch Control Standard | Standard for batch process control hierarchy |
| OPC | Open Platform Communications | Industrial communication standard |
| PackML | Packaging Machine Language | ISA-TR88.00.02 state machine standard |
| PID | Proportional-Integral-Derivative | Control loop feedback mechanism |
| PLC | Programmable Logic Controller | Industrial control computer |
| RTU | Remote Terminal Unit | Remote monitoring and control device |
| SCADA | Supervisory Control and Data Acquisition | Control system architecture |
| SDS | Software Design Specification | Detailed PLC implementation document |
| SIL | Safety Integrity Level | IEC 61508 safety classification |

### Project-Specific Abbreviations

Engineers should add project-specific abbreviations here. These entries persist across document regenerations.

| Abbreviation | Full Term | Description |
|--------------|-----------|-------------|
|  |  |  |

</div>

<!-- DUTCH VERSION -->
<div class="abbreviations" lang="nl">

## Afkortingen en Acroniemen

<!-- AUTO-GEËXTRAHEERDE SECTIE -->
### Automatisch Gedetecteerde Afkortingen

De volgende afkortingen zijn automatisch geëxtraheerd uit de FDS documentinhoud. **Engineers moeten deze controleren op juistheid en definities toevoegen waar ontbrekend.**

{AUTO_ABBREVIATIONS}

<!-- HANDMATIGE SECTIE -->
### Vooraf Ingevulde Industriële Afkortingen

Veelvoorkomende industriële automatiseringsafkortingen. Engineers mogen ongebruikte vermeldingen verwijderen voor definitieve release.

| Afkorting | Volledige Term | Beschrijving |
|-----------|----------------|--------------|
| AI | Analog Input | Continue meetsignaalingang naar PLC |
| AO | Analog Output | Continue stuursignaaluitgang van PLC |
| CM | Control Module | ISA-88 besturingsmodule (gecoördineerde apparatuurmodules) |
| DCS | Distributed Control System | Industrieel procesbesturingssysteem |
| DI | Digital Input | Binaire toestandsingang naar PLC (aan/uit) |
| DO | Digital Output | Binaire toestandsuitgang van PLC (aan/uit) |
| EM | Equipment Module | ISA-88 basis besturingseenheid (kleppen, motoren, etc.) |
| FDS | Functional Design Specification | Dit document |
| HMI | Human-Machine Interface | Operator besturings- en visualisatie-interface |
| I/O | Input/Output | Signalen tussen veldapparaten en besturingssysteem |
| IEC | International Electrotechnical Commission | Internationale normalisatieorganisatie |
| ISA | International Society of Automation | Automatiseringsindustrie normalisatie-instelling |
| ISA-88 | Batch Control Standard | Standaard voor batch procesbesturingshiërarchie |
| OPC | Open Platform Communications | Industriële communicatiestandaard |
| PackML | Packaging Machine Language | ISA-TR88.00.02 toestandsmachine standaard |
| PID | Proportional-Integral-Derivative | Regellus feedback mechanisme |
| PLC | Programmable Logic Controller | Industriële besturingscomputer |
| RTU | Remote Terminal Unit | Apparaat voor monitoring en besturing op afstand |
| SCADA | Supervisory Control and Data Acquisition | Besturingssysteem architectuur |
| SDS | Software Design Specification | Gedetailleerd PLC implementatiedocument |
| SIL | Safety Integrity Level | IEC 61508 veiligheidsclassificatie |

### Projectspecifieke Afkortingen

Engineers moeten projectspecifieke afkortingen hier toevoegen. Deze vermeldingen blijven bestaan bij document regeneraties.

| Afkorting | Volledige Term | Beschrijving |
|-----------|----------------|--------------|
|  |  |  |

</div>

<!--
ASSEMBLY INSTRUCTIONS - AUTO-EXTRACTION ALGORITHM
The /doc:complete-fds workflow should:

1. Scan entire assembled FDS document content (sections 1-7) for abbreviation candidates:
   - Pattern: Uppercase sequences of 2+ letters (regex: \b[A-Z]{2,}\b)
   - Exclude: Single letters, roman numerals (I, II, III, etc.), section references (e.g., "Section 4.1")
   - Context filter: Must appear in technical context (near equipment, control, system terms)

2. For each candidate abbreviation:
   a. Check if already defined in pre-populated list above
   b. If not, attempt dictionary lookup from built-in industrial abbreviations knowledge base
   c. If found, add to {AUTO_ABBREVIATIONS} section with format:
      | ABC | Abbreviated Term | Definition from knowledge base |
   d. If not found, add placeholder entry:
      | ABC | [Engineer: Please define] | Detected in section X.Y |

3. Sort all abbreviations alphabetically

4. Populate {AUTO_ABBREVIATIONS} placeholder with table rows

5. Select language version (en or nl) based on PROJECT.md language field

6. Include detection metadata for engineer review:
   - First occurrence location (section number)
   - Frequency count (how many times abbreviation appears)

ENGINEER REVIEW WORKFLOW:
- Review auto-extracted abbreviations for false positives
- Add missing definitions for "[Engineer: Please define]" entries
- Move confirmed abbreviations to project-specific section if needed
- Delete pre-populated entries not used in this project
- Verify definitions match project-specific usage (e.g., "CM" could be Control Module or Condition Monitoring)

PERSISTENCE RULES:
- Auto-extracted section regenerates on each /doc:complete-fds run
- Pre-populated section is static (same for all projects)
- Project-specific section persists across regenerations (manually maintained)
- Engineers should move any custom definitions to project-specific section to prevent overwrite
-->
