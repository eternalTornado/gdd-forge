# Contract — systems/<slug>.md

Owner: `gdd-system`. Read `shared/writing-rules.md` first.

## Inputs

- `concept.md` and `decisions.md` (whole; both are short).
- The system's row in `concept.md` § Systems.
- System docs this one interacts with, if they exist (whole).
- The guidance file for the system type (below).
- Data slices the skill selected via the selectors in the kit's `data/*/_index.md`, if any.
- Template: `shared/templates/system.md`.

## System types and guidance

The skill picks one type per system and passes its guidance file.

| Type | Covers |
| --- | --- |
| mechanics | Core verbs, controls, physics, combat, puzzles |
| progression | Unlocks, levels, power or skill growth, meta loop |
| economy | Currencies, sources and sinks, monetization mechanisms, store |
| level | Level or world structure, pacing, difficulty curve, procedural rules |
| enemy-behavior | Enemies, NPCs, opponents: what they do and how the player reads them |
| ui-flow | Screens, navigation, HUD, onboarding |
| narrative | Story, setting, characters, how story is delivered |
| presentation | Art and audio direction, game feel, asset list |

## Output

Budget: **≤ 1,200 words** per system. A simple system should land well under.

Required headings, in order: `Purpose`, `Rules`, `Player-Observable Behaviors`, `Open Questions`.
Optional, in template order: `Tunables`, `States and Edge Cases`, `Content`, `UI Touchpoints`,
`Interactions`.

Rules:

1. **Purpose** names the pillar(s) it serves. A rule that serves no pillar is cut or raised as an
   Open Question.
2. **Pillar Forbids hold.** Nothing in the doc does what a pillar forbids or what D-44 excludes.
3. **Tunables are owned here.** Every tunable of this system lives in this doc's table and nowhere
   else. Another system's value is a `→` reference.
4. **Monetization** uses only mechanisms in D-30 and respects D-31. A new mechanism is a `decisions.md`
   proposal row, never a silent addition.
5. **Player-Observable Behaviors:** 3–10 lines, each "When <situation>, <what the player sees or can
   do>." Observable in play, no internals.
6. **New decisions** go to `decisions.md` § Design as `proposal` rows; **new terms** go to the
   `concept.md` glossary (`writing-rules.md` §1, §2.4).
7. After writing, set this system's Doc cell in `concept.md` § Systems to `systems/<slug>.md`.

## Update mode

`--update` with the items to change: edit in place per `writing-rules.md` §3. If a change alters a
value another system doc references, list that doc under Open Questions so the review picks it up;
never edit another system's doc.
