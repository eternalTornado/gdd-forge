---
name: concept
description: Start or revise a game's GDD. Turns a pitch into concept.md (pillars, core loop, systems, glossary) and decisions.md, asking at most 4 questions first, then asks the user to approve. Use when the user wants a GDD, a game design document, or to turn a game idea into a design.
argument-hint: "<pitch | path to a pitch file> | --update [<GDD dir>] [<changes>]"
---

# Concept — start a GDD

You run this skill in the main conversation: only you talk to the user. Agents never see the user.

## Resolve once

- `SHARED` = absolute path of `${CLAUDE_SKILL_DIR}/../../shared`.
- Agent `gdd-concept`: use `gdd-forge:gdd-concept` if your agent types list it, else `gdd-concept`. If
  neither is listed, dispatch a general-purpose agent and start its prompt with "Read
  `<abs path of ${CLAUDE_SKILL_DIR}/../../agents/gdd-concept.md>` and act as that agent."
- Every path you put in a dispatch is absolute. Never paste a document's text into a prompt; give its
  path. The pitch and the user's answers are the exception: pass them verbatim.

## New GDD

1. **Pitch.** `$ARGUMENTS` is the pitch, or a path to a file holding it (read it). Empty: ask the user
   for the pitch in one plain sentence and stop until they answer.
2. **Must-ask questions.** Read `SHARED/contracts/concept.md` § Must-ask list. For each of its rows the
   pitch does not settle, ask it — all of them in **one** `AskUserQuestion` call, at most 4 questions,
   with the options the contract lists. Zero questions is fine and common. An answer like "chưa biết" or
   "skip" is recorded as `UNDECIDED`. Ask nothing else.
3. **Folder.** Slug = kebab-case ASCII of the title in the pitch, or of 2–3 key words of the pitch when
   it has none (strip diacritics). `GDD` = `<cwd>/deliverables/<slug>/GDD/`. If `GDD/concept.md` already
   exists, ask whether to update it (`--update` flow) or use another slug.
4. **Dispatch** `gdd-concept` with:
   - `MODE: NEW`
   - Read first: `SHARED/writing-rules.md`, `SHARED/contracts/concept.md`, `SHARED/guidance/concept.md`,
     `SHARED/templates/decisions.md`, `SHARED/templates/concept.md`, `SHARED/data/game-design-patterns.md`.
   - Write: `GDD/decisions.md`, `GDD/concept.md`.
   - Pitch (verbatim) and answers as `D-xx = <value> (user)`.
5. **Check.** Run `python3 SHARED/scripts/gdd_check.py GDD`. If it reports errors, dispatch once more
   with `MODE: UPDATE` and the error lines as the changes; run the check again. Errors that remain are
   shown to the user at the checkpoint.
6. **Checkpoint** (§ below).

## `--update [<GDD dir>] [<changes>]`

Find `GDD`: the given folder, else the only `**/GDD/concept.md` under the current folder (several: ask
which, up to 4 options). No changes given: ask what to change in one plain sentence and stop. Dispatch
`gdd-concept` with `MODE: UPDATE`, the same read-first list, the two file paths and the changes
verbatim. Then step 5 and the checkpoint.

## Checkpoint

Show the user, briefly and in their language:

- The pillars (name · forbids), the core loop in one line, and the systems (name · type · tier).
- Every `decisions.md` row with Source `proposal`, as `D-xx <decision>: <value>` — these are the
  choices the kit made for them.
- Open questions, if any, and any check errors left.

Then one `AskUserQuestion`: "Approve the concept and its proposals?" — options **Approve** and
**Approve, then name the game**; the question text says "To change something, choose Other and type
it." A typed answer is a change request: run the `--update` dispatch with it, check, and come back
here.

On approval, Edit `GDD/decisions.md`: in `## Core`, change Source `proposal` to `user` on every row
(the user has now reviewed them). This is the only edit you make yourself.

## Next step

End with one line, per the README's next-step convention:

- Approved: `**Tiếp theo:** /gdd-forge:system --core` — viết các system của core loop.
- Approved and the user asked to name the game: `**Tiếp theo:** /gdd-forge:name <GDD>`.
- `--update` of an approved concept whose Core values changed and `GDD/systems/` has docs:
  `**Tiếp theo:** /gdd-forge:review` — liệt kê system doc bị ảnh hưởng.
- Stopped waiting for the pitch or for answers: say what you are waiting for instead.
