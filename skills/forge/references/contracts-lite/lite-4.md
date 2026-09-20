# Contract — 4_Business and LiveOps.md (lite profile)
Conventions and writing rules: `dispatch-rules.md`. Headings keep the English `4.` prefix; never delete a numbered heading.

- **Owner**: `gdd-producer`
- **Reads**: brief `D-06, D-09, D-24, D-30, D-31, D-36, D-38, D-40, D-44, D-45, D-46, D-48`; `1_Concept.md` and `2_Core Gameplay.md` whole (mainly file 1 §1.5/§1.7, file 2 §2.1/§2.3/§2.4/§2.6/§2.9).
- **tmpl**: `templates/lite/4-business-liveops.md` · **check**: `checklists/lite/lite-4-business.md` · **data**: `data/monetization/` slices `D-06` selects; `data/casual/metrics-definitions.md`.
- **Owns**: ad placements and cadence, IAP catalogue and real-money prices, KPIs, UA/creative, roadmap, business risks, LiveOps, localisation/compliance path.
- **Budget**: file ≤ 1,500 words (`wc -w`, any language); per-section ceilings below — section ceilings are individual caps; the file ceiling binds.
- **Sections**:
  - §4.1 Business Model Summary (≤ 80) — restate `D-06`, map to §4.2/§4.3; no audience/platform re-derivation.
  - §4.2 Ad Placement Design (≤ 250) — rewarded video tied to a named moment in §2.1/§2.6; interstitial cadence as a named tunable, never a fixed invented number; banner policy or "no banners." Name `D-46`'s network if resolved, else network-agnostic + flag `D-46`.
  - §4.3 IAP Catalogue (≤ 150) — products and real-money prices, `D-30` mechanisms only; mention remove-ads only if `D-30` lists it. A price absent from the brief is a `value` GAP.
  - §4.4 KPI Definitions & Targets (≤ 200) — only metrics with a `D-45` target, plus ≤ 5 monitoring metrics the design depends on, one line each, meaning from `data/casual/metrics-definitions.md` (never pasted). `D-48 ∈ {No, UNDECIDED}` → omit acquisition metrics (CPI, IPM, CTR, CVR). An ad-health threshold is never a GAP — "monitor trend, no threshold" as a `(proposal)` if needed.
  - §4.5 Creative & Playable Ad Concept (≤ 150, or N/A) — CONDITIONAL on `D-48`. `Yes` → §2.3 mechanic demonstrated, first-5-second hook, CTA moment. `No — organic only` → `N/A — no paid user acquisition planned.` `UNDECIDED` → `N/A — paid user acquisition undecided.` (also in Open Decisions).
  - §4.6 Roadmap (≤ 250) — `D-48 = Yes`: prototype → CPI test → soft launch → global launch. Else: prototype → soft launch → global launch. Each phase: goal + testable exit criterion. Durations relative ("T+n") unless the brief gives timeline info.
  - §4.7 Risk Register (≤ 250; ≤ 6 rows) — casual-specific risks, every row sourced. `Owner` column only when `D-10` is a team of 2+.
  - §4.8 LiveOps Plan (≤ 120, or N/A) — CONDITIONAL on `D-24 ≠ None`: cadence from `D-36`, content scoped to `D-09`/`D-23`. Else `N/A — no live operations planned.`
  - §4.9 Localisation & Compliance (≤ 100) — `D-38` languages, `D-40` compliance path.
  - Open Decisions — one bullet per `UNDECIDED` field, GAP, `(proposal)`. None → `None.`
- **Depth rule**: `D-06 = Premium` → §4.2/§4.3 collapse to one paragraph, pricing as an Open Decision. `D-24 = None` → §4.8 N/A. `D-45 = UNDECIDED` → §4.4 definitions-only. `D-48 ∈ {No, UNDECIDED}` gates §4.4–§4.6 per above.
- **Hard rules**: every ad/IAP mechanism uses only `D-30`. Every KPI is defined, never given an invented target — a target with no `D-45` source is a fabrication. No currency or market-size figure beyond the brief.
