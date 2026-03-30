---
status: complete
phase: 13-export-assembly
source: [13-01-SUMMARY.md, 13-02-SUMMARY.md, 13-03-SUMMARY.md, 13-04-SUMMARY.md]
started: 2026-03-21T20:00:00Z
updated: 2026-03-21T21:40:00Z
---

## Tests

### 1. Export Tab Navigation
expected: Clicking "Exporteren" in the project sidebar navigates to the Export tab. The tab shows export mode selector (Concept/Definitief), language selector (Nederlands/English), and the FDS Export Pipeline section with stage cards.
result: pass

### 2. Export Readiness & Pandoc Status
expected: The Export tab shows a readiness indicator. For a project with content in draft mode, it should show as ready. Pandoc status should show as installed (no warning alert).
result: issue → resolved
reported: "shows as ready on pages where absolutely no content lives"
severity: major
fix_commit: "97aed75"

### 3. Run Export Pipeline (Draft Mode)
expected: Clicking the start/export button triggers the SSE streaming pipeline. Pipeline stages update in real-time showing progress through Samenstellen (assembly), Exporteren (Pandoc conversion), and completion. A toast notification appears on success.
result: issue → resolved
reported: "SSE stages stuck on spinner - onmessage doesn't receive named SSE events, and backend sent duplicate step_start(1)"
severity: blocker
fix_commit: "458bf26"

### 4. Version History Table
expected: After export completes, the version history section shows a table with the exported DOCX file(s). Each row shows filename, version, date, size, and a download button. Clicking download retrieves the file.
result: pass

### 5. Export Toast & Query Invalidation
expected: Export completion triggers success toast and version history auto-refreshes with new version.
result: pass

### 6. Download Endpoint
expected: Download API returns correct DOCX file with proper MIME type.
result: pass

### 7. Empty Project Guard
expected: Projects with no content show "Geen inhoud beschikbaar" alert and disable the pipeline start button.
result: pass

### 8. SDS Tab Navigation
expected: Clicking "SDS" in the project sidebar navigates to the SDS tab with scaffold trigger.
result: skipped (not tested this session)

## Summary

total: 8
passed: 6
issues: 2 (both resolved inline)
pending: 0
skipped: 1

## Gaps

- truth: "Export tab should show not-ready state when project has no content"
  status: resolved
  reason: "User reported: shows as ready on pages where absolutely no content lives"
  severity: major
  test: 2
  root_cause: "AssemblyPipeline.tsx did not check readiness.has_content — only checked isFinalBlocked and pandocStatus"
  artifacts:
    - path: "frontend/src/features/export/components/AssemblyPipeline.tsx"
      issue: "Missing has_content check for button disabled state and alert"
  missing:
    - "Add hasNoContent derived state and alert + disable button when no content"
  fix_commit: "97aed75"

- truth: "SSE pipeline stages update in real-time and complete successfully"
  status: resolved
  reason: "SSE stages stuck on spinner - onmessage doesn't receive named events, duplicate step_start(1) reset stage back to running"
  severity: blocker
  test: 3
  root_cause: "1) Frontend used onmessage which only handles unnamed SSE events; backend sends named events. 2) Backend loop emitted duplicate step_start for step 1."
  artifacts:
    - path: "frontend/src/features/export/hooks/useAssemblyStream.ts"
      issue: "Used onmessage instead of addEventListener for named SSE events"
    - path: "backend/app/api/export.py"
      issue: "Loop yielded step_start(1) twice - once manually, once from loop iteration"
  missing:
    - "Use addEventListener for named SSE events"
    - "Skip step 1 in loop since handled in step 0 block"
  fix_commit: "458bf26"
