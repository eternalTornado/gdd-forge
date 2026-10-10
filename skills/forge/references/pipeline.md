# Pipeline — how `/gdd-forge:forge` runs

The orchestrator is the **main conversation agent** (the one running this skill) and the only party that talks to the user. It runs the W0 gate, then drives one named workflow, `forge-run` (`workflows/forge-run.js`), segment by segment until the GDD is done. The workflow makes every dispatch and its own bookkeeping; it cannot call `AskUserQuestion`, so when it needs the user it stops at a **checkpoint** and you ask. Never dispatch a pipeline agent yourself with the `Agent` tool.

```
W0 Gate ─► W1 Name ─► W2 ch3 ✓ ─► ◆ anchor ─► W3a ch4 ✓ ─► W3b ch5 ✓ ─► W4 ch6 ‖ ch7 ✓ ─► W5 ch8 ‖ ch10 ✓
        ─► W6 ch9 → ch11 ✓ ─► W7 ch12 ✓ ─► W8 Review ✓ ─► W9 Fix ⟲ until clean (≤ 2 rounds, then ask)
        ─► W10 (ch1 → ch2) ‖ ch13 → 0_Index → completeness critic ─► Done
```
`✓` = adversarial verification (W8: of every finding). `◆` = the anchor checkpoint, the only stop that always happens; other stops come only when input is needed. `‖` = parallel. `→` = sequential: the right-hand file starts once the left-hand one is on disk.

## Paths the orchestrator computes once

| Var | Value |
|---|---|
| `KIT` | `${CLAUDE_SKILL_DIR}` (folder of this skill: `references/`, `templates/`, `checklists/`, `data/`, `scripts/`) |
| `OUT` | `brief:D-14` resolved to an absolute path, default `<cwd>/deliverables/<slug>/GDD/<D-15>/` |
| `WORK` | `OUT/_work/` — `brief.md`, `gap-log.md`, `run-meta.md`, `review-report.md`, `fact-ledger.md`, `reports/` (REPORT blocks), `checks/` (verification notes) |
| `INPUTS` | `WORK/inputs/` — slices the workflow builds |
| `agent_ns` | `gdd-forge:` when the available agent types list `gdd-forge:gdd-<role>` (plugin install); `''` when they list bare `gdd-<role>` (copied into `~/.claude/agents/`) |
| workflow | `Workflow({name: "gdd-forge:forge-run", args})` under a plugin install; for a local copy, or when the name is not found, `Workflow({scriptPath: "<absolute KIT>/../../workflows/forge-run.js", args})` |

Resolve `agent_ns` and the workflow form once, before W0 step 8, and record both in `run-meta.md` (`agent_namespace:`, `workflow:`). `slug` = kebab-case of the chosen game name, ASCII only. Every path in `args` is absolute — subagents never guess paths. This document writes bare role names.

## W0 — Gate (orchestrator)

Follow `brief-schema.md` exactly. Outcome: `WORK/brief.md` in the format of `brief-template.md`, frozen after the user confirms.

1. Parse the opening message (or the loaded brief file). Fill every `D-xx` you can find verbatim — do not paraphrase into a different meaning.
2. Refuse to proceed while D-02 (pitch) is empty — it is the one hard requirement. Everything else may be `UNDECIDED` subject to the required-set table for D-15.
3. Ask only for missing fields, via `AskUserQuestion`, ≤ 4 questions per call, grouped by brief-schema section (A → B → C), in the default order given in brief-schema.md "Gate question ordering". Offer the listed options under the ≤ 4-option rule stated after step 8 ("Other" is automatic). Skip any field already answered.
4. Ask trigger fields (D-20…D-24, marked ⚡) before their dependants; skip a dependant whose trigger is off.
5. Accept `UNDECIDED` whenever the user declines ("skip", "TBD", "chưa biết") — record it verbatim, never substitute a default.
6. Check the required-set table for the chosen D-15 (version). Every field in that set must be resolved (not `UNDECIDED`) before you can freeze; if one is missing, ask for it even if it wasn't in the default order.
7. Render the brief using `brief-template.md`, show it to the user, and ask the final confirmation: *Freeze this brief?* Do not proceed until they confirm.
8. Write the frozen text to `WORK/brief.md` (brief-template.md format), `WORK/run-meta.md` (date, kit version, D-15) — shape: `references/run-meta-template.md` — and `WORK/gap-log.md`, starting with just the header row — shape: `references/gap-log-template.md`. Create `OUT`/`WORK` with a provisional slug (see "Provisional paths" below); never write chapters into a provisional directory.

