# profile-casual.md — the lite pipeline for casual / hyper-casual mobile games

This is the counterpart to `pipeline.md` for `--profile casual` (synonym: `--profile lite`) and its
sub-profile shortcut `--profile hyper-casual`. **When one of these flags is active, the main agent
follows this document end to end and does not also follow `pipeline.md`** — it defines its own W0,
workflow stages, GAP handling, Done, Resume and re-runs. Shared with the full flow: `brief-schema.md`
(still the single source of truth for every `D-xx` field), the agents in `agents/`, the workflow
`workflows/forge-run.js` (args/return: SKILL.md § Workflow contract), and the non-negotiables (below).

```
--profile casual            entry point (synonym: --profile lite)
--profile hyper-casual      entry point, pre-selects the hyper-casual sub-profile (skips the sub-profile question)
--profile casual --file N   re-run a single lite output file, N ∈ {1,2,3,4,5} — see § Single-file re-run
--profile casual --resume <OUT dir>   resume an interrupted lite run — see § Resume
```

## What this profile is for

A casual or hyper-casual mobile game (endless runner, match-3, idle tap, physics puzzle, arcade
score-chaser) does not need 13 chapters or the full flow's dozen-plus design dispatches to reach a
build-ready design document. It has no real narrative, no AI worth a dedicated architecture chapter,
usually no multiplayer, and its business model lives almost entirely in ad placement and a thin IAP
layer rather than a deep economy. This profile produces **5 content files + 1 assembled index**, written
by the exact same agents as the full flow under different, compressed contracts
(`references/contracts-lite/`), and verified, reviewed and fixed by the same workflow.

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

Both use the same 6 files and the same workflow stages. They differ only in the gate preset and in how
much each lite file leans into meta-progression, framing, and IAP breadth. The preset itself — session
length, business model, narrative depth, obstacles, level structure, LiveOps, monetisation mix — lives
in `brief-schema.md` § Casual Profile Preset; do not duplicate those values here.

| | Hyper-casual | Casual |
|---|---|---|
| `1_Concept.md` §1.5 feature set | Leans toward 6 features | Can use the full 6–10 |
| `2_Core Gameplay.md` §2.2 meta-progression tier | Almost never present | Sometimes one light tier |

The user picks a sub-profile at the top of W0 (or it is pre-selected by `--profile hyper-casual`); the
choice determines which preset column the gate proposes. Nothing else in the pipeline branches on it —
every contract, template and checklist in this document already covers both.

## Non-negotiables (inherited, restated here for self-sufficiency)

Unchanged from the full flow — this profile does not relax any of them:

- Only you (the main agent) talk to the user. Subagents never see the user and cannot call
  `AskUserQuestion`; nor can the workflow — every question happens at a checkpoint, between segments.
- Decisions (`D-xx`) come only from the user's words or explicit `UNDECIDED`. Never invented, defaulted,
  or inferred — the casual gate preset (below) is a *proposal*, not an invention, precisely because it
  requires explicit user confirmation before a single value reaches `brief.md`.
- Reversible, local choices the brief doesn't make are written by agents as tagged `(proposal)`s, listed
  under Open Decisions with 1–2 alternatives (`dispatch-rules.md` §1) — never silently, never for a
  `D-xx` field.
- Subagents report **GAPs** instead of deciding; you ask the user on their behalf and resolve by class
  (§ GAP handling).
- Pass **absolute paths** for every input and output, in every arg and resolution.
- Never paste file bodies into a prompt or an arg — give a path (upstream lite files are read whole,
  never sliced).
- Chapter bodies are written in `D-12`; headings keep the English numbered prefix in every language.
- No external facts without a data file backing them.
- You — and the workflow's clerk and assembly steps — never write chapter prose; four exceptions
  (SKILL.md § Non-negotiables), two of them lite-only: `0_Index.md`, assembled by the workflow's INDEX
  step from `contracts-lite/lite-0.md` (never a designer dispatch), and the `1_Concept.md` §1.1 name
  line you `Edit` at the anchor checkpoint (§ W1).

## Paths

| Var | Value |
|---|---|
| `KIT` | `${CLAUDE_SKILL_DIR}` |
| `OUT` | `brief:D-14` resolved to an absolute path, default `<cwd>/deliverables/<slug>/GDD/<D-15>/` |
| `WORK` | `OUT/_work/` — `brief.md`, `gap-log.md`, `run-meta.md`, `review-report.md`, `fact-ledger.md`, `reports/`, `checks/` |

`slug` = kebab-case of the chosen game name, ASCII only, exactly as in the full flow. No `INPUTS` folder.

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
   `untitled-game`), exactly as the full flow does. Naming resolves at the W1 anchor checkpoint below —
   this profile has no `gdd-namer` dispatch.

