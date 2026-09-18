# Contract — 0_Index.md (lite profile)

**Conventions**: `brief:D-xx` = a decision field from `brief-schema.md` · `lite-N` = one of this profile's other four output files (`1_Concept.md` … `5_Tech Note.md`) · `tmpl` = `${CLAUDE_SKILL_DIR}/templates/lite/<file>` skeleton (headings fixed, guidance comments removed in output) · this file has no `check` — see Hard rules — and no `data`, since it cites nothing external. Output language = `brief:D-12`; heading keeps the English `0.` prefix in every language.

- **Owner / model**: the **orchestrator itself** — not a subagent dispatch. This is the one lite output file with no `Agent` call behind it; the orchestrator has every input already on disk (having driven W1–W4) and assembles it directly, the same way `pipeline.md` treats `0_Index.md` as boilerplate assembly rather than design work — except in the lite profile there is no `gdd-scribe` dispatch either, to keep the profile at exactly 6 dispatches / 4 waves.
- **Consumes**: `1_Concept.md`, `2_Core Gameplay.md`, `3_UX Art and Audio.md`, `4_Business and LiveOps.md`, `5_Tech Note.md`, `WORK/brief.md`, `WORK/gap-log.md`, and `WORK/review-report.md` if the lite review (W4) ran.
- **tmpl**: `templates/lite/0-index.md`
- **Sections**:
  - §0.1 Title Block — game name (`brief:D-01`/`game_name`), profile (`hyper-casual` or `casual`), GDD version (`brief:D-15`), date of this run, rights holder (`brief:D-41`, or literally `[RIGHTS HOLDER — UNDECIDED]`), language (`brief:D-12`).
  - §0.2 File Abstracts — one line per `1_Concept.md`…`5_Tech Note.md`: a link plus a single-sentence abstract, pulled from that file's own opening paragraph, never re-summarised from scratch.
  - §0.3 Status Table — one row per file: file · owner agent · model · word count (from that file's saved `## REPORT` block in `WORK/reports/`) · checklist pass % (from `review-report.md` if W4 ran, otherwise `"lite review skipped"`).
  - §0.4 How to Read — 3–4 bullets: e.g. a producer reads `1_Concept.md` → `4_Business and LiveOps.md`; an engineer reads `5_Tech Note.md` → `2_Core Gameplay.md` §2.3; an artist/UX hire reads `3_UX Art and Audio.md` alone. Anchor every path to real §-numbers.
  - Open Decisions — total count of `UNDECIDED` brief fields across all five files, plus total GAP count (resolved + left `UNDECIDED`), each stated as a number with a pointer to where the individual items live (there is no Appendices chapter in the lite profile — the full register lives inline in each file's own Open Decisions box, so this section says "see each file's Open Decisions box," not a re-listing).
- **Depth rule**: fixed. §0.3's checklist-pass column is the only part that varies — it reads `"lite review skipped"` whenever W4 was not run, never a fabricated percentage.
- **Hard rules**:
  1. Every value in §0.1–§0.3 is pulled verbatim from a file already on disk or a saved `## REPORT` block — the orchestrator never estimates a word count or a pass rate it does not have written evidence for.
  2. If any of the five files is missing or its report shows `STATUS: blocked`, `0_Index.md` is still written, but §0.3 marks that row `NOT COMPLETE` and §0.4 does not recommend a reading path through it.
  3. No `## REPORT` block is produced for this file — there is no dispatch to report from. The orchestrator simply writes the file and moves on to telling the user the run is done (see `profile-casual.md` § Done).
