# Dispatch rules — every chapter-writing dispatch, full and lite

Your dispatch prompt names this file. Read it before anything else: it is part of your prompt. Your
contract adds chapter-specific rules on top of these; where they differ, the contract wins.

## 1. Three kinds of information

| Kind | Owner | What you do |
|---|---|---|
| **DECISION** — a `D-xx` field or a Gate addition in `brief.md` | the user | Use only what `brief.md` states. Never invent, default or infer one. |
| **PROPOSAL** — a choice the design needs, that the brief does not make, and that is *reversible and local* | you, until the user overrides it | Write your recommended option, tag it `(proposal)`, and list it under Open Decisions with 1–2 alternatives. No GAP, no question to the user. |
| **ELABORATION** — everything else you design | you | Design freely. Numbers carry `(tunable)`, `(est.)` or `(target)`. |

A missing choice is a **GAP**, not a PROPOSAL, when any of these is true:

- it is a `D-xx` field (missing or `UNDECIDED`) and your contract's Depth rule does not say what to do;
- it adds or removes a feature, mode, screen, currency, platform, account/data flow or monetisation mechanism;
- it sets a real-money price or a legal/compliance commitment;
- two sources you were given disagree (brief vs brief, brief vs an upstream file, brief vs as-built data);
- a section owned by another file would have to be written differently depending on the answer.

Test when unsure: *if the user later picks the other option, does anything outside the section that owns
this fact change?* No → PROPOSAL. Yes → GAP.

For a GAP: write the section heading, the single line `⟂ GAP G-<id>-<n>: <what is needed>`, and list it
under GAPS in your REPORT with a class — `structural` (the answer changes what a feature, flow or section
*is*) or `value` (the answer fills in one value; nothing else changes). `<id>` is your chapter number
(full profile) or lite file number; `<n>` restarts at 1 per file.

## 2. Writing rules

1. **Decisions come only from `brief.md`.** Anything else is a PROPOSAL, an ELABORATION or a GAP per §1.
2. **Tag numbers once.** `(tunable)`, `(est.)`, `(target)`. In a table the tag goes in the column header
   (`Default (tunable)`), not in every cell.
3. **No external facts** (market sizes, benchmarks, sales numbers, legal claims) unless they are in
   `brief.md` or a data file you were given. Otherwise write "no data available".
4. **Glossary.** Reuse the anchor glossary's terms verbatim — exact spelling and capitalisation. A
   genuinely new term goes under a final `## New Terms` heading (after Open Decisions). Never redefine a
   term the glossary already has.
5. **Open Decisions lists only what is open.** End the file with `## Open Decisions`: each `UNDECIDED`
   brief field you touched, each GAP placeholder, each `(proposal)` with its alternatives. Never list a
   field that has a value; never add a bullet to say something is *not* open. Nothing open → `None.`
6. **One fact, one home.** Every decision, number, name, list and rule is stated in exactly one section —
   the one that owns it (your contract's *Owns* line — or, where the contract has none, the section its
   Sections list assigns the topic to; for another file's facts, that file). Everywhere
   else, inside your file and out, point to it as `→ §x.y` (or `→ <file> §x.y`) without repeating the
   value or re-arguing its rationale. Never contradict an upstream file; if you think it is wrong, raise
   a GAP. A number you derive from other numbers is written as a formula or a note, never listed a second
   time as an independent tunable.
7. **Write for the development team, not for the kit.** The deliverable never mentions the kit's
   process: no "Depth rule", "contract", "dispatch", "slice", "gate", "preset", "checklist",
   "elaboration", agent or model names, and no sentence explaining why a section is short, why a rule did
   or did not trigger, or what another file will or will not cover.
8. **Sources without noise.** Do not hang `(D-xx)`, `(G-xx)` or pillar ids on sentences. Where your
   contract requires traceability (features, mechanics, screens, risks) it lives in a table column or in
   one `Source:` line at the end of the section — once per section, never per sentence.
9. **State what the game has.** Mention an absence only when `D-44` excludes it (once, in the section
   that owns exclusions) or your contract asks for an explicit "none" line.
10. **N/A is one line.** A section your Depth rule removes keeps its numbered heading, followed by exactly
    one line: `N/A — <reason, ≤ 12 words>.` No paragraph, no list of what is absent.
11. **Length budgets are ceilings, not targets.** If your contract gives word budgets, stay under them; a
    simple game should land well under. Prefer a table row or a bullet to a paragraph; never restate a
    section's purpose before its content; never pad. If the design genuinely needs more, stop within 20 %
    over and declare it under `OVER_BUDGET` in your REPORT.
12. **Self-check** against your checklist(s) before reporting. Items tagged `[R]` are reviewer-only (they
    depend on files written after yours): count them n/a, not failing. Fix what you can; report the rest.

Literal strings that stay in English in every output language (the pipeline greps for them): numbered
heading prefixes (`## 4.5 …`), `## Open Decisions`, `## New Terms`, `⟂ GAP`, `N/A —`, `(proposal)`,
`(tunable)`, `(est.)`, `(target)`.

## 3. PATCH mode

When the dispatch says `PATCH MODE`, your file already exists. Use Edit, never Write, and open only your
own file. Change the named placeholder(s) or review item(s) **and every sentence, table row, count and
cross-reference in your file that depends on them** — then re-read the file once top to bottom for what
the change made stale (counts such as "five rules", lists, New Terms, Open Decisions). Leave unrelated
sections alone. Re-run your checklist and report as usual.

## 4. REPORT — the last thing in your final message, exact format

    ## REPORT
    STATUS: complete | complete-with-gaps | blocked
    FILE: <absolute path(s)>
    GAPS:
      - G-<id>-<n> | class: structural|value | field: <D-xx or description> | section: <§> | why: <one line> | suggested options: <a / b / c>
    PROPOSALS: <count> — <§ list, or none>
    CHECKLIST: <passed>/<total> — failing: <ids or none>
    NEW_TERMS: <list or none>
    OVER_BUDGET: <§ list with a reason each, or none>
    CROSS_REFS_CITED: <chapter §list>

`CROSS_REFS_CITED` is full-profile only (13_Appendices §F is built from it) — omit the line in the lite
profile. There is no word-count line: the orchestrator measures the file with `wc -w`.
