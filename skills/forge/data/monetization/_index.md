<!-- gdd-forge knowledge base · scavenged from BMad GDD Generator (MIT) · reference only: agents may cite facts from this file; nothing else counts as an external source -->
# Monetization Models — Index

Primary selector field: **D-06 `business_model`** (Premium, F2P + IAP, F2P + Ads, Subscription, Hybrid, UNDECIDED). Secondary fields: **D-30 `monetization_details`** and **D-31 `monetization_ethics`** (both triggered only when D-06 ∈ {F2P, Subscription, Hybrid}), **D-04 `platforms`**, **D-05 `audience`** region.

| File | Selector rule |
|---|---|
| `primary-models.md` | **Always passed.** The chapter must justify the chosen D-06 model against the Premium/F2P/Subscription alternatives — including to explain why the alternatives were rejected. |
| `hybrid-models.md` | Dispatch when D-06 = `Hybrid`, or D-30 contains `Battle pass`, `DLC/expansions`, or `Season pass`. |
| `platform-considerations.md` | Dispatch when D-04 contains a Mobile (iOS/Android), PC (Steam/Epic), or console (PlayStation/Xbox/Switch) platform — the file only covers those three platform families. |
| `mechanics.md` | Dispatch whenever **D-06 ≠ Premium**. Live-service mechanics (economic health, VIP/loyalty, cosmetic/convenience/content monetization) only apply to ongoing-revenue models. |
| `regional-strategies.md` | Dispatch whenever **D-06 ≠ Premium**, matched against D-05's region (file's Western / Eastern [China, Japan, Korea] / Emerging [SEA, LATAM, India] sections). |
| `ethics.md` | Dispatch whenever **D-06 ≠ Premium** (also whenever D-31 has any entries). |
| `metrics.md` | Dispatch whenever **D-06 ≠ Premium**. ARPU/ARPPU/LTV/conversion/retention metrics don't apply to a one-time purchase. |
| `implementation.md` | **Always passed.** Design-integration, technical-implementation, and community-management best practices apply to any monetization chapter dispatch, Premium included (e.g. "no ongoing monetization pressure" is itself a design pass). |
