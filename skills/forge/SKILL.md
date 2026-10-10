---
name: forge
description: Generate a complete 13-chapter Game Design Document (or a 6-file casual / hyper-casual GDD) from a pitch. Runs an input gate that asks only for missing decisions (never invents them), then drives the gdd-forge:forge-run workflow segment by segment — design agents write each wave, every new file is adversarially verified, a verified multi-lens review and a fix loop run until clean — stopping at checkpoints (name, anchor approval, GAPs, review Blockers, residual Majors) to ask the user. Use when the user wants a GDD, game design document, design bible, or to turn a game idea into a spec.
---

# Forge — GDD generation orchestrator

You (the agent running this skill) are the **orchestrator**: you run the input gate, then drive the
`forge-run` workflow segment by segment, asking the user at every checkpoint until done.

`$ARGUMENTS` selects the entry point:
- empty → start the gate from scratch (W0).
- free-text pitch → seed D-02 (and any other D-xx you can parse out of it) and start the gate.
- a path to an existing brief file → load it, treat every filled field as answered, resume the gate for what's missing.
- `--chapter N` → skip the gate (pipeline.md § Re-running a single chapter later); `mode: 'chapter'`, `target: N`, `from: 'RERUN'`.
- `--resume <OUT dir>` → decide `from` per pipeline.md § Resume.
- `--profile casual` (or `--profile lite`, passed as `profile: 'casual'`) → the lite casual / hyper-casual flow, 6 files. Follow [profile-casual.md](references/profile-casual.md) instead of pipeline.md; "Non-negotiables" still apply.
- `--profile hyper-casual` → same lite flow, sub-profile pre-selected.
- `--profile casual --file N` → `mode: 'file'`, `target: N` (1–5), `from: 'RERUN'` (profile-casual.md § Single-file re-run).
- `--profile casual --resume <OUT dir>` → decide `from` per profile-casual.md § Resume.

## Non-negotiables

- Only you talk to the user. The workflow cannot ask anything; subagents never see the user and cannot call `AskUserQuestion`.
- Decisions (`D-xx`) come only from the user's words or explicit `UNDECIDED`. Never invent, default, or infer one — not even a "reasonable" one.
- Reversible, local choices the brief doesn't make are written by agents as tagged `(proposal)`s with 1–2 alternatives (`dispatch-rules.md` §1) — never silently, never for a `D-xx` field. **PROPOSALs are never asked mid-run.**
- Subagents report **GAPs** (class `value` / `structural`, `dispatch-rules.md` §1) instead of deciding; you ask at a checkpoint and resolve by class (§ Checkpoints).
- Every path in `args` and in every dispatch is **absolute**. Never paste chapter bodies into a prompt or `args` — give the path.
- Chapter bodies are written in `D-12`; headings keep the English numbered prefix (`# 4. Gameplay and Mechanics`) in every language.
- You, and the workflow's clerk and assembly steps, never write chapter prose, with exactly four exceptions: (1) you substitute the user's answer for a `value`-class GAP via `Edit`; (2) a reviewer Minor ≤ 2 lines needing no design judgement (workflow clerk step); (3) the lite `0_Index.md` (workflow assembly from `contracts-lite/lite-0.md`, never a designer dispatch); (4) the lite `1_Concept.md` §1.1 game-name line, which you `Edit` at the anchor checkpoint. Everything else goes to the owning agent.

`KIT`, `OUT`, `WORK`, `INPUTS` are computed once — pipeline.md § Paths the orchestrator computes once / profile-casual.md § Paths. `slug` = kebab-case of the game name, ASCII only.

Full profile: read [pipeline.md](references/pipeline.md) in full before W0. Lite: read only [profile-casual.md](references/profile-casual.md). They hold the procedures and win on them; this file is the map and the workflow contract. On stage ids, args, checkpoint kinds and model routing, `workflows/forge-run.js` wins.

## How a run works

This skill's instructions are the user's opt-in to the `Workflow` tool — call it as described, without asking separately. Never run this skill with `context: fork`: checkpoints need `AskUserQuestion` and the user.

