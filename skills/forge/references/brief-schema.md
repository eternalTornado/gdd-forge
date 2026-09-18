# Brief Schema — the Input Gate

This file defines every field the gate collects before any chapter is written.
It is the single source of truth for **what the user decides** vs **what agents design**.

## Profiles

The gate above is the **default full profile** — every Section A/B field and all triggered Section C rows are asked, producing the 13-chapter GDD described in `pipeline.md`. Passing `--profile casual` (or `--profile hyper-casual`) to `/gdd-forge:forge` switches to the **lite gate**: instead of asking each Section A/B/C field one at a time, the orchestrator proposes a preset table of common casual/hyper-casual answers up front (see "Casual Profile Preset" below) and asks far fewer questions overall. The user reviews that single table and confirms, edits, or rejects it in one round — nothing from the preset reaches `brief.md` until explicitly confirmed. Full detail on the lite pipeline, its five output files, and how it differs from the full 13-chapter flow lives in [`profile-casual.md`](profile-casual.md). This schema file remains the single source of truth for every `D-xx` field regardless of profile; the casual profile changes *how* values are collected, never what a field means.

## Two kinds of information

| Kind | Owner | Rule |
|---|---|---|
| **DECISION** (`D-xx`) | User | Never invented. If missing and required → ask via `AskUserQuestion`. If the user explicitly declines → store `UNDECIDED`. |
| **ELABORATION** | Agent | Designed freely by the owning agent (mechanics, systems, levels, UI flows, AI behaviours, asset lists, schedules). Tunable numbers are marked `(tunable)`; estimates `(est.)`. |

An elaboration that *hinges on* a missing decision is not designed — it becomes a **GAP** (see `pipeline.md`).

## Gate behaviour

1. Parse the user's opening message / attached file. Fill every `D-xx` you can find. Quote the user's words; do not paraphrase into a different meaning.
2. Ask only for **missing** fields. Batch ≤ 4 questions per `AskUserQuestion` call, grouped by section below. Always give the listed options; the tool adds "Other" automatically.
3. Ask **trigger** fields (marked ⚡) before their dependants. Skip dependants whose trigger is off.
4. Accept `UNDECIDED` when the user says so ("chưa biết", "skip", "để trống", "TBD"). Record it verbatim as `UNDECIDED`. Never substitute a default.
5. After all required fields are resolved, render the brief (see `brief-template.md`), show it, and ask one final confirmation: *Freeze this brief?* Only then proceed.
6. `D-01` (working title) may legitimately be `GENERATE` → the naming step runs (`pipeline.md` W1).

## Section A — Identity (always required)

| ID | Field | Ask as | Options to offer | Consumed by |
|---|---|---|---|---|
| D-01 | `working_title` | Do you have a working title, or should the kit generate one? | `GENERATE`, (free text) | all |
| D-02 | `pitch` | One or two sentences: what is the game? | (free text — **hard requirement**, gate cannot proceed without it) | 3 |
| D-03 | `genre` | Primary genre + sub-genre | Action, RPG, Strategy, Puzzle/Casual, Simulation, Adventure/Narrative, Shooter, Platformer, Roguelike, Sports/Racing, Horror, Hybrid (specify) | 3,4,6 |
| D-04 | `platforms` (multi) | Target platforms at launch | iOS, Android, PC (Steam/Epic), PlayStation, Xbox, Switch, Web (HTML5/WebGL), VR (Quest/PSVR), AR, Mini-program (WeChat/Zalo) | 3,7,9,12 |
| D-05 | `audience` | Primary audience | Kids (<12), Teens (13–17), Young adults (18–24), Adults (25–40), 40+, Broad/all ages — plus region & player type (casual / mid-core / hardcore) | 3,5,7,12 |
| D-06 | `business_model` | Business model | Premium (one-time), F2P + IAP, F2P + Ads, Subscription, Hybrid (specify), UNDECIDED | 3,12 |
| D-07 | `art_direction` | Visual style keywords or 2–3 reference titles | Stylised/Cartoon, Pixel, Low-poly, Realistic, Anime, Hand-painted, Minimalist/Flat, Voxel, (free text refs) | 3,7,10 |
| D-08 | `tone_theme` | Tone and theme (mood, setting flavour) | Light-hearted, Epic/heroic, Dark/gritty, Cosy/relaxing, Mysterious, Comedic, Melancholic, (free text) | 3,5,10 |
| D-09 | `scope` | Session length + total content ambition | Micro (<5 min sessions, hours of content), Small (5–15 min, ~10 h), Medium (15–45 min, 20–40 h), Large (45+ min, 60 h+), Endless/service | 3,4,6,12 |
| D-10 | `team_budget` | Team size, timeline, budget tier | Solo, 2–5, 6–15, 16–50, 50+ • timeline months • budget tier: hobby / indie / AA / AAA, UNDECIDED | 3,12 |
| D-11 | `engine` | Engine / tech stack | Unity, Unreal, Godot, Phaser, Cocos, Custom, UNDECIDED | 9,11 |
| D-12 | `gdd_language` | Language to write the GDD in | Tiếng Việt, English, 中文 | all |
| D-13 | `reference_games` | 2–5 comparable titles and what to borrow / avoid from each | (free text; may be `none`) | 3,4,10,12 |
| D-14 | `output_dir` | Where to write the deliverable | `./deliverables/<slug>/GDD/<version>/` (default), (free text path) | pipeline |
| D-15 | `gdd_version` | Version tag for this GDD | `v0.1` concept, `v0.5` pre-production, `v1.0` production-ready | 2,12 |

