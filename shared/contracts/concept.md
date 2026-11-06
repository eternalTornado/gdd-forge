# Contract — concept.md + decisions.md

Owner: `gdd-concept`. Read `shared/writing-rules.md` first.

## Inputs

- The pitch (user text) or a brief file the user gave.
- The answers to the must-ask questions below, if the skill asked any.
- Data slices the skill selected via the selectors in the kit's `data/*/_index.md`, if any.
- Templates: `shared/templates/decisions.md`, `shared/templates/concept.md`.

## Must-ask list (the skill asks these, never the agent)

Before dispatching, the skill fills every Core row it can from the pitch, then asks the user **only**
the rows below that the pitch does not settle. Zero questions is the goal; four is the maximum, in one
`AskUserQuestion` call.

| ID | Ask when | Options to offer (Other is added automatically) | Why it is asked, not proposed |
| --- | --- | --- | --- |
| D-04 Platforms (multi) | the pitch names no platform | iOS + Android · PC (Steam) · Console · Web | Changes controls, session shape and UI everywhere. |
| D-06 Business model | the pitch names none | Premium · F2P + IAP · F2P + Ads · Hybrid (ads + IAP) | Changes economy, progression and UI everywhere. |
| D-20 Multiplayer | the pitch does not make it clear | Single-player · Local co-op/versus · Online co-op · Online competitive | Changes almost every system. |
| D-09 Scope | the pitch gives no hint of session length or content size | Micro (<5 min, replay-driven) · Small (5–15 min) · Medium (15–45 min) · Large (45+ min) | Sizes every system. |

Everything else is proposed. The user sees every proposal when reviewing `decisions.md`.

## Output 1 — decisions.md

- Fill every Core row from the template. Source `user` for what the pitch or the answers state;
  `proposal` for what you chose. Quote the user's words for `user` values; do not reinterpret them.
- Drop rows that do not apply (D-30/D-31 for a Premium game); never write N/A.
- `Affects`: fill for rows `concept.md` uses.
- `## Design` starts as "None yet."
- When the user approves the concept, the skill changes the reviewed Core rows from `proposal` to
  `user`. You never do that yourself.

## Output 2 — concept.md

Budget: **≤ 1,000 words**, counted like `wc -w` on the file. A hyper-casual game should land near 500.

Required headings, in order: `Pitch`, `Pillars`, `Core Loop`, `Target`, `Experience`, `Out of Scope`,
`Systems`, `Glossary`, `Open Questions`. Optional: `References` (only if D-13 names games).

Rules:

1. **Pillars:** 3–5. Each has a Forbids cell that rules something out. A pillar that forbids nothing is
   not a pillar.
2. **Core Loop:** numbered steps, each a player verb. No system internals.
3. **Target:** restates D-04, D-05, D-06, D-09 exactly as in `decisions.md`.
4. **Systems:** every system the game needs, each tied to one pillar and one Type from the system
   contract's type list. Tier `core` only for what the core loop cannot run without; everything else
   `later`. Doc column `—` until a system doc exists. A hyper-casual game usually has 2–4 systems.
5. **Glossary:** 5–15 terms the systems will reuse.
6. **Open Questions:** at most 3, each with your recommended answer.

## Update mode

`--update` with user feedback: edit both files in place per `writing-rules.md` §3. A changed Core
value updates every `concept.md` line that restates it. Never touch `systems/`; the review lists
system docs that the change affects.
