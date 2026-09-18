# Checklist ch11-tooling — Secondary Software & Tooling
Applies to: 11_Secondary Software.md · Used by: gdd-tech-designer (self-check) and gdd-reviewer.
`[R]` = reviewer-only — depends on a chapter written after this one; at self-check count it as n/a (exclude from passed/total), never as a fail.

## Coverage
- [ ] TO-01 Tool Matrix (§11.7) has tool, purpose, owner, build-vs-buy, and phase columns filled for every row
- [ ] TO-02 Every pipeline step named in ch9 has at least one corresponding tool row in the Tool Matrix
- [ ] TO-03 Editor & Engine Tooling (§11.2) is stated as engine-dependent when D-11 = UNDECIDED

## Conditional Tooling
- [ ] TO-04 Procedural generation tooling (§11.2) is present if ch6 §6.6 (procedural rules) exists
- [ ] TO-05 AI debug tooling (§11.5) is present if ch8 §8.10 (debug & tooling needs) exists
- [ ] TO-06 Content & Asset Pipeline Tools (§11.3) name validators for the naming/metadata convention defined in ch7 §7.11 / ch10 §10.8

## Build & Release
- [ ] TO-07 Build, CI/CD & Distribution (§11.4) states which platforms in D-04 the pipeline targets
- [ ] TO-08 Every build-vs-buy decision in the Tool Matrix states a reason (cost, team skill, or existing tooling from D-42)

## Debug & QA Tooling
- [ ] TO-09 [R] Debug, Telemetry & Live Tools (§11.5) references analytics hooks needed for the LiveOps plan (ch12 §12.7) when D-24 ≠ None
- [ ] TO-10 Localisation & QA tooling (§11.6) names tooling for the languages in D-38

## Anti-fabrication
- [ ] TO-11 No tool is named as already adopted unless it appears in D-42 (existing_tooling); otherwise it is proposed, not assumed
- [ ] TO-12 No engine-specific tool is recommended for an engine absent from D-11 when D-11 is resolved

## Consistency rules
- [ ] TO-13 [Rule 7] No tooling decision states an engine or platform absent from brief.md
- [ ] TO-14 [Rule 1] Tooling terminology matches the Glossary in ch3 §3.10
