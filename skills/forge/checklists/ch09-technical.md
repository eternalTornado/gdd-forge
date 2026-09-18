# Checklist ch09-technical — Technical Feasibility & Handoff Readiness
Applies to: 9_Technical.md · Used by: gdd-tech-designer (self-check) and gdd-reviewer.
`[R]` = reviewer-only — depends on a chapter written after this one; at self-check count it as n/a (exclude from passed/total), never as a fail.

## Architecture & Stack
- [ ] TE-01 Engine & Language stack (§9.2) states D-11; if D-11 = UNDECIDED, a comparison table of 2–3 candidates is given with no pick made
- [ ] TE-02 System Architecture (§9.3) lists core systems with responsibilities and includes a mermaid component diagram
- [ ] TE-03 Data Architecture (§9.4) states the save system format and a versioning/migration approach

## Pipeline & Networking
- [ ] TE-04 Asset Pipeline & Media Profiles (§9.5) references the naming convention from ch7 §7.11 / ch10 §10.8 rather than restating a new one
- [ ] TE-05 Networking (§9.6) is present only if D-20 ≠ None; otherwise it is the one-line Depth-rule statement
- [ ] TE-06 If present, Networking states topology, authority model, sync model, anti-cheat stance, and scale from D-32

## Performance & Feasibility
- [ ] TE-07 Performance Budgets (§9.7) are stated as targets tagged "(target)", not asserted benchmarks
- [ ] TE-08 Performance requirements are stated as realistic for the platforms in D-04 (no target exceeds what the `data/platforms/` slice supports)
- [ ] TE-09 Technical dependencies (engine, middleware, existing tooling from D-42) are clearly identified
- [ ] TE-10 Technical Risks & Spikes (§9.10) names at least one risk per major system introduced in §9.3

## Handoff Readiness
- [ ] TE-11 Technical specifications name platform/engine choices precisely enough to hand off to an implementer without further decisions (or flag what is still open)
- [ ] TE-12 Feature-relevant technical requirements in §9.3–§9.6 trace back to a feature in ch4 §4.11
- [ ] TE-13 Quality assurance approach for technical validation is stated (what gets tested, not just "QA will test it")

## Anti-fabrication
- [ ] TE-14 No engine, platform, or performance number is asserted that is absent from D-04/D-11/D-37 or the data files
- [ ] TE-15 No benchmark or third-party technical claim appears without citing the `data/platforms/` slice you were given or brief.md

## Consistency rules
- [ ] TE-16 [Rule 7] No technical decision states a platform, engine, or budget figure absent from brief.md
- [ ] TE-17 [Rule 1] Technical terminology matches the Glossary in ch3 §3.10
