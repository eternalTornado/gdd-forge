# Pipeline — how `/gdd-forge:forge` runs

The orchestrator is the **main conversation agent** (running this skill) and the only party that talks to the user. It runs the W0 gate, then drives one named workflow, `forge-run` (`workflows/forge-run.js`), segment by segment until the GDD is done. The workflow makes every dispatch and its own bookkeeping; it cannot call `AskUserQuestion`, so when it needs the user it stops at a **checkpoint** and you ask. Never dispatch a pipeline agent yourself with the `Agent` tool.

```
W0 Gate ─► W1 Name ─► W2 ch3 ✓ ─► ◆ anchor ─► W3a ch4 ✓ ─► W3b ch5 ✓ ─► W4 ch6 ‖ ch7 ✓ ─► W5 ch8 ‖ ch10 ✓
        ─► W6 ch9 → ch11 ✓ ─► W7 ch12 ✓ ─► W8 Review ✓ ─► W9 Fix ⟲ until clean (≤ 2 rounds, then ask)
        ─► W10 (ch1 → ch2) ‖ ch13 → 0_Index → completeness critic ─► Done
```
`✓` = adversarial verification (W8: of every finding). `◆` = the anchor checkpoint, the only stop that always happens (others only when input is needed). `‖` = parallel. `→` = sequential: the right-hand file starts once the left-hand one is on disk.

## Paths the orchestrator computes once

