<!-- TEMPLATE: XREF-REPORT.md
     Created by: /doc:complete-fds workflow (Step 12a)
     Consumed by: Engineers reviewing cross-reference resolution quality
     Location: .planning/assembly/v{VERSION}/XREF-REPORT.md

     Purpose: Comprehensive cross-reference resolution report generated during FDS
     assembly. Lists all references (resolved and broken), orphan sections (sections
     that exist but are never referenced), and resolution statistics.

     Orphan severity classification (Claude's discretion per CONTEXT.md):
       - HIGH: Equipment modules (section 4.x) — should always be referenced from System Overview
       - MEDIUM: Introduction/Safety sections — typically self-contained but better if referenced
       - LOW: Appendices — standalone by nature (signal lists, parameter tables)

     Broken references section: If --force flag was used, these appear as [BROKEN REF]
     placeholders in the assembled FDS document.

     Validation rules:
       - Resolution rate should be >95% for production-ready documents
       - HIGH severity orphans should be addressed before client delivery
       - Broken references indicate missing content or incorrect symbolic IDs

     Format matches existing template pattern: HTML comment doc block + structured markdown. -->

# Cross-Reference Resolution Report

**FDS Version:** v{VERSION}
**Generated:** {YYYY-MM-DD}
**Total References:** {RESOLVED + BROKEN}
**Resolved:** {RESOLVED_COUNT}
**Broken:** {BROKEN_COUNT}
**Orphan Sections:** {ORPHAN_COUNT}

---

## 1. Resolution Summary

Quick overview of cross-reference resolution status.

| Status | Count | Percentage |
|--------|-------|------------|
| Resolved | {RESOLVED_COUNT} | {RESOLVED_PERCENTAGE}% |
| Broken | {BROKEN_COUNT} | {BROKEN_PERCENTAGE}% |
| **Total** | **{TOTAL_REFERENCES}** | **100%** |

**Resolution rate:** {RESOLVED_PERCENTAGE}%

**Quality assessment:**
- ✓ Excellent: ≥95% resolved
- ⚠ Acceptable: 85-94% resolved
- ✗ Poor: <85% resolved (not recommended for client delivery)

---

## 2. Resolved References

Successfully resolved cross-references with final section numbers.

| Source Section | Target Section | Symbolic ID | Final Number | Context |
|----------------|----------------|-------------|--------------|---------|
| {SOURCE_NUM} {SOURCE_TITLE} | {TARGET_SECTION} | {SYMBOLIC_ID} | Section {FINAL_NUMBER} | {CONTEXT_DESCRIPTION} |

<!-- Example rows:

| Source Section | Target Section | Symbolic ID | Final Number | Context |
|----------------|----------------|-------------|--------------|---------|
| 2.3 Equipment Overview | 4.1 EM-100 Waterbad | 03-01 | Section 4.1 | Detailed description of water bath equipment module |
| 3.2 State Machine | 4.2 EM-200 Bovenloopkraan | EM-200 | Section 4.2 | Crane-specific state machine implementation |
| 4.1.2 Operating Principle | 2.1 System Description | system-overview | Section 2.1 | Overall system context for equipment module |

-->

**Total resolved:** {RESOLVED_COUNT} references

---

## 3. Broken References

Unresolved references with reasons and suggested fixes.

{IF_FORCE_FLAG}
**Note:** These broken references appear as [BROKEN REF] placeholders in the assembled FDS-{PROJECT}-v{VERSION}-DRAFT.md document.
{END_IF_FORCE_FLAG}

| Source Section | Symbolic ID | Reason | Suggested Fix |
|----------------|-------------|--------|---------------|
| {SOURCE_NUM} {SOURCE_TITLE} | {SYMBOLIC_ID} | {REASON} | {SUGGESTED_FIX} |

<!-- Example rows:

| Source Section | Symbolic ID | Reason | Suggested Fix |
|----------------|-------------|--------|---------------|
| 2.3 Equipment Overview | 05-07 | Target section not found in symbol table | Write section 05-07 (Advanced Diagnostics) or remove reference |
| 4.1 EM-100 State Machine | EM-500 | Equipment module not documented | Add EM-500 to ROADMAP and write corresponding CONTENT.md |
| 3.2 General Sequence | 04-03 | Plan not written | Run /doc:write-phase 4 to complete HMI sections |
| 4.2 Interlock Logic | phase-6/06-02 | Cross-phase reference to unwritten phase | Complete Phase 6 planning and writing, or defer reference to later version |

-->

**Total broken:** {BROKEN_COUNT} references

**Common reasons:**
- **Target not found:** Referenced section doesn't exist in assembled document (plan not written or symbolic ID incorrect)
- **Equipment module not documented:** Reference to equipment module that's not included in current ROADMAP
- **Plan not written:** Reference to a plan that exists in ROADMAP but hasn't been written yet
- **Cross-phase dependency:** Reference to content in a phase that hasn't been completed

**Resolution workflow:**
1. Review XREF-REPORT.md broken references table
2. For each broken reference:
   - If target should exist: Run /doc:verify-phase N to check gaps, write missing content
   - If target is future work: Remove reference or mark as "planned for v{NEXT_VERSION}"
   - If symbolic ID is wrong: Update CONTENT.md with correct ID
3. Re-run /doc:complete-fds to regenerate with all references resolved

---

## 4. Orphan Sections

Sections that exist in the document but are never referenced by any other section.

**Note:** Not all orphans are problems. Appendices and standalone sections are naturally orphaned. Review HIGH and MEDIUM severity orphans for potential integration improvements.

| Section Number | Section Title | Severity | Notes |
|----------------|---------------|----------|-------|
| {SECTION_NUM} | {SECTION_TITLE} | {SEVERITY} | {NOTES_AND_SUGGESTED_FIX} |

<!-- Example rows:

| Section Number | Section Title | Severity | Notes |
|----------------|---------------|----------|-------|
| 4.3 | EM-300 Vulunit | HIGH | Equipment module never referenced from System Overview (Section 2.3). Add reference: "The system includes three main equipment modules: EM-100 Water Bath, EM-200 Crane, and EM-300 Fill Unit (see Section 4.3)." |
| 3.4 | Emergency Stop Logic | MEDIUM | Safety section not referenced from Introduction or System Overview. Consider adding reference in Section 1.1 Purpose: "For emergency stop and safety requirements, see Section 3.4." |
| 7.2 | Historical Changes | LOW | Appendix section, standalone by nature. No action needed unless historical context is important for understanding current design (in which case, add "see Section 7.2 for historical context" from relevant sections). |
| 6.1 | Signal List | LOW | Appendix, standalone reference material. Expected to be orphaned. |

-->

**Total orphans:** {ORPHAN_COUNT} sections

**Severity breakdown:**
- HIGH: {HIGH_COUNT} — Should be addressed before client delivery
- MEDIUM: {MEDIUM_COUNT} — Review and consider adding references
- LOW: {LOW_COUNT} — Acceptable, standalone sections

**Orphan severity criteria (Claude's discretion per Phase 5 context):**

**HIGH severity (critical integration gaps):**
- Equipment modules (section 4.x) — These should ALWAYS be referenced from System Overview (2.3)
- Functional requirements without incoming references — Likely indicates missing integration with system design

**MEDIUM severity (recommended improvements):**
- Introduction/Safety sections — Typically self-contained but better if referenced from overview for document navigation
- Control philosophy sections — May be standalone but stronger if integrated with system architecture

**LOW severity (expected orphans):**
- Appendices (sections 6.x, 7.x) — Signal lists, parameter tables, historical notes are standalone by design
- References/Abbreviations sections — Support material, not narrative content requiring references

**Suggested fixes:**
1. HIGH severity: Add references from System Overview (2.3) to all equipment modules
2. MEDIUM severity: Add navigation references from Introduction (1.1) to key technical sections
3. LOW severity: No action needed (acceptable as standalone)

---

## 5. Statistics

Overall cross-reference metrics and analysis.

**Document structure:**
- Total sections in document: {TOTAL_SECTIONS}
- Top-level sections: {TOP_LEVEL_SECTIONS}
- Subsections (depth 2-4): {SUBSECTION_COUNT}
- Placeholder stubs: {PLACEHOLDER_COUNT}

**Cross-reference coverage:**
- Total cross-references found: {TOTAL_REFERENCES}
- Resolution rate: {RESOLVED_PERCENTAGE}%
- Average references per section: {AVG_REFS_PER_SECTION}
- Sections with no outgoing references: {SECTIONS_NO_OUTGOING}
- Sections with no incoming references (orphans): {ORPHAN_COUNT}

**Most-referenced section:**
- Section {MOST_REFERENCED_NUM}: {MOST_REFERENCED_TITLE}
- Incoming references: {MOST_REFERENCED_COUNT}
- **Analysis:** {ANALYSIS_WHY_MOST_REFERENCED}

<!-- Example:
- Section 4.1: EM-100 Waterbad
- Incoming references: 8
- **Analysis:** Central equipment module referenced by System Overview, Interlock Logic, State Machine, and HMI sections. High reference count indicates good integration with overall system design.
-->

**Most-referencing section (most outgoing references):**
- Section {MOST_REFERENCING_NUM}: {MOST_REFERENCING_TITLE}
- Outgoing references: {MOST_REFERENCING_COUNT}
- **Analysis:** {ANALYSIS_WHY_MOST_REFERENCING}

<!-- Example:
- Section 2.3: Equipment Overview
- Outgoing references: 12
- **Analysis:** System overview section naturally references all equipment modules and functional sections. High outgoing reference count indicates comprehensive system integration narrative.
-->

**Reference type distribution:**
- depends-on: {DEPENDS_ON_COUNT} ({DEPENDS_ON_PERCENTAGE}%)
- related-to: {RELATED_TO_COUNT} ({RELATED_TO_PERCENTAGE}%)
- see-also: {SEE_ALSO_COUNT} ({SEE_ALSO_PERCENTAGE}%)

**Cross-phase references:**
- References to other phases: {CROSS_PHASE_COUNT}
- External references (outside FDS): {EXTERNAL_REFS_COUNT}

---

## 6. Recommendations

Based on cross-reference analysis, recommended actions before client delivery.

### Critical (Must Fix)

{IF_BROKEN_COUNT > 0}
- **Fix broken references:** {BROKEN_COUNT} broken references must be resolved or assembly will remain in DRAFT status.
  - Review Section 3 (Broken References) for specific targets
  - Run /doc:verify-phase N to identify gaps
  - Write missing content or remove incorrect references
  - Re-run /doc:complete-fds
{END_IF_BROKEN_COUNT}

{IF_HIGH_SEVERITY_ORPHANS > 0}
- **Address HIGH severity orphans:** {HIGH_SEVERITY_ORPHANS} equipment modules or critical sections are not referenced anywhere.
  - Review Section 4 (Orphan Sections) for specific sections
  - Add references from System Overview (2.3) to all equipment modules
  - Ensure functional requirements are integrated with system design
{END_IF_HIGH_SEVERITY_ORPHANS}

### Recommended (Quality Improvements)

{IF_MEDIUM_SEVERITY_ORPHANS > 0}
- **Review MEDIUM severity orphans:** {MEDIUM_SEVERITY_ORPHANS} sections could benefit from integration references.
  - Consider adding navigation references from Introduction to key technical sections
  - Link safety sections from System Overview for better document flow
{END_IF_MEDIUM_SEVERITY_ORPHANS}

{IF_RESOLUTION_RATE < 95%}
- **Improve resolution rate:** Current {RESOLVED_PERCENTAGE}% is below 95% target.
  - Target for production documents: ≥95% resolution rate
  - Review all broken references and plan remediation
{END_IF_RESOLUTION_RATE}

### Optional (Nice to Have)

- **LOW severity orphans:** {LOW_SEVERITY_ORPHANS} appendix sections are orphaned (expected behavior).
  - No action needed unless specific navigation improvements desired
  - Appendices are standalone reference material by design

---

**Report generated by:** /doc:complete-fds workflow (Step 12a)
**Next steps:** Review broken references and orphans, fix critical issues, re-run assembly if needed
