---
name: forge
description: Generate a complete 13-chapter Game Design Document from a pitch. Runs an input gate that asks only for missing decisions (never invents them), then dispatches specialised design subagents chapter by chapter, reviews for consistency, and assembles the deliverable. Use when the user wants a GDD, game design document, design bible, or to turn a game idea into a spec.
---

# Forge — GDD generation orchestrator

This skill turns a pitch into a 13-chapter GDD by running an input gate, then dispatching one
specialised subagent per chapter (or wave of chapters), reviewing the result for consistency,
and assembling the final files. You (the agent running this skill) are the **orchestrator** —
you never write chapter prose yourself and you are the only party that talks to the user.

`$ARGUMENTS` selects the entry point:
- empty → start the gate from scratch (W0).
- free-text pitch → seed D-02 (and any other D-xx you can parse out of it) and start the gate.
- a path to an existing brief file → load it, treat every filled field as answered, resume the gate for what's missing.
- `--chapter N` → re-run a single chapter (pipeline.md § Re-running a single chapter later), skip the gate.
- `--resume <OUT dir>` → resume an interrupted run (pipeline.md § Resume).
- `--profile casual` (or `--profile lite`) → run the lightweight casual / hyper-casual flow instead: 4 waves, 6 dispatches, 6 files. Follow [profile-casual.md](references/profile-casual.md) end to end and ignore the full-flow waves (W1–W10) below. Everything in "Non-negotiables" still applies.
- `--profile hyper-casual` → same lite flow, sub-profile pre-selected (skips the sub-profile question).
- `--profile casual --file N` → re-run one lite output file (N ∈ 1–5); see profile-casual.md § Single-file re-run.
- `--profile casual --resume <OUT dir>` → resume an interrupted lite run; see profile-casual.md § Resume.

## Non-negotiables

- Only you (the main agent) talk to the user. Subagents never see the user and cannot call `AskUserQuestion`.
- Decisions (`D-xx`) come only from the user's words or explicit `UNDECIDED`. Never invent, default, or infer a decision on the user's behalf — not even a "reasonable" one.
- Reversible, local choices that the brief doesn't make are written by agents as tagged `(proposal)`s, listed under Open Decisions with 1–2 alternatives (`dispatch-rules.md` §1) — never silently, and never for a `D-xx` field.
- Subagents report **GAPs** instead of deciding; you ask the user on their behalf and resolve by class (pipeline.md / profile-casual.md § GAP handling).
- Pass **absolute paths** to every subagent for every input and output. Subagents never guess paths.
- Never paste chapter bodies into a subagent prompt — give the path and let the subagent read it.
- Chapter bodies are written in `D-12` language; chapter headings keep the English numbered prefix (e.g. `# 4. Gameplay and Mechanics`) in every language.
- You (the orchestrator) never write chapter prose yourself, with exactly four exceptions: (1) substituting the user's answer for a `value`-class GAP directly via `Edit`; (2) fixing a reviewer Minor that is ≤ 2 lines and needs no design judgement; (3) the lite `0_Index.md` (assembled from `contracts-lite/lite-0.md`, never dispatched); (4) the lite `1_Concept.md` §1.1 game-name line, filled in after the user picks a name (profile-casual.md § W1 naming step). Everything else goes to the owning agent.

Path variables (`KIT`, `OUT`, `WORK`, `INPUTS`) are computed once per run — full detail: pipeline.md § Paths the orchestrator computes once (full profile) or profile-casual.md § Paths (lite profile). `slug` = kebab-case of the chosen game name, ASCII only, in both.

For the full profile (no `--profile` flag), read [pipeline.md](references/pipeline.md) in full before W0 and follow it section by section — it is the procedure; this file is the map. Where this file and pipeline.md ever differ, pipeline.md wins. For `--profile casual|lite|hyper-casual`, read only [profile-casual.md](references/profile-casual.md) — it is self-sufficient, and where it differs from this file, profile-casual.md wins.

## Waves at a glance

