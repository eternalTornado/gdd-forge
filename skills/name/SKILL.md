---
name: name
description: Generate and choose a game name from a pitch or an existing gdd-forge brief. Use when the user asks for game title ideas or a name for their game.
---

# Name — game title generator

`$ARGUMENTS` is either free-text pitch, or a path to an existing gdd-forge `brief.md`.

1. **Resolve input.**
   - If `$ARGUMENTS` is a path to a `brief.md`, read it and use it directly as the namer's input.
   - Otherwise treat `$ARGUMENTS` as pitch text. If it's empty, or missing tone/audience, ask up to
     3 gate questions with `AskUserQuestion` (one call, ≤ 4 questions): pitch (`D-02`, what is the
     game — required if still missing), tone (`D-08`, options per
     [brief-schema.md](../forge/references/brief-schema.md) D-08), audience (`D-05`, options per
     brief-schema.md D-05). Skip any of the three you already have. Do not ask more than these three —
     this skill does not run the full gate.
   - Write a minimal brief-shaped note (pitch + tone + audience, or the loaded `brief.md`) to pass to
     the namer; use absolute paths if writing a scratch file, never paste large text back and forth
     needlessly.

2. **Dispatch.** Call the `Agent` tool with `subagent_type` set to the namer agent as it appears in your available agent types — `gdd-forge:gdd-namer` under a plugin install, `gdd-namer` if the agents were copied to `~/.claude/agents/`, passing the brief/pitch
   (as an absolute file path when one exists, otherwise the pitch text inline since there is no file
   yet). Ask for 8 candidates, each with rationale, a pronounceability note, and a "possible conflicts
   to check" line — the agent cannot verify trademarks and must say so per candidate.

3. **Present.** Ask the user with `AskUserQuestion`: top 4 candidates as options (`label` = name,
   `description` = rationale). "Other" is automatic; free text there becomes the chosen name too.

4. **Output.**
   - Print the chosen name.
   - Print the full list of 8 candidates (name + rationale) so the user has the rest for later.
   - Print the caveat verbatim: this skill cannot check trademark, domain, or store-listing conflicts —
     the user must verify the chosen name independently before committing to it.
   - If a `brief.md` path was given in step 1, write the chosen name into it: `game_name`: `<final name>`,
     `slug`: `<kebab-case, ASCII only>`, in the "Chosen game name" section of
     [brief-template.md](../forge/references/brief-template.md)'s format. Do not touch any other field
     in that file.

## Notes

- This skill never runs the full input gate — only the up-to-3 questions in step 1, at most once.
  For a full GDD, use `/gdd-forge:forge` instead, which includes its own naming wave (W1).
- Only this main agent talks to the user; `gdd-namer` never sees the user and cannot ask questions.
  If it needs more context than the pitch/tone/audience it was given, it still returns 8 candidates
  on a best-effort basis rather than blocking.
