# Guidance — mechanics systems

Core verbs, controls, physics, combat, puzzles.

- Fix the verbs and world rules first; every rule after them inherits them, so an ambiguous verb costs rewrites later.
- Write rules an implementer could turn into pseudocode: "the dash consumes 1 stamina and grants 6 frames of invulnerability" beats "the dash feels powerful".
- Rules are short declaratives of what is always true ("falling below 3 m deals no damage", "time pauses in menus").
- Every tunable lives in this doc's Tunables table once. A derived value is a formula in the Note column, never a second row.
- States and Edge Cases is where implementers get stuck: cover interrupted actions, simultaneous inputs, zero and max values, death mid-action.
- Separate skill challenge from knowledge puzzles; mixing them makes difficulty incoherent.
- If a cosmetic or upgrade can change physics or a hitbox, state the guardrail for the worst-case modifier, not just the default.
- Controls: one input map per platform in D-04; no gamepad scheme for a mobile-only game.
- Multiplayer rules only if D-20 is not single-player, and then state fairness (matchmaking basis, comeback mechanics) explicitly.
- No balance numbers borrowed from other games unless a data file you were given states them.
