<!-- gdd-forge lite template · 5-tech-note.md · contract: contracts-lite/lite-5.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 5. Tech Note

<!-- 2–3 lines: engine, device floor, architecture, storage, performance/build-size targets, SDK list, technical risks. Reads 1_Concept.md and 2_Core Gameplay.md whole. -->

## 5.1 Platform & Device Floor
<!-- D-04 platform list · minimum device/browser target from D-37 (or "UNDECIDED" verbatim). -->

## 5.2 Engine & Stack
<!-- D-11 = UNDECIDED → comparison table of 2–3 candidates, no pick made. Else state D-11 + one paragraph rationale. List existing tooling (D-42) once, here. -->
<!--
| Candidate | Fit | Licensing | Risk |
|---|---|---|---|
| … | … | … | … |
-->

## 5.3 Architecture & Data
<!-- Core systems list (from 2_Core Gameplay.md §2.3/§2.5 — no parallel inventions). A storage table for every persisted value files 1–2 name; one statement per data decision. One line: asset naming follows 3_UX Art and Audio.md §3.7. -->
<!--
| Value | Stored where | Written when | Trusted by |
|---|---|---|---|
| … | … | … | … |
-->

## 5.4 Performance & Build-Size Budgets
<!-- Frame time, memory, load time, download size — every figure tagged (target). Download size cites D-47, or flagged in Open Decisions with no number given. -->
<!--
| Metric | Target | Source |
|---|---|---|
| Download size | … (target, D-47) | … |
-->

## 5.5 SDK List
<!-- One row per SDK category the design actually needs (ads/IAP/backend/analytics/attribution per brief triggers — see contract). Product from D-46/D-42; else recommend one tagged (proposal) with alternatives in Open Decisions. -->
<!--
| Category | Product | Notes |
|---|---|---|
| Ad mediation | … (proposal) | D-46 |
-->

## 5.6 Compliance
<!-- D-40 requirements restated in technical terms. -->

## 5.7 Technical Risks
<!-- Engineering-only risks (business/schedule risk belongs to 4_Business and LiveOps.md §4.7), phrased so that register could lift them directly. -->

## Open Decisions
<!-- One bullet per UNDECIDED field, GAP, (proposal). None → "None." D-11/D-47 = UNDECIDED always appear. -->
<!-- ## New Terms — add only if this file introduces a term the glossary (1_Concept.md §1.9) doesn't already cover. -->