`AskUserQuestion` accepts at most 4 options per question ("Other" is added automatically). For a field whose option list is longer than 4: write the full option list into the question text, offer as the 4 options the values most consistent with what the user has already said (or, with no signal, the first 4 listed), and tell the user to type any other listed value via Other. For multi-select fields (D-04, D-22, D-30, D-38, D-39, D-40) set `multiSelect: true`; if more than 4 values are plausible, split the list across two questions in the same call. Never omit a listed option from the question text, and never pre-select a value on the user's behalf.

**Provisional paths.** `slug` is not known until W1, but `brief.md` must be on disk before the namer runs. Create `OUT`/`WORK` in W0 with a provisional slug: kebab-case of D-01 if it is a real title, else `untitled-game`. After W1 fixes the real name, rename the `<slug>` directory and update `run-meta.md`. Never write chapters into a provisional directory — renaming happens before W2.

## The main loop

After W0 and the keep-title question (§ W1), loop until `done`:

1. Call the workflow with `args`. One call = one **segment**: it runs from `from` until it needs the user, finishes or fails. One segment at a time.
2. `checkpoint` → ask the user per `kind` (`name` § W1 · `anchor` § W2 · `gaps` § GAP handling · `blockers` § W8 · `residual` § W9), write the answers to disk (`brief.md` Gate additions, `gap-log.md`), build `resolutions`, tell the user in one line what runs next, call again. `stage` = the stage that raised it (`resolve` when raised while applying your answers); `next` = where to continue.
3. `done` → § Done. `error` → § Failure modes.

State lives only in `OUT`/`WORK`, so the loop survives a new session (§ Resume; never `resumeFromRunId`). Shapes of `args`, `RESOLUTION` and returns: SKILL.md § Workflow contract.

| Arg | Value |
|---|---|
| `mode` · `profile` | `run` (`chapter`: § Re-running a single chapter later) · `full` |
| `from` | `W1` first, then the checkpoint's `next` (except *One more round*, § W9) |
| `target` · `date` | mode `chapter` only: N · today's ISO date |
| `paths` · `agent_ns` | `{kit, out, work, inputs}`, recomputed after the rename · § Paths |
| `game_name` · `lang` · `version` | brief `game_name` (D-01 until named; omit while D-01 ∈ {GENERATE, UNDECIDED}) · D-12 (bodies; headings keep the English numbered prefix) · D-15 |
| `flags` | `d21` = the D-21 option without its parenthetical (`None`, `Light framing`, `Medium`, `Story-driven`) · `d22` = `None` when D-22 = None, else its values · `f2p_or_hybrid` · `need_name` |
| `data` · `model_override` | § Data slices · omit (§ Model routing) |
| `resolutions` · `extra_round` | `[]` or the previous checkpoint's answers · `true` only for one more fix round (§ W9) |

Never paste chapter bodies into `args`: an `answer` is the user's words, a `file` is a path.

## Data slices

Chapter agents get only the data files in `args.data` (plus the fixed pattern files). Before the first call, apply each directory's `_index.md` selector rules to the frozen brief and pass absolute paths of **only** the selected files:

- `platforms` ← D-04 (`data/platforms/_index.md`).
- `monetization` ← D-06 and the secondary fields its index names (`data/monetization/_index.md`). `flags.f2p_or_hybrid` = D-06 ∈ {F2P + IAP, F2P + Ads, Hybrid}: ch 4 gets these slices only when true; ch 12 always.
- `cultural` ← D-05's region + D-38 (`data/cultural/_index.md`).
- `accessibility` ← D-39, plus D-04 / D-40 / D-05 as its index says (`data/accessibility/_index.md`).

