<!--
REVISION HISTORY TEMPLATE
Created by: /doc:new-fds command during project initialization
Consumed by: /doc:complete-fds workflow during document assembly
Validation: Hybrid approach - auto-generated from git as draft, engineer edits before release
Language: Bilingual support - table headers based on PROJECT.md language setting
-->

<!-- ENGLISH VERSION -->
<div class="revision-history" lang="en">

## Revision History

<!-- AUTO-GENERATED SECTION -->
### Git-Generated Revisions (Draft)

The following revisions were auto-generated from git commit history. **Engineers must review and edit this section before document release.**

| Version | Date | Author | Description |
|---------|------|--------|-------------|
{GIT_REVISION_ENTRIES}

<!-- MANUAL SECTION -->
### Official Revisions (Engineer-Approved)

Engineers should move approved revisions from the auto-generated section above to this table, editing descriptions for clarity and professional tone.

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | YYYY-MM-DD | Engineer Name | Initial release |
|  |  |  |  |

</div>

<!-- DUTCH VERSION -->
<div class="revision-history" lang="nl">

## Revisiehistorie

<!-- AUTO-GEGENEREERDE SECTIE -->
### Git-Gegenereerde Revisies (Concept)

De volgende revisies zijn automatisch gegenereerd uit de git commit geschiedenis. **Engineers moeten deze sectie controleren en bewerken voor document release.**

| Versie | Datum | Auteur | Beschrijving |
|--------|-------|--------|--------------|
{GIT_REVISION_ENTRIES}

<!-- HANDMATIGE SECTIE -->
### Officiële Revisies (Engineer-Goedgekeurd)

Engineers moeten goedgekeurde revisies van de bovenstaande auto-gegenereerde sectie naar deze tabel verplaatsen, waarbij beschrijvingen worden bewerkt voor duidelijkheid en professionele toon.

| Versie | Datum | Auteur | Beschrijving |
|--------|-------|--------|--------------|
| 1.0 | JJJJ-MM-DD | Engineer Naam | Initiële release |
|  |  |  |  |

</div>

<!--
ASSEMBLY INSTRUCTIONS - AUTO-GENERATION FROM GIT
The /doc:complete-fds workflow should:

1. Extract git commit history for project phases:
   git log --pretty=format:"%h|%ad|%an|%s" --date=short --all -- gsd-docs-industrial/projects/{PROJECT_NAME}/

2. Parse commit messages and group by logical versions:
   - Major version (1.0, 2.0): Phase completion, ROADMAP expansion
   - Minor version (1.1, 1.2): Equipment module additions, significant updates
   - Patch version (1.0.1): Bug fixes, minor corrections

3. Populate {GIT_REVISION_ENTRIES} with format:
   | 0.1 | 2026-01-15 | John Doe | Initial system overview and requirements |
   | 0.2 | 2026-01-20 | Jane Smith | Added equipment modules EM-01 through EM-05 |
   ...

4. Select language version (en or nl) based on PROJECT.md language field

5. Engineer workflow:
   - Run /doc:complete-fds to generate draft with auto-populated git revisions
   - Review auto-generated entries for accuracy
   - Edit descriptions to be concise and professional
   - Move approved entries to "Official Revisions" table
   - Delete or collapse git-generated section before final release
   - Manually add any external revisions (client feedback, regulation updates, etc.)

ENGINEER EDITING GUIDANCE:
- Consolidate related commits into single revision entries
- Use professional language (avoid "WIP", "fix typo", "oops")
- Focus on what changed from user perspective, not implementation details
- Example transformation:
  Git: "feat(phase-03): add conveyor module"
  → Professional: "Added conveyor belt control module with interlock logic"
-->
