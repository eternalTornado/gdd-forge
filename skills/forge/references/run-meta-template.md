# Run meta — <game_name or provisional slug>

<!-- gdd-forge · written by the orchestrator at W0 freeze, updated at W1 (slug), after every wave, and after W9. Never written by a subagent. -->

- date: <ISO date of freeze>
- kit_version: <version from .claude-plugin/plugin.json>
- profile: full | casual | hyper-casual
- gdd_version: <D-15>
- slug: <provisional slug> → <final slug after W1>
- out: <absolute OUT path>
- agent_namespace: gdd-forge:gdd-<role> | gdd-<role>   (resolved once at W0)

## Waves
| Wave | Dispatch | Agent | Model | Status | Words | Self-check | Notes |
|---|---|---|---|---|---|---|---|
<!-- one row per dispatch as it completes. Model: the model actually used (agent frontmatter, or an
explicit override — pipeline.md § Model override). Words: wc -w on the produced file. Self-check: the
agent's own CHECKLIST line (passed/total). Status: complete / complete-with-gaps / blocked / patched.
Notes hold MISSING handling, wrong-path moves, contract/template discrepancies, and any fallback to
whole-file input if a script step failed. -->

## Fix loop
- iterations: 0
- patched_chapters: none
- recheck: not run
<!-- filled after W9 (full profile) or a W4 patch (lite): iterations 0|1, the files patched, and the RECHECK PASS/FAIL summary; read by 2_Version History.md §2.2 -->

## Discrepancies
<!-- anything an agent flagged outside its REPORT block (contract vs dispatch disagreements), one bullet each -->
