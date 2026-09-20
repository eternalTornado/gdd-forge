# Checklist lite-1-concept — Concept (lite profile)
Applies to: 1_Concept.md · Used by: gdd-concept-architect (self-check) and gdd-reviewer.

## Header & Pillars
- [ ] LC-01 Document Header (§1.1) states game name (or the literal `[GAME NAME — pending §1.2]` placeholder when D-01 = GENERATE/UNDECIDED), version, profile (hyper-casual/casual), and rights holder (or the `[RIGHTS HOLDER — UNDECIDED]` placeholder)
- [ ] LC-02 Name Candidates (§1.2) is present only if D-01 = GENERATE/UNDECIDED, with exactly 3 candidates each carrying a rationale and a trademark-caveat line; otherwise it is exactly `N/A — working title set.`
- [ ] LC-03 Game Concept (§1.3) opens with D-02 quoted verbatim
- [ ] LC-04 Design Pillars (§1.4) has 3–5 pillars, each with a name, one-sentence meaning, and one-sentence forbid clause; no forbid clause blocks a D-43 must-have or a D-30 mechanism — a pillar that does is reworded, never rationalised around
- [ ] LC-05 Every pillar is derivable from D-02/D-08/D-43 — none invented from genre convention alone

## Feature Set & Scope
- [ ] LC-06 Feature Set (§1.5) table has priority and pillar columns filled for every row; no feature outranks a feature it depends on
- [ ] LC-07 Every D-43 item appears as P0; every D-44 item appears only under "Explicitly out," never as a feature
- [ ] LC-08 Genre & Comparables (§1.6) is a table stating one thing to borrow and one to avoid per D-13 title, or states plainly that D-13 = none
- [ ] LC-09 Target Audience & Platforms (§1.7) restates D-05/D-04/D-06 without adding a platform or audience absent from the brief
- [ ] LC-10 Setting & Theme (§1.8) depth matches D-21 (None → one line; Light framing → short paragraph); anything above Light framing is flagged as an escalation signal, not silently expanded
- [ ] LC-11 Scope & Glossary Seed (§1.9) states D-09's two parts (session length per app session, never per run/level; content ambition — no "hours of content" line when replay-driven) plus 8–15 glossary terms, ≤ 20 words each, every count tagged "(est.)"

## Anti-fabrication
- [ ] LC-12 No platform, audience, or business model appears that is absent from brief.md
- [ ] LC-13 If present, every Name Candidate in §1.2 carries the "cannot verify trademark/app-store availability" caveat — none claims availability

## Consistency rules
- [ ] LC-14 [Lite rule 1] Glossary terms in §1.9 are the ones every later lite file must reuse verbatim
- [ ] LC-15 [Lite rule 5] Every UNDECIDED field touched by this file appears in its Open Decisions box
- [ ] LC-16 [Lite rule 11] No pillar in §1.4 forbids a D-43 must-have or a D-30 mechanism; no feature in §1.5 outranks a feature it depends on

## Writing discipline
- [ ] LC-17 File and every section within its word ceiling, or declared OVER_BUDGET
- [ ] LC-18 No fact restated outside its owning section — pointers only
- [ ] LC-19 No kit/process vocabulary in the deliverable; no inline `(D-xx)`/`(G-xx)` tags on sentences
- [ ] LC-20 §1.2/§1.8 N/A cases are one line; Open Decisions lists only what is open
