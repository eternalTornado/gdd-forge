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
score-chaser) does not need 13 chapters, ~20 subagent dispatches, or roughly a million input tokens
(see § Token cost, below) to reach a build-ready design document. It has no real narrative, no AI
worth a dedicated architecture chapter, usually no multiplayer, and its business model lives almost
entirely in ad placement and a thin IAP layer rather than a deep economy. This profile produces
**5 content files + 1 assembled index, in 4 waves, at 6 subagent dispatches**, by reusing the exact
same agents as the full flow under different, compressed contracts (`references/contracts-lite/`).

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

Both use the same 6 files and the same 4 waves. They differ only in the gate preset (below) and in how
much each lite file leans into meta-progression, framing, and IAP breadth:

| | Hyper-casual | Casual |
|---|---|---|
| Session length (`D-09`) | Micro, <5 min | Small, 5–15 min |
| Business model (`D-06`) | F2P + Ads only | F2P hybrid — ads + IAP |
| Narrative (`D-21`) | None | Light framing |
| Obstacles/enemies (`D-22`) | Obstacle patterns only | Simple enemies allowed |
| Level structure (`D-23`) | Endless or level select | Level select (grid) preferred |
| LiveOps (`D-24`) | None or content updates only | Content updates or seasons |
| Monetisation mix (`D-30`) | Rewarded + interstitial + remove-ads IAP | + consumable IAP |
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
- Subagents report **GAPs** instead of deciding; the orchestrator asks on the user's behalf.
- Pass **absolute paths** to every subagent for every input and output.
- Never paste file bodies into a subagent prompt — give a path (whole file or a slice, see § Wave table)
  and let the subagent read it.
- Chapter bodies are written in `D-12`; headings keep the English numbered prefix in every language.
- No external facts without a data file backing them.
- Two orchestrator-written exceptions to "never writes chapter prose": `0_Index.md` and the §1.1
  game-name line in `1_Concept.md` — boilerplate assembly, never design prose.

## Paths

| Var | Value |
|---|---|
| `KIT` | `${CLAUDE_SKILL_DIR}` |
| `OUT` | `brief:D-14` resolved to an absolute path, default `<cwd>/deliverables/<slug>/GDD/<D-15>/` |
| `WORK` | `OUT/_work/` — `brief.md`, `gap-log.md`, `run-meta.md`, `review-report.md` (only if W4 ran), `inputs/` (holding `_anchor.md` and the per-dispatch slice files — same layout as the full flow), `reports/<file>.report.md` |

`slug` = kebab-case of the chosen game name, ASCII only, exactly as in the full flow.

## W0 — Gate

1. If the sub-profile is not already fixed by `--profile hyper-casual`, ask once: *hyper-casual or
   casual?* — a single `AskUserQuestion` with both options described in one line each (see the table
   above). Skip if the opening message already states it unambiguously.
2. Refuse to proceed while `D-02` (pitch) is empty, exactly as the full gate does — the preset can never
   supply it.
