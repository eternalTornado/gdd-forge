<!-- gdd-forge knowledge base index · skills/forge/data/casual/ · reference only -->

# data/casual/ — Index

This directory holds knowledge files specific to the casual/hyper-casual **lite profile** (see `references/profile-casual.md`). It is additional to, not a replacement for, the top-level `skills/forge/data/` files — a lite-profile agent may still be given `data/game-design-patterns.md` or slices from `data/monetization/`, `data/platforms/` and `data/accessibility/` where its contract calls for them (see each `references/contracts-lite/lite-N.md`).

## Files

| File | Contents | Selector rule |
|---|---|---|
| `metrics-definitions.md` | Definitions (no targets) for the casual acquisition/retention/monetisation funnel: CPI, IPM, CTR, CVR, D1/D7/D30, session length, sessions/day, playtime, ARPDAU, ARPU, LTV, ad ARPDAU, eCPM, fill rate, attach rate, rewarded-video engagement rate. | Given only to `gdd-producer` when dispatched for `4_Business and LiveOps.md` (contract `lite-4.md`), specifically for §4.4 KPI Definitions & Targets. No other lite dispatch reads it — `1_Concept.md`, `2_Core Gameplay.md`, `3_UX Art and Audio.md`, and `5_Tech Note.md` have no KPI-definition content in their contracts. |

## Selector rule (general)

A dispatch reads a file under `data/casual/` if and only if its own `references/contracts-lite/lite-N.md` names that file under **data** — the same rule the full profile uses for `skills/forge/data/`. Do not hand an agent a `data/casual/` file "for context" outside its contract; an unused data file in the prompt is an invitation to cite facts the chapter contract never asked for. If this directory gains a second file in a future revision, add its own row above rather than folding it into the `metrics-definitions.md` row.
