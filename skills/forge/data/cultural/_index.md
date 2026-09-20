<!-- gdd-forge knowledge base · scavenged from BMad GDD Generator (MIT) · reference only: agents may cite facts from this file; nothing else counts as an external source -->
# Cultural Design Guidelines — Index

Selector field: **D-05 `audience`** region sub-field (free text region attached to the audience decision, e.g. "Vietnam", "China", "US/EU", "Global"). Secondary/corroborating signal: **D-38 `localization_targets`** (multi: vi, en, zh-CN, zh-TW, ja, ko, th, id, es, pt-BR, de, fr, ru, ...).

| File | Selector rule |
|---|---|
| `east-asia.md` | Dispatch when D-05's region is China / Japan / South Korea (CN/JP/KR), or D-38 includes `zh-CN`, `zh-TW`, `ja`, or `ko`. |
| `western.md` | Dispatch when D-05's region is North America (US/Canada), Europe/EU, or United Kingdom, or D-38 includes `en`, `de`, or `fr`. |
| `emerging.md` | Dispatch when D-05's region is Southeast Asia, Latin America, or India, or D-38 includes `vi`, `th`, `id`, `es`, or `pt-BR`. |
| `cross-cultural-principles.md` | **Always passed.** Universal design elements, cultural-adaptation strategy, and sensitive-content guardrails apply regardless of which regions are targeted. |
| `implementation.md` | **Always passed.** Process/team-composition/QA guidance for integrating cultural design work is region-agnostic. |

If D-05's region is broad/global, or D-38 spans multiple buckets above, dispatch every matching regional file (not just one).
