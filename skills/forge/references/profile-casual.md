# profile-casual.md — the lite pipeline for casual / hyper-casual mobile games

This is the counterpart to `pipeline.md` for `--profile casual` (synonym: `--profile lite`) and its
sub-profile shortcut `--profile hyper-casual`. **When one of these flags is active, the orchestrator
follows this document end to end and does not also follow `pipeline.md`'s W0–W10** — this file defines
its own W0–W4, its own dispatch envelope, its own GAP handling, and its own Done/Resume/re-run
instructions, so nothing here assumes the reader has `pipeline.md` open at the same time. The two
files share only what is genuinely shared: `brief-schema.md` (still the single source of truth for
every `D-xx` field), the underlying agents in `agents/`, and the kit's non-negotiables (below).

```
--profile casual            entry point (synonym: --profile lite)
--profile hyper-casual      entry point, pre-selects the hyper-casual sub-profile (skips the sub-profile question)
--profile casual --file N   re-run a single lite output file, N ∈ {1,2,3,4,5} — see § Single-file re-run
--profile casual --resume <OUT dir>   resume an interrupted lite run — see § Resume
```

## What this profile is for

A casual or hyper-casual mobile game (endless runner, match-3, idle tap, physics puzzle, arcade
score-chaser) does not need 13 chapters or the full flow's dozen-plus subagent dispatches (`pipeline.md`
§ Wave order and parallelism) to reach a build-ready design document. It has no real narrative, no AI
worth a dedicated architecture chapter,
usually no multiplayer, and its business model lives almost entirely in ad placement and a thin IAP
layer rather than a deep economy. This profile produces **5 content files + 1 assembled index, in 4
waves, at 6 subagent dispatches**, by reusing the exact same agents as the full flow under different,
compressed contracts (`references/contracts-lite/`).

## When NOT to use this profile — escalate to the full flow instead

Switch to (or restart under) the default full profile — `/gdd-forge:forge` with no `--profile` flag —
when any of these is true, because the lite contracts explicitly do not cover them:

- **Real narrative** — `D-21` resolves above `Light framing` (a cast, an arc, world lore beyond a
  one-paragraph setting). `1_Concept.md` §1.8 only ever holds a thin setting/theme paragraph; it is not
  a substitute for `5_Story, Setting and Character.md`.
- **Real AI** — `D-22`/`D-34` imply anything beyond simple obstacle/spawn patterns: perception models,
  navmesh, behaviour trees, utility/GOAP, adaptive or learned behaviour. `2_Core Gameplay.md` §2.5 is
  contractually forbidden from describing any of that (see `contracts-lite/lite-2.md`) — if the pitch
  needs it, this profile cannot honestly produce it, and the owning agent will raise this as a GAP that
  reads "escalate to the full profile," not attempt to write around the gap.
- **Multiplayer** — `D-20 ≠ None`. The lite contracts have no networking/matchmaking section at all;
  `5_Tech Note.md` has no §9.6 counterpart.
- **Console or PC as a primary platform** — `D-04` is dominated by PlayStation/Xbox/Switch/PC rather
  than mobile. The lite profile's business model (§4.2 ad placement, §4.3 IAP) and tech note (§5.4
  build-size budgets, §5.5 mobile SDK list) assume a mobile-first, ads-plus-light-IAP title.
- **`D-09` resolves to Medium/Large/service scope** with deep meta-progression — the lite profile's
  §2.1/§2.9 assume a small enough feature set that 6–10 features and 2–5 mechanics are not a
  compression, they're the actual size of the game.

If the gate is already mid-flight and one of these surfaces (e.g. the user's pitch turns out to want a
branching story), stop, tell the user plainly which trigger fired, and offer to restart under the full
profile — do not keep patching lite contracts to cover ground they were not designed to cover.

## Two sub-profiles: hyper-casual vs casual

Both use the same 6 files and the same 4 waves. They differ only in the gate preset and in how much each
lite file leans into meta-progression, framing, and IAP breadth. The preset itself — session length,
business model, narrative depth, obstacles, level structure, LiveOps, monetisation mix — lives in
`brief-schema.md` § Casual Profile Preset; do not duplicate those values here.

