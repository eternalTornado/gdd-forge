# Writing rules — every v2 dispatch

Your dispatch names this file. Read it first: it is part of your prompt. Your contract adds rules for
the document you write; where the two differ, the contract wins.

## 1. Decisions and proposals

`decisions.md` is the only home of decisions. A decision is any choice where *picking the other
option would force a change outside the section you are writing*. Everything else is design you do
freely.

| You need… | You do |
| --- | --- |
| a value `decisions.md` already holds | Use it as written. Never contradict it. |
| a decision `decisions.md` does not hold | Pick the option you recommend, add a row to `decisions.md` with Source `proposal`, and use it. Do not stop, do not ask. |
| a local design choice (only this section changes if it changes) | Design it. No row, no tag. |
| something you cannot reasonably propose (two sources disagree; a real-money price; a legal commitment) | Write your best option, then list it under `## Open Questions`. At most 3 per document. |

A row you add uses the next free id `D-100`, `D-101`… and fills `Affects` with the document and
section that use it.

## 2. Writing

1. **No silent decisions.** Every decision you rely on is a row in `decisions.md`.
2. **Tag numbers once:** `(tunable)`, `(est.)` or `(target)`. In a table the tag goes in the column
   header, not in each cell.
3. **No external facts** (market sizes, benchmarks, sales, legal claims) unless they are in a data
   file you were given. Otherwise write "no data".
4. **Glossary.** `concept.md` § Glossary is the only glossary. Reuse its terms verbatim. A genuinely
   new term: append one row to that table (term · one-sentence definition). Never redefine a term.
5. **One fact, one home.** Every rule, number, list and name is stated once, in the section that owns
   it. Elsewhere point to it as `→ <file> §<Heading>` without repeating the value. A derived number is
   a formula, never a second tunable. Exception: `concept.md` § Target restates decision values from
   `decisions.md`; the checker verifies they match.
6. **Write for the team.** Never mention the kit, its process, agents, models, contracts, templates,
   budgets, or why a section is short.
7. **No traceability noise.** No `(D-xx)` tags on sentences. Where a pillar link is required, it is a
   table column or one line, never per sentence.
8. **State what the game has.** Mention an absence only in `concept.md` § Out of Scope.
9. **Omit, don't N/A.** An optional section that does not apply is left out entirely. Required
   sections are listed in your contract.
10. **Budgets are ceilings.** Stay under the contract's word budget; a simple game lands well under.
    Prefer a table row or bullet to a paragraph. No intro paragraphs, no restating a section's purpose.
11. **Language.** Body text in the GDD language from `decisions.md`. Headings stay exactly as in the
    template (English), because the checker reads them.

## 3. Update mode

When the dispatch says `UPDATE`, the file exists. Edit it, never rewrite it. Change what the dispatch
names **and every line in the file that depends on it** (counts, lists, references), then re-read the
file once for anything the change made stale. Leave unrelated sections alone.

## 4. Result — the last thing in your final message

    ## RESULT
    FILES: <absolute path(s) written or edited>
    NEW_DECISIONS: <D-1xx list, or none>
    NEW_TERMS: <terms appended to the glossary, or none>
    OPEN_QUESTIONS: <count>
    OVER_BUDGET: <reason, or none>
