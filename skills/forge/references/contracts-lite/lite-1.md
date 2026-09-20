# Contract — 1_Concept.md (lite profile)
Conventions and writing rules: `dispatch-rules.md`. Headings keep the English `1.` prefix; never delete a numbered heading.

- **Owner**: `gdd-concept-architect`
- **Reads**: `brief.md` whole (Section A/B, `D-43`, `D-44`). No upstream file — this is the anchor, dispatched first (W1).
- **tmpl**: `templates/lite/1-concept.md` · **check**: `checklists/lite/lite-1-concept.md` · **data**: `data/game-design-patterns.md`
- **Owns**: identity/header, pitch, pillars (+ forbids), feature set + every priority, exclusions, comparables, audience/platform/business-model summary, setting, scope counts, glossary.
- **Budget**: file ≤ 1,500 words (`wc -w`, any language); per-section ceilings below — section ceilings are individual caps; the file ceiling binds.
- **Sections**:
  - §1.1 Header (≤ 120) — game name (`D-01`, else `[GAME NAME — pending §1.2]`; never your own §1.2 pick), version (`D-15`), profile, date, rights holder (`D-41`/`[RIGHTS HOLDER — UNDECIDED]`), language (`D-12`), platforms (`D-04`); one-line copyright + confidentiality; seed a single-row version table (version · date · summary).
  - §1.2 Name Candidates (≤ 120, or N/A) — `D-01 ∈ {GENERATE, UNDECIDED}` → 3 candidates: name + one-line rationale + trademark-caveat each. Else `N/A — working title set.`
  - §1.3 Game Concept (≤ 150) — `D-02` verbatim + 3–5 sentence expansion (role, loop hint, challenge).
  - §1.4 Design Pillars (≤ 300) — 3–5 pillars: name + meaning sentence + forbid sentence (see Hard rules).
  - §1.5 Feature Set (≤ 250) — top 6–10 features, P0/P1/P2, each mapped to a pillar. `D-43` items = P0; `D-44` items only under "Explicitly out."
  - §1.6 Genre & Comparables (≤ 150) — table: comparable · borrow · avoid, one row per `D-13` title; `none` → say so. No essay.
  - §1.7 Audience & Platforms (≤ 120) — one paragraph: `D-05` + `D-04` + one-line `D-06` (mechanism detail lives in file 4).
  - §1.8 Setting & Theme (≤ 100) — `D-21`: `None` → one line; `Light framing` → short paragraph (`D-08` tone, setting flavour, player-character line); above `Light framing` → escalation, note in Open Decisions.
  - §1.9 Scope & Glossary Seed (≤ 380) — `D-09`'s two parts: session length (per app session, never per run/level) + content ambition, every number `(est.)`; `replay-driven` → no "hours of content" line; then 8–15 glossary terms, ≤ 20 words each — every later file reuses these verbatim.
  - Open Decisions — one bullet per `UNDECIDED` field, GAP, `(proposal)`. None → `None.`
- **Depth rule**: fixed except §1.2 (`D-01`) and §1.8 (`D-21`).
- **Hard rules**: pillars derivable only from `D-02`/`D-08`/`D-43`; before finalising, test every `D-43` must-have and `D-30` mechanism against every forbid — a pillar forbidding a brief requirement is a defect, reword it, never rationalise around it. No feature outranks a feature it depends on. Never introduce a business model, platform, or audience absent from the brief. Name candidates carry `gdd-namer`'s discipline — never claim trademark/app-store clearance.