## Section B — Structure triggers (always asked)

| ID | Field | Ask as | Options | Consumed by |
|---|---|---|---|---|
| D-20 ⚡ | `multiplayer` | Multiplayer? | None (single-player), Local co-op/versus, Online co-op, Online competitive, Async/social, MMO | 4,7,9,12 |
| D-21 ⚡ | `narrative_weight` | How much story? | None (pure systems), Light framing, Medium (arc + cast), Story-driven | 5,6,10 |
| D-22 ⚡ | `ai_agents` (multi) | What needs AI? | Enemies, NPCs/companions, Opponent (strategy/sports), Procedural/director systems, None | 8,9 |
| D-23 ⚡ | `level_structure` | Level / world structure | Linear levels, Hub + levels, Open world, Procedural/roguelike, Level select (grid), Endless/arena, Single persistent space | 6,9 |
| D-24 ⚡ | `liveops` | Live operations after launch? | None, Content updates only, Seasons/events, Full liveops (events + economy + community) | 12 |

## Section C — Conditional details (ask only when triggered)

| ID | Trigger | Field | Ask as | Options | Consumed by |
|---|---|---|---|---|---|
| D-30 | D-06 ∈ {F2P, Subscription, Hybrid} | `monetization_details` (multi) | Which mechanisms are acceptable? | Cosmetic IAP, Consumable IAP, Gacha/loot box, Battle pass, Rewarded ads, Interstitial ads, Subscription tier, Season pass, DLC/expansions | 4,12 |
| D-31 | D-06 ∈ {F2P, Subscription, Hybrid} | `monetization_ethics` | Hard limits (e.g. no pay-to-win, no gacha for minors) | No pay-to-win, No gacha, No ads for kids, Spend caps, None | 12 |
| D-32 | D-20 ≠ None | `multiplayer_scale` | Player count per match & persistence | 2, 3–4, 5–10, 11–64, 65+ • persistent world yes/no | 4,9 |
| D-33 | D-21 ≥ Medium | `narrative_givens` | Any fixed story elements (protagonist, setting, ending)? | (free text; may be `none — design freely`) | 5 |
| D-34 | D-22 ≠ None | `ai_ambition` | AI sophistication target | Scripted/simple FSM, Behaviour trees, Utility/GOAP, Learned/adaptive, UNDECIDED | 8,9 |
| D-35 | D-23 ∈ {Procedural, Endless} | `procgen_constraints` | Hand-authored content share vs generated | Mostly authored, Mixed, Mostly generated | 6 |
| D-36 | D-24 ≠ None | `liveops_cadence` | Update cadence | Weekly, Bi-weekly, Monthly, Seasonal (quarterly) | 12 |
| D-37 | D-04 contains mobile/web | `device_floor` | Minimum device / browser target | (free text, e.g. "iPhone 11 / Android 8, 3 GB RAM") , UNDECIDED | 9 |
| D-38 | always | `localization_targets` (multi) | Launch languages | vi, en, zh-CN, zh-TW, ja, ko, th, id, es, pt-BR, de, fr, ru, none beyond D-12 | 7,12 |
| D-39 | always | `accessibility` (multi) | Accessibility commitments | Colour-blind modes, Subtitles + captions, Remappable controls, Difficulty options, Screen-reader menus, Motion/photosensitivity options, None specified | 7 |
| D-40 | always | `compliance` (multi) | Compliance / rating constraints | Age rating target (ESRB/PEGI/IARC), COPPA, GDPR, China/Vietnam publishing rules, Platform cert (console TRC/XR), None known | 1,9,12 |
| D-41 | always | `rights_holder` | Copyright holder / studio name / license of the GDD itself | (free text) , UNDECIDED | 1 |
| D-42 | D-11 ≠ UNDECIDED | `existing_tooling` | Existing pipelines, CI, DCC tools the team already uses | (free text) , none | 9,11 |
| D-43 | always | `must_have_features` | Features that are non-negotiable | (free text list; may be `none`) | 3,4 |
| D-44 | always | `explicit_exclusions` | Things this game must NOT have | (free text; may be `none`) | 3,4,12 |
| D-45 | profile = casual or hyper-casual | `kpi_targets` | CPI / D1 / D7 / playtime targets for this game (or leave undecided) | (free text — give a value per metric you care about, e.g. `CPI <your cap>, D1 <your floor>, D7 <your floor>, playtime <your floor>`; the kit supplies no default numbers), UNDECIDED | lite-4 |
| D-46 | profile = casual or hyper-casual | `ad_networks` | Ad mediation platform and ad networks to integrate | AppLovin MAX, ironSource, Google AdMob (mediation), LevelPlay, Custom/direct, UNDECIDED | lite-4, lite-5 |
| D-47 | profile = casual or hyper-casual | `build_size_target` | Target install/build size cap | (free text — state your own cap and the store/connection it must satisfy; the kit supplies no default), UNDECIDED | lite-5 |

