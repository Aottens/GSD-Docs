# CLAUDE-CONTEXT.md - GSD-Docs Industrial

**Doel:** Context voor Claude Code om GSD-Docs te implementeren.  
**Bron:** SPECIFICATION.md v2.7.0 (SSOT)  
**Gegenereerd:** 2026-02-06

---

## 1. Wat is GSD-Docs?

**1-op-1 mapping van GSD naar documentatie.** Dezelfde workflow die GSD gebruikt voor code, gebruiken wij voor FDS/SDS documenten.

```
GSD (code)                    GSD-Docs (documentatie)
─────────────────────────────────────────────────────
/gsd:new-project         →    /doc:new-fds
/gsd:discuss-phase N     →    /doc:discuss-phase N
/gsd:plan-phase N        →    /doc:plan-phase N
/gsd:execute-phase N     →    /doc:write-phase N
/gsd:verify-phase N      →    /doc:verify-phase N
/gsd:verify-work N       →    /doc:review-phase N
/gsd:complete-milestone  →    /doc:complete-fds
-                        →    /doc:generate-sds
-                        →    /doc:export
-                        →    /doc:status
-                        →    /doc:resume
```

---

## 2. Workflow

```
/doc:new-fds ──▶ Classificatie (A/B/C/D) ──▶ ROADMAP.md
                                               │
┌──────────────────────────────────────────────┴───────────────┐
│  PER FASE:                                                    │
│                                                               │
│  discuss-phase N ──▶ CONTEXT.md + RATIONALE.md updates       │
│        │                                                      │
│        ▼                                                      │
│  plan-phase N ────▶ *-PLAN.md (section plans)                │
│        │                                                      │
│        ▼                                                      │
│  write-phase N ───▶ *-CONTENT.md + *-SUMMARY.md              │
│        │            + EDGE-CASES.md updates                   │
│        ▼                                                      │
│  verify-phase N ──▶ VERIFICATION.md + cross-ref check        │
│        │            + Fresh Eyes (optioneel)                  │
│        ├── PASS ──▶ volgende fase                            │
│        └── GAPS ──▶ plan-phase --gaps ──▶ fix ──▶ re-verify │
│                                                               │
│  review-phase N ──▶ REVIEW.md (optioneel, met klant)         │
└───────────────────────────────────────────────────────────────┘
                                               │
                                               ▼
/doc:complete-fds ──▶ FDS.md + ENGINEER-TODO.md + final checks
        │
        ▼
/doc:generate-sds ──▶ SDS.md + TRACEABILITY.md
        │
        ▼
/doc:export ──▶ DOCX met huisstijl
```

---

## 3. Project Types

```
/doc:new-fds classificeert:

Nieuw of Modificatie?
├── NIEUW → Standaarden?
│   ├── Ja  → TYPE A (6 fases, PackML/ISA-88)
│   └── Nee → TYPE B (4-5 fases, flex)
└── MODIFICATIE → Omvang?
    ├── Groot → TYPE C (3-4 fases + BASELINE.md)
    └── Klein → TYPE D (2 fases, TWN)
```

**ROADMAP verschilt per type** - Type A heeft 6 fases, Type D heeft 2.

### 3.1 Dynamische ROADMAP Evolutie

**Bij grote projecten (>5 units):** ROADMAP groeit na System Overview fase.

```
verify-phase 2 (System Overview) → PASS
    │
    ├── Analyseert content: 18 units in 5 gebieden
    │
    └── ROADMAP wordt uitgebreid:
        Phase 3: Intake (3 units)
        Phase 4: Mixing (4 units)
        Phase 5: Transport (4 units)
        Phase 6: Filling (4 units)
        Phase 7: Packaging (3 units)
        Phase 8: HMI & Interfaces
        Phase 9: Appendices
```

**Doel:** Elke discuss-phase blijft behapbaar (3-5 units, 15-25 vragen).

---

## 4. Commands

