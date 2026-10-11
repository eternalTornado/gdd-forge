# Run meta — <game_name or provisional slug>

<!-- gdd-forge · written by the main agent at W0 freeze (incl. `agent_namespace:` / `workflow:`), at
the slug rename (name pick), and for the notes pipeline.md / profile-casual.md § Failure modes assign it
(`workflow:` after a scriptPath fallback, § Discrepancies); § Waves rows and § Fix loop are written by the
forge-run workflow's own steps (bookkeeping clerk after every wave, review report, fix-loop bookkeeping,
lite index assembly). Never written by a chapter-writing agent. -->

- date: <ISO date of freeze>
- kit_version: <version from .claude-plugin/plugin.json>
- profile: full | casual | hyper-casual
- gdd_version: <D-15>
- slug: <provisional slug> → <final slug after W1>
- out: <absolute OUT path>
- agent_namespace: gdd-forge:gdd-<role> | gdd-<role>   (resolved once at W0) | agents_dir <abs path>   (role files read per dispatch when the agents are not registered)
- workflow: named gdd-forge:forge-run | scriptPath <absolute path to workflows/forge-run.js>   (resolved once at W0)

## Waves
| Wave | Dispatch | Agent | Model | Status | Words | Self-check | Notes |
|---|---|---|---|---|---|---|---|
<!-- one row per dispatch, appended by the workflow's bookkeeping step after each wave (the review and
lite INDEX rows by those steps). Wave: the workflow stage that ran it (incl. `resolve` when answers were
applied). Model: the tier's model as routed by workflows/forge-run.js — `session` when the tier inherits
the session's model, or the model_override when the user asked one model for every dispatch. Words:
wc -w on the produced file. Self-check: the agent's own CHECKLIST line (passed/total). Status: complete /
complete-with-gaps / blocked / patched. Notes: empty unless a bookkeeping step failed; the review row
carries the verified blocker/major/minor counts. Wrong-path moves and contract/template discrepancies go
under § Discrepancies. -->

## Fix loop
- iterations: 0
- patched_chapters: none
- recheck: not run
<!-- filled by the workflow after W9 (full profile) or FIX (lite): iterations 0–N (every fix round run,
including extra rounds the user asked for), the files patched, and one recheck line per round (fixed /
still open / new blockers); the per-item table is review-report.md § Fix loop. Read by
2_Version History.md §2.2 -->

## Discrepancies
<!-- written by the main agent, one bullet each: wrong-path moves, contract/template discrepancies (slice
still MISSING after a PATCH) and other failure-mode notes. Agents' contract-vs-dispatch notes are the
`NOTE:` lines inside their saved REPORTs (WORK/reports/<file>.report.md, dispatch-rules.md §4); the
workflow's bookkeeping step copies each one here as a bullet prefixed with the file name. -->