1. **W0 gate** — pipeline.md § W0 / profile-casual.md § W0. `need_name` = D-01 ∈ {GENERATE, UNDECIDED}; full profile with a real D-01: right after the freeze ask *Keep "<title>"?* (Keep / Generate alternatives) and set `need_name` from it.
2. **Resolve once**, record in `run-meta.md`:
   - `agent_ns` — `"gdd-forge:"` under a plugin install (agents listed as `gdd-forge:gdd-<role>`), `""` when copied to `~/.claude/agents/`. (`agent_namespace:`)
   - invocation — plugin install: `Workflow({name: "gdd-forge:forge-run", args})`; otherwise, or if that name is not found: `Workflow({scriptPath, args})` with `${CLAUDE_SKILL_DIR}/../../workflows/forge-run.js` resolved to an absolute path. (`workflow:`)
   - `paths`, `flags`, `lang`, `version`, `game_name`, and `data` — only the slices the brief selects, per each `data/<dir>/_index.md` (a mobile-only D-04 → `platforms/mobile.md` + `platforms/selection-criteria.md`, not the console / PC / VR specs).
3. **Loop** — first call: `from: 'W1'` unless the entry point says otherwise, `resolutions: []` (on `--resume`: the answers to what the interrupted checkpoint left open). On each result:
   - `done` → § Done.
   - `error` → tell the user `message`, fix what it names (or ask), call again: `stage: 'resolve'` or a missing-args error → the same call (args fixed); otherwise `from: stage` and `resolutions: []` (already applied).
   - `checkpoint` → § Checkpoints, then call again with `from: checkpoint.next` (`residual`: § Checkpoints) and the answers as `resolutions`. Other args unchanged, except: after a name pick, the new `paths` / `game_name` and `need_name: false`; after a Gate addition changing a field that feeds `flags` or `data`, recompute them; `extra_round` only on the one call right after *One more round*.

State lives on disk, never in the workflow, so runs resume across sessions; `resumeFromRunId` is never used.

## Workflow contract

Pass `args` as JSON values, not strings.

| Arg | Value |
|---|---|
| `mode` | `run` · `chapter` (full `--chapter N`) · `file` (lite `--file N`) |
| `profile` | `full` · `casual` · `hyper-casual` |
| `from` | stage id this segment starts at |
| `target`, `date` | modes `chapter`/`file`: N, and the ISO date for the version row |
| `paths` | `{kit, out, work, inputs}`, absolute; `inputs` = `WORK/inputs`, full only |
| `agent_ns` | `"gdd-forge:"` or `""` |
| `game_name`, `lang`, `version` | brief `game_name` — D-01 until named; omit when D-01 ∈ {GENERATE, UNDECIDED} · D-12 · D-15 |
| `flags` | `{d21, d22, f2p_or_hybrid, need_name}` — `d21` = the D-21 option without its parenthetical; `d22` = `None` or the D-22 selection; `f2p_or_hybrid` = D-06 is F2P or Hybrid |
| `data` | `{platforms, monetization, cultural, accessibility}` — brief-selected slice paths |
| `resolutions` | `[RESOLUTION]` from the last checkpoint, else `[]` |
| `extra_round` | `true` only on the call right after the user chose one more fix round; omit otherwise |
| `model_override` | only when the user explicitly asks for one model for every dispatch |

```
{ status: 'checkpoint', checkpoint: { kind, stage, next, items, file?, anchor?, candidates?, blocked?, note? } }
{ status: 'done', summary: { out, files: [{file, words}], open_decisions, proposals, minors_left, issues, stale? } }
{ status: 'error', stage, message }
ITEM       = { id, file, owner, class, field, section, why, options[] }
RESOLUTION = { id, file, owner, class: 'value'|'structural', answer, action, cascade: bool, sections: '§x.y …' }
```
`stage` raised the checkpoint (`resolve` = while applying answers); `next` = where to continue. Ids: GAP `G-<ch>-<n>`, verify decision `V-<ch>-…`, review `R-<n>`. `issues` = findings the workflow could not close; `stale` = files consuming a re-run one.

**Actions:** `edited` (you already Edited it — no dispatch) · `patch` (PATCH to the owner) · `fresh` (fresh owner re-dispatch, re-verified) · `undecided` · `approved` · `another_round` · `accept`. `cascade: true` (fact owned by `file`, cited downstream) → the workflow PATCHes every citing file after the owner. A file in `checkpoint.blocked` always gets `fresh`. **Special ids:** `ANCHOR` — `approved` (or omitted) | `fresh`; `RESIDUAL` — `another_round` | `accept`.

