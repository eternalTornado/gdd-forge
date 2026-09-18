# Consistency Rules

`gdd-reviewer` enforces these 8 rules across chapters 3–12 during the review pass. Each numbered rule is cited by id (`Rule 1` … `Rule 8`) in checklists and review reports — keep the numbering stable, since checklist files elsewhere in the kit reference specific rule numbers (e.g. `[Rule 2]`, `[Rule 6]`).

1. Every chapter uses the Glossary terms from ch 3 §3.10 (no synonyms for defined terms).
2. Every feature in ch 4 §4.11 traces to a pillar in ch 3 §3.2 and appears in ch 12 roadmap.
3. Every level in ch 6 §6.7 references mechanics that exist in ch 4 §4.4.
4. Every character in ch 5 §5.6 has an art entry in ch 10 §10.3 (when D-21 ≠ None).
5. Every asset table in ch 7 §7.11 and ch 10 §10.9, and the pipeline rules in ch 9 §9.5, use the naming convention defined in ch 7 §7.11; ch 10 §10.8 adopts and extends that pattern, never replaces it. Ch 6 §6.4 asset needs are category names only and carry no asset IDs.
6. Every `UNDECIDED` in `brief.md` appears in at least one Open Decisions box.
7. No chapter states a decision value absent from `brief.md` (platform, engine, price, audience, monetisation mechanism).
8. No numeric market/benchmark claims without a source in `data/` or `brief.md`.

Lite profile: see `consistency-rules-lite.md` — the same 8 concerns restated for the 5-file structure; **numbering differs**.