## Driving the workflow

After the freeze, the run is one workflow called one **segment** at a time — from `args.from` to a
checkpoint, the end, or an error. State lives on disk, never in the workflow.

1. **Resolve once, record in `run-meta.md`:** `agent_ns` (`gdd-forge:` under a plugin install, `''` for
   agents copied into `~/.claude/agents/`) and the call — `Workflow({name: "gdd-forge:forge-run",
   args})`; for a local copy `Workflow({scriptPath, args})` with
   `${CLAUDE_SKILL_DIR}/../../workflows/forge-run.js` made absolute (`workflow:` line). This is the
   user's opt-in.
2. **args** (SKILL.md § Workflow contract): `mode: 'run'`, `profile` = the W0 sub-profile (`casual` |
   `hyper-casual`; `--profile lite` → `casual`), `from: 'W1'`, `paths` without `inputs`; `game_name` =
   D-01 if a real title (slug final, no name question), else omitted until the anchor pick;
   `flags.need_name` = `D-01 ∈ {GENERATE, UNDECIDED}`, `flags.f2p_or_hybrid` from `D-06`; `data` needs
   only the `monetization` (`D-06`) and `accessibility` (`D-39`) slices, per each folder's `_index.md`.
   `model_override` only on explicit user request.
3. **Loop:** `checkpoint` → ask (§ W1, § GAP handling, § W4), write the answers to disk, call again
   with `from` = `checkpoint.next` and the answers as `resolutions`; `done` → § Done; `error` → tell the
   user its `message`, fix what it names (or ask), call again (`stage: 'resolve'` or missing args → the
   same call, args fixed; otherwise `from: stage`, `resolutions: []` — already applied).

## Stage table