| Command | Output |
|---------|--------|
| `/doc:new-fds` | PROJECT.md, ROADMAP.md, STATE.md |
| `/doc:discuss-phase N` | phase-N/CONTEXT.md, RATIONALE.md updates |
| `/doc:plan-phase N` | phase-N/*-PLAN.md |
| `/doc:write-phase N` | phase-N/*-CONTENT.md, *-SUMMARY.md |
| `/doc:verify-phase N` | phase-N/VERIFICATION.md, cross-ref check |
| `/doc:review-phase N` | phase-N/REVIEW.md |
| `/doc:complete-fds` | FDS.md, ENGINEER-TODO.md, archief |
| `/doc:generate-sds` | SDS.md, TRACEABILITY.md |
| `/doc:export` | DOCX met huisstijl |
| `/doc:status` | Project overzicht, progress |
| `/doc:resume` | Hervat na interrupt, toont opties |
| `/doc:release --type client` | v0.x → v1.0 (klant release) |
| `/doc:release --type internal` | v1.2 → v1.3 (intern) |

---

## 5. Key Principles

### 5.1 Verse Context per Taak
```
Bij write-phase wordt ALLEEN geladen:
✓ PROJECT.md
✓ phase-N/CONTEXT.md
✓ phase-N/03-02-PLAN.md
✓ Standards (indien enabled)

✗ Andere PLANs
✗ Andere CONTENTs
✗ Vorige conversatie
```

### 5.2 Goal-Backward Verification
> "Task completion ≠ Goal achievement"

verify-phase checkt:
- Zijn de DOELEN bereikt? (niet alleen: zijn secties geschreven)
- Is content substantive of stub?
- Voldoet het aan CONTEXT.md beslissingen?
- Cross-references geldig?

### 5.3 Gap Closure Loop
```
verify-phase ──▶ GAPS_FOUND
      │
      ▼
plan-phase --gaps ──▶ fix plans
      │
      ▼
write-phase ──▶ fixes
      │
      ▼
verify-phase ──▶ re-verify
```

### 5.4 STATE.md Checkpoint
Progress tracking die `/clear` overleeft + crash recovery:
```markdown
## Current Position
- Phase: 3
- Plan: 03-02
- Status: writing

## Current Operation
- command: write-phase
- wave: 2 of 3
- plans_done: [03-01, 03-02]
- plans_pending: [03-03, 03-04]
- status: IN_PROGRESS

## Completed
- Phase 1: ✓
- Phase 2: ✓
```

---

## 6. SUMMARY.md (AI Context)

Per sectie wordt een compacte samenvatting gegenereerd voor AI-agents:

```markdown
# SUMMARY: 03-02 EM-200 Bovenloopkraan

## Feiten
- Type: Equipment Module
- States: 6 (PackML)
- Parameters: 4
- Interlocks: 3

## Key Decisions
- Geen collision detection
- E-stop = controlled stop

## Dependencies
- Interlock met EM-100

## Cross-refs
- IL-200-01 → zie §6.3
```

**Regels:** Max 150 woorden, alleen feiten, geen proza.

---

## 7. Versioning

```
INTERN (draft)           KLANT RELEASE
────────────────────────────────────────
v0.1 → v0.9         →    v1.0  (eerste)
v1.1 → v1.9         →    v2.0  (tweede)
v2.1 → v2.9         →    v3.0  (derde)
```

**SDS:** Eigen versienummer + "Gebaseerd op: FDS vX.Y" op frontpage.

---

## 8. Kennisoverdracht

| Document | Trigger | Command |
|----------|---------|---------|
| RATIONALE.md | Bij beslissing | discuss-phase |
| EDGE-CASES.md | Bij failure modes | write-phase |
| Fresh Eyes | Na verify PASS | verify-phase |

---

## 9. Diagram Types

| Type | Mermaid | Auto-render |
|------|---------|-------------|
| State diagram | `stateDiagram-v2` | ✅ |
| Flowchart | `flowchart TD/LR` | ✅ |
| Sequence diagram | `sequenceDiagram` | ✅ |
| Block diagram | `block-beta` | ⚠️ Beperkt |
| P&ID / Electrical | ❌ | Engineering Package |

**Te complex → ENGINEER-TODO.md** (gegenereerd bij complete-fds)

---

## 10. Cross-reference Beheer

### Registry
`CROSS-REFS.md` logt alle verwijzingen (van → naar).

### Verificatie
| Moment | Check | Actie bij broken |
|--------|-------|------------------|
| verify-phase | Warn | ⚠️ Warning |
| complete-fds | Block | ❌ Kan niet completen |

### --force
Genereert met `[BROKEN REF]` placeholders + DRAFT suffix.

---

## 11. Error Recovery

**Strategie:** Forward only - wat geschreven is blijft behouden.

```
Bij crash/interrupt:
    │
    ├── STATE.md bevat checkpoint
    │
    └── /doc:resume detecteert + biedt opties:
        1. Hervat waar gestopt
        2. Bekijk status
        3. Start andere operatie
```

**Partial detection:** CONTENT.md < 200 chars of `[TO BE COMPLETED]` marker.

---

## 12. Folder Structure

```
project/
├── .planning/
│   ├── PROJECT.md
│   ├── ROADMAP.md
│   ├── STATE.md
│   ├── CROSS-REFS.md
│   ├── BASELINE.md          # (Type C/D)
│   │
│   └── phases/
│       └── 0N-name/
│           ├── CONTEXT.md
│           ├── NN-MM-PLAN.md
│           ├── NN-MM-CONTENT.md
│           ├── NN-MM-SUMMARY.md
│           └── VERIFICATION.md
│
├── output/
│   ├── FDS-[Project]-v[X.Y].md
│   ├── SDS-[Project]-v[X.Y].md
│   ├── RATIONALE.md
│   ├── EDGE-CASES.md
│   ├── ENGINEER-TODO.md
│   └── TRACEABILITY.md
│
├── diagrams/
│   ├── mermaid/
│   ├── rendered/
│   └── external/           # P&ID etc.
│
└── export/
    └── *.docx
```

---

## 13. Standards Integration

**Opt-in alleen.** Nooit pushen.

```yaml
# PROJECT.md
standards:
  packml:
    enabled: true
  isa88:
    enabled: true
```

---

## 14. Acceptance Criteria

- [ ] 1-op-1 mapping met GSD workflow
- [ ] STATE.md progress tracking + crash recovery
- [ ] Verse context per write taak
- [ ] Goal-backward verification
- [ ] Gap closure loop werkt
- [ ] 4 project types met eigen ROADMAP
- [ ] Dynamische ROADMAP evolutie (>5 units)
- [ ] Versioning: v0.x intern, v1.0+ klant
- [ ] Kennisoverdracht: RATIONALE, EDGE-CASES, Fresh Eyes
- [ ] Cross-ref registry + strict validation
- [ ] ENGINEER-TODO.md voor complexe diagrams
- [ ] DOCX export met huisstijl
- [ ] Werkt voor Type D (30 min) én Type A (100 motoren)

---

*Gegenereerd uit SPECIFICATION.md v2.7.0*
