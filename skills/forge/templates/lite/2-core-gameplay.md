<!-- gdd-forge lite template · 2-core-gameplay.md · contract: contracts-lite/lite-2.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 2. Core Gameplay

<!-- 2–3 lines: the systemic + spatial heart of the design — loop, mechanics, economy, obstacles, and stage/level structure in one file. Reads 1_Concept.md. -->

## 2.1 Core Loop
<!-- The session loop as a numbered verb cycle, citing a §1.4 pillar per beat. Add a second (meta-progression) tier only if D-09 genuinely needs it — casual sessions rarely support three nested loops the way the full kit's ch4 does. -->

## 2.2 World Rules
<!-- 3–5 short declaratives on what is always true — movement, collision, fail state. Condensed from the full kit's ch4 §4.3. -->

## 2.3 Mechanics Catalogue
<!-- One sub-section per mechanic: intent · rules · inputs/outputs · a tunables table. Every mechanic cites a §1.4 pillar (hard rule) — a mechanic with no pillar is a GAP. Casual scope typically yields 2–5 mechanics. -->
<!--
### Mechanic: <name>
Intent · Rules · Inputs/Outputs

| Tunable | Default | Range |
|---|---|---|
| … | … (tunable) | … |
-->

## 2.4 Economy
<!-- Sources/sinks table for every currency. If D-06 is F2P/hybrid, mark monetised sinks using only D-30 mechanisms — anything else is a GAP. -->
<!--
| Currency | Sources | Sinks | Monetised? (D-30) |
|---|---|---|---|
| … | … | … | No |
-->

## 2.5 Obstacle & Spawn Patterns
<!-- Replaces the full kit's ch8 entirely. Patterns and spawn rules ONLY — obstacle archetypes, spawn-rate/difficulty scaling, simple enemy movement if D-22 includes it. No perception model, navmesh, or behaviour tree — that's an escalation signal, not something to elaborate around (profile-casual.md § When not to use this profile). CONDITIONAL: D-22 = None → "No enemies or scripted obstacles beyond terrain/level geometry (D-22)." -->

## 2.6 Level / Stage Structure
<!-- Reflects D-23. Discrete structure (level select etc.): a structure map + how stages group into difficulty bands. Endless: the meta-structure of a run (start/end conditions, what escalates). -->

## 2.7 Difficulty & Pacing Curve
<!-- Short table/paragraph plotting difficulty across §2.6. Qualitative — name the tunables that drive it, never fabricate benchmark numbers. -->

## 2.8 First Stages / Generator Rules
<!-- CONDITIONAL on D-23. Discrete structure → first 10 stages as compact rows (id · name · mechanic taught/tested · tier · duration (est.)) — no full prose entries. Endless/generator-driven → generator rules instead (what generates, guardrails, authored-vs-generated share per D-35); state there is no fixed stage list. -->
<!--
| ID | Name | Mechanic | Tier | Duration (est.) |
|---|---|---|---|---|
| S01 | … | … | … | … |
-->

## 2.9 Feature List Table
<!-- Every feature this file designs: id · feature · §1.4 pillar · priority · depends-on. Cross-referenced to §1.5. -->

## Open Decisions
<!-- One bullet per UNDECIDED brief field touched and per GAP placeholder. Format: "- D-xx <field> — UNDECIDED — affects §N.x" or "- G-<file>-<n> — <what is needed> — §N.x". If none: "None." -->
