<!--
TITLE PAGE TEMPLATE
Created by: /doc:new-fds command during project initialization
Consumed by: /doc:complete-fds workflow during document assembly
Validation: Must contain all placeholder fields; assembly workflow substitutes with PROJECT.md metadata
Language: Template supports both Dutch (NL) and English (EN) - assembly selects based on PROJECT.md language setting
-->

<!-- ENGLISH VERSION -->
<div class="title-page" lang="en">

# Functional Design Specification

## {PROJECT_NAME}

---

**Client:** {CLIENT}

**Document Type:** Functional Design Specification (FDS)

**Version:** {VERSION}

**Date:** {DATE}

**Status:** {STATUS}

**Author:** {AUTHOR}

---

### Confidentiality Notice

This document contains proprietary and confidential information. It is intended solely for the use of the client specified above. Unauthorized distribution, copying, or use of this document or any part thereof is strictly prohibited.

---

**Document Control**

| Field | Value |
|-------|-------|
| Project Number | {PROJECT_NUMBER} |
| Document ID | {DOCUMENT_ID} |
| Revision | {VERSION} |
| Language | English |

</div>

<!-- DUTCH VERSION -->
<div class="title-page" lang="nl">

# Functioneel Ontwerp Specificatie

## {PROJECT_NAME}

---

**Klant:** {CLIENT}

**Documenttype:** Functioneel Ontwerp Specificatie (FDS)

**Versie:** {VERSION}

**Datum:** {DATE}

**Status:** {STATUS}

**Auteur:** {AUTHOR}

---

### Vertrouwelijkheidsverklaring

Dit document bevat eigendomsrechtelijke en vertrouwelijke informatie. Het is uitsluitend bedoeld voor gebruik door de hierboven genoemde klant. Ongeautoriseerde verspreiding, kopiëren of gebruik van dit document of enig deel daarvan is ten strengste verboden.

---

**Documentbeheer**

| Veld | Waarde |
|------|--------|
| Projectnummer | {PROJECT_NUMBER} |
| Document ID | {DOCUMENT_ID} |
| Revisie | {VERSION} |
| Taal | Nederlands |

</div>

<!--
ASSEMBLY INSTRUCTIONS
The /doc:complete-fds workflow should:
1. Read PROJECT.md to extract: project_name, client, version, language, project_number, document_id, author
2. Generate current date in ISO format (YYYY-MM-DD)
3. Determine status: "DRAFT" if any [TO BE COMPLETED] stubs exist, "RELEASE" otherwise
4. Select language version (en or nl) based on PROJECT.md language field
5. Replace all {PLACEHOLDER} values with actual metadata
6. Insert as first page of assembled FDS document
-->
