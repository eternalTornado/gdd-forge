# Contract — 5_Tech Note.md (lite profile)
Conventions and writing rules: `dispatch-rules.md`. Headings keep the English `5.` prefix; never delete a numbered heading.

- **Owner**: `gdd-tech-designer`
- **Reads**: brief `D-04, D-11, D-37, D-40, D-42, D-46, D-47, D-48`; `1_Concept.md` and `2_Core Gameplay.md` whole (mainly file 1 §1.7, file 2 §2.3/§2.5/§2.6/§2.8).
- **tmpl**: `templates/lite/5-tech-note.md` · **check**: `checklists/lite/lite-5-tech.md` · **data**: `data/platforms/mobile.md`
- **Owns**: platform floor, engine/stack (incl. existing tooling), system architecture, the storage location of every persisted value, trust boundary, budgets, SDK products, technical risks.
- **Budget**: file ≤ 1,300 words (`wc -w`, any language); per-section ceilings below — section ceilings are individual caps; the file ceiling binds.
- **Sections**:
  - §5.1 Platform & Device Floor (≤ 80) — `D-04` list, minimum device/browser target from `D-37` (or `UNDECIDED` verbatim).
  - §5.2 Engine & Stack (≤ 120) — `D-11 = UNDECIDED` → a 2–3 candidate comparison table, no pick made. Else state `D-11` + one paragraph rationale. Existing tooling (`D-42`) listed once, here.
  - §5.3 Architecture & Data (≤ 450) — core systems list (naming systems already implied by `2_Core Gameplay.md` §2.3/§2.5, not parallel inventions); a storage table — `value | stored where | written when | trusted by` — one row per persisted value files 1–2 name (scores/records per mode, unlock counters, owned items, selected item, settings, linked-account state…); one statement per data decision, never both "add alongside" and "replace." One line: asset naming follows file 3 §3.7.
  - §5.4 Performance & Build-Size Budgets (≤ 100) — frame time, memory, load time, download size, each tagged `(target)`. Download size cites `D-47` if resolved, else flagged in Open Decisions with no number given.
  - §5.5 SDK List (≤ 150) — one row per SDK category the design actually needs: ads if `D-30` has ads; IAP if it has IAP; backend/auth if `D-43` needs accounts/leaderboards; analytics if `D-45` has targets; attribution only if `D-48 = Yes`; remote config/crash reporting optional. Product from `D-46`/`D-42`; else recommend one tagged `(proposal)` with 1–2 alternatives in Open Decisions — not a GAP.
  - §5.6 Compliance (≤ 120) — `D-40` requirements restated in technical terms.
  - §5.7 Technical Risks (≤ 200) — engineering-only risks (business/schedule risk belongs to `4_Business and LiveOps.md` §4.7), phrased so that register could lift them directly.
  - Open Decisions — one bullet per `UNDECIDED` field, GAP, `(proposal)`. None → `None.`
- **Depth rule**: `D-11 = UNDECIDED` → §5.2 comparison-only, §5.3 stays engine-agnostic. `D-47 = UNDECIDED` → §5.4's download-size row has no target.
- **Hard rules**: every performance/build-size figure is tagged `(target)`, traceable to `D-47`, the brief, or `data/platforms/mobile.md` — never a fabricated benchmark. Asset naming is file 3 §3.7's, cited not redefined. Architecture choices local to this file (where a gate is enforced, snapshot vs join, client vs server counter) are `(proposal)`s with a one-line trade-off, not GAPs — unless they change a gameplay rule in file 2 (then GAP).
