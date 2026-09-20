# Checklist lite-5-tech — Tech Note (lite profile)
Applies to: 5_Tech Note.md · Used by: gdd-tech-designer (self-check) and gdd-reviewer.

## Platform & Architecture
- [ ] LT-01 Platform & Device Floor (§5.1) states D-04 and D-37 (or "UNDECIDED" verbatim)
- [ ] LT-02 Engine & Stack (§5.2) is a comparison table with no pick made when D-11 = UNDECIDED; existing tooling (D-42) is listed once, here
- [ ] LT-03 Architecture & Data (§5.3) names systems already implied by 2_Core Gameplay.md §2.3/§2.5, not invented parallel ones
- [ ] LT-04 §5.3 references the naming convention from 3_UX Art and Audio.md §3.7 rather than defining a second one
- [ ] LT-10 §5.3's storage table has one row for every persisted value named in files 1–2, with one statement per data decision — never both "add alongside" and "replace"

## Performance, SDKs & Tooling
- [ ] LT-05 Every figure in Performance & Build-Size Budgets (§5.4) is tagged "(target)"
- [ ] LT-06 The download-size target in §5.4 cites D-47 as its source; if D-47 = UNDECIDED, no number is given and it is flagged in Open Decisions
- [ ] LT-07 SDK List (§5.5) has one row per SDK category the design actually needs — gated per the brief triggers in the contract (ads/IAP/backend/analytics/attribution), not a fixed list regardless of need
- [ ] LT-08 Each SDK row's product comes from D-46/D-42, or is a named product tagged `(proposal)` with 1–2 alternatives in Open Decisions — never invented with no source and never a bare GAP
- [ ] LT-09 Compliance (§5.6) restates D-40 only — no legal advice or invented obligation
- [ ] LT-11 Technical Risks (§5.7) contains only engineering risk, not business/schedule risk (that belongs to 4_Business and LiveOps.md §4.7)

## Anti-fabrication
- [ ] LT-12 No engine, platform, or performance number is asserted that is absent from D-04/D-11/D-37/D-47 or the `data/platforms/` slice it was given
- [ ] LT-13 Build-size and performance figures are never presented as measured benchmarks

## Consistency rules
- [ ] LT-14 [Lite rule 7] No numeric CPI/build-size/performance claim appears without a brief citation or an explicit "(target)" tag
- [ ] LT-15 [Lite rule 5] Every UNDECIDED field touched (including D-11/D-47 when unresolved) appears in the Open Decisions box
- [ ] LT-16 [Lite rule 10] Every persisted value in §5.3 has exactly one storage location; every SDK category names a product or an explicit `(proposal)`

## Writing discipline
- [ ] LT-17 File and every section within its word ceiling, or declared OVER_BUDGET
- [ ] LT-18 No fact restated outside its owning section — pointers only
- [ ] LT-19 No kit/process vocabulary in the deliverable; no inline `(D-xx)`/`(G-xx)` tags on sentences
- [ ] LT-20 N/A sections are one line; Open Decisions lists only what is open
