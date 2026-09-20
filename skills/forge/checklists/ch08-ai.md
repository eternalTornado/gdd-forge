# Checklist ch08-ai — Artificial Intelligence
Applies to: 8_Artificial Intelligence.md · Used by: gdd-ai-designer (self-check) and gdd-reviewer.
`[R]` = reviewer-only — depends on a chapter written after this one; at self-check count it as n/a (exclude from passed/total), never as a fail.

## Architecture & Intent
- [ ] AI-01 AI Goals & Player Experience Intent (§8.1) states what the AI must make the player feel, not just what it does
- [ ] AI-02 AI Architecture (§8.2) names a specific approach (FSM / BT / utility / GOAP) with a stated rationale
- [ ] AI-03 The chosen architecture is bounded by D-34 (ai_ambition); it does not exceed or ignore that target

## Archetypes & Behaviour
- [ ] AI-04 Enemy/Opponent archetype table (§8.3) has role, behaviour summary, perception, attack/decision pattern, counter-play, and tunables filled for every row
- [ ] AI-05 Every enemy/opponent archetype states an explicit counter-play the player can use
- [ ] AI-06 NPC & Companion AI (§8.4) is present and distinct from the Enemy/Opponent section
- [ ] AI-07 Director/Procedural Systems (§8.5) is present only if D-22 includes it

## Perception & Movement
- [ ] AI-08 Perception & Awareness Model (§8.6) is defined once and referenced by name in the archetype table, not redefined per archetype
- [ ] AI-09 Navigation & Movement (§8.7) states how agents traverse the level types defined in ch6

## Difficulty & Tuning
- [ ] AI-10 Difficulty Adaptation & Fairness rules (§8.8) state the adaptation mechanism and why it is fair to the player (no silent rubber-banding presented as neutral)
- [ ] AI-11 Tunable Parameters table (§8.9) is complete and every parameter is tagged "(tunable)"

## Tooling & Performance
- [ ] AI-12 Debug & Tooling needs (§8.10) name concrete tools (e.g. behaviour visualisers, perception gizmos), not a generic "debug tools needed"
- [ ] AI-13 Performance envelope requests (§8.11) are qualitative asks (e.g. "many concurrent agents") with no invented numeric benchmark

## N/A Handling
- [ ] AI-14 If D-22 = None, §8.1 explains why there is no designed AI (plus any trivial automated behaviour), and every §8.2–§8.11 heading is present followed only by the one-line N/A statement — no heading deleted
- [ ] AI-15 If D-20 is competitive-only with no bots, the absence of bots is flagged as an Open Decision, not silently omitted

## Anti-fabrication
- [ ] AI-16 No AI sophistication (e.g. machine-learned/adaptive behaviour) is claimed beyond what D-34 specifies
- [ ] AI-17 No performance number (agent count, frame budget) is asserted as fact instead of a qualitative request

## Consistency rules
- [ ] AI-18 [Rule 1] AI terminology matches the Glossary in ch3 §3.10
- [ ] AI-19 [Rule 7] No AI decision states a platform or scale value absent from D-04/D-32