| | Hyper-casual | Casual |
|---|---|---|
| `1_Concept.md` §1.5 feature set | Leans toward 6 features | Can use the full 6–10 |
| `2_Core Gameplay.md` §2.2 meta-progression tier | Almost never present | Sometimes one light tier |

The user picks a sub-profile at the top of W0 (or it is pre-selected by `--profile hyper-casual`); the
choice determines which preset column the gate proposes. Nothing else in the pipeline branches on it —
every contract, template and checklist in this document already covers both.

## Non-negotiables (inherited, restated here for self-sufficiency)

Unchanged from the full flow — this profile does not relax any of them:

- Only the orchestrator talks to the user. Subagents never see the user and cannot call `AskUserQuestion`.
- Decisions (`D-xx`) come only from the user's words or explicit `UNDECIDED`. Never invented, defaulted,
  or inferred — the casual gate preset (below) is a *proposal*, not an invention, precisely because it
  requires explicit user confirmation before a single value reaches `brief.md`.
- Reversible, local choices the brief doesn't make are written by agents as tagged `(proposal)`s, listed
  under Open Decisions with 1–2 alternatives (`dispatch-rules.md` §1) — never silently, never for a
  `D-xx` field.
- Subagents report **GAPs** instead of deciding; the orchestrator asks on the user's behalf and resolves
  by class (§ GAP handling, below).
- Pass **absolute paths** to every subagent for every input and output.
- Never paste file bodies into a subagent prompt — give a path (§ Wave table: `brief.md` alone for W1,
  whole upstream lite files for W2–W4 — never a slice) and let the subagent read it.
- Chapter bodies are written in `D-12`; headings keep the English numbered prefix in every language.
- No external facts without a data file backing them.
- Four orchestrator-written exceptions to "never writes chapter prose" apply across the kit (full list:
  SKILL.md § Non-negotiables); the two used only in this profile are the lite `0_Index.md` and the
  `1_Concept.md` §1.1 game-name line (§ W1 naming step, below) — boilerplate assembly, never design prose.

## Paths

| Var | Value |
|---|---|
| `KIT` | `${CLAUDE_SKILL_DIR}` |
| `OUT` | `brief:D-14` resolved to an absolute path, default `<cwd>/deliverables/<slug>/GDD/<D-15>/` |
| `WORK` | `OUT/_work/` — `brief.md`, `gap-log.md`, `run-meta.md`, `review-report.md`, `reports/<file>.report.md` |

`slug` = kebab-case of the chosen game name, ASCII only, exactly as in the full flow.

## W0 — Gate

1. If the sub-profile is not already fixed by `--profile hyper-casual`, ask once: *hyper-casual or
   casual?* — a single `AskUserQuestion` with both options described in one line each (see the table
   above). Skip if the opening message already states it unambiguously.
2. Refuse to proceed while `D-02` (pitch) is empty, exactly as the full gate does — the preset can never
   supply it.
3. Render the **Proposed values** table from `brief-schema.md` § Casual Profile Preset, using the column
   for the chosen sub-profile. The table is shown to the user as text (not through `AskUserQuestion`).
   Then ask via `AskUserQuestion`: *confirm as-is, edit specific rows, or reject the whole preset and
   answer each field individually?*, offered as exactly 3 options — `Confirm all as-is` / `Edit rows
   (name them)` / `Reject preset — ask each field`. This is one round for the top-level choice; if the
   user picks "Edit rows," collect the per-row edits in follow-up `AskUserQuestion` calls under the same
   ≤4-option rule (`brief-schema.md` § Gate behaviour rule 3). Nothing from this table is written to
   `brief.md` until this confirmation happens.
4. Ask, via `AskUserQuestion` batches of ≤4, every field in brief-schema.md's "Always asked, never
   presumed" list for the casual profile: `D-02` (already have it from step 2), `D-03`, `D-07`, `D-08`,
   `D-11`, `D-12`, `D-41`, `D-37`, `D-48`, `D-45`, `D-46`, `D-47` — ask `D-48` (paid UA) before `D-45`, its
   ask text notes that a CPI target is only relevant when `D-48 = Yes`. Accept `UNDECIDED` wherever the
   user declines, recorded verbatim — this applies to `D-48`/`D-45`/`D-46`/`D-47` exactly as to any other
   field; a missing paid-UA answer, KPI target, ad network, or build-size cap is `UNDECIDED`, never a
   guess.
