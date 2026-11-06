---
name: name
description: Generate and choose a game title from a pitch or a gdd-forge GDD folder. Use when the user asks for game title ideas or a name for their game.
argument-hint: "<pitch | GDD dir>"
---

# Name — game title

1. **Input.** `$ARGUMENTS` is a GDD folder (holding `decisions.md`) or pitch text. Pitch text missing
   tone or audience: ask at most those two in one `AskUserQuestion` call. Empty: ask for the pitch in
   one plain sentence and stop.
2. **Dispatch** `gdd-forge:gdd-namer` (or `gdd-namer`; if neither is listed, a general-purpose agent
   told to read `<abs path of ${CLAUDE_SKILL_DIR}/../../agents/gdd-namer.md>` and act as it) with the
   folder's absolute path, or the pitch, tone and audience verbatim. Ask for 8 ranked candidates.
3. **Choose.** `AskUserQuestion` with the top 4 (`label` = name, `description` = rationale); Other lets
   the user type any name.
4. **Output.** Print the chosen name, the full list of 8, and this caveat: the kit cannot check
   trademark, domain or store-listing conflicts; verify the name before committing to it.
5. **Write** (GDD folder only): in `decisions.md` set D-01's Value to the chosen name and Source to
   `user`; replace the title in the first line of `concept.md` (`# <name> — Concept`). Touch nothing
   else. The folder keeps its slug; say so if the slug no longer matches.

**Tiếp theo:** quay lại bước đang dở — thường là `/gdd-forge:system --core` nếu concept vừa được duyệt.
