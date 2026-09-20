# Pipeline — how `/gdd-forge:forge` runs

The orchestrator is the **main conversation agent** (the one running this skill). It is the only party that talks to the user. Subagents cannot call `AskUserQuestion`; they report GAPs and the orchestrator asks on their behalf.

```
W0 Gate ─► W1 Name ─► W2 ch3 ─► W3 ch4 → ch5 ─► W4 ch6 ‖ ch7 ─► W5 ch8 ‖ ch10 ─► W6 ch9 → ch11 ─► W7 ch12 ─► W8 Review ─► W9 Fix loop (≤1) ─► W10 (ch1→ch2) ‖ ch13 → 0_Index ─► Done
```
`‖` = dispatch in parallel (one message, several `Agent` calls). `→` = sequential inside the wave: the right-hand dispatch starts only after the left-hand file is on disk and its GAPs are handled.

## Paths the orchestrator computes once

| Var | Value |
|---|---|
| `KIT` | `${CLAUDE_SKILL_DIR}` (folder of this skill: `references/`, `templates/`, `checklists/`, `data/`, `scripts/`) |
| `OUT` | `brief:D-14` resolved to an absolute path, default `<cwd>/deliverables/<slug>/GDD/<D-15>/` |
| `WORK` | `OUT/_work/` — `brief.md`, `gap-log.md`, `review-report.md`, `run-meta.md`, `reports/<chapter file>.report.md` (each agent's REPORT block, saved verbatim on arrival) |
| `INPUTS` | `WORK/inputs/` — pre-sliced upstream sections, one subfolder per dispatch (see "Input slicing" below) |

`slug` = kebab-case of the chosen game name, ASCII only.

Pass **absolute paths** to every subagent. Subagents never guess paths.

**Agent names.** Under a plugin install the `Agent` tool lists these agents as `gdd-forge:gdd-<role>`; when the files are copied into `~/.claude/agents/` they appear as `gdd-<role>`. Resolve once at the start of the run by checking the available agent types, and use that exact string as `subagent_type` everywhere. This document writes the bare role name for brevity.

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

## W1 — Name

- If `D-01 ∈ {GENERATE, UNDECIDED}` (UNDECIDED is treated as GENERATE): dispatch `gdd-namer` (opus) with `brief.md`. It returns 8 candidates, each with rationale, pronounceability note, and a "possible conflicts to check" line (the agent cannot check trademarks — it must say so).
- Ask the user with `AskUserQuestion`: top 4 as options (label = name, description = rationale); "Other" is automatic. If they pick Other with free text, that is the name.
- If `D-01` is a real title, skip the agent but still ask once: *Keep "<title>" as the game name?* (options: Keep / Generate alternatives). "Generate alternatives" falls back to the `gdd-namer` path above.
- Write the final name into `brief.md` (`game_name`) and compute `slug`. Finalize `OUT` and `WORK` at their real paths — rename the provisional `<slug>` directory created in W0 if it differs, update `run-meta.md` (`slug:` line). Never write chapters into a provisional directory.

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
| ch 5 | ch 4 → `4.1-4.3` | ch 3 |
| ch 6 | ch 3 → `3.9` · ch 4 → `4.1-4.6` · ch 5 → `5.3`, `5.5`, `5.9` | — |
| ch 7 | ch 3 → `3.7`, `3.8` · ch 4 → `4.4`, `4.9` · ch 5 → `5.8` | — |
| ch 8 | ch 4 → `4.3-4.6`, `4.10` · ch 5 → `5.6` · ch 6 → `6.4` | — |
| ch 9 | ch 4 → `4.5`, `4.8`, `4.9`, `4.11` · ch 6 → `6.2`, `6.6` · ch 7 → `7.5`, `7.11` · ch 8 → `8.2`, `8.11` · ch 10 → `10.8`, `10.9` | — |
| ch 10 | ch 3 → `3.8` · ch 5 → `5.2`, `5.3`, `5.6`, `5.9` · ch 6 → `6.4` · ch 7 → `7.4`, `7.11` | — |
| ch 11 | ch 6 → `6.6` · ch 8 → `8.10` · ch 10 → `10.8` | ch 9 (the agent's own just-finished file) |
| ch 12 | ch 3 → `3.3`, `3.9` · ch 4 → `4.2`, `4.7`, `4.11` · ch 6 → `6.7` · ch 9 → `9.10` · ch 10 → `10.9` · ch 11 → `11.5`, `11.7` | — |

W8 (review) and W10 (scribe) are **not** sliced — both exist to see whole chapters.

If a slice comes back with a `MISSING:` line, never dispatch around it. Three possible causes: either the upstream agent failed to write that section (re-dispatch it); the contract and the template disagree (a discrepancy to record in `run-meta.md`); or the upstream agent applied a Depth rule but deleted the heading instead of keeping it with the one-line N/A statement — re-dispatch that agent in PATCH mode with the instruction `restore heading §x.y followed by the single line 'N/A — <reason, ≤ 12 words>.'` (`dispatch-rules.md` §2, rule 10), then re-slice. A Depth-rule N/A section that keeps its heading is a valid slice, not a MISSING.

**Data files** are sliced the same way, by physical file rather than script: `data/platforms/`, `data/cultural/`, `data/monetization/` and `data/accessibility/` each hold one file per topic with an `_index.md` giving the selector. Pass only the slices the brief selects — a mobile-only `D-04` gets `platforms/mobile.md`, not the console, PC and VR specs.

## W2–W7 — Chapter generation

For each dispatch, the prompt to the subagent is assembled from the **dispatch envelope** below. Do not paste chapter contents into the prompt; give paths.

```
ROLE: you are <agent> writing <file> for the GDD of "<game_name>".
LANGUAGE: write the body in <D-12>. Keep heading numbers in English ("# 4. Gameplay and Mechanics").
RULES: read <KIT>/references/dispatch-rules.md first and obey it in full — it is part of this prompt.
CONTRACT: read <KIT>/references/contracts/ch<NN>.md. Obey Sections, Depth rule, Hard rules (and Owns / Budget where the contract has them).
GUIDANCE: read <KIT>/references/guidance/<role>.full.md — craft advice for this chapter. (Line present only when that file exists.)
INPUTS (read all of these, read nothing else — the slices already contain every upstream
section your contract lets you consume, so never open the full chapter they came from):
  - <WORK>/brief.md
  - <INPUTS>/_anchor.md — ch 3 §3.2 pillars + §3.10 glossary; reuse these terms verbatim
  - <INPUTS>/ch<N>/<sliced upstream files...>
  - template: <KIT>/templates/chapters/<tmpl>
  - checklists: <KIT>/checklists/<...>
  - data: <KIT>/data/<dir>/<only the slices the brief selects>
OUTPUT: write exactly one file <OUT>/<file> (two for the tech-designer run: ch9 then ch11).
```
No inline RULES list, no inline REPORT block — the dispatch closes with the `## REPORT` block defined in
`dispatch-rules.md` §4.

The five dual-profile agents (`gdd-concept-architect`, `gdd-mechanics-designer`, `gdd-ux-designer`,
`gdd-producer`, `gdd-tech-designer` — the ones that also run in the lite profile) have a
`guidance/<role>.full.md` file; the others (`gdd-narrative-designer`, `gdd-level-designer`,
`gdd-ai-designer`, `gdd-art-director`, `gdd-scribe`) do not — omit the GUIDANCE line for them.

Dispatch every subagent with the `Agent` tool. For a wave with more than one dispatch, put every `Agent` call for that wave in **one message**, `run_in_background: true`, then wait for every completion notification before doing anything else. Read only the `## REPORT` block of each result — never the chapter body — to decide next steps.

### Model override

Pass `model: "sonnet"` explicitly on the `Agent` call for the ch 5 (`gdd-narrative-designer`) dispatch
when `D-21 ∈ {None, Light framing}`, and for the ch 8 (`gdd-ai-designer`) dispatch when `D-22 = None` — in
both cases the chapter is mostly `N/A —` lines and does not need the chapter's default model. Otherwise
omit `model` entirely and let the agent's own frontmatter apply (SKILL.md § Agent roster: the frontmatter
is authoritative).

### Utility envelope (W1, W8, W10)

W1, W8 and W10 dispatches are not chapter-writing dispatches — they use a shorter envelope (no template/checklist/data lines):

```
ROLE: you are <agent> producing <deliverable> for the GDD of "<game_name>".
LANGUAGE: body in <D-12>; headings keep the English numbered prefix. (W1: candidate names may be any language; pronounceability notes cover <D-12> and English.)
RULES: read <KIT>/references/dispatch-rules.md first and obey it in full — it is part of this prompt.
CONTRACT: W10 → <KIT>/references/contracts/ch<NN>.md · W8 → <KIT>/references/consistency-rules.md plus contracts ch03.md–ch12.md · W1 → none (agents/gdd-namer.md is the whole contract).
INPUTS (read all of these, read nothing else): <absolute paths — see the wave's input list>
OUTPUT: write exactly one file <absolute path>. (W1: no file — return the ranked list in-message.)
REPORT: the same `## REPORT` block as W2–W7, `dispatch-rules.md` §4 (W8: the reviewer's own BLOCKERS/MAJORS/MINORS block plus the fact ledger; W1: none).
```

### Wave order and parallelism

| Wave | Dispatches (parallel within a wave) | Blocks on | Why this order |
|---|---|---|---|
| W2 | `gdd-concept-architect` → 3 | brief frozen, name chosen, dirs renamed | anchor for everything |
| W3a | `gdd-mechanics-designer` → 4 | ch 3 | reads only ch 3 |
| W3b | `gdd-narrative-designer` → 5 | ch 4 (§4.1–4.3, GAPs handled) | ch 5 §5.2/§5.5 intersect ch 4's world rules and progression, so it must read the finished ch 4 |
| W4 | `gdd-level-designer` → 6 ‖ `gdd-ux-designer` → 7 | ch 4, ch 5 | both read only 3/4/5 |
| W5 | `gdd-ai-designer` → 8 ‖ `gdd-art-director` → 10 | ch 6, ch 7 | 8 reads ch 6 §6.4; 10 reads ch 6 §6.4 and ch 7 §7.4/§7.11 |
| W6 | `gdd-tech-designer` → 9 then 11 | ch 7, ch 8, ch 10 | 9 reads 7/8/10; 11 reads 9 |
| W7 | `gdd-producer` → 12 | ch 9, ch 11 | 12 reads ch 9 §9.10 and ch 11 §11.7 |
| W8 | `gdd-reviewer` → `WORK/review-report.md` | all of 3–12 | |
| W9 | fix loop (below) | review | |
| W10a | `gdd-scribe` → 1 then 2 (one dispatch, two files) ‖ `gdd-scribe` → 13 (second, parallel dispatch) | fixes applied | |
| W10b | `gdd-scribe` → 0_Index (one dispatch) | ch 1, 2, 13 | §0.2/§0.3 abstract and count every chapter 1–13, so those three must exist first |

Waves are serial because every chapter's *Consumes* list in its contract (`references/contracts/ch<NN>.md`) must already be on disk. Do not merge waves to save time; a chapter that reads a file being written in the same wave will read nothing or stale text.

Between waves the orchestrator reads each agent's REPORT block only (not the chapter), saves it verbatim to `WORK/reports/<chapter file>.report.md`, and appends GAPS (with their class) to `WORK/gap-log.md`. When saving a REPORT, the orchestrator runs `wc -w "<OUT>/<file>"` and records the count in `run-meta.md` § Waves, column `Words` — the only word count the kit keeps; agents never report one themselves. `0_Index.md` §0.3 and the Done message read that column.

### GAP handling (after each wave or half-wave W3a/W3b, before the next)

1. Collect all `G-n` from the wave's reports, each tagged with its class (`value` or `structural`,
   `dispatch-rules.md` §1). De-duplicate by field. GAP ids are `G-<ch>-<n>` — `<ch>` is the chapter number
   the agent owns (`G-4-1`, `G-11-2`), `<n>` restarts at 1 per chapter — so parallel agents never collide.
2. Ask the user with `AskUserQuestion` — ≤ 4 per call — using the agent's *suggested options*. Offer an
   explicit option "Leave UNDECIDED". If an answer contradicts a frozen brief value or a pillar, ask the
   user which one yields before writing anything.
3. Write the answer into `brief.md` under `## Gate additions (W<n>)` with the G-id. Log the Q/A and the
   class in `gap-log.md`.
4. Resolve by class:
   - **`value`** — the answer fills in one value; nothing else about the file changes. The orchestrator
     itself replaces the `⟂ GAP` line with the user's value via `Edit` (the value and its unit, no added
     prose) and removes the item from that file's Open Decisions. If more than ~3 lines of the file depend
     on the value, use a PATCH dispatch to the owner instead of editing it yourself:
     ```
     PATCH MODE: <file> exists. Replace only the placeholder(s) G-<ch>-<n> and everything that depends on
     them. Report as usual.
     ```
     (`dispatch-rules.md` §3 defines exactly what the agent then does — do not restate those rules here.)
   - **`structural`** — the answer changes what a feature, flow or section *is*. Re-dispatch the owning
     agent **fresh** (the normal envelope above, not PATCH mode) so the change is integrated through the
     whole file rather than patched around.
   - The agent only proposes the class; the orchestrator upgrades `value` → `structural` whenever the
     user's answer introduces something the suggested options did not (a new feature, mode, screen, flow).
   - A fact owned by an upstream file (per the chapter whose contract Sections list defines that fact) is
     fixed in the **owning** file first; every file that cites it is then PATCHed with "upstream §x.y
     changed — align only what cites it."
   Wait for the fix (edit, PATCH, or fresh dispatch) before starting the next wave — downstream chapters
   read the corrected text.
