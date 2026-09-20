# Checklist lite-4-business — Business and LiveOps (lite profile)
Applies to: 4_Business and LiveOps.md · Used by: gdd-producer (self-check) and gdd-reviewer.

## Monetisation
- [ ] LB-01 Business Model Summary (§4.1) restates D-06 without inventing a mechanism
- [ ] LB-02 Ad Placement Design (§4.2) ties rewarded-video placement to a named moment in §2.1/§2.6
- [ ] LB-03 Interstitial cadence in §4.2 is stated as a named tunable, never a fixed invented number
- [ ] LB-04 IAP Catalogue (§4.3) uses only mechanisms listed in D-30; a real-money price absent from the brief is a `value` GAP

## KPIs & Creative
- [ ] LB-05 KPI Definitions & Targets (§4.4) defines every metric from data/casual/metrics-definitions.md without restating a definition differently elsewhere; when D-48 ∈ {No, UNDECIDED}, §4.4 omits acquisition metrics (CPI, IPM, CTR, CVR); an ad-health threshold with no target is a `(proposal)`, never a GAP
- [ ] LB-06 Every KPI target value in §4.4 is tagged "(target)" and cites D-45 as its source — no target appears while D-45 = UNDECIDED
- [ ] LB-07 Creative & Playable Ad Concept (§4.5) is present only when D-48 = Yes (else exactly the N/A line) and, when present, names a mechanic that exists in 2_Core Gameplay.md §2.3

## Roadmap & Risk
- [ ] LB-08 Roadmap (§4.6) states prototype → CPI test → soft launch → global launch when D-48 = Yes, else prototype → soft launch → global launch; each phase has a testable exit criterion
- [ ] LB-09 Roadmap durations stay relative ("T+n") unless the brief supplies team/timeline data — no invented calendar dates
- [ ] LB-10 Risk Register (§4.7) has a source for every row, ≤ 6 rows; an `Owner` column exists only when D-10 is a team of 2+
- [ ] LB-11 LiveOps Plan (§4.8) is present only if D-24 ≠ None; otherwise it is exactly the one-line Depth-rule statement

## Anti-fabrication
- [ ] LB-12 No ad network or mediation platform is named beyond what D-46 states
- [ ] LB-13 No currency or market-size figure appears unless stated in brief.md

## Consistency rules
- [ ] LB-14 [Lite rule 3] Every ad/IAP mechanism in §4.2/§4.3 uses only D-30 entries
- [ ] LB-15 [Lite rule 5] Every UNDECIDED field touched (including D-45/D-46/D-48 when unresolved) appears in the Open Decisions box
- [ ] LB-16 [Lite rule 9] Every KPI target, price, and cadence tunable has the same value everywhere it appears in this file

## Writing discipline
- [ ] LB-17 File and every section within its word ceiling, or declared OVER_BUDGET
- [ ] LB-18 No fact restated outside its owning section — pointers only
- [ ] LB-19 No kit/process vocabulary in the deliverable; no inline `(D-xx)`/`(G-xx)` tags on sentences
- [ ] LB-20 N/A sections are one line; Open Decisions lists only what is open
