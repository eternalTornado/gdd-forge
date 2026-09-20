<!-- gdd-forge lite template · 2-core-gameplay.md · contract: contracts-lite/lite-2.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 2. Core Gameplay

<!-- 2–3 lines: loop, mechanics, economy, obstacles, stage structure — the systemic heart of the design. Reads 1_Concept.md whole. -->

## 2.1 Core Loop
<!-- Session loop as ≤ 8 one-line verb beats. No per-beat pillar citation. -->

## 2.2 World Rules
<!-- 3–5 short declaratives: movement, collision, fail state. -->

## 2.3 Mechanics Catalogue
<!-- One sub-section per mechanic: Pillar line · intent · rules · I/O · one tunables table. A mechanic with no pillar is a GAP. Casual scope: ≤ 5 mechanics, each tunable in exactly one table file-wide. -->
<!--
### Mechanic: <name>
Pillar: <§1.4 pillar> — Intent · Rules · Inputs/Outputs

| Tunable | Default (tunable) | Range |
|---|---|---|
| … | … | … |
-->

## 2.4 Economy
<!-- Sources/sinks table per currency. Monetised sinks use only D-30 mechanisms — anything else is a GAP. -->
<!--
| Currency | Sources | Sinks | Monetised? (D-30) |
|---|---|---|---|
| … | … | … | No |
-->

## 2.5 Obstacles & Generator
<!-- Always designs the non-enemy obstacle/hazard archetypes implied by §2.3/§2.6; enemy patterns only if D-22 includes Enemies; nothing at all → one-line N/A, heading stays. D-23 generator-driven (Endless/arena, Procedural) → also owns every spawn/generator tunable + guardrails here, one table — §2.6–§2.8 point here instead of repeating values. No perception/navmesh/behaviour-tree language — that's an escalation GAP, not something to write around. -->

## 2.6 Level / Stage Structure
<!-- Discrete D-23: structure map + difficulty bands. Generator-driven: only the run's start/end flow — spawn/generator content lives in §2.5. -->

## 2.7 Difficulty & Pacing Curve
<!-- Qualitative table/paragraph. Name the tunables that drive it (§2.3/§2.5) — never fabricate benchmark numbers. -->

## 2.8 First Stages
<!-- Discrete → first 10 stages as compact rows. Generator-driven → "N/A — generator-driven; rules are in §2.5." -->
<!--
| ID | Name | Mechanic | Tier | Duration (est.) |
|---|---|---|---|---|
| S01 | … | … | … | … |
-->

## 2.9 Feature List Table
<!-- Every feature this file designs: id · feature · §1.4 pillar · priority · depends-on. ≤ 12 rows. Cross-ref §1.5. -->

## Open Decisions
<!-- One bullet per UNDECIDED field, GAP, (proposal). None → "None." -->
<!-- ## New Terms — add only if this file introduces a term the glossary (1_Concept.md §1.9) doesn't already cover. -->
