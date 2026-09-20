<!-- gdd-forge template · 02-version-history.md · contract: references/contracts/ch02.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 2. Version History

<!-- 2–3 lines: audit trail of how this GDD came to exist and how it changes over time. Read by producers tracking scope creep and by future pipeline runs deciding what changed since the last freeze. -->

## 2.1 Version Table
<!-- guidance: seed with exactly one row for this run.
- columns: version (D-15) · date (run date) · author (orchestrator/agent-team name) · summary (what this run produced, e.g. chapter range)
- append future rows on later runs — never delete or rewrite prior rows
- ELABORATION: the summary wording; DECISION: version tag itself is D-15, never invented -->
<!--
| Version | Date | Author | Summary |
|---|---|---|---|
| v0.1 | 2025-01-01 | gdd-forge run | Initial draft, chapters 0–13 |
-->

## 2.2 Change Log — This Run
<!-- guidance: bullets grouped under three heads.
- chapters generated (list each with its owner agent)
- GAPs raised and resolved this run (id + one-line resolution)
- fixes applied by the gdd-reviewer fix loop (what changed, which chapter) — read from `run-meta.md` § Fix loop and `gap-log.md`, not estimated
ELABORATION: factual reporting of orchestrator-provided run metadata, nothing invented. -->

## 2.3 Versioning Policy
<!-- guidance: one paragraph stating the semantic-version convention this GDD follows going forward.
- major = a design pillar (ch 3 §3.2) changed
- minor = a full chapter rewrite
- patch = wording/typo/formatting only
State it as standing policy, not as history — this section does not change between runs unless the policy itself is amended. -->

## Open Decisions
<!-- One bullet per UNDECIDED brief field touched and per GAP placeholder in this chapter. Format: "- D-xx <field> — UNDECIDED — affects §N.x" or "- G-2-<n> — <what is needed> — §N.x". If none: "None." -->

<!-- Optional: add a real `## New Terms` heading here (after Open Decisions) only if this chapter introduces a term not already in 3_Game Overview §3.10 — one line per term: **Term** — one-sentence definition. Omit entirely if no new term. -->
