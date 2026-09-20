Craft guidance — `2_Core Gameplay.md` (lite)

Fix the core verbs and world rules before anything else — every mechanic, tunable and guardrail you write afterward inherits them, so an ambiguous verb here costs you rewrites later, not just once.

Every tunable lives in exactly one table in the whole file — if a number is derived from others (a total, a rate, a percentage), write it as a formula or a note next to the table it depends on, never as a second independent row.

If a cosmetic item, skin or power-up can modify physics or a hitbox, state the guardrail for the worst-case modifier explicitly — a guardrail that only holds for the default loadout isn't a guardrail.

When a must-have needs a mechanism a pillar's forbid clause rules out, that's a defect to escalate as a `structural` GAP — never soften the pillar's wording or the mechanic's behaviour to make the conflict quietly disappear.

State only *that* a player choice exists and *when* it locks — which screen hosts it and where it's stored belong to the files that own them, not to you.

For a generator-driven structure, keep every spawn and generator tunable in one place — don't let a second section quietly restate or re-derive them.

Don't invent monitoring or telemetry targets the brief never asked for.
