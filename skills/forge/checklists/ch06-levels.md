# Checklist ch06-levels — Level Design Quality
Applies to: 6_Levels.md · Used by: gdd-level-designer (self-check) and gdd-reviewer.
`[R]` = reviewer-only — depends on a chapter written after this one; at self-check count it as n/a (exclude from passed/total), never as a fail.

## Structure & Philosophy
- [ ] LV-01 Level Design Philosophy (§6.1) states how the pillars (ch3 §3.2) show up spatially
- [ ] LV-02 Structure Map (§6.2) is a mermaid diagram reflecting the D-23 level structure
- [ ] LV-03 Tutorial/Onboarding Level (§6.3) states the mechanic introduction order and ties it to ch4 §4.4

## Level Entries
- [ ] LV-04 Every level/zone entry states a clear objective
- [ ] LV-05 Every level/zone entry names the core mechanic(s) it introduces or tests, each of which exists in ch4 §4.4
- [ ] LV-06 Every level/zone entry ties its narrative beat to a beat in ch5 §5.5 (when D-21 ≠ None)
- [ ] LV-07 Every level/zone entry states target duration tagged "(est.)"
- [ ] LV-08 Every level/zone entry states a difficulty tier consistent with the Difficulty & Pacing Curve (§6.5)
- [ ] LV-09 [R] Every level/zone entry lists asset needs that reappear in ch10 §10.9 or ch7 §7.11
- [ ] LV-10 Difficulty & Pacing Curve (§6.5) is a table spanning the full level list, not prose

## Scale Compliance
- [ ] LV-11 If ch3 §3.9's level count is > 20, full entries exist for the first 5 plus one per act, and the remainder appear as table rows only
- [ ] LV-12 If D-23 = Single persistent space, §6.4 uses zone entries instead of level entries
- [ ] LV-13 Procedural Rules (§6.6) are present only if D-23 ∈ {Procedural, Endless}, and state the authored-vs-generated share from D-35

## Level List
- [ ] LV-14 Level List table (§6.7) has id, name, act, duration, tier, and status columns filled for every row

## Anti-fabrication
- [ ] LV-15 No level names a platform-specific constraint not present in D-04
- [ ] LV-16 No procedural generation claim is made when D-23 does not trigger it

## Consistency rules
- [ ] LV-17 [Rule 3] Every level in §6.7 references mechanics that exist in ch4 §4.4
- [ ] LV-18 [Rule 5] Asset needs in §6.4 are category names only — no asset IDs and no naming pattern invented here (naming is defined in ch7 §7.11)
