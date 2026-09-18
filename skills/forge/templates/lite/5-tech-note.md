<!-- gdd-forge lite template · 5-tech-note.md · contract: contracts-lite/lite-5.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 5. Tech Note

<!-- 2–3 lines: engine, device floor, architecture, performance/build-size targets, SDK list and tool matrix in one short note. Reads only 1_Concept.md and 2_Core Gameplay.md. -->

## 5.1 Platform & Device Floor
<!-- D-04 platform list · minimum device/browser target from D-37 (or "UNDECIDED" verbatim). -->

## 5.2 Engine & Stack
<!-- CONDITIONAL: D-11 = UNDECIDED → comparison table of 2–3 candidates against requirements, no pick made. Otherwise state D-11 with one paragraph of rationale. -->
<!--
| Candidate | Fit | Licensing | Risk |
|---|---|---|---|
| … | … | … | … |
-->

## 5.3 Architecture & Data
<!-- Core systems list (naming systems already implied by 2_Core Gameplay.md §2.3/§2.5 — do not invent parallel ones), save/config format choice. One line: asset naming follows 3_UX Art and Audio.md §3.7 — do not define a second scheme here. -->

## 5.4 Performance & Build-Size Budgets
<!-- Frame time, memory, load time, download size — every figure tagged (target). Download size cites D-47 if resolved; if UNDECIDED, state no build-size target exists yet and list D-47 in Open Decisions. -->
<!--
| Metric | Target | Source |
|---|---|---|
| Download size | … (target, D-47) | … |
-->

## 5.5 SDK List
<!-- Ad mediation (name the platform from D-46 if resolved, else "see D-46, UNDECIDED"), analytics, attribution, remote config, IAP, crash reporting. One row per category. -->
<!--
| Category | Product | Notes |
|---|---|---|
| Ad mediation | … | D-46 |
| Analytics | … | … |
-->

## 5.6 Compliance
<!-- D-40 requirements restated in technical terms — privacy consent flows, rating-appropriate content gates, ad-SDK consent management for regulated regions. -->

## 5.7 Tool Matrix
<!-- The full kit's tool matrix compressed to ONE table: tool · purpose · build vs buy · phase. D-11 = UNDECIDED → engine-specific rows read "engine-dependent." Integrate D-42's existing tooling rather than proposing a parallel new tool. -->
<!--
| Tool | Purpose | Build vs buy | Phase |
|---|---|---|---|
| … | … | … | … |
-->

## 5.8 Technical Risks
<!-- Engineering-specific risks only (business/schedule risk belongs to 4_Business and LiveOps.md §4.7), phrased so that file's risk register could lift them directly. -->

## Open Decisions
<!-- One bullet per UNDECIDED brief field touched and per GAP placeholder. Format: "- D-xx <field> — UNDECIDED — affects §N.x" or "- G-n — <what is needed> — §N.x". If none: "None." D-11/D-47 = UNDECIDED always appear here per the Depth rule. -->
