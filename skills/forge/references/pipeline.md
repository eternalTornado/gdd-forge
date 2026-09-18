# Pipeline — how `/gdd-forge:forge` runs

The orchestrator is the **main conversation agent** (the one running this skill). It is the only party that talks to the user. Subagents cannot call `AskUserQuestion`; they report GAPs and the orchestrator asks on their behalf.

```
W0 Gate ─► W1 Name ─► W2 ch3 ─► W3 ch4 ‖ ch5 ─► W4 ch6 ‖ ch7 ─► W5 ch8 ‖ ch10 ─► W6 ch9→ch11 ─► W7 ch12 ─► W8 Review ─► W9 Fix loop (≤1) ─► W10 ch1 ‖ ch2 ‖ ch13 ‖ 0_Index ─► Done
```
`‖` = dispatch in parallel (one message, several `Agent` calls). `→` = same agent, sequential.

## Paths the orchestrator computes once

| Var | Value |
|---|---|
| `KIT` | `${CLAUDE_SKILL_DIR}` (folder of this skill: `references/`, `templates/`, `checklists/`, `data/`, `scripts/`) |
| `AGENTS` | `${CLAUDE_PLUGIN_ROOT}/agents` — if unset, `${CLAUDE_SKILL_DIR}/../../agents` |
| `OUT` | `brief:D-14` resolved to an absolute path, default `<cwd>/deliverables/<slug>/GDD/<D-15>/` |
| `WORK` | `OUT/_work/` — `brief.md`, `gap-log.md`, `review-report.md`, `run-meta.md`, `reports/<chapter file>.report.md` (each agent's REPORT block, saved verbatim on arrival) |
| `INPUTS` | `WORK/inputs/` — pre-sliced upstream sections, one subfolder per dispatch (see "Input slicing" below) |

`slug` = kebab-case of the chosen game name, ASCII only.

Pass **absolute paths** to every subagent. Subagents never guess paths.

**Agent names.** Under a plugin install the `Agent` tool lists these agents as `gdd-forge:gdd-<role>`; when the files are copied into `~/.claude/agents/` they appear as `gdd-<role>`. Resolve once at the start of the run by checking the available agent types, and use that exact string as `subagent_type` everywhere. This document writes the bare role name for brevity.

## W0 — Gate (orchestrator)

Follow `brief-schema.md` exactly. Outcome: `WORK/brief.md` in the format of `brief-template.md`, frozen after the user confirms. Also write `WORK/run-meta.md` (date, kit version, D-15, brief sha256 of the frozen text).

Refuse to proceed while D-02 is empty. Everything else may be `UNDECIDED` subject to the required-set table for D-15.

**Provisional paths.** `slug` is not known until W1, but `brief.md` must be on disk before the namer runs. Create `OUT`/`WORK` in W0 with a provisional slug: kebab-case of D-01 if it is a real title, else `untitled-game`. After W1 fixes the real name, rename the `<slug>` directory and update `run-meta.md`. Never write chapters into a provisional directory — renaming happens before W2.

## W1 — Name

- If `D-01 ∈ {GENERATE, UNDECIDED}` (UNDECIDED is treated as GENERATE): dispatch `gdd-namer` (opus) with `brief.md`. It returns 8 candidates, each with rationale, pronounceability note, and a "possible conflicts to check" line (the agent cannot check trademarks — it must say so).
- Ask the user with `AskUserQuestion`: top 4 as options (label = name, description = rationale); "Other" is automatic. If they pick Other with free text, that is the name.
- If `D-01` is a real title, skip the agent but still ask once: *Keep "<title>" as the game name?* (options: Keep / Generate alternatives).
- Write the final name into `brief.md` (`game_name`) and compute `slug`. Create `OUT` and `WORK`.

## Input slicing (run before every W3–W7 dispatch)

A chapter's *Consumes* list names sections, not whole files — but an agent handed a whole chapter path reads the whole chapter. Slice first, then dispatch: it is the single largest saving in the run.

`KIT/scripts/extract-sections.sh <source.md> <dest.md> <spec>...` writes only the requested sections, in source order. Specs are `4.5`, a range `4.3-4.6`, or `all`. A section that isn't found becomes a `<!-- MISSING: §4.5 ... -->` marker in the destination and a `MISSING:` line on stdout — never a silent omission.

**The anchor.** Envelope rule 4 obliges every chapter to reuse the Glossary from ch 3 §3.10 verbatim, and most chapters must cite a pillar from §3.2. Neither is in most *Consumes* lists, so slicing strictly by contract would break rule 4. Immediately after W2, build the anchor once:

```
extract-sections.sh "OUT/3_Game Overview.md" "INPUTS/_anchor.md" 3.2 3.10
```

Pass `INPUTS/_anchor.md` to **every** W3–W7 dispatch in addition to that chapter's own slices. Build it once and reuse it; rebuild it only if ch 3 is patched.

**Slice map.** One subfolder per dispatch, `INPUTS/ch<N>/`:

| Dispatch | Slices to build | Passed whole |
|---|---|---|
| ch 4 | — | ch 3 (the anchor chapter; mechanics reads it in full) |
| ch 5 | ch 4 → `4.1`, `4.3` | ch 3 |
| ch 6 | ch 3 → `3.9` · ch 4 → `4.1-4.6` · ch 5 → `5.3`, `5.5`, `5.9` | — |
| ch 7 | ch 3 → `3.7`, `3.8` · ch 4 → `4.4`, `4.9` · ch 5 → `5.8` | — |
| ch 8 | ch 4 → `4.3-4.6`, `4.10` · ch 5 → `5.6` · ch 6 → `6.4` | — |
| ch 9 | ch 4 → `4.5`, `4.8`, `4.9` · ch 6 → `6.2`, `6.6` · ch 7 → `7.5`, `7.11` · ch 8 → `8.2`, `8.11` · ch 10 → `10.8`, `10.9` | — |
| ch 10 | ch 3 → `3.8` · ch 5 → `5.2`, `5.3`, `5.6`, `5.9` · ch 6 → `6.4` · ch 7 → `7.4`, `7.11` | — |
| ch 11 | ch 6 → `6.6` · ch 8 → `8.10` · ch 10 → `10.8` | ch 9 (the agent's own just-finished file) |
| ch 12 | ch 3 → `3.3`, `3.9` · ch 4 → `4.7`, `4.11` · ch 6 → `6.7` · ch 9 → `9.10` · ch 10 → `10.9` · ch 11 → `11.7` | — |

W8 (review) and W10 (scribe) are **not** sliced — both exist to see whole chapters.

If a slice comes back with a `MISSING:` line, do not dispatch around it: either the upstream agent failed to write that section (re-dispatch it) or the contract and the template disagree (a discrepancy to record in `run-meta.md`).

**Data files** are sliced the same way, by physical file rather than script: `data/platforms/`, `data/cultural/`, `data/monetization/` and `data/accessibility/` each hold one file per topic with an `_index.md` giving the selector. Pass only the slices the brief selects — a mobile-only `D-04` gets `platforms/mobile.md`, not the console, PC and VR specs.

## W2–W7 — Chapter generation

For each dispatch, the prompt to the subagent is assembled from the **dispatch envelope** below. Do not paste chapter contents into the prompt; give paths.

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

### Wave order and parallelism

| Wave | Dispatches (parallel within a wave) | Blocks on | Why this order |
|---|---|---|---|
| W2 | `gdd-concept-architect` → 3 | brief frozen, name chosen, dirs renamed | anchor for everything |
| W3 | `gdd-mechanics-designer` → 4 ‖ `gdd-narrative-designer` → 5 | ch 3 | both read only ch 3 |
| W4 | `gdd-level-designer` → 6 ‖ `gdd-ux-designer` → 7 | ch 4, ch 5 | both read only 3/4/5 |
| W5 | `gdd-ai-designer` → 8 ‖ `gdd-art-director` → 10 | ch 6, ch 7 | 8 reads ch 6 §6.4; 10 reads ch 6 §6.4 and ch 7 §7.4/§7.11 |
| W6 | `gdd-tech-designer` → 9 then 11 | ch 7, ch 8, ch 10 | 9 reads 7/8/10; 11 reads 9 |
| W7 | `gdd-producer` → 12 | ch 9, ch 11 | 12 reads ch 9 §9.10 and ch 11 §11.7 |
| W8 | `gdd-reviewer` → `WORK/review-report.md` | all of 3–12 | |
| W9 | fix loop (below) | review | |
| W10 | `gdd-scribe` → 1 ‖ 2 ‖ 13 ‖ 0_Index (four parallel dispatches) | fixes applied | |

Waves are serial because every chapter's *Consumes* list in its contract (`references/contracts/ch<NN>.md`) must already be on disk. Do not merge waves to save time; a chapter that reads a file being written in the same wave will read nothing or stale text.

Between waves the orchestrator reads each agent's REPORT block only (not the chapter), saves it verbatim to `WORK/reports/<chapter file>.report.md`, and appends GAPS to `WORK/gap-log.md`.

### GAP handling (after each wave, before the next)

1. Collect all `G-n` from the wave's reports. De-duplicate by field.
2. Ask the user with `AskUserQuestion` — ≤ 4 per call — using the agent's *suggested options*. Offer an explicit option "Leave UNDECIDED".
3. Write answers into `brief.md` under `## Gate additions (W<n>)` with the G-id. Log Q/A in `gap-log.md`.
4. If the answer is a real value: re-dispatch the owning agent in **PATCH mode**:
   ```
   PATCH MODE: <file> exists. Replace only the placeholder(s) G-<n> and any sentence that directly depends on them. Do not rewrite other sections. Re-run your checklist. Report as usual.
   ```
   Wait for the patch before starting the next wave (downstream chapters read the patched text).
5. If the answer is "Leave UNDECIDED": the placeholder stays; it is picked up by the Appendices register. Do not re-dispatch.

## W8 — Review

Dispatch `gdd-reviewer` (sonnet) with: all chapter paths (whole, not sliced), `brief.md`, `gap-log.md`, `KIT/references/consistency-rules.md` (the 8 rules), the contract files of the chapters under review, and every checklist in `KIT/checklists/`. It writes `WORK/review-report.md`:

```
# Review report — <game_name> <version>
## Blockers   (decision missing → needs the user)          — id · chapter § · what · suggested options
## Majors     (cross-chapter contradiction / contract miss) — id · chapters · what · owner agent
## Minors     (wording, formatting, checklist nits)         — id · chapter · what
## Checklist matrix   chapter × checklist → pass % 
## Consistency rules  1–8 → PASS/FAIL + evidence
```

## W9 — Fix loop (maximum one iteration)

- **Blockers** → treat exactly like GAPs (ask user, patch owner).
- **Majors** → re-dispatch each owner agent once in PATCH mode with the Major items verbatim. If two chapters contradict, the *downstream* chapter (higher number) is patched to match the upstream one, unless the Major says otherwise.
- **Minors** → not fixed automatically; they are listed in the Appendices §G. (Tell the user how many.)
- After patches, do **not** re-run the full review. Re-run only the Consistency rules check by asking `gdd-reviewer` in a short "RECHECK" dispatch limited to the patched chapters.

## W10 — Boilerplate & assembly

`gdd-scribe` (haiku) writes 1, 2, 13, 0_Index using everything final. It needs `run-meta.md`, `gap-log.md`, `review-report.md`.

## Done — what the orchestrator tells the user

- Absolute path of `OUT`, the file list with word counts (from REPORTs).
- Number of Open Decisions and where they live (Appendices §D).
- Number of Minors left.
- Offer, in one line, to (a) re-run a single chapter with new inputs, (b) bump version, (c) run `/gdd-forge:review` later.

## Resume (`--resume <OUT>`)

1. Read `WORK/run-meta.md` and `WORK/brief.md`; confirm the brief is frozen (else restart W0 from what exists).
2. List `OUT/*.md`. A chapter counts as done only if its file exists **and** `WORK/reports/<file>.report.md` shows `STATUS: complete` or `complete-with-gaps` (the orchestrator saves each REPORT block there as it arrives).
3. Resume at the first wave whose chapters are not all done. Re-dispatch only the missing/blocked chapters of that wave, then continue normally.
4. If `review-report.md` exists but W10 files do not, resume at W9/W10.

## Re-running a single chapter later

`/gdd-forge:forge --chapter 6` (or natural language) → orchestrator loads `WORK/brief.md`, asks only for brief fields that chapter consumes and that are `UNDECIDED`, re-dispatches the owner, then re-runs `gdd-scribe` for 13 and 0_Index. Version patch bump in ch 2.

## Failure modes

| Situation | Orchestrator does |
|---|---|
| Agent returns `blocked` | Read its GAPS; ask user; re-dispatch (fresh, not PATCH). |
| Agent wrote to the wrong path | Move the file; note in run-meta; do not re-run. |
| Agent invented a decision (reviewer rule 7 FAIL) | PATCH mode with the exact sentence to remove; add to gap-log as "fabrication caught". |
| User abandons mid-run | Everything so far is on disk in `OUT`/`WORK`; say so and how to resume (`--resume <OUT>`). |