If a Gate addition changes a selector field, pass recomputed lists on the next call.

## W1 — Name

1. Right after the freeze, if `D-01` is a real title, ask once: *Keep "<title>" as the game name?* (Keep / Generate alternatives). Keep → `need_name: false`, `game_name` = D-01, provisional slug final; write both under `brief.md` `## Chosen game name` now (§ Resume reads it). Generate alternatives, or `D-01 ∈ {GENERATE, UNDECIDED}` (UNDECIDED is treated as GENERATE) → `need_name: true`.
2. First call `from: 'W1'`. Without `need_name`, W1 is a no-op and the segment runs on into W2. With it, `gdd-namer` runs and the `name` checkpoint returns 8 ranked `candidates` (rationale, pronounceability, conflicts — the agent cannot check trademarks; tell the user).
3. Ask with `AskUserQuestion`: top 4 as options (label = name, description = rationale). Free text via Other is the name.
4. Write `game_name` and `slug` under `brief.md` `## Chosen game name`, rename the provisional `<slug>` directory if it differs, update `run-meta.md` (`slug:`, `out:`), then call `from: 'W2'` with the new `paths`, `game_name` and `need_name: false`.

## W2 — Anchor chapter and anchor checkpoint

The segment writes and verifies ch 3 (`concept-architect`), builds `INPUTS/_anchor.md`, and always stops at the `anchor` checkpoint — nothing downstream runs before the user approves.

1. Show `anchor.pillars` (name · meaning · forbids) and `anchor.features` (name · priority · pillar) as two tables; ask *Approve the anchor?* — Approve / Request changes, notes via Other (no notes → ask what to change). Ask the checkpoint's `items` in the same round (§ GAP handling).
2. **Approve** → `{id: 'ANCHOR', action: 'approved'}` (or omit it); call from `next` with the item resolutions.
3. **Request changes** → write the notes to `brief.md` under `## Gate additions (W2 anchor review)`, add `{id: 'ANCHOR', file: <checkpoint file>, owner: 'concept-architect', class: 'structural', action: 'fresh'}`, give ch 3's items `fresh` too (never Edit a file about to be rewritten), call from `next`. The workflow rewrites and re-verifies ch 3, rebuilds the anchor and returns this checkpoint again. Repeat until Approve.

## W3–W7 — Chapter waves

Order and owners: SKILL.md § Waves at a glance. Waves are serial — every chapter's *Consumes* list (`references/contracts/ch<NN>.md`) must already be on disk — and a segment runs as many as it can. Per wave the workflow:

