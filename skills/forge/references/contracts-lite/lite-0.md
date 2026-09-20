# Contract — 0_Index.md (lite profile)
Conventions and writing rules: `dispatch-rules.md`. Headings keep the English `0.` prefix; never delete a numbered heading.

- **Owner**: the orchestrator itself — no agent dispatch, no `## REPORT` block for this file.
- **Reads**: `1_Concept.md` … `5_Tech Note.md` whole, `WORK/brief.md`, `WORK/gap-log.md`, `WORK/review-report.md` (the lite review is mandatory, so this is always on disk).
- **tmpl**: `templates/lite/0-index.md` · **check**: none (see Hard rules) · **data**: none.
- **Owns**: the file abstracts (§0.2) and the status table (§0.3) — every value here is pulled verbatim from a file or report already on disk, never estimated.
- **Budget**: none — assembly only; length follows its five inputs.
- **Sections**:
  - §0.1 Title Block — game name (`D-01`), profile (hyper-casual/casual), GDD version (`D-15`), date, rights holder (`D-41` or `[RIGHTS HOLDER — UNDECIDED]`), language (`D-12`).
  - §0.2 File Abstracts — one line per file 1–5: a link plus a one-sentence abstract taken from that file's own opening paragraph, never re-summarised.
  - §0.3 Status Table — `file | status | open items`. Open items = that file's UNDECIDED brief fields + unresolved GAPs + `(proposal)`s, all counted from its own Open Decisions box.
  - §0.4 How to Read — 3–4 bullets, each a reading path anchored to real §-numbers (e.g. producer: §1 → §4; engineer: §5 → §2.3; artist/UX: §3 alone).
  - Open Decisions — total UNDECIDED count and total GAP count across files 1–5, pointing to each file's own box; never re-listed here. Both zero → `None.`
- **Depth rule**: fixed. If a file is missing, or its saved report shows `STATUS: blocked`, still write this file: mark that row `NOT COMPLETE` in §0.3 and drop it from §0.4's reading paths.
- **Hard rules**: every value in §0.1–§0.3 is pulled verbatim from a file on disk or a saved report — never a fabricated word count or pass rate. This file produces no `## REPORT`.