**No input slicing** — every dispatch reads its upstream lite files whole (per its contract's *Reads*)
plus `brief.md` (files this small gain nothing from slicing; a sliced agent once denied a section
existed). Models: MODEL ROUTING (`TIERS` / `ROLE_TIER`) in `workflows/forge-run.js`;
no agent pins one.

| Stage | Work | Stops at |
|---|---|---|
| W1 | `gdd-concept-architect` → `1_Concept.md` | `anchor` (always) |
| W2 | `gdd-mechanics-designer` → `2_Core Gameplay.md` | `gaps` if items |
| W3 | `gdd-ux-designer` → `3_UX Art and Audio.md` ‖ `gdd-producer` → `4_Business and LiveOps.md` ‖ `gdd-tech-designer` → `5_Tech Note.md` | `gaps` if items |
| W4 | review → `review-report.md` | `blockers` if any |
| FIX | fix loop, ≤ 2 rounds | `blockers` / `residual` |
| INDEX | `0_Index.md` assembly → completeness critic | `done` |

Stages are serial (each contract's *Reads* must be on disk); W3's writers read only files 1–2, so they
run in parallel. Every new or fresh file gets **per-file verify**: finder → three voters per Major →
one auto-PATCH for confirmed Majors needing no user decision; the rest become `V-` items. Bookkeeping
(REPORTs, word counts, gap-log rows) is the workflow's.

## W1 — Concept, then the anchor checkpoint (main agent)

W1 always returns checkpoint `anchor` (`file`, pillars, features, items; with `need_name`, `candidates`
= the three §1.2 names); nothing downstream starts before the user approves file 1.

1. Show pillars (§1.4: name · meaning · forbids) and features (§1.5: name · priority · pillar) as a
   table; ask `Approve` / `Request changes` (notes via Other). With `candidates`, also ask the name: the
   3 as options (label = name, description = rationale), 'Other' = the name. W1 items: § GAP handling.
2. **Name** (only with `candidates`): write `game_name`/`slug` into `brief.md` under 'Chosen game
   name'; rename `OUT`/`WORK` from the provisional slug; update `run-meta.md`; replace the
   `[GAME NAME — pending §1.2]` placeholder in `1_Concept.md` §1.1 by a direct `Edit`, never a
   re-dispatch. Later calls carry the new `paths`, `game_name`, `flags.need_name: false`.
3. **Request changes** → notes into `brief.md` under `## Gate additions (W1 anchor review)`; resolution
   `{id: 'ANCHOR', file: <1_Concept.md>, owner: 'concept-architect', class: 'structural', action:
   'fresh'}`; file 1's items get `fresh` too — never `Edit` a file about to be rewritten (a name pick:
   step 2 now, minus the §1.1 `Edit`); call from `W2`. File 1 is rewritten, re-verified and this
   checkpoint returns; do the §1.1 `Edit` then if the placeholder is there.
4. **Approve** → `{id: 'ANCHOR', action: 'approved'}` (or none) plus item resolutions; call from `W2`.
   Record it on disk: `brief.md` `## Gate additions (W1 anchor review)`: `ANCHOR · approved · <date>`,
   and a `gap-log.md` row `ANCHOR | W1 | gdd-concept-architect | anchor approval | structural |
   §1.4–§1.5 | Approve the anchor? | approved | <date> | —` (§ Resume reads it; Request changes logs
   the notes as that row's Answer instead).

## GAP handling — your half (`gaps` / `blockers`)

You ask and choose resolutions; the workflow applies them when the next segment starts. Classes:
`dispatch-rules.md` §1. Ids: `G-<file>-<n>` (writer GAP; `<file>` = 1–5, `<n>` per file; a rewritten
file numbers new GAPs after the highest logged), `V-<file>-…` (verify decision; `<file>` raised it),
`R-<n>` (review), `R<round>-<n>` (fix-loop RECHECK).

1. De-duplicate against `gap-log.md` by id **and** field: same id and field already answered → reuse
   the answer; same id, different field → a new question, logged and resolved as `<id>~2` (next free
   suffix). A field several W3 files raise is asked once and resolved in each.
2. Ask via `AskUserQuestion` (≤ 4 per call): the item's options plus "Leave UNDECIDED". If an answer
   contradicts a frozen brief value or a pillar, ask which yields before writing anything.
3. Write the answer to `brief.md` under `## Gate additions (lite)` with the id; log Q/A, class and date
   in `gap-log.md` (fill the G-id row; add rows for V-/R- ids; Patched files for `edited`).
4. Resolution by class:
   - **`value`** — replace the `⟂ GAP` line yourself via `Edit` (value and unit, no prose) and drop the
     item from that file's Open Decisions → `edited`; more than ~3 dependent lines → `patch`.
   - **`structural`** → `fresh`: the owner integrates the change through the whole file. Upgrade
     `value` → `structural` when the answer adds what the options did not (a new feature, mode, screen,
     flow). A `blocked` file → always `fresh` after its items (reason: its saved REPORT); blocked again
     after that → tell the user and ask, never re-dispatch blindly.
   - A `V-` item about an upstream fault: *fix the upstream file* → `patch` on the item's `file` with
     `cascade: true`; *align this file* → `patch` on the raising file.
   - "Leave UNDECIDED" → `undecided`; the placeholder stays in that file's own Open Decisions box
     (no central register).
5. **Cascade:** an upstream-owned fact is fixed in the owning file first — its resolution names the
   owner, `cascade: true`, the changed `sections`; the workflow then PATCHes only on-disk files citing
   that `§x.y` or term (file 1 feeds 2–5, file 2 feeds 3–5). The raising file still gets its own
   resolution; the cascade PATCH only aligns citations.
6. Call from `next`; items from re-verified fresh files bring the checkpoint back.

**PROPOSALS are never asked mid-run** (`dispatch-rules.md` §1): leave each `(proposal)` as written,
count them in Done, treat a later answer like a GAP. **PATCH mode** edits only the named items and what
depends on them, `Edit` never `Write` (`dispatch-rules.md` §3); `fresh` rewrites the whole file.
Envelopes: `writePrompt` / `patchPrompt` in the script.

## W4 — Lite review, then the FIX loop

**W4** (mandatory): `gdd-reviewer` (normal contract: `consistency-rules-lite.md` rules 1–12, lite
contracts and checklists → `fact-ledger.md` + `review-report.md`) ‖ four lens finders → merge → three
voters per Major/Blocker (one evidence check per Minor) → `review-report.md` keeps confirmed findings
only, plus `## Verification`. Blockers (here or from a RECHECK) → checkpoint `blockers`, `next` = `FIX`.

**FIX** — until clean, ≤ 2 rounds per call. Per round: one PATCH per owner file, in parallel (a
`structural` Major → that file fresh) → RECHECK (`gdd-reviewer` on patched files, rules 1–12,
fact-ledger rows ‖ regression lens) → verified survivors feed the next round. Answers applied at the
start of a FIX call (Blockers) are rechecked the same way even with no Major open; a Major with no
lite file to patch, or a GAP a fix PATCH raised, comes back as a checkpoint. Minors ≤ 2 lines, no
judgement → clerk fix (exception 2); the rest stay listed. Majors left after the cap → checkpoint
`residual`: show them, ask `Another round` / `Accept as known issues` → call from `FIX` with
`extra_round: true` and `{id: 'RESIDUAL', action: 'another_round'}`, or from `INDEX` with `action:
'accept'`; log the choice per R-id. The workflow records `## Fix loop` in `review-report.md` and
`run-meta.md` (iterations 0–N).

## INDEX — 0_Index.md, assembled by the workflow

The workflow's assembly step (tier `spec`, no designer dispatch, no `## REPORT`) writes `0_Index.md`
per `contracts-lite/lite-0.md` and `templates/lite/0-index.md` — every value pulled from disk, never
estimated. Then the completeness critic runs: an index finding gets one re-assembly, others come back
in `summary.issues`.

## Done — tell the user

- Absolute path of `OUT`, the six-file list with word counts (`summary.files`).
- Blockers/Majors/Minors counts from the verified review, and the fix-loop outcome (patched, accepted).
- Open Decisions and `(proposal)`s across the five files, Minors left, and any critic `issues`.
- One line offering: (a) `--file N` with new inputs, (b) a version bump, (c) escalating to the full
  profile if scope grew, (d) `/gdd-forge:review` later.

## Single-file re-run — `--profile casual --file N`

Counterpart of the full flow's `--chapter N`; `N` = lite file 1–5.

1. Load `WORK/brief.md`; `run-meta.md` must show `profile: casual|hyper-casual` — else point the user
   at `pipeline.md`'s `--chapter`.
2. First ask the `UNDECIDED` fields file `N`'s contract lists under *Reads*; record as § GAP handling
   step 3.
3. Call with `mode: 'file'`, `target: N`, `from: 'RERUN'`, `date` (ISO), `flags.need_name: false`,
   other args as usual.
4. **RERUN** — fresh owner dispatch, per-file verify; items or `blocked` → checkpoint `gaps`, `next` =
   `RERUN-POST`.
5. **RERUN-POST** — version row in `1_Concept.md` §1.1 (every re-run: the profile's only version
   history); `gdd-reviewer` RECHECK of `N` ‖ regression lens; PATCH of confirmed Majors in `N`;
   `0_Index.md` re-assembled; critic. `done` carries `stale` (N = 1 → files 2–5; N = 2 → 3–5) and
   leftover `issues`.
6. Report both. Re-run stale files only on explicit confirmation — never cascade unasked (an invented
   decision). N = 1 with a chosen name: re-apply the §1.1 name `Edit` if the placeholder is back.

## Resume — `--profile casual --resume <OUT dir>`

1. Read `WORK/run-meta.md`; no `profile:` → infer a lite run from `1_Concept.md` + `2_Core Gameplay.md`,
   or hand off to `pipeline.md`'s Resume.
2. Brief never frozen → W0; re-show confirmed preset rows, never re-ask them.
3. Reuse `agent_namespace` and `workflow:` from `run-meta.md`; rebuild args from disk.
4. A file is done only if it exists **and** `WORK/reports/<file>.report.md` shows `STATUS: complete` or
   `complete-with-gaps`. `from` =
   - `W1` — file 1 not done;
   - no `ANCHOR` row answered `approved` in `gap-log.md` → `ANCHOR` (re-shows the anchor checkpoint
     without rewriting file 1; pass `need_name: true` while the slug is still provisional so it carries
     the §1.2 candidates);
   - else the first stage with a file not done (`W2`/`W3`; a stage re-runs all its files);
   - no `W4` row in run-meta § Waves → `W4`; unanswered review Blockers → ask, then `FIX`; run-meta
     § Fix loop `iterations: 0` while the report lists Majors → `FIX`; no `0_Index.md` → `INDEX` (open
     Majors in review-report § Fix loop not accepted in gap-log → residual question first). Progress
     comes from run-meta / gap-log, never from optional report sections — `/gdd-forge:review` may have
     rewritten the report.
5. First ask what the interrupted checkpoint left open (gap-log rows without an Answer, "asked the
   user" lines in `WORK/checks/*.check.md` — they carry the `V-` id — that gap-log does not answer,
   unanswered review Blockers); pass the answers as `resolutions`.

## Failure modes

| Situation | You do |
|---|---|
| Writer returns `blocked` (`checkpoint.blocked`, or `STATUS: blocked` in `WORK/reports/`) | "Needs the full profile" → escalation trigger (§ When NOT to use this profile), not a GAP; otherwise ask, resolve that file `fresh`. |
| `gdd-forge:forge-run` not found | Use `scriptPath`; update `workflow:` in `run-meta.md`. |
| Agent wrote to the wrong path | Move the file; note it in `run-meta.md` § Discrepancies; do not re-run the writer. |
| Agent invented a decision (Lite Consistency rule 6 FAIL) | Verify or review PATCHes it out, or it reaches you as an item. Log "fabrication caught" in `gap-log.md`. |
| User abandons mid-run | All work is on disk in `OUT`/`WORK`; tell them `--profile casual --resume <OUT>`. |

## Token cost

A clean run makes 6 design dispatches (five writers, `gdd-reviewer`) plus verification, review,
assembly and clerk agents; GAP re-dispatches, cascades and fix rounds are extra. No token estimate is
given.

## Agent roster

See SKILL.md § Agent roster — one table covers both profiles. Models: § Stage table.
