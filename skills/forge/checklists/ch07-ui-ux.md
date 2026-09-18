# Checklist ch07-ui-ux — Interface, UX & Accessibility
Applies to: 7_Interface.md · Used by: gdd-ux-designer (self-check) and gdd-reviewer.

## Structure & Flow
- [ ] UI-01 UX Principles (§7.1) are 3–5 items, each derived from a pillar in ch3 §3.2
- [ ] UI-02 Information Architecture & Screen Flow (§7.2) is a mermaid state diagram
- [ ] UI-03 Screen Inventory (§7.3) table has purpose, entry/exit, key elements, and notes filled for every screen
- [ ] UI-04 Screen Inventory includes lobby/matchmaking/social screens when D-20 ≠ None
- [ ] UI-05 HUD & In-game Visual System (§7.4) states what information is always visible vs contextual

## Controls & Feedback
- [ ] UI-06 Control System (§7.5) lists one input map per platform listed in D-04
- [ ] UI-07 Control System states which inputs are remappable, consistent with D-39
- [ ] UI-08 Camera & Feedback (§7.6) names distinct feedback channels for hit/success/failure

## Accessibility
- [ ] UI-09 Every accessibility commitment in D-39 is mapped to at least one concrete feature in §7.9
- [ ] UI-10 If D-39 = None specified, §7.9 lists baseline-only support and flags it as an Open Decision
- [ ] UI-11 Colour-blind support, when committed, cites a specific mechanism (palette, pattern, or setting), not just the word "supported"
- [ ] UI-12 Text scaling or resizing claims state a target consistent with WCAG 2.1 AA guidance (from the `data/accessibility/` slice you were given) when cited
- [ ] UI-13 Subtitle/caption commitments state what content they cover (dialogue, SFX cues, or both)

## Localisation
- [ ] UI-14 Localisation Considerations (§7.10) name the specific D-38 target languages
- [ ] UI-15 Text expansion/contraction handling is stated for UI layout, not assumed
- [ ] UI-16 Font and character-set needs are stated only for languages present in D-38/D-12

## Asset Inventory
- [ ] UI-17 UI & Audio Asset Inventory (§7.11) table states a naming pattern and every row follows it

## Anti-fabrication
- [ ] UI-18 No accessibility feature is claimed that is not tied to a D-39 commitment or flagged as an Open Decision
- [ ] UI-19 No platform control scheme is described for a platform absent from D-04
- [ ] UI-20 No accessibility standard is cited without naming the source document

## Consistency rules
- [ ] UI-21 [Rule 5] Asset Inventory (§7.11) uses the naming convention from ch10 §10.8
- [ ] UI-22 [Rule 1] UI terminology matches the Glossary in ch3 §3.10
