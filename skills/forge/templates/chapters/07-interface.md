<!-- gdd-forge template · 07-interface.md · contract: references/contracts/ch07.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 7. Interface

<!-- 2–3 lines: everything the player sees, hears and touches to operate the game — screens, controls, camera, audio direction, accessibility. Read by UX/UI implementers and audio designers. -->

## 7.1 UX Principles
<!-- guidance: 3–5 principles derived directly from ch 3 §3.2 pillars — each principle should be traceable to a named pillar. -->

## 7.2 Information Architecture & Screen Flow
<!-- guidance: how screens connect and gate one another. -->
```mermaid
```
<!-- diagram type: mermaid state diagram (stateDiagram-v2) of screen flow -->

## 7.3 Screen Inventory
<!-- guidance: every screen in the game. DEPTH RULE: if D-20 ≠ None, add lobby/matchmaking/social screens to this table. -->
<!--
| Screen | Purpose | Entry/Exit | Key elements | Notes |
|---|---|---|---|---|
| Main Menu | … | … | … | … |
-->

## 7.4 HUD & In-game Visual System
<!-- guidance: persistent on-screen elements during play — health/resource readouts, minimap, objective markers. Tie each to a mechanic from ch 4 §4.4 it surfaces. -->

## 7.5 Control System
<!-- guidance: one input map per platform in D-04, plus remapping support per D-39. Table or per-platform list. -->
<!--
| Action | PC (KB/M) | Gamepad | Touch |
|---|---|---|---|
| … | … | … | … |
-->

## 7.6 Camera & Feedback
<!-- guidance: camera model (fixed/follow/free/first-person, per D-03 genre) · feedback channels for hit/success/failure (screen shake, colour flash, haptics, audio sting). -->

## 7.7 Audio Direction
<!-- guidance: music style & adaptive layers · SFX categories · VO/dialogue delivery (ties to ch 5 §5.8) · mix priorities · platform audio profiles per D-04. ELABORATION: style and layering; DECISION: none invented beyond D-07/D-08 tone. -->

## 7.8 Help, Tutorialisation & Onboarding UI
<!-- guidance: how the tutorial in ch 6 §6.3 is surfaced in UI — hint prompts, contextual help, replayable tutorial access. -->

## 7.9 Accessibility
<!-- guidance: map each D-39 commitment to a concrete, buildable feature, using the `data/accessibility/` slice you were given for the standard it satisfies. DEPTH RULE: if D-39 = "None specified", list baseline-only support (platform defaults) and flag the absence of commitments as an Open Decision rather than inventing features. -->
<!--
| D-39 commitment | Concrete feature | Standard reference |
|---|---|---|
| … | … | … |
-->

## 7.10 Localisation Considerations
<!-- guidance: text expansion allowance, font support, RTL handling if any target in D-38 requires it, and how D-38's language list maps to UI string budget. -->

## 7.11 UI & Audio Asset Inventory
<!-- guidance: naming pattern must match ch 10 §10.8's convention (consistency rule #5) — do not invent a separate scheme. Feeds ch 13 §C. -->
<!--
| ID | Asset | Type | Naming pattern | Priority |
|---|---|---|---|---|
| … | … | UI / Audio | … | … |
-->

## Open Decisions
<!-- One bullet per UNDECIDED brief field touched and per GAP placeholder in this chapter. Format: "- D-xx <field> — UNDECIDED — affects §N.x" or "- G-n — <what is needed> — §N.x". If none: "None." D-39 = "None specified" must always appear here per the Depth rule. -->

<!-- New terms (only if you introduced a term not in 3_Game Overview §3.10): -->
