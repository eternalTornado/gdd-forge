<!-- gdd-forge template · 04-gameplay-mechanics.md · contract: references/contracts/ch04.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 4. Gameplay and Mechanics

<!-- 2–3 lines: the systemic heart of the design — every mechanic, loop and rule an implementer needs to build the moment-to-moment game. Read by engineers, designers and (via ch 5/6/8) narrative, level and AI teams. -->

## 4.1 Core Loop
<!-- guidance: three nested cycles, each a numbered sequence naming the *verb* the player performs — the 30-second loop, the 5-minute loop, the session loop. Cite ch 3 §3.2 pillars each verb serves. ELABORATION: pacing and beat count; DECISION: none invented beyond D-03/D-09 genre and scope. -->

## 4.2 Meta Loop & Progression
<!-- guidance: unlock structure, currencies (soft/hard), power/skill growth curve, retention hooks scaled to D-09 scope. 3–6 bullets. If D-09 = Micro or Small, this section is a single progression track, not a full tree — say so explicitly. -->

## 4.3 World Rules & Physics
<!-- guidance: what is always true in this game world — movement model, collision, time flow, death/failure handling. These rules are load-bearing for ch 5 §5.2 (setting) and ch 6 (level layout); keep them genre-consistent with D-03. -->

## 4.4 Mechanics Catalogue
<!-- guidance: one sub-section per mechanic — intent · rules · inputs · outputs · edge cases · a tunables table. Every mechanic must cite the pillar (§3.2) it serves (hard rule) — a mechanic with no pillar is a GAP, not a free addition. -->
<!--
### Mechanic: <name>
Intent · Rules · Inputs · Outputs · Edge cases

| Tunable | Default | Range | Notes |
|---|---|---|---|
| … | … (tunable) | … | … |
-->

## 4.5 Systems Interaction Map
<!-- guidance: how mechanics feed systems feed resources — the map ch 8/9 read to understand system coupling. -->
```mermaid
```
<!-- diagram type: graph (mechanics → systems → resources) -->

## 4.6 Objectives, Challenge & Puzzle Structure
<!-- guidance: objective types (primary/secondary/optional), how challenge escalates, puzzle structure if any. 3–6 bullets tied to §4.1's loops. -->

## 4.7 Economy
<!-- guidance: sources/sinks table for every currency named in §4.2. DECISION: if D-06 is F2P/hybrid, mark which sinks are monetised using only mechanisms listed in D-30 — any sink monetised by a mechanism outside D-30 is a GAP, never invented. -->
<!--
| Currency | Sources | Sinks | Monetised? (D-30 mechanism) |
|---|---|---|---|
| Soft currency | … | … | No |
-->

## 4.8 Multiplayer Rules
<!-- CONDITIONAL: only if D-20 ≠ None. Otherwise write the single line: "Single-player only (D-20)." -->
<!-- guidance: modes, match flow, fairness model, scale per D-32 (player count, persistence). ELABORATION: match structure; DECISION: mode roster must not exceed what D-20/D-32 imply. -->

## 4.9 Game Options, Saving & Replay
<!-- guidance: difficulty options, save model (checkpoints/manual/auto), New Game+ or replay value if any. 3–5 bullets. -->

## 4.10 Balance Framework
<!-- guidance: target curves described qualitatively (difficulty, power, economy) + which tunables from §4.4/§4.7 drive each curve. No fabricated numeric benchmarks — curves are described in words, tunables are named. -->

## 4.11 Feature List Table
<!-- guidance: every feature this chapter designs, cross-referenced to ch 3 §3.3. DECISION: every row's pillar must exist in §3.2 — a row with no pillar is a GAP. Ch 12's roadmap must later carry every id here (consistency rule #2); the reviewer checks that, never you — ch 12 does not exist yet, so do not raise a GAP for it. -->
<!--
| ID | Feature | Pillar | Priority | Depends on |
|---|---|---|---|---|
| F01 | … | … | P0 | — |
-->

## Open Decisions
<!-- One bullet per UNDECIDED brief field touched and per GAP placeholder in this chapter. Format: "- D-xx <field> — UNDECIDED — affects §N.x" or "- G-4-<n> — <what is needed> — §N.x". If none: "None." -->

<!-- Optional: add a real `## New Terms` heading here (after Open Decisions) only if this chapter introduces a term not already in 3_Game Overview §3.10 — one line per term: **Term** — one-sentence definition. Omit entirely if no new term. -->
