# Guidance — enemy behavior systems

Enemies, NPCs, opponents: what they do and how the player reads them.

- Start from the player feeling ("outmaneuvered, not cheated"), then design behavior to produce it.
- Each archetype: what it does, how the player reads its intent (tell, telegraph), and how the player beats it (counter-play). An enemy the player cannot learn to beat is a gap, not a difficulty setting.
- Describe behavior as states and triggers an implementer can build ("sees player within 8 m (tunable) → chase; loses sight 3 s (tunable) → return"), not personality prose.
- Keep sophistication proportional to scope: simple patterns for casual games; no learned or adaptive AI unless the user asked for it.
- Archetypes are reused across levels; build a table of archetypes, then let level docs place them.
- Difficulty adaptation must be fair and visible; secretly weakening enemies is a design decision for the user, not a default.
- Competitive multiplayer with no bots stated: do not add bots silently; ask under Open Questions.
- One vocabulary: state names in rules, tables and any diagram must match.
