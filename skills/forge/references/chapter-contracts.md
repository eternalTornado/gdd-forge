# Chapter Contracts

A contract says who writes a chapter, with which model, what it may read, what it must contain, and how deep it goes given the brief. Each chapter's contract now lives in its own file under `contracts/chNN.md`, passed by the orchestrator to that agent. Agents read only their own contract, never this index.

## Conventions
- `brief:D-xx` — a decision field from `brief-schema.md`
- `ch N` — the finished markdown of chapter N (path given by the orchestrator)
- `tmpl` — the template skeleton you must follow (headings fixed, guidance comments removed in output); path given in your dispatch
- `check` — the checklist you self-check against before reporting; path given in your dispatch
- `data` — reference knowledge; the only allowed source of external facts
- **Depth rule** — how this chapter shrinks or grows based on triggers. A "N/A chapter" is still written: heading, one paragraph stating why it is minimal and which decision caused it, and any residual content.
- Output language for the body = `brief:D-12`. Headings keep the English chapter-number prefix (e.g. `# 4. Gameplay and Mechanics`) in every language.

Contract files live under `contracts/`.

| Chapter file | Owner agent | Model | Contract file |
|---|---|---|---|
| 0_Index.md | gdd-scribe | haiku | ch00.md |
| 1_Copyright Information.md | gdd-scribe | haiku | ch01.md |
| 2_Version History.md | gdd-scribe | haiku | ch02.md |
| 3_Game Overview.md | gdd-concept-architect | opus | ch03.md |
| 4_Gameplay and Mechanics.md | gdd-mechanics-designer | opus | ch04.md |
| 5_Story, Setting and Character.md | gdd-narrative-designer | opus | ch05.md |
| 6_Levels.md | gdd-level-designer | opus | ch06.md |
| 7_Interface.md | gdd-ux-designer | sonnet | ch07.md |
| 8_Artificial Intelligence.md | gdd-ai-designer | opus | ch08.md |
| 9_Technical.md | gdd-tech-designer | sonnet | ch09.md |
| 10_Game Art.md | gdd-art-director | sonnet | ch10.md |
| 11_Secondary Software.md | gdd-tech-designer* | sonnet | ch11.md |
| 12_Management.md | gdd-producer | sonnet | ch12.md |
| 13_Appendices.md | gdd-scribe | haiku | ch13.md |

\* same run as ch 9, after it.

8 cross-chapter consistency rules enforced by `gdd-reviewer`: see `consistency-rules.md` (full profile) or `consistency-rules-lite.md` (lite profile — different numbering).
