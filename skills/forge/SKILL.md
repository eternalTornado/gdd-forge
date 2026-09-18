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
- `--chapter N` → re-run a single chapter (see "Re-run a single chapter" below), skip the gate.
- `--resume <OUT dir>` → resume an interrupted run (see "Resume" below).
- `--profile casual` (or `--profile lite`) → run the lightweight casual / hyper-casual flow instead: 4 waves, 6 dispatches, 6 files. Follow [profile-casual.md](references/profile-casual.md) end to end and ignore W1–W10 below. Everything in "Non-negotiables" still applies.

## Non-negotiables

- Only you (the main agent) talk to the user. Subagents never see the user and cannot call `AskUserQuestion`.
- Decisions (`D-xx`) come only from the user's words or explicit `UNDECIDED`. Never invent, default, or infer a decision on the user's behalf — not even a "reasonable" one.
- Subagents report **GAPs** instead of deciding; you ask the user on their behalf and patch.
- Pass **absolute paths** to every subagent for every input and output. Subagents never guess paths.
- Never paste chapter bodies into a subagent prompt — give the path and let the subagent read it.
- Chapter bodies are written in `D-12` language; chapter headings keep the English numbered prefix (e.g. `# 4. Gameplay and Mechanics`) in every language.

## Paths (compute once, reuse for the whole run)

