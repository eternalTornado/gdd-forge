<!-- gdd-forge template · 09-technical.md · contract: references/contracts/ch09.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 9. Technical

<!-- 2–3 lines: engineering-facing specification — stack, architecture, data, performance and pipeline decisions everything else in the GDD assumes are buildable. -->

## 9.1 Target Platforms & Hardware Floor
<!-- guidance: D-04 platform list · minimum device/browser target from D-37 (or "UNDECIDED" verbatim if so). -->

## 9.2 Engine & Language Stack
<!-- CONDITIONAL: only if D-11 = UNDECIDED, replace this section's body with a comparison table of 2–3 candidate engines against the requirements below — no pick is made. Otherwise state D-11 directly with one paragraph of rationale. -->
<!--
| Candidate | Fit to D-03/D-04 | Team familiarity (D-42) | Licensing | Risk |
|---|---|---|---|---|
| … | … | … | … | … |
-->

## 9.3 System Architecture
<!-- guidance: core systems list with responsibilities (rendering, physics, audio, input, save, networking if applicable). DEPTH RULE: if D-11 = UNDECIDED, keep this section engine-agnostic (responsibilities, not engine-specific subsystem names). -->
```mermaid
```
<!-- diagram type: mermaid component diagram of core systems and their dependencies -->

## 9.4 Data Architecture
<!-- guidance: save system (format, location, versioning/migration strategy) · config system · content data formats. ELABORATION: format choices; DECISION: security/compliance constraints only from D-40. -->

## 9.5 Asset Pipeline & Media Profiles
<!-- guidance: import rules and compression per platform (D-04), naming convention inherited from ch 7 §7.11 (as extended by ch 10 §10.8) — do not invent a separate naming scheme. -->

## 9.6 Networking
<!-- CONDITIONAL: only if D-20 ≠ None. Otherwise write the single line: "Not applicable — single-player only (D-20)." -->
<!-- guidance: topology (client-server/P2P), authority model, sync/prediction strategy, anti-cheat stance, scale target per D-32. -->

## 9.7 Performance Budgets
<!-- guidance: frame time, memory, load time, download size — every figure marked (target), meaning "to validate," never presented as a measured benchmark. No fabricated numbers without a source in the `data/platforms/` slice you were given or the brief. -->
<!--
| Metric | Target | Platform | Source |
|---|---|---|---|
| Frame time | … (target) | … | data/platforms/ |
-->

## 9.8 Platform Compliance & Certification
<!-- guidance: D-40 requirements restated in technical terms — what engineering must implement to pass certification (save data handling, privacy consent flows, rating-appropriate content gates). -->

## 9.9 Build, CI & Release Pipeline
<!-- guidance: existing tooling from D-42, build automation, release cadence tied to D-42/platform requirements. If D-42 = none, say the pipeline starts from scratch and flag as scope risk in §9.10. -->

## 9.10 Technical Risks & Spikes
<!-- guidance: risks specific to engineering (not business/schedule risk — that's ch 12 §12.5) and any prototype spikes needed to de-risk them before production. -->
<!--
| Risk | Area | Likelihood | Impact | Spike / mitigation |
|---|---|---|---|---|
| … | … | … | … | … |
-->

## Open Decisions
<!-- One bullet per UNDECIDED brief field touched and per GAP placeholder in this chapter. Format: "- D-xx <field> — UNDECIDED — affects §N.x" or "- G-9-<n> — <what is needed> — §N.x". If none: "None." D-11 = UNDECIDED must always appear here per the Depth rule. -->

<!-- New terms (only if you introduced a term not in 3_Game Overview §3.10): -->
