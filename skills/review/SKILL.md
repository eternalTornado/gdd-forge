---
name: review
description: Review an existing GDD folder (gdd-forge output or any 13-chapter markdown GDD) against the kit's chapter checklists and consistency rules; produces review-report.md. Use when the user asks to check, audit, or QA a game design document.
---

# Review — GDD QA pass

`$ARGUMENTS` is a path to a GDD folder. If missing, ask for it with `AskUserQuestion` (one question,
free text) before doing anything else.

1. **Detect the profile first.** Read `<folder>/_work/run-meta.md` if it exists and look for a
   `profile:` line. Otherwise infer from the file set: a folder holding `1_Concept.md` and
   `2_Core Gameplay.md` is a **casual (lite)** GDD; one holding `3_Game Overview.md` and
   `4_Gameplay and Mechanics.md` is a **full** 13-chapter GDD. If the folder matches neither shape,
   say so and ask the user which to review rather than guessing.

2. **Resolve and map files.** Resolve the folder to an absolute path, list its markdown files and map
   each by its leading number, tolerating close name variants. Note any number missing entirely —
   report it, do not block on it.
   - **Full**: `0_...` → Index, `1_...` → Copyright, … `13_...` → Appendices, per the contract files
     in [`references/contracts/`](../forge/references/contracts/).
   - **Lite**: `0_Index`, `1_Concept`, `2_Core Gameplay`, `3_UX Art and Audio`,
     `4_Business and LiveOps`, `5_Tech Note`, per
     [`references/contracts-lite/`](../forge/references/contracts-lite/). A lite folder is complete
     at 6 files — do not report chapters 6–13 as missing.

3. **Locate supporting inputs.**
   - Checklists — `${CLAUDE_SKILL_DIR}/../forge/checklists/` for a full GDD, or
     `${CLAUDE_SKILL_DIR}/../forge/checklists/lite/` for a lite one. Pass only the directory that
     matches the profile; the other one's ids will not resolve.
   - `${CLAUDE_SKILL_DIR}/../forge/references/consistency-rules.md` for a full GDD, or
     `${CLAUDE_SKILL_DIR}/../forge/references/consistency-rules-lite.md` for a lite one. The two files
     number their 8 rules differently — pass only the one matching the profile, and cite its numbering
     in the report.
   - The contract files for the mapped files, from `contracts/` or `contracts-lite/`.
   - `<folder>/_work/brief.md` (or `<folder>/brief.md`) if present — pass it along; if absent, tell
     `gdd-reviewer` no brief is available and it must skip brief-dependent checks (full: rules 6, 7;
     lite: rules 3, 5, 6, 7) rather than guessing brief content.

4. **Dispatch.** Call the `Agent` tool with `subagent_type` set to the reviewer agent as it appears in your available agent types — `gdd-forge:gdd-reviewer` under a plugin install, `gdd-reviewer` if the agents were copied to `~/.claude/agents/`. Pass absolute paths to:
   every mapped chapter file, the matching checklists directory, the matching consistency-rules file (full or lite), the
   relevant contract files, and brief.md (if found). Never paste chapter bodies into the prompt — paths only. Ask it
   to write the same report shape `gdd-forge:forge` uses internally:
   ```
   # Review report — <game name if known, else folder name> <version if known>
   ## Blockers   (decision missing → needs the user)          — id · chapter § · what · suggested options
   ## Majors     (cross-chapter contradiction / contract miss) — id · chapters · what · owner agent
   ## Minors     (wording, formatting, checklist nits)         — id · chapter · what
   ## Checklist matrix   chapter × checklist → pass %
   ## Consistency rules  1–8 → PASS/FAIL + evidence (numbered per the rules file passed)
   ```

5. **Write output.** Create `<folder>/_work/` if it doesn't exist. Write the reviewer's report to
   `<folder>/_work/review-report.md`.

6. **Summarise.** Report the counts of Blockers / Majors / Minors to the user, and the Consistency
   rules pass/fail summary, naming the profile you reviewed and any rule you skipped. Offer, in one
   line, to fix findings by re-running `/gdd-forge:forge --chapter N` (full) or
   `/gdd-forge:forge --profile casual --file N` (lite) for each affected file — do not run it
   yourself unless asked.
