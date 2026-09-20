<!-- gdd-forge template · 08-artificial-intelligence.md · contract: references/contracts/ch08.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 8. Artificial Intelligence

<!-- 2–3 lines: behaviour specification for every non-player actor — enemies, NPCs, directors — so it can be implemented and tuned consistently with the design and performance budget. -->

<!-- CONDITIONAL: if D-22 = None, §8.1 is written in full (stating why there is no designed AI, plus a short note on any trivial automated behaviour that still exists — ambient traffic, wildlife, decorative motion); §8.2–§8.11 each keep their numbered heading, followed only by the single line "N/A — no designed AI." Never delete a heading — downstream dispatches are sliced by heading number. -->

## 8.1 AI Goals & Player Experience Intent
<!-- guidance: what the AI must make the player *feel* (threatened, outsmarted, supported, immersed) — not a technical section, a design-intent one. -->

## 8.2 AI Architecture
<!-- guidance: choice of FSM / behaviour tree / utility system / GOAP, with rationale, bounded by D-34's ambition level. DECISION: do not pick an architecture more sophisticated than D-34 states (a GAP if D-34 = UNDECIDED and a choice can't be made responsibly). -->

## 8.3 Enemy / Opponent AI
<!-- guidance: archetype table — one row per enemy/opponent type. -->
<!--
| Archetype | Role | Behaviour summary | Perception | Attack/decision pattern | Counter-play | Tunables |
|---|---|---|---|---|---|---|
| … | … | … | … | … | … | … (tunable) |
-->

## 8.4 NPC & Companion AI
<!-- guidance: behaviour patterns for non-hostile actors.
- companions: follow/assist/combat-support logic and how it stays useful without trivialising challenge
- quest-givers and crowds: idle/routine behaviour, reaction to player presence
- cross-reference personalities from ch 5 §5.6 so behaviour matches characterisation -->

## 8.5 Director / Procedural Systems
<!-- CONDITIONAL: only if D-22 includes "Procedural/director systems". Otherwise write the single line: "N/A — no director/procedural AI system." -->
<!-- guidance: what the director observes (player state, pacing), what it adjusts, and the rules bounding its adjustments. -->

## 8.6 Perception & Awareness Model
<!-- guidance: vision cones, hearing radius, memory/forgetting rules, threat evaluation — the shared perception model every archetype in §8.3/§8.4 draws from.
- describe the model once here; archetype entries should reference it, not restate it -->

## 8.7 Navigation & Movement
<!-- guidance: navigation data structure (navmesh/grid/waypoint graph), obstacle avoidance, group/formation movement if relevant. -->

## 8.8 Difficulty Adaptation & Fairness Rules
<!-- guidance: how AI responds to player skill/performance, and the fairness limits that keep adaptation from feeling cheap (no reading player input directly, no aim-bot-tier reactions unless D-34 explicitly allows it). -->

## 8.9 Tunable Parameters Table
<!-- guidance: consolidate every (tunable) value introduced in §8.2–§8.8 into one reference table. -->
<!--
| Parameter | Default | Range | Affects |
|---|---|---|---|
| … | … (tunable) | … | §8.3 archetype X |
-->

## 8.10 Debug & Tooling Needs
<!-- guidance: what debug visualisation/tooling the AI needs to be tunable in practice (perception gizmos, behaviour-tree inspector, spawn/encounter debug commands). Feeds ch 11 §11.5. -->

## 8.11 Performance Envelope Requests
<!-- guidance: qualitative asks to ch 9 (e.g. "pathfinding must support N concurrent agents," "perception checks must not run every frame") — no fabricated numbers; if a number matters, ask ch 9 to confirm it or raise a GAP. -->

## Open Decisions
<!-- One bullet per UNDECIDED brief field touched and per GAP placeholder in this chapter. Format: "- D-xx <field> — UNDECIDED — affects §N.x" or "- G-8-<n> — <what is needed> — §N.x". If none: "None." If D-20 is competitive-only with no stated bot support, flag that here as an Open Decision. -->

<!-- Optional: add a real `## New Terms` heading here (after Open Decisions) only if this chapter introduces a term not already in 3_Game Overview §3.10 — one line per term: **Term** — one-sentence definition. Omit entirely if no new term. -->
