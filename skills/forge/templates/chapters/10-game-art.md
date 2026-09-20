<!-- gdd-forge template · 10-game-art.md · contract: references/contracts/ch10.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 10. Game Art

<!-- 2–3 lines: visual bible translating ch 3's mood and ch 5's cast/world into production-ready art direction and an asset list.
Read by artists producing content and by ch 9's asset pipeline validating it. -->

## 10.1 Art Direction Statement & Visual Pillars
<!-- guidance: expand ch 3 §3.8's mood seed into 2–4 visual pillars (shape language, palette philosophy, lighting mood) each traceable to D-07/D-08. -->

## 10.2 Style Guide
<!-- guidance: shape language · colour script per region/act (ties to ch 5 §5.3) · materials · lighting rules · line/texture rules. ELABORATION throughout, seeded by D-07. -->

## 10.3 Character Art
<!-- guidance: per character in ch 5 §5.6 — silhouette, palette, costume rules. DEPTH RULE: if D-21 = None (ch 5 dropped), this section covers only the player avatar and enemy/opponent types named in ch 6 §6.4 encounters (ch 8 is written in parallel with you) — say so explicitly. -->

## 10.4 Environment Art
<!-- guidance: per region (ch 5 §5.3) or zone (ch 6 §6.4).
- biome/architecture style, key set pieces, mood lighting
- note where environment art must support a gameplay read (take the read from ch 6 §6.4's 'mechanics introduced/tested' — e.g. climbable surfaces must look climbable) -->

## 10.5 Props, VFX & Animation Principles
<!-- guidance: cover —
- prop design language
- VFX style (readability vs spectacle trade-off, and how VFX communicates the mechanic states surfaced in ch 7 §7.4's HUD and ch 6 §6.4's encounters)
- animation principles (weight, timing, exaggeration) consistent with D-07 -->

## 10.6 UI Art
<!-- guidance: visual treatment of the HUD from ch 7 §7.4 and the UI asset rows in ch 7 §7.11 — icon style, panel treatment, motion language for transitions. Coordinate with ch 7, don't re-derive its inventory. -->

## 10.7 Marketing & Store Art Needs
<!-- guidance: key art, store page/listing assets, screenshot composition guidelines, trailer/social crop needs.
- list only what's needed (specs and purpose), not the assets themselves
- align aspect ratios/crops to the platforms in brief D-04 (ch 9 is written after you) -->

## 10.8 Asset Pipeline & Naming Convention
<!-- guidance: naming pattern + 2–3 examples · directory structure · variant/version rules (_01, v001, LOD0) · texture channel suffixes if applicable. Adopt ch 7 §7.11's pattern VERBATIM (it was written before you), then extend it with art categories, directory structure, variant/version rules and texture suffixes. Never restate a competing scheme — consistency rule #5 checks every asset table against that one pattern. -->
<!--
Pattern: `<Type>_<Category>_<Name>_<Variant>.<ext>`
Example: `CHR_Hero_MainOutfit_01.png`
-->

## 10.9 Asset List — Minimum Deliverable
<!-- guidance: every asset implied by ch 5/6/7 plus this chapter's own needs. Feeds ch 13 §C. -->
<!--
| ID | Type | Name | Source chapter | Priority | Notes |
|---|---|---|---|---|---|
| A01 | 3d_model | … | ch5 §5.6 | P0 | … |
-->

## 10.10 Reference & Mood Board Descriptions
<!-- guidance: text descriptions of reference material (from D-13 and D-07) — no image generation.
- describe what a mood board would contain and why each reference was chosen
- one description per region/character where a distinct visual reference applies -->

## Open Decisions
<!-- One bullet per UNDECIDED brief field touched and per GAP placeholder in this chapter. Format: "- D-xx <field> — UNDECIDED — affects §N.x" or "- G-10-<n> — <what is needed> — §N.x". If none: "None." -->

<!-- Optional: add a real `## New Terms` heading here (after Open Decisions) only if this chapter introduces a term not already in 3_Game Overview §3.10 — one line per term: **Term** — one-sentence definition. Omit entirely if no new term. -->