1. **slices** the inputs: each dispatch reads `INPUTS/_anchor.md` (ch 3 §3.2 pillars + §3.10 glossary, reused verbatim; rebuilt whenever ch 3 changes) plus its `SLICES` entry in workflows/forge-run.js — `whole` chapters passed as they are (ch 3 → ch 4/5; ch 9 → ch 11), `parts` cut into `INPUTS/ch<N>/` by `KIT/scripts/extract-sections.sh`;
2. **dispatches** each owner with the chapter envelope (`writePrompt`) — paths only; the agent returns its `## REPORT` block (`dispatch-rules.md` §4) as structured output;
3. **verifies** each new file (finder → 3 voters per Major, ≥ 2 upholds → one owner auto-PATCH for those needing no decision; the rest become `V-` items; `blocked` files skipped);
4. **bookkeeps** (clerk): REPORTs verbatim to `WORK/reports/`, `wc -w` into `run-meta.md` § Waves `Words` (the kit's only word count), § Waves rows, `gap-log.md` rows for new G-ids, `WORK/checks/<file>.check.md`;
5. **stops** with a `gaps` checkpoint only for items or a `blocked` file; otherwise runs the next wave.

W8 reads whole chapters; W10 reads its own extracts (§ W10). A `MISSING:` slice line is never dispatched around: the workflow PATCHes the upstream owner once — restore the heading plus `N/A — <reason, ≤ 12 words>.` if a Depth rule removed it (`dispatch-rules.md` §2, rule 10), else write the section — re-slices, and errors if still missing. A Depth-rule N/A section that keeps its heading is a valid slice.

Never read chapter bodies to steer the run (of a REPORT, § Resume reads only the `STATUS:` line); open a chapter only for a `value`-GAP Edit.

## GAP handling — every checkpoint with `items`

Ids: `G-<ch>-<n>` (an agent's GAP; `<ch>` = its chapter, so parallel agents never collide) · `V-…` (a verified finding needing a decision) · `R-<n>` (a review finding). Each item: `file` (absolute), `owner`, `class` (`value` | `structural`, `dispatch-rules.md` §1), `field`, `section`, `why`, `options`.

1. De-duplicate against `gap-log.md`: an id or field already answered → reuse the answer, never re-ask. A field raised by several files is asked once.
2. Ask with `AskUserQuestion` — ≤ 4 per call — using the item's options plus an explicit "Leave UNDECIDED" (≤ 4 options each; longer lists per the rule after W0 step 8). If an answer contradicts a frozen brief value or a pillar, ask the user which one yields before writing anything.
3. Write each answer into `brief.md` under `## Gate additions (<checkpoint stage>)` with its id. In `gap-log.md`, fill Question asked / Answer / Answered on of a G-id's row (the workflow wrote it); a V- or R-id gets a new row (Raised by `verify` / `review`).
4. Build one resolution per answer (`id, file, owner, class, answer, action, cascade, sections`), choosing `action` by class:
   - **`value`** — fills in one value; nothing else about the file changes. Replace the `⟂ GAP` line (or the one value the item names) yourself via `Edit` — the value and its unit, no added prose — and remove the item from that file's Open Decisions → `edited` (fill its gap-log Patched files yourself). More than ~3 lines depend on it → `patch` (the owner replaces only the placeholder and what depends on it, `dispatch-rules.md` §3).
   - **`structural`** — changes what a feature, flow or section *is* → `fresh`: the owner rewrites the whole file, then it is re-verified.
   - The agent only proposes the class; upgrade `value` → `structural` whenever the answer introduces something the suggested options did not (a new feature, mode, screen, flow).
   - A fact owned by an upstream file (the chapter whose contract Sections list defines it) is fixed in the **owning** file: point `file`/`owner` there, `cascade: true`, `sections` = its §x.y. The workflow fixes the owner, then PATCHes every citing file ("align only what cites it").
   - "Leave UNDECIDED" → `undecided`: the placeholder stays for the Appendices register; nothing is re-dispatched.
   - A file in the checkpoint's `blocked` list → always `fresh`.
5. Call again from `next`. The workflow applies every resolution first (upstream files, then cascades), so downstream chapters read the corrected text; items raised meanwhile return as another checkpoint with the same `next`.

**PROPOSALS are never asked mid-run** (`dispatch-rules.md` §1) — leave every `(proposal)` exactly as the agent wrote it. The Done message reports their count and where they live; the user may answer any of them later, at which point treat the answer like a `value`/`structural` GAP above (a `structural` one through § Re-running a single chapter later).

## W8 — Review

Nothing to do unless Blockers survive. In parallel: `gdd-reviewer` on its normal contract (writes `WORK/fact-ledger.md`, `WORK/review-report.md`) ‖ the four `LENS_FINDERS` (contradictions · brief fidelity · closure · hygiene). Findings are merged; each Blocker/Major is judged by three voters (≥ 2 upholds survive), each Minor by one evidence check; `review-report.md` is rewritten with verified findings only: Blockers · Majors · Minors · Checklist matrix · Consistency rules 1–12 · `## Verification` counts.

Blockers → `blockers` checkpoint (R-ids) → § GAP handling → call from `next` (`W9`). None → W9 runs in the same segment.

## W9 — Fix loop (until clean, ≤ 2 rounds per segment)

- **Minors** → a clerk step fixes those ≤ 2 lines needing no design judgement (SKILL.md § Non-negotiables, exception 2); the rest are listed, unfixed, in Appendices §G.
- **Majors**, per round → one PATCH per owner file (the file the finders and voters named), in parallel.
- **RECHECK** each round: `gdd-reviewer` RECHECK (patched files, rules 1–12, their fact-ledger rows) ‖ a regression lens → merge → verify as in W8. Open or new Majors → next round. The full review is never re-run.
- New Blockers → `blockers` checkpoint with `next` = `W9`; the loop resumes after the answers.
- Clean → W10 in the same segment. Majors left after the cap → `residual` checkpoint: list them (id · file · what), ask *One more fix round* / *Accept as known issues*. One more → `{id: 'RESIDUAL', action: 'another_round'}`, call from `stage` (`W9`) with `extra_round: true` (one round; may return `residual` again). Accept → `action: 'accept'`, call from `next`; they stay open in the report. Log the choice in `gap-log.md` per R-id.
- Bookkeeping (clerk): `review-report.md` `## Fix loop` (id · severity · file · status · round); `run-meta.md` § Fix loop (`iterations` 0–N, every round counted; patched chapters; RECHECK summary), read by `2_Version History.md` §2.2.

## W10 — Boilerplate & assembly

No checkpoint; the segment ends with `done`.

1. **Pre-extraction** (clerk): `INPUTS/ch13/ch<N>.md` per chapter 3–12 — `@Open Decisions`, `@New Terms` and the `CH13_EXTRA` sections. `ABSENT: @New Terms` is normal; a failed extract falls back to the whole chapter (logged).
2. **W10a**, in parallel: `gdd-scribe` → `1_Copyright Information.md` then `2_Version History.md` (one dispatch, no chapter inputs) ‖ `gdd-scribe` → `13_Appendices.md` (from the extracts).
3. **Abstracts**: the `intro` of chapters 1–13 → `INPUTS/ch00/abstracts.md`.
4. **W10b**: `gdd-scribe` → `0_Index.md`, only after 1, 2 and 13 exist.
5. **Completeness critic**: files and template headings present, every `⟂ GAP` logged, every UNDECIDED field in an Open Decisions box and §D, counts consistent across 0_Index, Version History, run-meta and review-report. Findings on 0/1/2/13 → one scribe PATCH; others → the summary's `issues`.

## Model routing

The workflow picks every dispatch's model; `TIERS`, `ROLE_TIER` and `tierFor` in workflows/forge-run.js are the only place the kit chooses one. No agent frontmatter pins a model; you never pass one. Tiers: `deep` (the session's model, or `CLAUDE_CODE_SUBAGENT_MODEL`) for design judgement and verification · `spec` (a lighter model) for template-driven writing and merging · `clerk` (the same at low effort) for bookkeeping; per role: SKILL.md § Agent roster. Ch 5 drops to `spec` when `flags.d21` ∈ {None, Light framing}, ch 8 when `flags.d22` = None (mostly `N/A —` lines). Re-dispatches use the owner's tier; run-meta § Waves `Model` records the tier's model (`session` when inherited). `model_override` only when the user explicitly asks for one model for every dispatch: it replaces every tier; pass it on every later call.

## Done — what the orchestrator tells the user

From the `done` summary:

- Absolute path of `OUT` (`out`) and the file list with word counts (`files`, as in `run-meta.md` § Waves `Words`).
- Number of Open Decisions (`open_decisions`) and of `(proposal)`s (`proposals`), and where they live (Appendices §D, each chapter's Open Decisions).
- Number of Minors left (`minors_left`), any Majors accepted at `residual` (open rows of `review-report.md` § Fix loop), and each entry of `issues`.
- Offer, in one line, to (a) re-run a single chapter with new inputs, (b) bump version, (c) run `/gdd-forge:review` later.

## Resume (`--resume <OUT>`)

1. Read `WORK/run-meta.md` and `WORK/brief.md`; confirm the brief is frozen (else restart W0 from what exists). Reuse `agent_namespace:` and `workflow:` (resolve again if absent); recompute `paths`, `flags`, `data`.
2. List `OUT/*.md`. A chapter counts as done only if its file exists **and** `WORK/reports/<file>.report.md` shows `STATUS: complete` or `complete-with-gaps`.
3. `from`, first match wins:
   - `brief.md` `## Chosen game name` still the template placeholder → `W1` (ask the keep-title question again if D-01 is a real title);
   - a wave W2–W7 whose chapters are not all done → the first one (the workflow re-runs it whole);
   - no `review-report.md` → `W8`;
   - Blockers (`## Blockers`, or open Blocker rows in `## Fix loop`) with no gap-log answer → ask them first (§ GAP handling), then `W9`;
   - no `## Fix loop` → `W9`;
   - open Major rows in `## Fix loop` that gap-log does not mark accepted → ask the § W9 residual question first (`W9` + `extra_round`, or `W10`);
   - otherwise `W10`.
4. Ask what an interrupted `gaps` or `anchor` checkpoint left open — `gap-log.md` rows with an empty Answer, "asked the user" findings in `WORK/checks/*.check.md` that gap-log does not answer (match by section + what: a note carries the finder's `F-` id, not the `V-` id, and no options) — and pass the resolutions on the first call. If ch 3 is the last file done, the anchor may be unapproved: offer to review it (`from: 'W2'` rewrites ch 3 and returns the checkpoint) or continue from `W3a`. Then run § The main loop.

## Re-running a single chapter later

`/gdd-forge:forge --chapter N` (or natural language):

1. Load `WORK/brief.md`; ask only for fields chapter N consumes that are still `UNDECIDED`, written as Gate additions. Compute `paths`, `flags`, `data` as for a run.
2. N ∈ 3–12 → `mode: 'chapter'`, `target: N`, `date`, `from: 'RERUN'`. **RERUN** re-slices from the chapters now on disk (`_anchor.md` too when N = 3), fresh-dispatches the owner, verifies, bookkeeps. Items → `gaps` checkpoint, `next` = `RERUN-POST` → § GAP handling → call from `RERUN-POST`.
3. **RERUN-POST**: scribe PATCH of `2_Version History.md` (one version row — patch bump of D-15's tag, `date`, "re-run of chapter N" — and one change-log bullet); `13_Appendices.md` then `0_Index.md` rebuilt; a verified regression lens on N against what it cites and what cites it; the completeness critic. Returns `done`; regression findings land in `issues`, unpatched.
4. N ∈ {0, 1, 2, 13} → `mode: 'run'`, `from: 'W10'`.
5. Report `issues` (offer to re-run the files they name) and the `stale` chapters (consumers of N per `SLICES`; all of 4–12 when N = 3); offer to re-run them — only on explicit confirmation, never cascade unasked.

## Failure modes

| Situation | Orchestrator does |
|---|---|
| `status: 'error'` | Tell the user `message`, fix what it names (or ask), call again from `stage` with `resolutions: []` (already applied); `stage: 'resolve'` or missing args → repeat the same call, args fixed. |
| upstream file not on disk | Resume from the wave that writes it (§ Resume). |
| slice still MISSING after a PATCH | Contract and template disagree: record it in run-meta § Discrepancies, tell the user, fix the kit's contract/template (or ask), call again from `stage`. Never `--chapter` mid-run: RERUN-POST needs W10's files. |
| a dispatch returned no result twice | Retry from `stage` once; if it fails again, stop and report. |
| Named workflow not found | Fall back to `scriptPath`; update run-meta `workflow:`. |
| File at the wrong path (critic `issues`) | Move it; note in run-meta; do not re-run. |
| Agent invented a decision (rule 7) | Verify and review PATCH it; if it reaches you as an item, answer it as a GAP and log "fabrication caught" in gap-log. |
| User abandons mid-run | Everything so far is on disk in `OUT`/`WORK`; say so and how to resume (`--resume <OUT>`). |