| Wave | Dispatch(es) (bare agent role → file) | Blocks on | `pipeline.md` § |
|---|---|---|---|
| W0 | orchestrator runs the gate — no subagent dispatch | — | § W0 — Gate (orchestrator) |
| W1 | `gdd-namer` → name candidates (only if `D-01 ∈ {GENERATE, UNDECIDED}`) | brief frozen | § W1 — Name |
| W2 | `gdd-concept-architect` → `3_Game Overview.md` | brief frozen, name chosen, dirs renamed | § W2–W7 — Chapter generation |
| W3a | `gdd-mechanics-designer` → `4_Gameplay and Mechanics.md` | ch 3 | § W2–W7 — Chapter generation |
| W3b | `gdd-narrative-designer` → `5_Story, Setting and Character.md` | ch 4 (§4.1–4.3, GAPs handled) | § W2–W7 — Chapter generation |
| W4 | `gdd-level-designer` → `6_Levels.md` ‖ `gdd-ux-designer` → `7_Interface.md` | ch 4, ch 5 | § W2–W7 — Chapter generation |
| W5 | `gdd-ai-designer` → `8_Artificial Intelligence.md` ‖ `gdd-art-director` → `10_Game Art.md` | ch 6, ch 7 | § W2–W7 — Chapter generation |
| W6 | `gdd-tech-designer` → `9_Technical.md` then `11_Secondary Software.md` | ch 7, ch 8, ch 10 | § W2–W7 — Chapter generation |
| W7 | `gdd-producer` → `12_Management.md` | ch 9, ch 11 | § W2–W7 — Chapter generation |
| W8 | `gdd-reviewer` → `review-report.md` | all of 3–12 | § W8 — Review |
| W9 | fix loop — Blockers / Majors / Minors, ≤ 1 iteration | review | § W9 — Fix loop |
| W10a | `gdd-scribe` → `1_Copyright Information.md` then `2_Version History.md` (one run, two files) ‖ `gdd-scribe` → `13_Appendices.md` | fixes applied | § W10 — Boilerplate & assembly |
| W10b | `gdd-scribe` → `0_Index.md` | ch 1, 2, 13 | § W10 — Boilerplate & assembly |

GAP handling (collect, ask, resolve by class — `value`/`structural`, `dispatch-rules.md` §1) runs after every wave and after W3a before W3b — full procedure: pipeline.md § GAP handling. Re-running a single chapter, resuming an interrupted run, and every failure mode are documented once, in pipeline.md only: § Re-running a single chapter later, § Resume, § Failure modes.

## Rules that are easy to get wrong

- **`subagent_type` is namespaced under a plugin install, bare otherwise.** Resolve it once at the start of the run from the available agent types, then reuse that exact string for the whole run. pipeline.md § Paths the orchestrator computes once.
- **Full profile only — slice inputs before every W3–W7 dispatch**, and build `_anchor.md` once right after W2 (rebuild only if ch 3 is patched). A `MISSING:` line is a stop — never dispatch around it — but a Depth-rule N/A section that kept its numbered heading is a valid slice, not a MISSING. pipeline.md § Input slicing. The lite profile never slices.
- **`AskUserQuestion` shows at most 4 options.** For a field with a longer list, write the full list into the question text and chunk it across questions — follow the rule in pipeline.md § W0.

## Done

Full profile: follow [pipeline.md § Done](references/pipeline.md). Lite profile: follow
[profile-casual.md § Done](references/profile-casual.md).

## Casual / hyper-casual profile

`--profile casual` replaces W1–W10 with a 4-wave, 6-dispatch flow producing 6 files instead of 14.
Use it when the game is a casual or hyper-casual mobile title: no real narrative, no AI architecture,
no multiplayer, mobile-only. Escalate back to the full flow the moment one of those stops being true.

The gate changes shape but not principle: the orchestrator **proposes** a preset of typical casual
values, the user confirms or edits it in one round, and only confirmed values reach `brief.md`
(recorded as `Source: casual preset — confirmed by user`). An unconfirmed preset value is never used,
and D-02 (pitch) is still a hard requirement no preset can supply.

Everything under "Non-negotiables" above still holds. Follow
[profile-casual.md](references/profile-casual.md) for the wave table, contracts, templates and the
preset itself.

## Agent roster

The `model:` line in each agent's frontmatter is authoritative; this table mirrors it for reference — if
the two ever disagree, the frontmatter wins.

| Agent | Model | Full chapters | Lite file |
|---|---|---|---|
| `gdd-concept-architect` | opus | 3 | 1 |
| `gdd-mechanics-designer` | opus | 4 | 2 |
| `gdd-narrative-designer` | opus | 5 | — |
| `gdd-level-designer` | opus | 6 | — |
| `gdd-ux-designer` | sonnet | 7 | 3 |
| `gdd-ai-designer` | opus | 8 | — |
| `gdd-tech-designer` | opus | 9 + 11 | 5 |
| `gdd-art-director` | sonnet | 10 | — |
| `gdd-producer` | sonnet | 12 | 4 |
| `gdd-reviewer` | opus | review | review |
| `gdd-scribe` | sonnet | 0 / 1 / 2 / 13 | — |
| `gdd-namer` | opus | naming | — |

No `gdd-namer`, `gdd-narrative-designer`, `gdd-level-designer`, `gdd-ai-designer`, `gdd-art-director` or
`gdd-scribe` dispatch exists in the lite profile — their full-profile responsibilities are folded into the
five lite agents above, or out of scope (profile-casual.md § When NOT to use this profile). The lite
`0_Index.md` has no dispatch at all: the orchestrator assembles it directly.