5. Ask, via `AskUserQuestion` batches of ≤4, the remaining fields `brief-schema.md` § Casual Profile
   Preset → "Always asked, never presumed" lists beyond step 4: `D-01` (working title — `GENERATE`
   accepted), `D-10` (team/timeline/budget — `UNDECIDED` accepted), `D-13` (reference games — `none`
   accepted), `D-14` (output dir — offer the default path), `D-38`, `D-40`, `D-43`, `D-44` (each
   `none`/`UNDECIDED` accepted). Honour the Section C triggers exactly as that section states: ask
   `D-35` only if `D-23 ∈ {Procedural, Endless}`, `D-36` only if `D-24 ≠ None`, `D-42` only if
   `D-11 ≠ UNDECIDED` (from step 4's answer), and `D-32`/`D-33`/`D-34` only if an edited preset row from
   step 3 made their own trigger fire (`D-20 ≠ None`, `D-21 ≥ Medium`, `D-22 ≠ None` respectively).
   Accept `UNDECIDED`/`none` wherever offered, recorded verbatim.
6. Confirmed preset rows are written to `brief.md` with `Source: casual preset — confirmed by user`;
   edited rows are written with the edited value and `Source: casual preset — edited by user`; rejected
   rows fall back to being asked individually and get the normal `Source: asked`.
7. Render `brief.md` using `brief-template.md` as-is — the template already carries the `Profile:` header
   field and the `D-45`–`D-48` rows (which read `—` in the full profile), so no ad-hoc rows need to be
   appended to the rendered instance. Fill the `Profile:` header field with `<hyper-casual|casual>` and
   fill the `D-45`–`D-48` rows from steps 4–5's answers. Show the rendered brief and ask the final
   confirmation: *Freeze this brief?* Do not proceed until they confirm.
8. Write the frozen text to `WORK/brief.md` and write `WORK/run-meta.md` with: date, kit version, `D-15`,
   **and a `profile: casual` or `profile: hyper-casual` line** — this line is load-bearing:
   `/gdd-forge:review` reads it to pick lite checklists/contracts over full ones, falling back to
   detecting `1_Concept.md` + `2_Core Gameplay.md` in the folder when the line is absent (e.g. a
   `run-meta.md` from before this profile existed). Write this line for both sub-profiles, not just one.
   `run-meta.md` follows `references/run-meta-template.md` and `gap-log.md` follows
   `references/gap-log-template.md`.
9. Create `OUT`/`WORK` with a provisional slug (kebab-case of `D-01` if it is a real title, else
   `untitled-game`), exactly as the full flow does. Naming resolves in the W1 naming step below — this
   profile has no `gdd-namer` dispatch.

## Wave table

**No input slicing in this profile** — every W1–W4 dispatch reads its upstream lite files whole. With the
budgets in `contracts-lite/*` (files 1–2 are 1,500–2,800 words), slicing a file this small saves no
meaningful tokens and caused real defects in practice: an agent handed a slice denied a section existed
because its slice happened not to include it. Models: see SKILL.md § Agent roster — the agent's own
frontmatter is authoritative.

| Wave | Dispatch(es) | Blocks on | Inputs delivered | Why |
|---|---|---|---|---|
| W1 | `gdd-concept-architect` → `1_Concept.md` | brief frozen | whole `brief.md` | anchor file; no upstream lite file exists yet |
| W2 | `gdd-mechanics-designer` → `2_Core Gameplay.md` | file 1 complete | whole `1_Concept.md` + `brief.md` | single dispatch, not contended by parallel siblings |
| W3 | `gdd-ux-designer` → `3_UX Art and Audio.md` ‖ `gdd-producer` → `4_Business and LiveOps.md` ‖ `gdd-tech-designer` → `5_Tech Note.md` | files 1+2 complete | whole `1_Concept.md` and `2_Core Gameplay.md` + `brief.md` | all three read only files 1/2, never each other — genuinely independent |
| W4 | `gdd-reviewer` → `review-report.md` (mandatory) | files 1–5 complete, GAPs patched | whole files 1–5 + `brief.md` + `gap-log.md` | consistency check |

Waves are serial for the same reason as the full flow: each dispatch's *Reads* list in the matching
`contracts-lite/lite-N.md` must already be on disk.

## W1 — Concept, then the naming step (orchestrator)

W1 dispatches `gdd-concept-architect` → `1_Concept.md` (whole `brief.md`). When its REPORT arrives, the
orchestrator runs the naming step **before W2**:

1. If `D-01` is a real title: `game_name` = D-01, compute `slug`, no question asked.
2. If `D-01 ∈ {GENERATE, UNDECIDED}`: read §1.2 of the finished file (exactly 3 candidates), ask the user
   once with `AskUserQuestion` — the 3 candidates as options (label = name, description = rationale);
   'Other' free text becomes the name.
3. Write `game_name` and `slug` into `brief.md` under 'Chosen game name'; rename `OUT`/`WORK` from the
   provisional slug; update `run-meta.md`.
4. Replace the literal `[GAME NAME — pending §1.2]` placeholder in `1_Concept.md` §1.1 with the chosen
   name by a direct `Edit` — boilerplate assembly, not design prose (same exemption as `0_Index.md`); do
   not re-dispatch the agent for this.
5. Resolve all W1 GAPs (§ GAP handling, below) before dispatching W2.

## Lite dispatch envelope

Assemble every W1–W4 prompt from this envelope (the counterpart to `pipeline.md`'s § W2–W7 envelope):

```
ROLE: you are <agent> writing <lite file> for the GDD of "<game_name>" (lite profile — <hyper-casual|casual>).
LANGUAGE: write the body in <D-12>. Keep heading numbers in English ("# 2. Core Gameplay").
RULES: read <KIT>/references/dispatch-rules.md first and obey it in full — it is part of this prompt.
CONTRACT: read <KIT>/references/contracts-lite/lite-<n>.md in full. Obey Sections, Owns, Budget, Depth rule, Hard rules.
GUIDANCE: read <KIT>/references/guidance/<role>.lite.md — craft advice for this file. (Line present only when that file exists.)
INPUTS (read all, read nothing else):
  - <WORK>/brief.md
  - <OUT>/<consumed lite file(s)>, whole — see wave table for which files
  - template: <KIT>/templates/lite/<tmpl>
  - checklist: <KIT>/checklists/lite/<check>
  - data: <KIT>/data/<file>, and <KIT>/data/casual/<file> only where the contract names it
OUTPUT: write exactly one file <OUT>/<lite file>.
```
No inline RULES list, no inline REPORT block — the dispatch closes with the `## REPORT` block from
`dispatch-rules.md` §4 (this profile omits `CROSS_REFS_CITED`).

Dispatch W1 alone; dispatch W3's three calls in **one message**, `run_in_background: true`, then wait for
all three before proceeding — same mechanics as the full flow's parallel waves. Save each `## REPORT`
block verbatim to `WORK/reports/<file>.report.md` as it arrives, then run `wc -w` on the produced lite
file itself and record the count in `run-meta.md` § Waves, column `Words` — the agent's own REPORT never
carries a word count.

**PATCH mode** (used only during § GAP handling, never mid-wave): `PATCH MODE: <file> exists. Replace
only the placeholder(s) G-<file>-<n> and everything that depends on them. Report as usual.` —
`dispatch-rules.md` §3 defines exactly what the agent then does. Use `Edit`, never `Write`, in PATCH mode.

## GAP handling — every wave, before the next starts

GAPs are resolved at the end of every wave, before the next wave starts (after W1, after W2, after W3),
using the GAP classes defined in `dispatch-rules.md` §1 and the class-based resolution below — the same
procedure the full flow uses (`pipeline.md` § GAP handling), applied here per lite file. GAP ids are
`G-<file>-<n>` (`<file>` = lite file number 1–5, `<n>` restarts per file), so W3's three parallel agents
never collide.

Procedure, run after each wave's report(s) are in:

1. Collect every `G-n` from that wave's report(s), each tagged with its class (`value` or `structural`).
   In W3 only, more than one file can raise a GAP on the same field — ask the user about it once, then
   resolve it in every file that raised it.
2. Ask via `AskUserQuestion` (≤ 4 per call), offering each agent's own suggested options plus "Leave
   UNDECIDED". If an answer contradicts a frozen brief value or a pillar, ask the user which one yields
   before writing anything.
3. Write the answer into `brief.md` under `## Gate additions (lite)` with the G-id, and log the Q/A and
   class in `gap-log.md`.
4. Resolve by class:
   - **`value`** — the orchestrator itself replaces the `⟂ GAP` line with the user's value via `Edit` and
     removes the item from that file's Open Decisions. Use a PATCH dispatch to the owner instead if more
     than ~3 lines of the file depend on the value.
   - **`structural`** — re-dispatch the owning agent **fresh** (the normal envelope above, not PATCH mode)
     so the change is integrated through the whole file.
   - The orchestrator upgrades `value` → `structural` whenever the user's answer introduces something the
     suggested options did not (a new feature, mode, screen, flow).
5. "Leave UNDECIDED" → the placeholder stays; it surfaces in that file's own Open Decisions box (there is
   no central register in this profile).

Because nothing downstream exists yet when a W1 or W2 GAP is resolved, no cascade is needed there. A
cascade rule applies only to an answer given *after* the run, or a W3 GAP on a fact owned by file 1 or 2:
fix the owning file first (`Edit` for `value`, fresh dispatch for `structural`), then PATCH only the
downstream files that actually cite the changed section or term — find them with `grep` for the `§x.y`
reference and for the changed term. File 1 feeds files 2–5; file 2 feeds files 3–5.

**PROPOSALS are never asked mid-run** (`dispatch-rules.md` §1) — leave every `(proposal)` exactly as
written. Report their count and location in the Done message (below); treat any later answer like a
`value`/`structural` GAP above.

## W4 — Lite review (mandatory)

Dispatch `gdd-reviewer` with all five finished lite files, `brief.md`, `gap-log.md`, every
`references/contracts-lite/lite-N.md`, `KIT/references/consistency-rules-lite.md` (12 rules), every
`checklists/lite/*.md`, and `WORK/reports/*`. It writes `WORK/fact-ledger.md` and `WORK/review-report.md`
in the same Blockers/Majors/Minors shape the full flow uses.

- **Blockers** → resolve exactly like a GAP (§ GAP handling above).
- **Majors** → PATCH the named owner; if the Major is `structural`, re-dispatch that agent fresh instead
  of patching it.
- **Minors** → the orchestrator fixes one itself, via `Edit`, only when it is ≤ 2 lines and needs no
  design judgement (SKILL.md § Non-negotiables, exception 2); every other Minor stays in
  `review-report.md` only; the Done message gives the count.
- After patches, RECHECK only if an agent actually patched a file: a short `gdd-reviewer` dispatch,
  limited to the patched files and rules 1–12, updating the fact-ledger rows for them. No patches → no
  RECHECK.

## 0_Index.md — assembled by the orchestrator, not dispatched

Once files 1–5 are final and W4's review report is in, the orchestrator writes `0_Index.md` itself,
following `templates/lite/0-index.md` and `contracts-lite/lite-0.md` directly — no `Agent` call. Per
`contracts-lite/lite-0.md`, §0.3 is `file | status | open items` (no owner agent, model, word count or
checklist %) — open items = `UNDECIDED` fields + unresolved GAPs + `(proposal)`s, counted from that
file's own Open Decisions. Pull §0.1–§0.3 from the finished files, `run-meta.md`'s `Words` column, and
`review-report.md`; never estimate a count you don't have written evidence for. This keeps the profile at
exactly 6 dispatches in the clean-run case: W1(1) + W2(1) + W3(3) + W4(1) = 6 — GAP re-dispatches and
review patches are extra — with `0_Index.md` itself free (orchestrator-written).

## Done — tell the user

- Absolute path of `OUT`, the six-file list with word counts (`run-meta.md` § Waves, column `Words`).
- Blockers/Majors/Minors counts from W4's review.
- Number of Open Decisions and number of `(proposal)`s across all five files (sum, since there's no
  central register).
- One line offering to: (a) re-run a single file with new inputs (`--file N`), (b) bump the version, (c)
  escalate to the full profile if scope grew, (d) run `/gdd-forge:review` later.

## Single-file re-run — `--profile casual --file N`

The counterpart to the full flow's `--chapter N`. `N` is the lite file number, 1–5.

1. Load `WORK/brief.md`; confirm `run-meta.md` shows `profile: casual` or `profile: hyper-casual` — if
   it doesn't, this is a full-profile output directory, stop and point the user at `pipeline.md`'s
   `--chapter` instead.
2. Ask the user only for fields file `N`'s contract lists under *Reads* that are currently `UNDECIDED`.
3. Re-dispatch file `N`'s owning agent fresh (not PATCH mode), with the same inputs its wave normally
   gets (whole upstream files, per § Wave table).
4. If `N = 1`: the pillars/glossary anchor may have changed. Do **not** automatically cascade a rerun of
   files 2–5 — warn the user that downstream files may now be stale relative to the new `1_Concept.md`,
   and offer to also re-run the affected ones, but only on their explicit confirmation (re-running them
   unasked would be an invented decision about what the user wants redone).
5. Append one row to `1_Concept.md` §1.1's version table noting the rerun (version bump, date, what
   changed) — this is the profile's one piece of version history, so every rerun touches it regardless of
   which file `N` actually was; do this as a direct `Edit`, not a subagent dispatch.