## Casual Profile Preset

`--profile casual` and `--profile hyper-casual` do not relax the gate's core rule — **no value reaches `brief.md` without the user's explicit confirmation.** Instead of asking every Section A/B/C row individually, the orchestrator renders the proposed table below, shows it once, and asks the user to confirm it as-is, edit specific rows, or reject the whole preset and fall back to the full per-field questions. Only rows the user confirms (verbatim or edited) are written to `brief.md`; each such row is recorded with `Source: casual preset — confirmed by user`. An unconfirmed preset value is never used, never assumed, and never silently carried forward — if the user does not respond to a row, it is asked individually rather than defaulted.

`D-02` (pitch) is a hard requirement in every profile, including casual — the preset table below can never supply it. The gate still refuses to proceed without the user's own pitch text.

### Proposed values

| ID | Field | Hyper-casual preset | Casual preset |
|---|---|---|---|
| D-04 | platforms | iOS + Android | iOS + Android |
| D-05 | audience | Broad/all ages, casual | Broad/all ages, casual |
| D-06 | business_model | F2P + Ads | F2P hybrid (ads + IAP) |
| D-09 | scope | Micro (<5 min sessions) | Small (5–15 min sessions) |
| D-15 | gdd_version | v0.5 | v0.5 |
| D-20 | multiplayer | None | None |
| D-21 | narrative_weight | None | Light framing |
| D-22 | ai_agents | None (obstacle patterns only) | Simple enemies |
| D-23 | level_structure | Endless or Level select | Level select (grid) |
| D-24 | liveops | None or content updates only | Content updates or seasons |
| D-30 | monetization_details | Rewarded ads + Interstitial ads + remove-ads IAP | Rewarded ads + Interstitial ads + remove-ads IAP + consumable IAP |
| D-31 | monetization_ethics | No pay-to-win, no ads targeted at kids | No pay-to-win, no ads targeted at kids |
| D-39 | accessibility | Colour-blind safe palette + difficulty options | Colour-blind safe palette + difficulty options |

### Always asked, never presumed

Regardless of profile, the following are still asked individually — a preset must never guess them: `D-02` (pitch), `D-03` (genre), `D-07` (art direction), `D-08` (tone), `D-11` (engine), `D-12` (gdd_language), `D-41` (rights holder), `D-37` (device floor), `D-45` (kpi_targets), `D-46` (ad_networks), `D-47` (build_size_target).

### Required-set — casual profile

For both `--profile casual` and `--profile hyper-casual`, the brief cannot freeze until these are resolved (not `UNDECIDED`): `D-02, D-03, D-07, D-08, D-11, D-12, D-37, D-41, D-45, D-46, D-47`, plus every row in the Proposed Values table above — each must be confirmed, edited, or explicitly rejected to `UNDECIDED` by the user (silence is not acceptance). This required-set replaces the `D-15`-keyed table below only while a casual profile is active; the full profile's required-set table below is unaffected.

## Required-set per version (D-15)

| D-15 | Must be resolved (not UNDECIDED) |
|---|---|
| `v0.1` | D-02, D-03, D-04, D-05, D-08, D-12, D-20…D-24 |
| `v0.5` | v0.1 set + D-06, D-07, D-09, D-11 |
| `v1.0` | v0.5 set + D-10, D-13, D-41, all triggered Section C fields |

Fields outside the required set may be `UNDECIDED`; chapters render them in an **Open Decisions** box and the Appendices collect them.

## Gate question ordering (default)

1. Section A: D-02, D-01, D-03, D-04 → D-05, D-06, D-07, D-08 → D-09, D-10, D-11, D-12 → D-13, D-14, D-15, D-43
2. Section B: D-20, D-21, D-22, D-23 → D-24, D-38, D-39, D-40
3. Section C: only triggered rows, ≤ 4 per call
4. Freeze confirmation

Skip any question already answered in the opening message.