**Stage ids, in order:** full `run` — `W1` `W2` `W3a` `W3b` `W4` `W5` `W6` `W7` `W8` `W9` `W10`; lite `run` — `W1` `W2` `W3` `W4` `FIX` `INDEX`; full `chapter` (N 3–12) and lite `file` (N 1–5) — `RERUN` `RERUN-POST`. Chapters 0/1/2/13 are rebuilt by `mode: 'run'` from `W10`.

## Checkpoints

Before asking, for every kind:
- De-duplicate `items` against `gap-log.md` (same id or field already answered → reuse, don't re-ask); a field raised by several files is asked once and resolved in each.
- `AskUserQuestion`: ≤ 4 questions per call, ≤ 4 options each, from the item's `options`, plus "Leave UNDECIDED" on every decision item; longer lists go into the question text (pipeline.md § W0). An answer contradicting a frozen brief value or a pillar → ask which yields before writing.
- Write each answer into `brief.md` `## Gate additions (<checkpoint.stage>)` (lite `(lite)`) with its id, and into `gap-log.md` (Question asked · Answer · Answered on; add the row for a `V-`/`R-` id — the workflow logs only `G-` rows; fill Patched files for `edited`).
- Resolve by class: **`value`** → `Edit` the `⟂ GAP` line (value and unit, no prose), drop it from that file's Open Decisions → `edited`; more than ~3 dependent lines → `patch`. **`structural`** → `fresh`; upgrade `value` → `structural` when the answer adds what the options did not (feature, mode, screen, flow). An upstream-owned fact → its **owning** file, `cascade: true`. "Leave UNDECIDED" → `undecided`.

Per kind — what you ask, then what you write before calling again:
- **`name`** (full W1) — top 4 of the 8 ranked `candidates` (rationale + pronounceability; trademarks unchecked); Other = the name. Write `game_name`/`slug` under brief `## Chosen game name`, rename the provisional dir, update run-meta `slug:`/`out:`.
- **`anchor`** (full W2 / lite W1, always) — `anchor.pillars` (name · meaning · forbids) and `anchor.features` (name · priority · pillar) as a table, then *Approve* / *Request changes* (notes via Other), plus any `items`; lite with `candidates`: the name too (3 + Other). Changes → notes under `## Gate additions (W2 anchor review)` (lite `(W1 anchor review)`) and `{id: 'ANCHOR', file: checkpoint.file, owner: 'concept-architect', class: 'structural', action: 'fresh'}`; the anchor file's items get `fresh` too (never `Edit` a file about to be rewritten) — rewritten, re-verified, asked again. Approve → `{id: 'ANCHOR', action: 'approved'}`. Lite name → as `name`, plus `Edit` `[GAME NAME — pending §1.2]` in 1_Concept.md §1.1 (exception 4; re-apply after an ANCHOR `fresh`).
- **`gaps`** (after a writing wave, `RERUN` or `resolve`; only with items or `blocked` files) — `G-` and `V-` items. One RESOLUTION per item; `fresh` for every `blocked` file.
- **`blockers`** (review W8 / W4, or a fix-loop RECHECK) — `R-` items, resolved like GAPs.
- **`residual`** (W9 / FIX after the round cap) — open Majors (id · file · what), then *One more round* / *Accept as known issues*. More → `{id: 'RESIDUAL', action: 'another_round'}`, call from `checkpoint.stage` with `extra_round: true`. Accept → `action: 'accept'`, call from `next`; the Majors stay open for § Done.

## Waves at a glance

Every new or fresh file is verified: one finder, three perspective-diverse voters per Major (≥ 2 upholds), one auto-PATCH to the owner for confirmed Majors needing no decision; the rest become `V-` items (`WORK/checks/`). Full W3–W7 inputs are sliced (`SLICES` in workflows/forge-run.js, plus `INPUTS/_anchor.md` from W2); lite never slices. Waves are serial.

| Full | Dispatch(es) → chapter | Checkpoint |
|---|---|---|
| W1 | `gdd-namer` → 8 names (only if `need_name`) | `name` |
| W2 | `gdd-concept-architect` → 3 (bookkeeping builds `_anchor.md`) | `anchor` |
| W3a | `gdd-mechanics-designer` → 4 | `gaps` |
| W3b | `gdd-narrative-designer` → 5 | `gaps` |
| W4 | `gdd-level-designer` → 6 ‖ `gdd-ux-designer` → 7 | `gaps` |
| W5 | `gdd-ai-designer` → 8 ‖ `gdd-art-director` → 10 | `gaps` |
| W6 | `gdd-tech-designer` → 9 then 11 (one dispatch) | `gaps` |
| W7 | `gdd-producer` → 12 | `gaps` |
| W8 | `gdd-reviewer` ‖ 4 lens finders → merge → 3 voters each → `review-report.md` | `blockers` |
| W9 | fix loop: PATCH per owner, clerk Minors, RECHECK ‖ regression → voters; ≤ 2 rounds | `blockers` / `residual` |
| W10 | `gdd-scribe` 1+2 ‖ 13, then 0_Index; completeness critic | — |

| Lite | Dispatch(es) → file | Checkpoint |
|---|---|---|
| W1 | `gdd-concept-architect` → 1 | `anchor` (+ name) |
| W2 | `gdd-mechanics-designer` → 2 | `gaps` |
| W3 | `gdd-ux-designer` → 3 ‖ `gdd-producer` → 4 ‖ `gdd-tech-designer` → 5 | `gaps` |
| W4 / FIX | review and fix loop as W8 / W9 (structural Major → fresh) | `blockers` / `residual` |
| INDEX | 0_Index assembly; completeness critic | — |

Re-run: `RERUN` (fresh owner dispatch, verify) → `RERUN-POST` (version row, index rebuilt, regression recheck).

## Rules that are easy to get wrong

- **`agentType` needs the exact namespaced name** — the workflow builds `agent_ns + "gdd-<role>"`; a wrong `agent_ns` fails every dispatch.
- **Named workflow vs scriptPath** — `gdd-forge:forge-run` exists only under a plugin install; a local copy uses an absolute `scriptPath`. Never pass the script inline.
- **`AskUserQuestion`: ≤ 4 questions per call, ≤ 4 options each.** Chunk; put long lists in the question text; never pre-select.
- **PROPOSALs are never asked** — at no checkpoint. Done reports their count.
- **One workflow call at a time** — never two segments at once, never edit `OUT` while one runs.

## Agent roster

No agent pins a model. Tiers live in MODEL ROUTING (`TIERS` / `ROLE_TIER` / `tierFor`) in workflows/forge-run.js: `deep` = the session's model, `spec` / `clerk` = sonnet; ch 5 and ch 8 drop to `spec` when mostly `N/A —` (D-21 ∈ {None, Light framing}; D-22 = None). Re-dispatches use the owner's tier. `args.model_override` only when the user explicitly asks for one model for every dispatch.

| Agent | Default tier | Full chapters | Lite file |
|---|---|---|---|
| `gdd-concept-architect` | deep | 3 | 1 |
| `gdd-mechanics-designer` | deep | 4 | 2 |
| `gdd-narrative-designer` | deep | 5 | — |
| `gdd-level-designer` | deep | 6 | — |
| `gdd-ux-designer` | spec | 7 | 3 |
| `gdd-ai-designer` | deep | 8 | — |
| `gdd-tech-designer` | deep | 9 + 11 | 5 |
| `gdd-art-director` | spec | 10 | — |
| `gdd-producer` | spec | 12 | 4 |
| `gdd-reviewer` | deep | review | review |
| `gdd-scribe` | spec | 0 / 1 / 2 / 13 | — |
| `gdd-namer` | deep | naming | — |

An agent with no lite file is never dispatched in the lite profile; the lite `0_Index.md` is a workflow assembly step.

## Done

Report from `summary` per [pipeline.md § Done](references/pipeline.md) (full) or
[profile-casual.md § Done](references/profile-casual.md) (lite), plus accepted residual Majors (open rows of
review-report.md § Fix loop) and every `issues` line. Re-run modes: list `stale` and offer to re-run those files — only on explicit
confirmation, never cascade unasked.

## Casual / hyper-casual profile

`--profile casual` replaces W1–W10 with three writing waves, review, fix loop and index: 6 files instead
of 14. Use it for a casual or hyper-casual mobile title: no real narrative, no AI architecture, no
multiplayer, mobile-only. Escalate to the full flow the moment one of those stops being true.

The gate **proposes** a preset of typical casual values; the user confirms or edits it in one round, and
only confirmed values reach `brief.md` (`Source: casual preset — confirmed by user`). An unconfirmed
preset value is never used; D-02 (pitch) is still required. Follow
[profile-casual.md](references/profile-casual.md) for the gate, preset, contracts, resume and re-run.