3. Render the **Proposed values** table from `brief-schema.md` § Casual Profile Preset, using the column
   for the chosen sub-profile. Show it to the user as one block and ask: *confirm as-is, edit specific
   rows, or reject the whole preset and answer each field individually?* This is one round (it may need
   a second `AskUserQuestion` call only if the user wants to edit more than fits in one call's options).
   Nothing from this table is written to `brief.md` until this confirmation happens.
4. Ask, via `AskUserQuestion` batches of ≤4, every field in brief-schema.md's "Always asked, never
   presumed" list for the casual profile: `D-02` (already have it from step 2), `D-03`, `D-07`, `D-08`,
   `D-11`, `D-12`, `D-41`, `D-37`, `D-45`, `D-46`, `D-47`. Accept `UNDECIDED` wherever the user declines,
   recorded verbatim — this applies to `D-45`/`D-46`/`D-47` exactly as to any other field; a missing KPI
   target, ad network, or build-size cap is `UNDECIDED`, never a guess.
5. Confirmed preset rows are written to `brief.md` with `Source: casual preset — confirmed by user`;
   edited rows are written with the edited value and `Source: casual preset — edited by user`; rejected
   rows fall back to being asked individually and get the normal `Source: asked`.
6. Render `brief.md` using `brief-template.md`'s shape, with three additional Section C rows appended
   for `D-45`, `D-46`, `D-47` (the template file lists only `D-30`–`D-44`; this profile appends these
   three rows to the *rendered instance* in the same table shape — it does not require editing
   `brief-template.md` itself). Add `· Profile: <hyper-casual|casual>` to the header line alongside the
   existing `Target:`/`Language:` fields. Show the rendered brief and ask the final confirmation:
   *Freeze this brief?* Do not proceed until they confirm.
7. Write the frozen text to `WORK/brief.md` and write `WORK/run-meta.md` with: date, kit version, `D-15`,
   sha256 of the frozen brief text, **and a `profile: casual` or `profile: hyper-casual` line** — this
   line is load-bearing: `/gdd-forge:review` reads it to pick lite checklists/contracts over full ones,
   falling back to detecting `1_Concept.md` + `2_Core Gameplay.md` in the folder when the line is absent
   (e.g. a `run-meta.md` from before this profile existed). Write this line for both sub-profiles, not
   just one.
8. Create `OUT`/`WORK` with a provisional slug (kebab-case of `D-01` if it is a real title, else
   `untitled-game`), exactly as the full flow does. Naming resolves in the W1 naming step below — this
   profile has no `gdd-namer` dispatch.

## Wave table

| Wave | Dispatch(es) | Model | Blocks on | Inputs delivered | Why |
|---|---|---|---|---|---|
| W1 | `gdd-concept-architect` → `1_Concept.md` | opus | brief frozen | whole `brief.md` | anchor file; no upstream lite file exists yet |
| W2 | `gdd-mechanics-designer` → `2_Core Gameplay.md` | opus | file 1 complete | whole `1_Concept.md` (not sliced — see below) + `brief.md` | single dispatch, not contended by parallel siblings |
| W3 | `gdd-ux-designer` → `3_UX Art and Audio.md` ‖ `gdd-producer` → `4_Business and LiveOps.md` ‖ `gdd-tech-designer` → `5_Tech Note.md` | sonnet ×3 | files 1+2 complete | `_anchor.md` + slices of files 1 and 2 (see below) | all three read only files 1/2, never each other — genuinely independent |
| W4 | `gdd-reviewer` → `review-report.md` (optional) | sonnet | files 1–5 complete, GAPs patched | whole files 1–5 + `brief.md` + `gap-log.md` (never sliced — see below) | consistency check only, skippable |

Waves are serial for the same reason as the full flow: each dispatch's *Consumes* list in the matching
`contracts-lite/lite-N.md` must already be on disk.

### Input slicing

The full flow's `KIT/scripts/extract-sections.sh <source> <dest> <spec>...` (specs like `4.5`,
`4.3-4.6`, or `all`) is available here too, and this profile uses it **only where it actually saves
tokens** — it is not a hard dependency of any dispatch:

- **After W1**, build the anchor once: `extract-sections.sh <OUT>/"1_Concept.md" <WORK>/inputs/_anchor.md
  1.4 1.9` (pillars + glossary). Every dispatch from W2 onward that is given anything less than the whole of
  `1_Concept.md` should also receive `_anchor.md` so it always has the pillars to cite and the glossary
  to reuse verbatim, regardless of what else it was sliced.
- **W2** is a single, uncontended dispatch reading only one upstream file that targets 3–5 KB. Slicing it
  adds a script call for no measurable saving — give it the whole `1_Concept.md` file directly, and skip
  `_anchor.md` too (redundant once the whole file is already in hand).
