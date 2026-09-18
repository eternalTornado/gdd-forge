<!-- gdd-forge template · 06-levels.md · contract: references/contracts/ch06.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 6. Levels

<!-- 2–3 lines: spatial expression of the design — every level/zone an implementer and level artist need to block out. Reads ch 3 §3.9 counts, ch 4 mechanics, ch 5 narrative beats. -->

## 6.1 Level Design Philosophy
<!-- guidance: how the pillars (ch 3 §3.2) show up spatially, and the pacing rhythm (tension/release cadence) across the whole game.
- 3–5 bullets, each naming a pillar and how space/encounter design expresses it
- note where D-09 scope caps total content volume (fewer, denser levels vs many short ones) -->

## 6.2 Structure Map
<!-- guidance: reflects D-23 (linear/hub/open/procedural/level-select/endless/single space). -->
```mermaid
```
<!-- diagram type: mermaid graph reflecting D-23's level/world structure -->

## 6.3 Tutorial / Onboarding Level
<!-- guidance: the order mechanics from ch 4 §4.4 are introduced, tied to a concrete level/zone.
- one mechanic per beat, no more than the pacing in §6.1 allows
- state explicitly which §4.4 mechanic each beat teaches, so ch 4/ch 6 stay traceable to each other -->

## 6.4 Level Entries
<!-- guidance: one per level/zone — synopsis · objectives · narrative beat (ch 5 §5.5) · layout sketch · critical path · encounters/challenges · mechanics introduced/tested (ch 4 §4.4) · target duration (est.) · difficulty tier · asset needs (feeds ch 10 §10.9, ch 13 §C). DEPTH RULE: number of full entries follows ch 3 §3.9's level count — if that count is > 20, write full entries for the first 5 + one per act, and list the rest as §6.7 table rows only. If D-23 = Single persistent space, these become zone entries instead of levels. -->

### 6.4.x <Level id> — <Level name>
<!-- repeat per level; see Depth rule for how many full entries -->
<!-- fields: synopsis · objectives · narrative beat · layout sketch (ASCII or mermaid) · critical path · encounters/challenges · mechanics introduced/tested · target duration (est.) · difficulty tier · asset needs -->

## 6.5 Difficulty & Pacing Curve
<!-- guidance: a table plotting difficulty tier and target duration across the full level list, showing the intended curve.
- call out where the curve dips for a breather beat vs where it spikes for a set-piece -->
<!-- ELABORATION throughout — no fabricated benchmark numbers, only the ordering/shape of the curve. -->
<!--
| Level | Difficulty tier | Duration (est.) | Notes |
|---|---|---|---|
| … | … | … | … |
-->

## 6.6 Procedural Rules
<!-- CONDITIONAL: only if D-23 ∈ {Procedural, Endless}. Otherwise write the single line: "Not applicable — level structure is not procedural (D-23)." -->
<!-- guidance: cover —
- which generators are used and what they produce (layout, encounters, loot)
- constraints/guardrails they operate under so output stays playable
- the authored-vs-generated content share per D-35 -->

## 6.7 Level List Table
<!-- guidance: every level/zone, including ones not given a full §6.4 entry.
- status column tracks production state (Planned / Blocked / Done), not design completeness
- this table is what ch 12 §12.10 QA planning and ch 13 §B feature list both cross-check against -->
<!--
| ID | Name | Act | Duration (est.) | Tier | Status |
|---|---|---|---|---|---|
| L01 | … | 1 | … | … | Planned |
-->

## Open Decisions
<!-- One bullet per UNDECIDED brief field touched and per GAP placeholder in this chapter. Format: "- D-xx <field> — UNDECIDED — affects §N.x" or "- G-n — <what is needed> — §N.x". If none: "None." -->

<!-- New terms (only if you introduced a term not in 3_Game Overview §3.10): -->