| Var | Value |
|---|---|
| `KIT` | `${CLAUDE_SKILL_DIR}` (this skill's folder: `references/`, `templates/`, `checklists/`, `data/`, `scripts/`) |
| `AGENTS` | `${CLAUDE_PLUGIN_ROOT}/agents` — if unset, `${CLAUDE_SKILL_DIR}/../../agents` |
| `OUT` | `brief:D-14` resolved to an absolute path, default `<cwd>/deliverables/<slug>/GDD/<D-15>/` |
| `WORK` | `OUT/_work/` — `brief.md`, `gap-log.md`, `review-report.md`, `run-meta.md`, `reports/<chapter file>.report.md` |
| `INPUTS` | `WORK/inputs/` — pre-sliced upstream sections, one subfolder per dispatch |

`slug` = kebab-case of the chosen game name, ASCII only. Full detail: [pipeline.md](references/pipeline.md).

## W0 — Gate

Follow [pipeline.md § W0](references/pipeline.md) and [brief-schema.md](references/brief-schema.md) exactly.

1. Parse the opening message (or the loaded brief file). Fill every `D-xx` you can find verbatim — do not paraphrase into a different meaning.
2. Refuse to proceed while D-02 (pitch) is empty — it is the one hard requirement.
3. Ask only for missing fields, via `AskUserQuestion`, ≤ 4 questions per call, grouped by brief-schema section (A → B → C), in the default order given in brief-schema.md "Gate question ordering". Always offer the listed options ("Other" is automatic). Skip any field already answered.
4. Ask trigger fields (D-20…D-24, marked ⚡) before their dependants; skip a dependant whose trigger is off.
5. Accept `UNDECIDED` whenever the user declines ("skip", "TBD", "chưa biết") — record it verbatim, never substitute a default.
6. Check the required-set table for the chosen D-15 (version). Every field in that set must be resolved (not `UNDECIDED`) before you can freeze; if one is missing, ask for it even if it wasn't in the default order.
7. Render the brief using [brief-template.md](references/brief-template.md), show it to the user, and ask the final confirmation: *Freeze this brief?* Do not proceed until they confirm.
8. Write the frozen text to `WORK/brief.md` (brief-template.md format) and write `WORK/run-meta.md` (date, kit version, D-15, sha256 of the frozen brief text). Create `OUT`/`WORK` with a provisional slug (kebab-case of D-01 if it is a real title, else `untitled-game`); after W1 fixes the real name, rename the `<slug>` directory and update `run-meta.md`; never write chapters into a provisional directory.

## W1 — Name

Follow [pipeline.md § W1](references/pipeline.md).

- If `D-01 = GENERATE` (or `UNDECIDED`): dispatch `gdd-namer` (`subagent_type`: the resolved name — `gdd-forge:gdd-namer` under a plugin install, `gdd-namer` otherwise) with `WORK/brief.md`. It returns 8 candidates, each with rationale, pronounceability note, and a "possible conflicts to check" line.
- Ask the user with `AskUserQuestion`: top 4 candidates as options (label = name, description = rationale). If they pick "Other" with free text, that is the name.
- If `D-01` is a real title, skip the agent but still ask once: *Keep "<title>" as the game name?* (options: Keep / Generate alternatives). "Generate alternatives" falls back to the `gdd-namer` path above.
- Write the final name into `brief.md` (`game_name`) and compute `slug`. Finalize `OUT` and `WORK` at their real paths (rename from the provisional W0 paths if they differ).

## W2–W7 — Chapter generation

For every subagent dispatch in W2–W7, assemble the prompt from this **dispatch envelope**
(verbatim from [§ W2–W7](references/pipeline.md), fill in the placeholders):

```
ROLE: you are <agent> writing <file> for the GDD of "<game_name>".
LANGUAGE: write the body in <D-12>. Keep heading numbers in English ("# 4. Gameplay and Mechanics").
CONTRACT: read <KIT>/references/contracts/ch<NN>.md. Obey Sections, Depth rule, Hard rules.
INPUTS (read all of these, read nothing else — the slices already contain every upstream
section your contract lets you consume, so never open the full chapter they came from):
  - <WORK>/brief.md
  - <INPUTS>/_anchor.md — ch 3 §3.2 pillars + §3.10 glossary; reuse these terms verbatim
  - <INPUTS>/ch<N>/<sliced upstream files...>
  - template: <KIT>/templates/chapters/<tmpl>
  - checklists: <KIT>/checklists/<...>
  - data: <KIT>/data/<dir>/<only the slices the brief selects>
OUTPUT: write exactly one file <OUT>/<file> (or two for the tech-designer run: ch9 then ch11).
RULES:
  1. DECISIONS come only from brief.md. If a section needs a decision that is missing or UNDECIDED and the Depth rule does not tell you what to do, do NOT invent it — write the section header, a one-line placeholder "⟂ GAP G-<n>: <what is needed>" and list it under GAPS in your report.
  2. Design elaborations are yours. Mark tunables "(tunable)", estimates "(est.)", targets "(target)".
  3. No external facts (market sizes, benchmarks, sales numbers, legal claims) unless present in brief.md or the data files you were given. Otherwise write "no data available".
  4. Use the Glossary from 3_Game Overview §3.10 verbatim. If you must introduce a new term, add it under a "New terms" note at the end of your file.
  5. End every chapter with an "Open Decisions" box listing each UNDECIDED brief field you touched and each GAP placeholder.
  6. Self-check against the checklists before reporting; fix what you can; report the rest.
REPORT (last thing in your final message, exact format):
  ## REPORT
  STATUS: complete | complete-with-gaps | blocked
  FILE: <absolute path(s)>
  WORDS: <n>
  GAPS:
    - G-<n> | field: <D-xx or description> | section: <§> | why: <one line> | suggested options: <a / b / c>
  CHECKLIST: <passed>/<total> — failing: <ids or none>
  NEW_TERMS: <list or none>
  CROSS_REFS_CITED: <chapter §list>
```

Dispatch every subagent with the `Agent` tool. **Resolve the `subagent_type` string first**: when the kit is loaded as a plugin the agents are namespaced — `gdd-forge:gdd-concept-architect`, `gdd-forge:gdd-namer`, … — while a copy installed into `~/.claude/agents/` exposes the bare names (`gdd-concept-architect`). Look at the agent types available to you, pick the exact string that matches the role, and use that same form for the whole run. Every `subagent_type: "gdd-…"` below means "the resolved name for that role". For a wave with more
than one dispatch, put every `Agent` call for that wave in **one message**, `run_in_background: true`,
then wait for every completion notification before doing anything else. Read only the `## REPORT`
block of each result — never the chapter body — to decide next steps. Save each REPORT block verbatim
to `WORK/reports/<chapter file>.report.md` as it arrives, then append its GAPS to `WORK/gap-log.md`.

### Input slicing — do this before every W3–W7 dispatch

A contract's *Consumes* list names sections, not files; an agent handed a whole chapter reads the
whole chapter. Slice first with `KIT/scripts/extract-sections.sh <source> <dest> <spec>...`
(specs: `4.5`, `4.3-4.6`, `all`) and pass only the slices. The full slice map per dispatch is the
table in [pipeline.md § Input slicing](references/pipeline.md).

Two rules that are easy to get wrong:

- **Build the anchor once, right after W2**: `extract-sections.sh "<OUT>/3_Game Overview.md" "<INPUTS>/_anchor.md" 3.2 3.10`. Envelope rule 4 makes every chapter reuse ch 3's Glossary (§3.10) and most must cite a pillar (§3.2), but neither is in most *Consumes* lists — slicing strictly by contract would break rule 4. Pass `_anchor.md` to every W3–W7 dispatch. Rebuild it only if ch 3 is patched.
- **A `MISSING:` line on the script's stdout is a stop, not a warning.** Either the upstream agent never wrote that section (re-dispatch it) or the contract and template disagree (record it in `run-meta.md`). Never dispatch around it.

Data files are sliced by file, not script: pass only what the brief selects (a mobile-only `D-04`
gets `data/platforms/mobile.md`, not the console, PC and VR specs). Each `data/<dir>/_index.md`
gives the selector rule.

### W2 — Chapter 3

Dispatch `gdd-concept-architect` → `3_Game Overview.md`. Blocks on: brief frozen, name chosen,
directories renamed to the final slug.

### W3 — Chapters 4 + 5 (parallel)

One message, two `Agent` calls: `gdd-mechanics-designer` → `4_Gameplay and Mechanics.md`,
`gdd-narrative-designer` → `5_Story, Setting and Character.md`. Blocks on: ch 3.

### W4 — Chapters 6 + 7 (parallel)

One message, two `Agent` calls: `gdd-level-designer` → 6, `gdd-ux-designer` → 7. Blocks on: ch 4, ch 5.

### W5 — Chapters 8 + 10 (parallel)

One message, two `Agent` calls: `gdd-ai-designer` → 8, `gdd-art-director` → 10. Blocks on: ch 6, ch 7 —
ch 8 reads ch 6 §6.4; ch 10 reads ch 6 §6.4 and ch 7 §7.4/§7.11.

### W6 — Chapters 9 then 11

Single `gdd-tech-designer` dispatch: writes `9_Technical.md` then, in the same run, `11_Secondary
Software.md` (sequential inside that one dispatch — ch 11 needs ch 9's finished content). Blocks on:
ch 7, ch 8, ch 10.

### W7 — Chapter 12

Dispatch `gdd-producer` → `12_Management.md`. Blocks on: ch 9, ch 11 (reads §9.10 and §11.7).

Waves are serial because every chapter's *Consumes* list must already be on disk; do not merge waves
to save time.

## GAP handling (after each wave, before the next)

Follow [pipeline.md § GAP handling](references/pipeline.md):

1. Collect every `G-n` from the wave's REPORT blocks. De-duplicate by field.
2. Ask the user with `AskUserQuestion`, ≤ 4 per call, using each agent's *suggested options* plus an explicit "Leave UNDECIDED" option.
3. Write answers into `brief.md` under `## Gate additions (W<n>)` with the G-id. Log the Q/A in `gap-log.md`.
4. If the answer is a real value, re-dispatch the owning agent in **PATCH mode**:
   ```
   PATCH MODE: <file> exists. Replace only the placeholder(s) G-<n> and any sentence that directly depends on them. Do not rewrite other sections. Re-run your checklist. Report as usual.
   ```
   Wait for the patch to complete before starting the next wave — downstream chapters must read the patched text.
5. If the answer is "Leave UNDECIDED", the placeholder stays as-is; do not re-dispatch. It surfaces later in the Appendices Open Decisions register.

## W8 — Review

Dispatch `gdd-reviewer` with: every chapter path (3–12), `brief.md`, `gap-log.md`,
`KIT/references/consistency-rules.md` (the 8 rules), the contract files of the chapters under
review, and every checklist in `KIT/checklists/`. Chapters go to the reviewer **whole, not sliced**. It writes `WORK/review-report.md`:

```
# Review report — <game_name> <version>
## Blockers   (decision missing → needs the user)          — id · chapter § · what · suggested options
## Majors     (cross-chapter contradiction / contract miss) — id · chapters · what · owner agent
## Minors     (wording, formatting, checklist nits)         — id · chapter · what
## Checklist matrix   chapter × checklist → pass %
## Consistency rules  1–8 → PASS/FAIL + evidence
```

## W9 — Fix loop (maximum one iteration)

- **Blockers** → treat exactly like GAPs above (ask user, patch owner).
- **Majors** → re-dispatch each owner agent once in PATCH mode with the Major items verbatim. If two chapters contradict, patch the *downstream* chapter (higher number) to match the upstream one, unless the Major says otherwise.
- **Minors** → do not auto-fix; list the count and let the Appendices §G record them.
- After patches, do **not** re-run the full review. Re-run only the Consistency rules check: a short "RECHECK" dispatch to `gdd-reviewer` limited to the patched chapters.

## W10 — Boilerplate & assembly

Dispatch `gdd-scribe` four times in parallel (one message, four `Agent` calls, `run_in_background: true`):
`1_Copyright Information.md`, `2_Version History.md`, `13_Appendices.md`, `0_Index.md`. Every
dispatch needs `run-meta.md`, `gap-log.md`, and `review-report.md`; 0_Index and 13_Appendices also
need every finished chapter. Wait for all four completions.

## Done — tell the user

- Absolute path of `OUT`, the file list with word counts (from the REPORTs).
- Number of Open Decisions and where they live (Appendices §D).
- Number of Minors left unfixed.
- One line offering to: (a) re-run a single chapter with new inputs, (b) bump the version, (c) run `/gdd-forge:review` later.

## Re-run a single chapter

`--chapter N` (or the equivalent natural-language request): load `WORK/brief.md`, ask the user only
for fields that chapter N consumes and that are currently `UNDECIDED`, re-dispatch that chapter's
owner agent (fresh dispatch, not PATCH mode), then re-run `gdd-scribe` for `13_Appendices.md` and
`0_Index.md` only. Bump the patch version in `2_Version History.md`.

## Resume

`--resume <OUT dir>`: read `WORK/run-meta.md`, `WORK/brief.md`, `WORK/gap-log.md`, and
`WORK/review-report.md` if present. List `OUT/*.md` to see which chapters already exist. A chapter
counts as done only if its file exists **and** `WORK/reports/<file>.report.md` shows `STATUS: complete`
or `complete-with-gaps`. Resume at the first wave whose chapters are not all done — re-dispatch only
that wave's missing/blocked chapters, then continue W2–W10 forward as normal. If `brief.md` was never
frozen, resume at W0 instead. If `review-report.md` exists but the W10 files do not, resume at W9/W10.

## Failure modes

| Situation | Orchestrator does |
|---|---|
| Agent returns `blocked` | Read its GAPS; ask user; re-dispatch (fresh, not PATCH). |
| Agent wrote to the wrong path | Move the file; note in run-meta; do not re-run. |
| Agent invented a decision (reviewer rule 7 FAIL) | PATCH mode with the exact sentence to remove; add to gap-log as "fabrication caught". |
| User abandons mid-run | Everything so far is on disk in `OUT`/`WORK`; say so and how to resume (`--resume <OUT>`). |

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

| Agent | Model | Chapters |
|---|---|---|
| `gdd-concept-architect` | opus | 3 |
| `gdd-mechanics-designer` | opus | 4 |
| `gdd-narrative-designer` | opus | 5 |
| `gdd-level-designer` | opus | 6 |
| `gdd-ux-designer` | sonnet | 7 |
| `gdd-ai-designer` | opus | 8 |
| `gdd-tech-designer` | sonnet | 9 + 11 |
| `gdd-art-director` | sonnet | 10 |
| `gdd-producer` | sonnet | 12 |
| `gdd-reviewer` | sonnet | review |
| `gdd-scribe` | haiku | 0 / 1 / 2 / 13 |
| `gdd-namer` | opus | naming |