- **W3 is where slicing earns its keep**: three parallel dispatches would otherwise each read two whole
  upstream files, tripling the duplicated token cost of content most of them never use. Build, right
  after W2 completes:
  - UX: `extract-sections.sh <OUT>/"1_Concept.md" <WORK>/inputs/ux-1.md 1.7 1.8` and
    `extract-sections.sh <OUT>/"2_Core Gameplay.md" <WORK>/inputs/ux-2.md 2.1 2.3 2.8` (§3.4 FTUE ties to
    §2.8's first stage)
  - Business: specs `1.5 1.7` from file 1, `2.1 2.3 2.4 2.6 2.9` from file 2 (§4.2 ties ad placement to
    §2.1/§2.6 moments, §4.5 names a §2.3 mechanic)
  - Tech: specs `1.7` from file 1, `2.6 2.8` from file 2
  Each W3 dispatch gets `_anchor.md` plus its own two slice files.
- **W4 (review) is never sliced.** `gdd-reviewer`'s own contract is explicit that it reads full chapters,
  "not excerpts — contradictions hide in details"; that discipline applies here unchanged.
- **Fallback**: if `KIT/scripts/extract-sections.sh` is missing or fails for any reason, fall back to
  giving the affected W3 dispatch the whole file(s) instead of blocking the run on the script's
  existence. Note the fallback in that dispatch's entry in `run-meta.md` so a later resume knows slicing
  wasn't used.

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
5. Only then build `_anchor.md` and start W2.

## Lite dispatch envelope

Assemble every W1–W4 prompt from this envelope (the counterpart to `pipeline.md`'s § W2–W7 envelope):

```
ROLE: you are <agent> writing <lite file> for the GDD of "<game_name>" (lite profile — <hyper-casual|casual>).
LANGUAGE: write the body in <D-12>. Keep heading numbers in English ("# 2. Core Gameplay").
CONTRACT: read <KIT>/references/contracts-lite/lite-<n>.md in full. Obey Sections, Depth rule, Hard rules.
INPUTS (read all, read nothing else):
  - <WORK>/brief.md
  - <WORK>/inputs/_anchor.md (pillars + glossary), when provided — see wave table for which dispatches get it
  - <OUT>/<consumed lite file(s)>, whole file OR <WORK>/inputs/<name>.md — see wave table for which
  - template: <KIT>/templates/lite/<tmpl>
  - checklist: <KIT>/checklists/lite/<check>
  - data: <KIT>/data/<file>, and <KIT>/data/casual/<file> only where the contract names it
OUTPUT: write exactly one file <OUT>/<lite file>.
RULES:
  1. DECISIONS come only from brief.md. If a section needs a decision that is missing or UNDECIDED and
     the Depth rule doesn't say what to do, do NOT invent it — write the section header, a one-line
     placeholder "⟂ GAP G-<file>-<n>: <what is needed>", and list it under GAPS in your report. If the gap is
     that this pitch actually needs the full profile (real narrative/AI/multiplayer/console-PC), say so
     explicitly in the GAP text rather than writing around it.
  2. Design elaborations are yours. Mark tunables "(tunable)", estimates "(est.)", targets "(target)".
  3. No external facts unless present in brief.md or the data files you were given. Otherwise write "no
     data available".
  4. Use the Glossary from 1_Concept.md §1.9 verbatim (or from `_anchor.md` if that's what you were
     given). New terms go under a "New terms" note at the end of your file.
  5. End with an "Open Decisions" box listing every UNDECIDED brief field you touched and every GAP.
  6. Self-check against your checklist before reporting. Items tagged `[R]` are reviewer-only: count them
     as n/a, not failing. Fix what you can; report the rest.
REPORT (last thing in your final message, exact format — identical shape to the full flow's):
  ## REPORT
  STATUS: complete | complete-with-gaps | blocked
  FILE: <absolute path>
  WORDS: <n>
  GAPS:
    - G-<file>-<n> | field: <D-xx or description> | section: <§> | why: <one line> | suggested options: <a / b / c>
  CHECKLIST: <passed>/<total> — failing: <ids or none>
  NEW_TERMS: <list or none>
  CROSS_REFS_CITED: <file §list>
```

Dispatch W1 alone; dispatch W3's three calls in **one message**, `run_in_background: true`, then wait for
all three before proceeding — same mechanics as the full flow's parallel waves. Save each `## REPORT`
block verbatim to `WORK/reports/<file>.report.md` as it arrives.

**PATCH mode** (used only during § GAP handling, never mid-wave): identical shape to the full flow —
`PATCH MODE: <file> exists. Replace only the placeholder(s) G-<file>-<n> and any sentence that directly depends
on them. Do not rewrite other sections. Re-run your checklist. Report as usual.` Use `Edit`, never
`Write`, in PATCH mode.

## GAP handling — collected once, asked once, at the end

**This profile does not ask GAP questions between waves.** It collects every `G-n` from every REPORT
across W1, W2, and W3 into `WORK/gap-log.md` as they arrive, and asks them all together in one place —
after W3 finishes, before W4 — rather than after each of the four waves. State this rule explicitly to
the user if they ask why the gate feels quieter mid-run than the full flow's. GAP ids are `G-<file>-<n>`
(`<file>` = lite file number 1–5, `<n>` restarts per file), so W3's three parallel agents never collide.

**Why**: three reasons, all specific to this profile's shape, not a shortcut taken for its own sake.

1. **No lite file's drafting depends on another lite file's GAP resolution within this run.** In the full
   flow, ch6 genuinely cannot be written well until ch4/ch5's open questions are settled, because ch6
   reads their finished text. Here, W3's three files read only files 1 and 2 — never each other — so a
   GAP in `3_UX Art and Audio.md` cannot block `4_Business and LiveOps.md`'s drafting, and neither can
   block `2_Core Gameplay.md`, which is already finished before either starts. Asking mid-pipeline buys
   no downstream-consistency benefit here that it buys in the full flow.
2. **Casual-scope GAPs are overwhelmingly tunable, not structural.** A missing D-45 KPI target or an
   unresolved D-46 ad network doesn't reshape a design the way a missing narrative premise reshapes ch6's
   level list — it leaves one table cell open. Deferring resolution to one batch rarely wastes drafting
   work the way it might in the full flow's more interdependent chapters.
3. **The profile's entire value proposition is fewer interruptions, not just fewer dispatches.** Asking
   after every one of 4 waves could mean up to 4 separate `AskUserQuestion` interruptions for a flow
   explicitly designed to be fast. Batching to one round (split into ≤4-question calls only if volume
   requires it) preserves that.

Procedure: after W3's three reports are in, de-duplicate all collected `G-n` by field, ask via
`AskUserQuestion` (≤4 per call, offering each agent's own suggested options plus "Leave UNDECIDED"),
write answers into `brief.md` under `## Gate additions (lite)` with the G-id, and log the Q/A in
`gap-log.md`. For every real (non-UNDECIDED) answer, re-dispatch the owning agent in PATCH mode for that
one file — these patch dispatches are **additional** to the 6-dispatch baseline (see § Token cost); a
clean brief with no GAPs costs exactly 6. For every "Leave UNDECIDED" answer, the placeholder stays;
it surfaces in that file's own Open Decisions box (there is no Appendices register in this profile to
collect it centrally).

## W4 — Lite review (optional)

Ask the user once, after GAP patches are applied: *run the lite consistency review, or skip straight to
assembly?* If they skip, `0_Index.md` §0.3's checklist-pass column reads "lite review skipped" for every
row, and Done still reports normally.

If run: dispatch `gdd-reviewer` with all five finished lite files, `brief.md`, `gap-log.md`, every
`references/contracts-lite/lite-N.md`, `KIT/references/consistency-rules-lite.md`, and every
`checklists/lite/*.md`. It writes `WORK/review-report.md` in the same Blockers/Majors/Minors shape the
full flow uses, checked against `KIT/references/consistency-rules-lite.md` (the 8 lite rules — same
concerns as the full kit's, renumbered for 5 files).

**Blockers** → ask the user, patch the owner (same as § GAP handling). **Majors** → PATCH mode dispatch
to the named owner once. **Minors** → listed, not auto-fixed; each file's own Open Decisions box is the
only register, so a Minor about a missing box entry should itself be fixed in the same PATCH pass as any
Major touching that file, not left dangling. After patches, do not re-run the full review — a short
RECHECK dispatch to `gdd-reviewer`, limited to the patched files and the 8 rules, is enough.

## 0_Index.md — assembled by the orchestrator, not dispatched

Once files 1–5 are final (and W4's report, if it ran), the orchestrator writes `0_Index.md` itself,
following `templates/lite/0-index.md` and `contracts-lite/lite-0.md` directly — no `Agent` call. Pull
§0.1–§0.3 verbatim from the finished files and saved REPORT blocks; never estimate a word count or a
checklist percentage you don't have written evidence for. This keeps the profile at exactly 6 dispatches
in the clean-run case: W1(1) + W2(1) + W3(3) + W4(1) = 6, with `0_Index.md` free.

## Done — tell the user

- Absolute path of `OUT`, the six-file list with word counts (from the REPORTs).
- Whether W4 ran, and if so, Blockers/Majors/Minors counts.
- Number of Open Decisions across all five files (sum, since there's no central register).
- One line offering to: (a) re-run a single file with new inputs (`--file N`), (b) bump the version, (c)
  escalate to the full profile if scope grew, (d) run `/gdd-forge:review` later.

## Single-file re-run — `--profile casual --file N`

The counterpart to the full flow's `--chapter N`. `N` is the lite file number, 1–5.

1. Load `WORK/brief.md`; confirm `run-meta.md` shows `profile: casual` or `profile: hyper-casual` — if
   it doesn't, this is a full-profile output directory, stop and point the user at `pipeline.md`'s
   `--chapter` instead.
2. Ask the user only for fields file `N`'s contract lists under *Consumes* that are currently `UNDECIDED`.
3. Re-dispatch file `N`'s owning agent fresh (not PATCH mode), with the same inputs its wave normally
   gets (whole file or slice, per § Wave table — rebuild `_anchor.md`/slices first if `N = 1` or `N = 2`
   changed content those depend on).
4. If `N = 1`: the pillars/glossary anchor may have changed. Do **not** automatically cascade a rerun of
   files 2–5 — warn the user that downstream files may now be stale relative to the new `1_Concept.md`,
   and offer to also re-run the affected ones, but only on their explicit confirmation (re-running them
   unasked would be an invented decision about what the user wants redone).
5. Append one row to `1_Concept.md` §1.1's version table noting the rerun (version bump, date, what
   changed) — this is the profile's one piece of version history, so every rerun touches it regardless of
   which file `N` actually was; do this as a direct `Edit`, not a subagent dispatch.
6. Re-assemble `0_Index.md` only (no `13_Appendices.md` equivalent exists in this profile).

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
5. Resume at the first wave whose file(s) are not all done. If resuming into W3, rebuild `_anchor.md` and
   the relevant slice files first if they're missing (W1/W2 finished but the session ended before slicing
   ran). Then continue W1→W4 forward normally, including the single end-of-run GAP batch.
6. If `review-report.md` exists but `0_Index.md` does not, resume at 0_Index assembly directly.

## Failure modes

| Situation | Orchestrator does |
|---|---|
| Agent returns `blocked` | Read its GAPS; if one says "this needs the full profile," treat it as an escalation trigger (see § When not to use this profile) rather than a normal GAP; otherwise ask the user and re-dispatch fresh. |
| Agent wrote to the wrong path | Move the file; note it in `run-meta.md`; do not re-run. |
| Agent invented a decision (Lite Consistency rule 6 FAIL) | PATCH mode with the exact sentence to remove; log it in `gap-log.md` as "fabrication caught". |
| `extract-sections.sh` missing/fails for a W3 slice | Fall back to whole-file input for that dispatch (see § Input slicing); do not block the run. |
| User abandons mid-run | Everything so far is on disk in `OUT`/`WORK`; say so and how to resume (`--profile casual --resume <OUT>`). |

## Token cost — lite vs full

The full flow costs roughly 20 subagent dispatches and on the order of a million input tokens across the
whole run (`README.md` §4 gives the ~20-dispatch figure; the token figure is this file's own estimate and
is stated nowhere else in the kit). This profile's clean-run baseline is 6 dispatches — about
30% of the full flow's dispatch count — and each dispatch reads at most two upstream files (often just a
slice of each) instead of the full flow's later waves, which can read four or five finished chapters at
once (e.g. `12_Management.md` reads six upstream sections across four chapters). Combined with templates
targeting 3–5 KB each (versus the full profile's longer per-chapter templates) and no separate naming,
narrative, level-design, AI, art-direction, or tooling waves, a reasonable estimate is on the order of
**10–15% of the full flow's total input tokens (est.)** — roughly 100–150K tokens rather than ~1M. This
is a reasoning-based estimate from dispatch count and per-dispatch input size, not a measured benchmark;
treat it the same way this profile treats every other unsourced number — as an `(est.)`, not a promise.

## Agent roster (lite profile)

| Agent | Model | Lite file | Full-profile equivalent |
|---|---|---|---|
| `gdd-concept-architect` | opus | 1 (`1_Concept.md`) | ch 3 (+ thin ch1/ch2/ch5) |
| `gdd-mechanics-designer` | opus | 2 (`2_Core Gameplay.md`) | ch 4 (+ ch6, ch8) |
| `gdd-ux-designer` | sonnet | 3 (`3_UX Art and Audio.md`) | ch 7 (+ ch10, game-feel) |
| `gdd-producer` | sonnet | 4 (`4_Business and LiveOps.md`) | ch 12 |
| `gdd-tech-designer` | sonnet | 5 (`5_Tech Note.md`) | ch 9 (+ ch11) |
| `gdd-reviewer` | sonnet | (review, optional) | review |
| — orchestrator — | — | 0 (`0_Index.md`) + the §1.1 game-name line | ch 0 (`gdd-scribe`) |

No `gdd-namer`, `gdd-narrative-designer`, `gdd-level-designer`, `gdd-ai-designer`, or `gdd-art-director`
dispatch exists in this profile — their full-profile responsibilities are either folded into the five
agents above under the lite contracts, or out of scope per § When not to use this profile.
