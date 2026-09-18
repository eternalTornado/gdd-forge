# Checklist lite-5-tech — Tech Note (lite profile)
Applies to: 5_Tech Note.md · Used by: gdd-tech-designer (self-check) and gdd-reviewer.

## Platform & Architecture
- [ ] LT-01 Platform & Device Floor (§5.1) states D-04 and D-37 (or "UNDECIDED" verbatim)
- [ ] LT-02 Engine & Stack (§5.2) is a comparison table with no pick made when D-11 = UNDECIDED
- [ ] LT-03 Architecture & Data (§5.3) names systems already implied by 2_Core Gameplay.md §2.3/§2.5, not invented parallel ones
- [ ] LT-04 §5.3 references the naming convention from 3_UX Art and Audio.md §3.7 rather than defining a second one

## Performance, SDKs & Tooling
- [ ] LT-05 Every figure in Performance & Build-Size Budgets (§5.4) is tagged "(target)"
- [ ] LT-06 The download-size target in §5.4 cites D-47 as its source; if D-47 = UNDECIDED, no number is given and it is flagged in Open Decisions
- [ ] LT-07 SDK List (§5.5) covers ad mediation, analytics, attribution, remote config, IAP, and crash reporting as distinct rows
- [ ] LT-08 The ad mediation row in §5.5 names D-46's platform, or states "see D-46, UNDECIDED" — never a product invented with no brief source
- [ ] LT-09 Compliance (§5.6) restates D-40 only — no legal advice or invented obligation
- [ ] LT-10 Tool Matrix (§5.7) is a single table; D-11 = UNDECIDED rows read "engine-dependent"
- [ ] LT-11 Technical Risks (§5.8) contains only engineering risk, not business/schedule risk (that belongs to 4_Business and LiveOps.md §4.7)

## Anti-fabrication
- [ ] LT-12 No engine, platform, or performance number is asserted that is absent from D-04/D-11/D-37/D-47 or the `data/platforms/` slice it was given
- [ ] LT-13 Build-size and performance figures are never presented as measured benchmarks

## Consistency rules
- [ ] LT-14 [Lite rule 7] No numeric CPI/build-size/performance claim appears without a brief citation or an explicit "(target)" tag
- [ ] LT-15 [Lite rule 5] Every UNDECIDED field touched (including D-11/D-47 when unresolved) appears in the Open Decisions box