| Var | Value |
|---|---|
| `KIT` | `${CLAUDE_SKILL_DIR}` (this skill's folder) |
| `OUT` | `brief:D-14` resolved to an absolute path, default `<cwd>/deliverables/<slug>/GDD/<D-15>/` |
| `WORK` | `OUT/_work/` — `brief.md`, `gap-log.md`, `run-meta.md`, `review-report.md`, `fact-ledger.md`, `reports/` (REPORT blocks), `checks/` (verification notes) |
| `INPUTS` | `WORK/inputs/` — workflow-built slices |
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
2. `checkpoint` → ask the user per `kind` (`name` § W1 · `anchor` § W2 · `gaps` § GAP handling · `blockers` § W8 · `residual` § W9), write the answers to disk (`brief.md` Gate additions, `gap-log.md`), build `resolutions`, tell the user in one line what runs next, call again.
3. `done` → § Done. `error` → § Failure modes.

State lives only in `OUT`/`WORK`, so the loop survives a new session (§ Resume; never `resumeFromRunId`). Shapes of `args`, `RESOLUTION` and returns: SKILL.md § Workflow contract.

| Arg | Value |
|---|---|
| `mode` · `profile` | `run` (`chapter`: § Re-running a single chapter later) · `full` |
| `from` | `W1` first, then the checkpoint's `next` (except *One more round*, § W9) |
| `target` · `date` | mode `chapter` only: N · today's ISO date |
| `paths` · `agent_ns` | `{kit, out, work, inputs}`, recomputed after the rename · § Paths |
| `game_name` · `lang` · `version` | brief `game_name` (D-01 until named; omit while D-01 ∈ {GENERATE, UNDECIDED}) · D-12 (bodies; headings keep the English numbered prefix) · D-15 |
| `flags` | `d21` = D-21 without its parenthetical (`None` · `Light framing` · `Medium` · `Story-driven`) · `d22` = `None` or the D-22 values · `f2p_or_hybrid` (§ Data slices) · `need_name` (§ W1) |
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

1. Right after the freeze, if `D-01` is a real title, ask once: *Keep "<title>" as the game name?* (Keep / Generate alternatives). Keep → `need_name: false`, `game_name` = D-01, provisional slug final; write both under `brief.md` `## Chosen game name` (§ Resume reads it). Generate alternatives, or `D-01 ∈ {GENERATE, UNDECIDED}` → `need_name: true`.
2. First call `from: 'W1'`. Without `need_name`, W1 is a no-op and the segment runs on into W2. With it, `gdd-namer` runs and the `name` checkpoint returns 8 ranked `candidates` (rationale, pronounceability; trademarks unchecked — tell the user).
3. Ask with `AskUserQuestion`: top 4 as options (label = name, description = rationale). Free text via Other is the name.
4. Write `game_name` and `slug` under `brief.md` `## Chosen game name`, rename the provisional `<slug>` directory if it differs, update `run-meta.md` (`slug:`, `out:`), then call `from: 'W2'` with the new `paths`, `game_name` and `need_name: false`.

## W2 — Anchor chapter and anchor checkpoint

The segment writes and verifies ch 3 (`concept-architect`), builds `INPUTS/_anchor.md`, and always stops at the `anchor` checkpoint — nothing downstream runs before approval.

1. Show `anchor.pillars` (name · meaning · forbids) and `anchor.features` (name · priority · pillar) as two tables; ask *Approve the anchor?* — Approve / Request changes, notes via Other (no notes → ask what to change). Ask the checkpoint's `items` in the same round (§ GAP handling).
2. **Approve** → `{id: 'ANCHOR', action: 'approved'}` (or omit it); call from `next` with the item resolutions. Record it on disk — `brief.md` `## Gate additions (W2 anchor review)`: `ANCHOR · approved · <date>`, and a `gap-log.md` row `ANCHOR | W2 | gdd-concept-architect | anchor approval | structural | §3.2–§3.3 | Approve the anchor? | approved | <date> | —` (§ Resume reads it).
3. **Request changes** → write the notes to `brief.md` under `## Gate additions (W2 anchor review)` and as the Answer of a new `ANCHOR` gap-log row, add `{id: 'ANCHOR', file: <checkpoint file>, owner: 'concept-architect', class: 'structural', action: 'fresh'}`, give ch 3's items `fresh` too (never Edit a file about to be rewritten), call from `next`. The workflow rewrites and re-verifies ch 3, rebuilds the anchor and returns this checkpoint; repeat until Approve.

## W3–W7 — Chapter waves

Order and owners: SKILL.md § Waves at a glance. Waves are serial — every chapter's *Consumes* list (`references/contracts/ch<NN>.md`) must already be on disk — and a segment runs as many as it can. Per wave the workflow:

1. **slices** the inputs: each dispatch reads `INPUTS/_anchor.md` (ch 3 §3.2 pillars + §3.10 glossary, reused verbatim; rebuilt whenever ch 3 changes) plus its `SLICES` entry in workflows/forge-run.js — `whole` chapters passed as they are (ch 3 → ch 4/5; ch 9 → ch 11), `parts` cut into `INPUTS/ch<N>/` by `KIT/scripts/extract-sections.sh`;
2. **dispatches** each owner with the chapter envelope (`writePrompt`) — paths only; the agent returns its `## REPORT` block (`dispatch-rules.md` §4) as structured output;
3. **verifies** each new file (finder → 3 voters per Major, ≥ 2 upholds → one owner auto-PATCH for those needing no decision; the rest become `V-` items — one whose fault is in an upstream file comes with the options *fix the upstream file* / *align this file instead*; `blocked` files skipped);
4. **bookkeeps** (clerk): REPORTs verbatim to `WORK/reports/`, `run-meta.md` § Waves rows (`Words` = `wc -w`, the kit's only word count), `gap-log.md` rows for new G-ids, `WORK/checks/<file>.check.md`;
5. **stops** with a `gaps` checkpoint only for items or a `blocked` file; otherwise runs the next wave.

W8 reads whole chapters; W10 reads its own extracts (§ W10). A `MISSING:` slice line is never dispatched around: the workflow PATCHes the upstream owner once (restore a Depth-rule `N/A —` heading, `dispatch-rules.md` §2 rule 10, else write the section), re-slices, and errors if still missing (§ Failure modes). A Depth-rule N/A section that keeps its heading is a valid slice.

Never read chapter bodies to steer the run (of a REPORT, § Resume reads only the `STATUS:` line); open a chapter only for a `value`-GAP Edit.

## GAP handling — every checkpoint with `items`

Ids: `G-<ch>-<n>` (an agent's GAP, `<ch>` = its chapter; a rewritten file numbers new GAPs after the highest already logged) · `V-<ch>-…` (a verified finding needing a decision, `<ch>` = the file that raised it) · `R-<n>` (a W8 review finding) · `R<round>-<n>` (a fix-loop RECHECK finding). Item shape: SKILL.md § Workflow contract; `class` (`value` | `structural`) per `dispatch-rules.md` §1.

1. De-duplicate against `gap-log.md` by **id and field together**: same id, same field, already answered → reuse the answer, never re-ask. Same id but a different field → a new question: ask it and log / resolve it as `<id>~2` (next free suffix). A field raised by several files is asked once.
2. Ask with `AskUserQuestion` — ≤ 4 per call — using the item's options plus "Leave UNDECIDED" (≤ 4 options each; longer lists per the rule after W0 step 8). If an answer contradicts a frozen brief value or a pillar, ask the user which one yields before writing anything.
3. Write each answer into `brief.md` under `## Gate additions (<checkpoint stage>)` with its id. In `gap-log.md`, fill Question asked / Answer / Answered on of a G-id's row (the workflow wrote it); a V- or R-id gets a new row (Raised by `verify` / `review`).
4. Build one resolution per answer; `action` by class:
   - **`value`** (fills one value; nothing else changes) → `Edit` the `⟂ GAP` line (or the one value the item names) yourself — value and unit, no added prose — drop the item from that file's Open Decisions, fill its gap-log Patched files → `edited`. More than ~3 dependent lines → `patch` (the owner replaces only the placeholder and what depends on it, `dispatch-rules.md` §3).
   - **`structural`** (changes what a feature, flow or section *is*) → `fresh`: the owner rewrites the whole file, then it is re-verified.
   - Upgrade `value` → `structural` (the agent only proposes the class) when the answer adds what the options did not (a new feature, mode, screen, flow).
   - A fact owned by an upstream file (the chapter whose contract Sections list defines it) is fixed in the **owning** file: point `file`/`owner` there, `cascade: true`, `sections` = its §x.y. The workflow fixes the owner, then PATCHes every citing file.
   - "Leave UNDECIDED" → `undecided`: the placeholder stays for the Appendices register; nothing is re-dispatched.
   - A file in the checkpoint's `blocked` list → always `fresh`, after asking its items; read its saved REPORT (`WORK/reports/<file>.report.md`) for the reason. Blocked again after a fresh re-dispatch → the checkpoint says so: tell the user the reason and ask how to proceed rather than re-dispatching blindly.
   - A `V-` item about an upstream fault: *fix the upstream file* → `patch` on the item's `file` with `cascade: true`; *align this file* → `patch` on the raising file (`V-<ch>-…`).
5. Call again from `next`. The workflow applies every resolution first (upstream files, then cascades); items raised meanwhile return as another checkpoint with the same `next`.

**PROPOSALS are never asked mid-run** (`dispatch-rules.md` §1) — leave every `(proposal)` exactly as the agent wrote it. Done reports their count and where they live; an answer given later is handled like a `value`/`structural` GAP (a `structural` one through § Re-running a single chapter later).

## W8 — Review

Nothing to do unless Blockers survive. In parallel: `gdd-reviewer` on its normal contract (writes `WORK/fact-ledger.md`, `WORK/review-report.md`) ‖ the four `LENS_FINDERS` (contradictions · brief fidelity · closure · hygiene). Findings are merged; each Blocker/Major is judged by three voters — evidence / rule / severity + ownership (≥ 2 upholds survive) — each Minor by one evidence check; `review-report.md` is rewritten with verified findings only: Blockers · Majors · Minors · Checklist matrix · Consistency rules 1–12 · `## Verification` counts.

Blockers → `blockers` checkpoint (R-ids) → § GAP handling → call from `next` (`W9`). None → W9 runs in the same segment.

## W9 — Fix loop (until clean, ≤ 2 rounds per segment)

- **Minors** → a clerk step fixes those ≤ 2 lines needing no design judgement (SKILL.md § Non-negotiables, exception 2); the rest are listed in Appendices §G.
- **Majors**, per round → one PATCH per owner file (the file the finders and voters named), in parallel.
- **RECHECK** each round: `gdd-reviewer` RECHECK (patched files, rules 1–12, their fact-ledger rows) ‖ a regression lens → merge → verify as in W8. Open or new Majors → next round. The full review is never re-run.
- Answers applied at the start of a W9 segment (Blockers) are rechecked the same way even when no Major is open, so every user decision passes a RECHECK before W10.
- New Blockers, a Major with no GDD file to patch (e.g. one that sits in `brief.md`), or GAPs a fix-loop PATCH raised → `blockers` / `gaps` checkpoint (`next` = `W9`); the loop resumes after the answers.
- Clean → W10 in the same segment. Majors left after the cap → `residual` checkpoint: list them (id · file · what), ask *One more fix round* / *Accept as known issues*. One more → `{id: 'RESIDUAL', action: 'another_round'}`, call from `stage` (`W9`) with `extra_round: true` (one round; may return `residual` again). Accept → `action: 'accept'`, call from `next`; they stay open in the report. Log the choice in `gap-log.md` per R-id.
- Bookkeeping (clerk): `review-report.md` `## Fix loop` (id · severity · file · status · round); `run-meta.md` § Fix loop (`iterations` 0–N, every round counted; patched chapters; RECHECK summary), read by `2_Version History.md` §2.2.

## W10 — Boilerplate & assembly

No checkpoint; the segment ends with `done`.

1. **Pre-extraction** (clerk): `INPUTS/ch13/ch<N>.md` per chapter 3–12 — `@Open Decisions`, `@New Terms` and the `CH13_EXTRA` sections. `ABSENT: @New Terms` is normal; a failed extract falls back to the whole chapter (logged).
2. **W10a**, in parallel: `gdd-scribe` → `1_Copyright Information.md` then `2_Version History.md` (one dispatch) ‖ `gdd-scribe` → `13_Appendices.md` (from the extracts).
3. **Abstracts**: the `intro` of chapters 1–13 → `INPUTS/ch00/abstracts.md`.
4. **W10b**: `gdd-scribe` → `0_Index.md`, only after 1, 2 and 13 exist.
5. **Completeness critic**: missing files or template headings, unlogged `⟂ GAP`s, UNDECIDED fields absent from Open Decisions / §D, counts that disagree across 0_Index, Version History, run-meta and review-report. Findings on 0/1/2/13 → one scribe PATCH; others → the summary's `issues`.

## Model routing

`TIERS`, `ROLE_TIER` and `tierFor` in workflows/forge-run.js pick every dispatch's model — the only place the kit chooses one; no agent frontmatter pins a model and you never pass one. `deep` = the session's model (or `CLAUDE_CODE_SUBAGENT_MODEL`), for design judgement and verification; `spec` and `clerk` are lighter, for template-driven writing and bookkeeping; ch 5 / ch 8 drop to `spec` when mostly `N/A —` lines (per SKILL.md § Agent roster). Re-dispatches use the owner's tier. `model_override` only when the user explicitly asks for one model for every dispatch: it replaces every tier; pass it on every later call.

## Done — what the orchestrator tells the user

From the `done` summary:

- Absolute path of `OUT` (`out`) and the file list with word counts (`files`).
- Number of Open Decisions (`open_decisions`) and of `(proposal)`s (`proposals`), and where they live (Appendices §D, each chapter's Open Decisions).
- Number of Minors left (`minors_left`), any Majors accepted at `residual` (open rows of `review-report.md` § Fix loop), and each entry of `issues`.
- Offer, in one line, to (a) re-run a single chapter with new inputs, (b) bump version, (c) run `/gdd-forge:review` later.

## Resume (`--resume <OUT>`)

1. Read `WORK/run-meta.md` and `WORK/brief.md`; confirm the brief is frozen (else restart W0 from what exists). Reuse `agent_namespace:` and `workflow:` (resolve again if absent); recompute `paths`, `flags`, `data`.
2. List `OUT/*.md`. A chapter counts as done only if its file exists **and** `WORK/reports/<file>.report.md` shows `STATUS: complete` or `complete-with-gaps`.
3. `from`, first match wins (progress is read from `run-meta.md` and `gap-log.md`, never from optional `review-report.md` sections — `/gdd-forge:review` may have rewritten that file):
   - `brief.md` `## Chosen game name` still a placeholder → `W1` (re-ask the keep-title question if D-01 is a real title);
   - ch 3 not done → `W2`;
   - no `ANCHOR` row answered `approved` in `gap-log.md` → `ANCHOR` (re-shows the anchor checkpoint without rewriting ch 3);
   - a W3–W7 chapter not done → the first such wave (re-run whole);
   - no `W8` row in run-meta § Waves → `W8`;
   - Blockers in `review-report.md` (§ Blockers, or open Blocker rows of § Fix loop) with no gap-log answer → ask them (§ GAP handling), then `W9`;
   - run-meta § Fix loop still `iterations: 0` while the report lists Majors → `W9`;
   - open Major rows in § Fix loop that gap-log does not mark accepted → ask the § W9 residual question first (`W9` + `extra_round`, or `W10`);
   - otherwise `W10`.
4. Ask what an interrupted `gaps` or `anchor` checkpoint left open — `gap-log.md` rows with an empty Answer, and "asked the user" lines in `WORK/checks/*.check.md` (they carry the `V-` id) that gap-log does not answer — and pass the resolutions on the first call. Then run § The main loop.

## Re-running a single chapter later

`/gdd-forge:forge --chapter N` (or natural language):

1. Load `WORK/brief.md`; ask only for fields chapter N consumes that are still `UNDECIDED`, written as Gate additions. Compute `paths`, `flags`, `data` as for a run.
2. N ∈ 3–12 → `mode: 'chapter'`, `target: N`, `date`, `from: 'RERUN'`. **RERUN** re-slices from the chapters now on disk (`_anchor.md` too when N = 3), fresh-dispatches the owner, verifies, bookkeeps. Items → `gaps` checkpoint, `next` = `RERUN-POST` → § GAP handling → call from `RERUN-POST`.
3. **RERUN-POST**: scribe PATCH adds one version row (`date`) to `2_Version History.md`; `13_Appendices.md` then `0_Index.md` rebuilt; a verified regression lens on N against what it cites and what cites it; the completeness critic. Returns `done`; regression findings land in `issues`, unpatched.
4. N ∈ {0, 1, 2, 13} → `mode: 'run'`, `from: 'W10'`.
5. Report `issues` and the `stale` chapters (consumers of N per `SLICES`; all of 4–12 when N = 3), offering to re-run the files they name — only on explicit confirmation, never cascade unasked.

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
| User abandons mid-run | Everything so far is in `OUT`/`WORK`; say so and how to resume (`--resume <OUT>`). |
