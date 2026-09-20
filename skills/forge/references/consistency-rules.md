# Consistency Rules

`gdd-reviewer` enforces these 12 rules across chapters 3–12 during the review pass. Each numbered rule is cited by id (`Rule 1` … `Rule 12`) in checklists and review reports — keep the numbering stable, since checklist files elsewhere in the kit reference specific rule numbers (e.g. `[Rule 2]`, `[Rule 6]`). Rules 9–12 carry the same numbers in both this file and `consistency-rules-lite.md`.

1. Every chapter uses the Glossary terms from ch 3 §3.10 (no synonyms for defined terms).
2. Every feature in ch 4 §4.11 traces to a pillar in ch 3 §3.2 and appears in ch 12 roadmap.
3. Every level in ch 6 §6.7 references mechanics that exist in ch 4 §4.4.
4. Every character in ch 5 §5.6 has an art entry in ch 10 §10.3 (when D-21 ≠ None).
5. Every asset table in ch 7 §7.11 and ch 10 §10.9, and the pipeline rules in ch 9 §9.5, use the naming convention defined in ch 7 §7.11; ch 10 §10.8 adopts and extends that pattern, never replaces it. Ch 6 §6.4 asset needs are category names only and carry no asset IDs.
6. Every `UNDECIDED` in `brief.md` appears in at least one Open Decisions box.
7. No chapter states a decision value absent from `brief.md` (platform, engine, price, audience, monetisation mechanism) — unless it is tagged `(proposal)` and listed in that file's Open Decisions box (dispatch-rules.md §1).
8. No numeric market/benchmark claims without a source in `data/` or `brief.md`.
9. **One fact, one value.** Any number, price, threshold, count, name, priority or yes/no rule that appears in more than one place has the same value everywhere — within a file and across files. A count equals the length of the list it counts. A value stated as derived is not also listed as an independent tunable.
10. **Inventories and flows close.** Every screen, system, SDK, asset, mode, currency or data field that any section references exists in the section that owns that inventory. Every player choice the gameplay chapter requires has a home screen, and the screen flow has the edges needed to reach it. Every persisted value has exactly one storage location. Every `§x.y` cross-reference points to a section that exists and actually contains the cited content.
11. **Pillars, exclusions and priorities hold.** No mechanic, screen, monetisation mechanism or tech choice violates a pillar's forbid clause or a `D-44` exclusion. No feature has a higher priority than a feature it depends on.
12. **Proportionate and clean.** Scope matches `D-09`/`D-10` (no section sized for a bigger game or team than the brief describes; lite files within their contract budgets). No fact restated outside its owning section (dispatch rule 6). No kit/process vocabulary in the deliverable (dispatch rule 7). N/A sections are one line (dispatch rule 10).

Severity: a FAIL of 9, 10 or 11 is always a **Major**. A rule-12 finding is a **Major** when a lite file exceeds its total budget by more than 20 %, a section is sized for a scope the brief rules out, or a restated fact carries a value (it can drift); otherwise a **Minor**.
Owner of a rule-9/10 Major: the chapter that does *not* own the fact (a fact is owned by the chapter whose contract Sections list defines it); if the owning file contradicts itself, the owning file.

Lite profile: see `consistency-rules-lite.md` — the same 12 rules restated for the 5-file structure; rules 1–8 are renumbered, rules 9–12 keep the same numbers.
