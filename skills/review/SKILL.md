---
name: review
description: Check a gdd-forge GDD or one document of it. Runs gdd_check.py, then an independent reviewer, and lists documents affected by changed decisions. Read-only. Use when the user asks to check, review, audit or QA their GDD.
argument-hint: "[<document path>] [--gdd <GDD dir>]"
---

# Review — check a GDD

You run this skill in the main conversation. It never edits documents.

## Resolve once

- `SHARED` = absolute path of `${CLAUDE_SKILL_DIR}/../../shared`.
- Agent `gdd-reviewer`: `gdd-forge:gdd-reviewer` if listed, else `gdd-reviewer`; if neither, a
  general-purpose agent told to read `<abs path of ${CLAUDE_SKILL_DIR}/../../agents/gdd-reviewer.md>`
  and act as it.
- `GDD`: `--gdd <dir>`; else the folder of the given document (for `systems/x.md`, its parent's parent);
  else the only `**/GDD/concept.md` under the current folder (several: ask which). A folder without
  `concept.md` and `decisions.md` is not a gdd-forge GDD: say so and stop.

## Steps

1. **Script.** Run `python3 SHARED/scripts/gdd_check.py GDD --changed`, adding `--file <rel path>` when
   one document was given. Keep the full output.
2. **Reviewer.** Dispatch `gdd-reviewer` with: read first `SHARED/writing-rules.md`, the checklist(s) —
   `SHARED/checklists/concept.md` when reviewing `concept.md`/`decisions.md` or the whole GDD,
   `SHARED/checklists/system.md` when reviewing any system doc; `GDD/concept.md`, `GDD/decisions.md`;
   the documents under review (the one given, or `concept.md` plus every `systems/*.md`); the script
   output verbatim.
3. **Report** to the user, in their language:
   - Script errors first, then warnings (group by file; skip the `words:` line unless a doc is over).
   - Reviewer findings by file, as returned (severity · § · what · fix).
   - `changed:` lines: decisions changed since the last commit and the documents they affect.
   - Open questions still listed in the reviewed documents.

## Next step

End with one line, choosing the first case that applies (README's next-step convention):

| Result | Next |
| --- | --- |
| Script errors | `/gdd-forge:system --update <name> "<the errors>"` (or `/gdd-forge:concept --update` for concept/decisions), then `/gdd-forge:review <file>` |
| `high` findings | `/gdd-forge:system --update <name> "<the findings>"`, then `/gdd-forge:review <file>` |
| Changed decisions affect system docs | `/gdd-forge:system --update <name> "<D-xx changed to …>"` for each listed doc |
| Clean, open questions remain | The user answers them, then `/gdd-forge:system --update <name> "<answers>"` |
| Clean, a system in concept § Systems has Doc `—` | `/gdd-forge:system <next system, core tier first>` |
| Clean, every system has a doc | "GDD xong ở tier hiện tại." |
