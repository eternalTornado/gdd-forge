# Consistency Rules — lite profile

`gdd-reviewer` enforces these 12 rules across `1_Concept.md` … `5_Tech Note.md` during the lite review (profile-casual.md § W4). Rules 1–8 are the full kit's 8 concerns restated for a 5-file structure — **numbering differs from `consistency-rules.md`** for these; lite checklists cite `[Lite rule n]` against this file only. Rules 9–12 carry the same numbers as `consistency-rules.md`. Keep the numbering stable.

1. Every file uses the Glossary terms from 1_Concept.md §1.9 (no synonyms for defined terms).
2. Every feature in 2_Core Gameplay.md §2.9 traces to a pillar in 1_Concept.md §1.4.
3. Every ad/IAP mechanism in 4_Business and LiveOps.md §4.2/§4.3 uses only D-30 entries.
4. Every asset row (3_UX Art and Audio.md §3.7) uses the naming convention stated in that same section.
5. Every UNDECIDED in brief.md appears in at least one file's Open Decisions box.
6. No file states a decision value absent from brief.md (platform, engine, ad network, KPI target, etc.) — unless it is tagged `(proposal)` and listed in that file's Open Decisions box (dispatch-rules.md §1).
7. No numeric CPI/retention/build-size/performance claim appears without a brief citation (D-45/D-47) or
   an explicit "(target)" tag.
8. Every GAP raised during the run is logged in gap-log.md with its resolution or explicit UNDECIDED.
9. **One fact, one value.** Any number, price, threshold, count, name, priority or yes/no rule that appears in more than one place has the same value everywhere — within a file and across files. A count equals the length of the list it counts. A value stated as derived is not also listed as an independent tunable.
10. **Inventories and flows close.** Every screen, system, SDK, asset, mode, currency or data field that any section references exists in the section that owns that inventory. Every player choice the gameplay chapter requires has a home screen, and the screen flow has the edges needed to reach it. Every persisted value has exactly one storage location. Every `§x.y` cross-reference points to a section that exists and actually contains the cited content.
11. **Pillars, exclusions and priorities hold.** No mechanic, screen, monetisation mechanism or tech choice violates a pillar's forbid clause or a `D-44` exclusion. No feature has a higher priority than a feature it depends on.
12. **Proportionate and clean.** Scope matches `D-09`/`D-10` (no section sized for a bigger game or team than the brief describes; lite files within their contract budgets). No fact restated outside its owning section (dispatch rule 6). No kit/process vocabulary in the deliverable (dispatch rule 7). N/A sections are one line (dispatch rule 10).

Severity: a FAIL of 9, 10 or 11 is always a **Major**. A rule-12 finding is a **Major** when a lite file exceeds its total budget by more than 20 %, a section is sized for a scope the brief rules out, or a restated fact carries a value (it can drift); otherwise a **Minor**.
Owner of a rule-9/10 Major: the file that does *not* own the fact (owner = the contract's *Owns* line); if the owning file contradicts itself, the owning file.
