---
name: system
description: Write or update one system document of a gdd-forge GDD (combat, economy, progression, UI flow, levels, enemies, narrative, presentation), or every core system with --core. Needs concept.md from /gdd-forge:concept. Use when the user wants to design a game system for their GDD.
argument-hint: "<system name> | --core | --update <system name> [<changes>]  [--gdd <GDD dir>]"
---

# System — design one system

You run this skill in the main conversation: only you talk to the user.

## Resolve once

- `SHARED` = absolute path of `${CLAUDE_SKILL_DIR}/../../shared`.
- Agent `gdd-system`: `gdd-forge:gdd-system` if listed, else `gdd-system`; if neither, a general-purpose
  agent told to read `<abs path of ${CLAUDE_SKILL_DIR}/../../agents/gdd-system.md>` and act as it.
- `GDD`: `--gdd <dir>`, else the only `**/GDD/concept.md` under the current folder (several: ask which;
  none: tell the user to run `/gdd-forge:concept` first and stop).
- Every path in a dispatch is absolute; never paste a document's text into a prompt.

## Steps

1. **Concept approved?** If `GDD/decisions.md` § Core still has a row with Source `proposal`, the concept
   has not been approved. Say so and ask (`AskUserQuestion`): continue anyway, or run
   `/gdd-forge:concept --update` first.
2. **Which systems.** Read `GDD/concept.md` § Systems.
   - `--core`: every row with Tier `core` and Doc `—`, in table order. None left: say the core systems
     are done and go to the next step.
   - `<name>`: the row whose System matches (case-insensitive, or by slug). No match: ask whether to add
     it as a new system (give your proposed Type) or pick one of the closest existing rows.
   - `--update <name> [<changes>]`: that row's doc must exist. No changes given: ask what to change in
     one plain sentence and stop.
3. **For each system, one at a time** (later ones may read earlier ones):
   - `slug` = kebab-case ASCII of the System name (strip diacritics). Doc = `GDD/systems/<slug>.md`.
   - Type = the row's Type; guidance = `SHARED/guidance/<type>.md`.
   - Data = the files `SHARED/data/_index.md` selects for this type, narrowed by each topic's
     `_index.md` and the values in `decisions.md`.
   - Dispatch `gdd-system` with: `MODE: NEW` or `MODE: UPDATE` (+ the changes verbatim); read first
     `SHARED/writing-rules.md`, `SHARED/contracts/system.md`, the guidance file,
     `SHARED/templates/system.md`, `GDD/concept.md`, `GDD/decisions.md`, the data files; the system's
     row (name, type, one line, pillar, tier); the doc path; the list of existing docs in `GDD/systems/`;
     for a new system, "add the row to concept.md § Systems".
   - Run `python3 SHARED/scripts/gdd_check.py GDD --file systems/<slug>.md`. Errors: dispatch once more
     with `MODE: UPDATE` and the error lines; check again. Errors that remain go in your report.
4. **Report** to the user, briefly and in their language, per doc: word count, new decisions the agent
   proposed (`D-1xx <decision>: <value>` — the user should see every choice made for them), open
   questions, remaining check errors.

## Next step

End with one line, per the README's next-step convention:

- One doc written or updated: `**Tiếp theo:** /gdd-forge:review systems/<slug>.md`.
- `--core` wrote several: `**Tiếp theo:** /gdd-forge:review` — kiểm toàn bộ GDD.
- Stopped waiting for the user: say what you are waiting for instead.
