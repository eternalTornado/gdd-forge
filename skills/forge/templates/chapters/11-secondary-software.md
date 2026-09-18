<!-- gdd-forge template · 11-secondary-software.md · contract: references/contracts/ch11.md -->
<!-- Fill every section. Keep heading numbers. Remove all <!-- --> comments in the output. Body language = brief D-12. -->

# 11. Secondary Software

<!-- 2–3 lines: the non-runtime software that supports production — editor tooling, pipeline tools, build/CI, debug and QA tooling.
Written in the same run as ch 9, right after it, since tool choices follow from the engine/stack decision made there. Read by engineering leads and producers scoping tooling budget. -->

## 11.1 Tooling Overview & Principles
<!-- guidance: 3–5 principles guiding tool choices.
- build vs buy default stance, and when to override it
- in-editor vs standalone tooling preference
- how team size (D-10) bounds tooling investment — a solo/small team should not be planned a AAA-scale toolchain
- DECISION: team size and existing tooling come only from D-10/D-42; ELABORATION: which principle follows from them
- state the principle before any tool is named in §11.2–§11.6, so every later tool choice can be checked against it -->

## 11.2 Editor & Engine Tooling
<!-- guidance: level editor needs (ties to ch 6 §6.2 structure), custom inspectors, procgen tools if ch 6 §6.6 requires them.
- DEPTH RULE: if D-11 = UNDECIDED, mark engine-specific rows "engine-dependent" rather than naming a specific engine's tools
- list tooling per system: level, encounter, dialogue (ch 5 §5.8), AI behaviour (ch 8 §8.2) -->

## 11.3 Content & Asset Pipeline Tools
<!-- guidance: importers and validators enforcing the naming/metadata convention from ch 10 §10.8.
- automated checks, not manual review, wherever feasible
- state what happens on a validation failure (block commit / warn / block build)
- cover audio/media profile validation from ch 7 §7.11 alongside art assets — one validator family, not two -->

## 11.4 Build, CI/CD & Distribution
<!-- guidance: installers, launchers, patching/update delivery.
- coordinate with ch 9 §9.9's pipeline rather than duplicating it — this section covers the tooling, ch 9 covers the process
- reuse existing tooling from D-42 before proposing new tools
- note distribution-channel-specific packaging needs implied by D-04 platforms -->

## 11.5 Debug, Telemetry & Live Tools
<!-- guidance: cover —
- AI debug tooling requested in ch 8 §8.10 (perception gizmos, behaviour inspectors)
- analytics/telemetry hooks feeding ch 12's KPIs (§12.6/§12.7)
- in-game debug console/commands for QA and support
- if D-24 (liveops) ≠ None, include the content-scheduling/remote-config tool that ch 12 §12.7 events rely on -->

## 11.6 Localisation & QA Tooling
<!-- guidance: cover —
- string extraction/import tools for D-38 languages
- test-case/checklist tooling supporting ch 12 §12.10's QA plan
- pseudo-localisation or text-expansion check tooling tied to ch 7 §7.10 -->

## 11.7 Tool Matrix
<!-- guidance: consolidate every tool named in §11.1–§11.6 into one table — this is the chapter's single source of truth; §11.1–§11.6 explain, this table lists. -->
<!--
| Tool | Purpose | Owner | Build vs buy | Phase |
|---|---|---|---|---|
| … | … | … | … | … |
-->

## Open Decisions
<!-- One bullet per UNDECIDED brief field touched and per GAP placeholder in this chapter.
Format: "- D-xx <field> — UNDECIDED — affects §N.x" or "- G-n — <what is needed> — §N.x".
If none: "None." D-11 = UNDECIDED must always appear here per the Depth rule, since it forces every engine-specific row above to read "engine-dependent" instead of a concrete tool name. -->

<!-- New terms (only if you introduced a term not in 3_Game Overview §3.10): -->
