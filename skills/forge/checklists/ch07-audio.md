# Checklist ch07-audio — Audio Direction
Applies to: 7_Interface.md · Used by: gdd-ux-designer (self-check) and gdd-reviewer.
`[R]` = reviewer-only — depends on a chapter written after this one; at self-check count it as n/a (exclude from passed/total), never as a fail.

## Direction & Style
- [ ] AU-01 Audio Direction (§7.7) states a music style consistent with D-07/D-08 tone
- [ ] AU-02 Adaptive music layers, if claimed, state the trigger condition (state, intensity, or event)
- [ ] AU-03 SFX categories are listed and mapped to at least one gameplay system from ch4

## Voice & Delivery
- [ ] AU-04 VO/dialogue delivery approach (cutscene / barks / codex / none) is stated and matches ch5 §5.8
- [ ] AU-05 Mix priorities state which audio category takes precedence during conflicts (e.g. VO over ambience)

## Platform & Accessibility
- [ ] AU-06 Platform audio profiles are stated only for platforms present in D-04
- [ ] AU-07 Audio accessibility features (subtitles, visual cues for sound) are cross-referenced with §7.9, not restated independently
- [ ] AU-08 Audio localisation needs are stated for languages present in D-38
- [ ] AU-15 Audio cues intended to support accessibility (e.g. footstep direction, danger stingers) are named specifically, not left as a generic "audio feedback" statement

## Asset Inventory
- [ ] AU-09 UI & Audio Asset Inventory (§7.11) includes BGM/SFX/VO/UI/ambience categories where applicable
- [ ] AU-10 Every audio asset row follows the naming pattern stated in the same table

## Anti-fabrication
- [ ] AU-11 No audio technology (e.g. 3D/spatial audio, surround) is claimed for a platform that does not support it per D-04 and the `data/platforms/` slice it was given
- [ ] AU-12 No audio performance number (file size, voice count) is stated without an "(est.)" or "(target)" tag

## Consistency rules
- [ ] AU-13 [Rule 5] Audio asset rows follow the naming convention defined in §7.11 of this chapter
- [ ] AU-14 [Rule 7] No audio decision (VO language, platform profile) appears that is absent from brief.md
