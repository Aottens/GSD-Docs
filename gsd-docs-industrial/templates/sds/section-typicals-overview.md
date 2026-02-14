---
type: typicals-overview
language: "{LANGUAGE}"
section: 3
subsections:
  required: [library-metadata, typicals-summary]
  optional: [unmatched-equipment]
---

<!-- TEMPLATE: SDS Typicals Library Reference Section
     Used by: /doc:generate-sds workflow to create section 3 of SDS
     Filled by: /doc:write-phase writer subagent or auto-generation from CATALOG.json
     This section documents which typicals library is used, which typicals are deployed, and which equipment modules need new typical development.
     Bilingual headers: writer selects language based on PROJECT.md output.language setting. -->

## 3. {Typicals Library Reference / Typicals Bibliotheek Referentie}

### 3.1 {Library Metadata / Bibliotheek Metadata}

{Brief description of the typicals library used for this project: source, version, platform compatibility.}

| {Property / Eigenschap} | {Value / Waarde} |
|-----|-----|
| {Library Name / Bibliotheek Naam} | {NAME from CATALOG.json} |
| {Version / Versie} | {VERSION from CATALOG.json} |
| Platform | {PLATFORM from CATALOG.json (e.g., "TIA Portal V18")} |
| {Last Updated / Laatst Bijgewerkt} | {UPDATED_DATE from CATALOG.json} |
| {Load Mode / Laadmodus} | {External / Imported} |
| {Library Path / Bibliotheek Pad} | {PATH from PROJECT.md or "Imported to project references/"} |

**{Load Mode Explanation / Laadmodus Toelichting}:**
- **External:** Library is referenced via shared network path. Changes to library affect this project. Requires access to library location during TIA Portal project loading.
- **Imported:** Library is copied into project references/ folder. Project is self-contained. Library changes do not affect this project unless manually re-imported.

### 3.2 {Typicals Summary / Typicals Overzicht}

{Table listing all typicals from CATALOG.json that are used in this project. Shows which equipment modules use each typical and key interface summary.}

| {Typical ID / Typical ID} | {Category / Categorie} | {Description / Beschrijving} | {Used By / Gebruikt Door} | {Interfaces Summary / Interfaces Samenvatting} |
|-----|-----|-----|-----|-----|
| {FB_NAME from CATALOG} | {CATEGORY from CATALOG} | {DESCRIPTION from CATALOG} | {List of EM IDs using this typical} | {Brief I/O summary: e.g., "4 inputs, 3 outputs"} |

**{Total Typicals Used / Totaal Gebruikte Typicals}:** {COUNT} {typicals from library / typicals uit bibliotheek}

**{Documentation References / Documentatie Referenties}:**

{For each typical with available documentation, list the reference path:}
- {FB_NAME}: {Path to documentation from CATALOG.json or "—"}

### 3.3 {Unmatched Equipment Modules / Ongepaarde Apparatuurmodules}

<!-- OPTIONAL: Only include this subsection if there are equipment modules that did not match any existing typical. If all modules matched, OMIT this section entirely. -->

{Description: These equipment modules require NEW TYPICAL development because no suitable typical exists in the library. Each has a skeleton SDS section derived from its FDS specification to serve as a development starting point.}

| {Equipment Module ID / Apparatuurmodule ID} | {Equipment Name / Apparatuurnaam} | {Reason Unmatched / Reden Niet Gematcht} | {SDS Section / SDS Sectie} |
|-----|-----|-----|-----|
| {EM_ID} | {EM_NAME} | {WHY_NO_MATCH (e.g., "Unique control logic", "Missing library coverage", "Custom requirements")} | {Section 4.x reference} |

**{Development Priority / Ontwikkelprioriteit}:** {HIGH / MEDIUM / LOW based on project criticality}

**{Recommendation / Aanbeveling}:** {Engineer's guidance on whether to: (1) develop custom FB, (2) extend existing typical, (3) request library update from library maintainer}

---

<!-- TEMPLATE NOTES:
     - Library Metadata (3.1): Always required. Auto-filled from CATALOG.json and PROJECT.md.
     - Typicals Summary (3.2): Always required. Shows which typicals are actually deployed in this project.
     - Unmatched Equipment (3.3): Optional. Only include if matching algorithm found equipment modules without suitable typicals.
     - Writers should NOT document typical internals here - that's library documentation's job. Focus on WHICH typicals are used WHERE.
     - "NEW TYPICAL NEEDED" markers in equipment sections (4.x.1) reference this section 3.3 for context. -->