6. Run a RECHECK dispatch of `gdd-reviewer`, limited to file `N` (and any file patched because of it),
   rules 1–12; handle Majors as in § W4 above.
7. Re-assemble `0_Index.md` only (no `13_Appendices.md` equivalent exists in this profile).

## Resume — `--profile casual --resume <OUT dir>`

1. Read `WORK/run-meta.md`; confirm `profile:` is set — if absent, fall back to detecting whether
   `1_Concept.md` and `2_Core Gameplay.md` exist to infer this was a lite run (same detection
   `/gdd-forge:review` uses), or hand off to `pipeline.md`'s Resume if it looks like a full run instead.
2. If `brief.md` was never frozen, resume at W0 — re-show any preset rows already confirmed before the
   session ended rather than re-asking them.
3. If `1_Concept.md` exists but `run-meta.md` still shows the provisional slug and `D-01 ∈ {GENERATE,
   UNDECIDED}`, run the W1 naming step before anything else.
4. List `OUT/*.md`. A file counts as done only if it exists **and**
   `WORK/reports/<file>.report.md` shows `STATUS: complete` or `complete-with-gaps`.
5. Resume at the first wave whose file(s) are not all done, then continue W1→W4 forward normally,
   resolving GAPs at the end of each wave as usual (§ GAP handling).
6. If `review-report.md` exists but `0_Index.md` does not, resume at 0_Index assembly directly.

## Failure modes

| Situation | Orchestrator does |
|---|---|
| Agent returns `blocked` | Read its GAPS; if one says "this needs the full profile," treat it as an escalation trigger (see § When not to use this profile) rather than a normal GAP; otherwise ask the user and re-dispatch fresh. |
| Agent wrote to the wrong path | Move the file; note it in `run-meta.md`; do not re-run. |
| Agent invented a decision (Lite Consistency rule 6 FAIL) | PATCH mode with the exact sentence to remove; log it in `gap-log.md` as "fabrication caught". |
| User abandons mid-run | Everything so far is on disk in `OUT`/`WORK`; say so and how to resume (`--profile casual --resume <OUT>`). |

## Token cost

6 dispatches on a clean run (§ Wave table). Each dispatch reads `brief.md` plus at most two small
upstream lite files, whole. Total output ceiling ≈ 9,000 words — the sum of the five contracts' budgets
(`contracts-lite/lite-N.md` § Budget). No token estimate is given; none of these numbers is measured.

## Agent roster

See SKILL.md § Agent roster — one table covers both profiles; the agent's own frontmatter is authoritative
for its model.