5. If the answer is "Leave UNDECIDED": the placeholder stays; it is picked up by the Appendices register. Do not re-dispatch.

**PROPOSALS are never asked mid-run** (`dispatch-rules.md` §1) — leave every `(proposal)` exactly as the
agent wrote it. The Done message reports their count and where they live; the user may answer any of them
later, at which point treat the answer like a `value`/`structural` GAP above.

## W8 — Review

Dispatch `gdd-reviewer` (opus) with: all chapter paths (whole, not sliced), `brief.md`, `gap-log.md`, `KIT/references/consistency-rules.md` (the 12 rules), the contract files of the chapters under review, `WORK/reports/*` (each chapter's saved self-check score), and every checklist in `KIT/checklists/*.md` — top level only, never `checklists/lite/` (its ids do not resolve against full chapters). It writes `WORK/fact-ledger.md` (one table `key | kind | value | file §`, built before the rules are judged) and `WORK/review-report.md`:

```
# Review report — <game_name> <version>
## Blockers   (decision missing → needs the user)          — id · chapter § · what · suggested options
## Majors     (cross-chapter contradiction / contract miss) — id · chapters · what · owner agent
## Minors     (wording, formatting, checklist nits)         — id · chapter · what
## Checklist matrix   chapter × checklist → pass % 
## Consistency rules  1–12 → PASS/FAIL + evidence
```

## W9 — Fix loop (maximum one iteration)

- **Blockers** → treat exactly like GAPs (ask user, resolve by class, § GAP handling above).
- **Majors** → PATCH dispatch to the file the Major names as owner. A rule-9/10 Major is owned by the file
  that does *not* own the contradicting fact (owner = the chapter whose contract Sections list defines that
  fact); if the owning file contradicts itself, PATCH the owning file instead. If two chapters contradict
  for a reason the Major doesn't resolve, the *downstream* chapter (higher number) is patched to match the
  upstream one.
- **Minors** → the orchestrator fixes a Minor itself, directly via `Edit`, only when the fix is ≤ 2 lines
  and needs no design judgement (SKILL.md § Non-negotiables, exception 2); every other Minor is listed,
  unfixed, in the Appendices §G. (Tell the user how many.)
- After patches, do **not** re-run the full review. Re-run only the Consistency rules check by asking `gdd-reviewer` in a short "RECHECK" dispatch limited to the patched chapters — rules 1–12, updating the fact-ledger rows for those chapters.
- After the RECHECK, update `run-meta.md` § Fix loop (iterations, patched chapters, RECHECK summary) — `2_Version History.md` §2.2 reads it.

## W10 — Boilerplate & assembly

Run § Pre-extraction for W10 (below) before dispatching W10a.

`gdd-scribe` (sonnet) is dispatched twice in W10a, in parallel:
- **ch1+ch2 run** — one dispatch, two files: `1_Copyright Information.md` then `2_Version History.md`.
  Inputs: `brief.md`, `run-meta.md`, `gap-log.md`, `review-report.md` only — no chapter files, no
  `WORK/reports/*`.
- **ch13 run** — `13_Appendices.md`. Inputs: the per-chapter extracts `INPUTS/ch13/ch<N>.md` (not whole
  chapters 3–12), `brief.md`, `run-meta.md`, `gap-log.md`, `review-report.md`, `WORK/reports/*` (§F needs
  each report's `CROSS_REFS_CITED` line).

W10b is unchanged in order: one dispatch for `0_Index.md` after ch1, ch2 and ch13 all exist, reading
`INPUTS/ch00/abstracts.md` (see § Pre-extraction below), `13_Appendices.md` whole, `run-meta.md` and
`review-report.md`. Never dispatch 0_Index in parallel with the ch1+ch2 or ch13 runs.

### Pre-extraction for W10

`KIT/scripts/extract-sections.sh` gains two spec forms used only here: `@<Heading title>` (matches an
unnumbered heading such as `@Open Decisions` or `@New Terms`, case-insensitive) and `intro` (the chapter's
opening abstract — the text between the H1 line and the first `##` heading).

- **`13_Appendices.md` inputs** — for each of chapters 3–12, build `INPUTS/ch13/ch<N>.md`:
  ```
  extract-sections.sh "OUT/<chapter file>" "INPUTS/ch13/ch<N>.md" "@Open Decisions" "@New Terms" <extra §>
  ```
  where `<extra §>` is the numbered section(s) §13 consolidates from that chapter: ch 3 → `3.2 3.3 3.10`,
  ch 4 → `4.11`, ch 6 → `6.4`, ch 7 → `7.11`, ch 10 → `10.9` (every other chapter gets only
  `"@Open Decisions" "@New Terms"`). Pass the resulting extracts, not the whole chapters, to the ch13
  dispatch.
- **`0_Index.md` inputs** — after `13_Appendices.md` is written, run `extract-sections.sh "OUT/<chapter
  file>" "INPUTS/ch00/ch<N>.intro.md" intro` once per chapter 1–13 (the script overwrites its destination,
  so each chapter needs its own file), then concatenate those files in chapter order into
  `INPUTS/ch00/abstracts.md` with `cat`. Pass this file, `13_Appendices.md` whole, `run-meta.md` and
  `review-report.md` to W10b — never the whole chapters.
- `ABSENT: @New Terms` on stdout is normal (the chapter introduced no term) — do not treat it as a
  problem. A `MISSING:` line (from a numbered-section spec) is still a stop, handled exactly as in §
  Input slicing above.
- **Fallback**: if the script fails for any of the above, pass the whole chapter(s) instead and note the
  fallback in `run-meta.md`.

## Done — what the orchestrator tells the user

- Absolute path of `OUT`, the file list with word counts (`run-meta.md` § Waves, column `Words`).
- Number of Open Decisions and where they live (Appendices §D), and the number of `(proposal)`s and where they live.
- Number of Minors left.
- Offer, in one line, to (a) re-run a single chapter with new inputs, (b) bump version, (c) run `/gdd-forge:review` later.

## Resume (`--resume <OUT>`)

1. Read `WORK/run-meta.md` and `WORK/brief.md`; confirm the brief is frozen (else restart W0 from what exists).
2. List `OUT/*.md`. A chapter counts as done only if its file exists **and** `WORK/reports/<file>.report.md` shows `STATUS: complete` or `complete-with-gaps` (the orchestrator saves each REPORT block there as it arrives).
3. Resume at the first wave whose chapters are not all done. Re-dispatch only the missing/blocked chapters of that wave, then continue normally.
4. If `review-report.md` exists but W10 files do not, resume at W9/W10.

## Re-running a single chapter later

`/gdd-forge:forge --chapter N` (or natural language):

1. Load `WORK/brief.md`; ask only for fields chapter N consumes that are still `UNDECIDED`.
2. Rebuild `INPUTS/ch<N>/` slices from the chapters as they are now on disk (they may have been patched since the original run); if N = 3, rebuild `_anchor.md` afterwards.
3. Fresh dispatch (not PATCH) of the owner agent with the normal W2–W7 envelope.
4. Dispatch `gdd-scribe` in PATCH mode on `2_Version History.md`: append one version row (patch bump of D-15's tag, date, "re-run of chapter N") and one change-log bullet. Rebuild `INPUTS/ch13/ch<N>.md` for the re-run chapter (§ Pre-extraction for W10), then fresh dispatches for `13_Appendices.md` and `0_Index.md`, sequential (13 then 0), with the same W10 input lists (rebuilding `INPUTS/ch00/abstracts.md` after 13 finishes).
5. From the slice map, list the chapters that consume chapter N; tell the user those may now be stale and offer to re-run them — only on explicit confirmation, never cascade unasked.
6. Update `run-meta.md` (a new row under § Waves).

## Failure modes

| Situation | Orchestrator does |
|---|---|
| Agent returns `blocked` | Read its GAPS; ask user; re-dispatch (fresh, not PATCH). |
| Agent wrote to the wrong path | Move the file; note in run-meta; do not re-run. |
| Agent invented a decision (reviewer rule 7 FAIL) | PATCH mode with the exact sentence to remove; add to gap-log as "fabrication caught". |
| User abandons mid-run | Everything so far is on disk in `OUT`/`WORK`; say so and how to resume (`--resume <OUT>`). |
| `MISSING:` line for a section a Depth rule legitimately reduced | Upstream agent deleted the heading. PATCH upstream to restore heading + one-line N/A, re-run the slice, then dispatch. |
