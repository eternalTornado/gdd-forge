# Contract — 2_Core Gameplay.md (lite profile)
Conventions and writing rules: `dispatch-rules.md`. Headings keep the English `2.` prefix; never delete a numbered heading.

- **Owner**: `gdd-mechanics-designer`
- **Reads**: brief `D-03, D-09, D-20, D-22, D-23, D-30, D-35, D-43, D-44`; `1_Concept.md` whole (mainly §1.3–§1.5, §1.7, §1.9).
- **tmpl**: `templates/lite/2-core-gameplay.md` · **check**: `checklists/lite/lite-2-gameplay.md` · **data**: `data/game-design-patterns.md`; `data/monetization/` slices `D-06` selects, only if F2P/hybrid.
- **Owns**: core loop, world rules, mechanics + every gameplay tunable (each in exactly one table), unlock conditions/thresholds, economy counters, score/leaderboard rules, obstacle + generator rules, difficulty curve and modes, feature list. States *that* a player choice exists and when it locks — never which screen hosts it (file 3) nor where it's stored (file 5).
- **Budget**: file ≤ 2,800 words (`wc -w`, any language); per-section ceilings below — section ceilings are individual caps; the file ceiling binds.
- **Sections**:
  - §2.1 Core Loop (≤ 150) — session loop, ≤ 8 one-line verb beats. No per-beat pillar citation (mechanics and §2.9 carry it).
  - §2.2 World Rules (≤ 120) — 3–5 declaratives: movement, collision, fail state.
  - §2.3 Mechanics Catalogue (≤ 1,200; ≤ 5 mechanics) — per mechanic: one `Pillar:` line, 1-sentence intent, rules (≤ 120 words), one I/O line, one tunables table. Every tunable in exactly one table file-wide. An item (skin/character/power-up) touching physics/hitboxes must hold §2.5's guardrails for the worst case — say how. A `D-43` must-have that breaks a pillar's forbid is a `structural` GAP, never rationalised.
  - §2.4 Economy (≤ 200) — sources/sinks table per currency; monetised sinks use only `D-30` mechanisms.
  - §2.5 Obstacles & Generator (≤ 350) — see Depth rule for the `D-23` split.
  - §2.6 Level / Stage Structure (≤ 150) — see Depth rule.
  - §2.7 Difficulty & Pacing Curve (≤ 250) — qualitative; name tunables, never fabricate benchmark numbers.
  - §2.8 First Stages (≤ 300, or N/A) — see Depth rule.
  - §2.9 Feature List Table (≤ 250; ≤ 12 rows) — id · feature · §1.4 pillar · priority · depends-on, cross-ref to §1.5.
  - Open Decisions — one bullet per `UNDECIDED` field, GAP, `(proposal)`. None → `None.`
- **Depth rule**: §2.3/§2.6 imply no obstacles/hazards → §2.5 is a one-line N/A, regardless of `D-22`. `D-22` excludes Enemies → §2.5 still designs non-enemy archetypes, no enemy subsection. `D-23` generator-driven (Endless/arena, Procedural) → §2.5 owns archetypes + every spawn/generator tunable (one table) + guardrails; §2.6 holds only the run's start/end flow; §2.7 owns the curve/modes, naming §2.5's tunables without repeating values; §2.8 = `N/A — generator-driven; rules are in §2.5.` `D-23` discrete structure → §2.5 obstacle/enemy patterns, §2.6 a structure map, §2.7 the curve, §2.8 a first-10-stages table. `D-09` Micro session length → §2.1 stays single-tier.
- **Hard rules**: every mechanic cites a §1.4 pillar. Monetised sinks use only `D-30`; else it's a GAP. §2.5 never contains perception, navmesh, or behaviour-tree language — an escalation GAP, not something to elaborate around. Each tunable lives in exactly one table file-wide; a derived value is a formula, never a second tunable. State that a choice exists and when it locks; never assign it a screen or storage location.
