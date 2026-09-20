# Checklist lite-2-gameplay — Core Gameplay (lite profile)
Applies to: 2_Core Gameplay.md · Used by: gdd-mechanics-designer (self-check) and gdd-reviewer.

## Loop & Mechanics
- [ ] LG-01 Core Loop (§2.1) is ≤ 8 one-line verb beats; no per-beat pillar citation (mechanics and §2.9 carry it)
- [ ] LG-02 World Rules (§2.2) states 3–5 declaratives before any mechanic detail
- [ ] LG-03 Every mechanic in the Mechanics Catalogue (§2.3) has a `Pillar:` line, intent, rules, inputs/outputs, and one tunables table; an item/skin/power-up touching physics or hitboxes proves §2.5's guardrails hold for the worst case
- [ ] LG-04 Every mechanic cites a §1.4 pillar — a mechanic with no pillar is a GAP; a D-43 must-have that cannot be built without breaking a pillar's forbid clause is raised as a `structural` GAP, never rationalised
- [ ] LG-05 Economy (§2.4) lists sources/sinks in a table; if D-06 is F2P/hybrid, monetised sinks use only D-30 mechanisms

## Obstacles & Structure
- [ ] LG-06 Obstacles & Generator (§2.5) always designs obstacle/hazard archetypes and spawn-rate/difficulty-scaling rules for the non-enemy obstacles implied by §2.3/§2.6, independent of D-22 — no perception, navmesh, or behaviour-tree language
- [ ] LG-07 §2.5 adds enemy movement patterns only if D-22 includes Enemies, and is the one-line N/A statement only when §2.3/§2.6 imply no obstacles at all
- [ ] LG-08 Level/Stage Structure (§2.6) reflects D-23 without introducing a structure type absent from the brief; when D-23 is generator-driven, §2.6 holds only the run's start/end flow (spawn/generator rules live in §2.5)
- [ ] LG-09 Difficulty & Pacing Curve (§2.7) is qualitative — no fabricated benchmark numbers, tunables named instead; when D-23 is generator-driven, it names §2.5's tunables without repeating their values
- [ ] LG-10 First Stages (§2.8) is a stage table for discrete `D-23` structures, or exactly `N/A — generator-driven; rules are in §2.5.` for Endless/procedural — never both, and never generator rules written here

## Feature List
- [ ] LG-11 Feature List Table (§2.9) has id, feature, pillar, priority, and depends-on filled for every row, ≤ 12 rows

## Anti-fabrication
- [ ] LG-12 No monetised sink uses a mechanism absent from D-30
- [ ] LG-13 No balance number is stated as fixed fact — every target is tagged "(tunable)" or "(est.)"; each tunable lives in exactly one table in the whole file

## Consistency rules
- [ ] LG-14 [Lite rule 2] Every feature in §2.9 traces to a §1.4 pillar
- [ ] LG-15 [Lite rule 5] Every UNDECIDED field touched by this file appears in its Open Decisions box
- [ ] LG-16 [Lite rule 11] No mechanic, obstacle, or economy sink violates a pillar's forbid clause; no feature in §2.9 outranks a feature it depends on
- [ ] LG-17 [Lite rule 10] This file states only that a player choice exists and when it locks — never its home screen (file 3) or storage location (file 5)

## Writing discipline
- [ ] LG-18 File and every section within its word ceiling, or declared OVER_BUDGET
- [ ] LG-19 No fact restated outside its owning section — pointers only
- [ ] LG-20 No kit/process vocabulary in the deliverable; no inline `(D-xx)`/`(G-xx)` tags on sentences
- [ ] LG-21 N/A sections are one line; Open Decisions lists only what is open
