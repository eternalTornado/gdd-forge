# Brief Schema — the Input Gate

This file defines every field the gate collects before any chapter is written.
It is the single source of truth for **what the user decides** vs **what agents design**.

## Profiles

The gate defined in this file is the **default full profile** — every Section A/B field and all triggered Section C rows are asked, producing the 13-chapter GDD described in `pipeline.md`. Passing `--profile casual` (or `--profile hyper-casual`) to `/gdd-forge:forge` switches to the **lite gate**: instead of asking each Section A/B/C field one at a time, the orchestrator proposes a preset table of common casual/hyper-casual answers up front (see "Casual Profile Preset" below) and asks far fewer questions overall. The user reviews that single table and confirms, edits, or rejects it in one round — nothing from the preset reaches `brief.md` until explicitly confirmed. Full detail on the lite pipeline, its five output files, and how it differs from the full 13-chapter flow lives in [`profile-casual.md`](profile-casual.md). This schema file remains the single source of truth for every `D-xx` field regardless of profile; the casual profile changes *how* values are collected, never what a field means.

## Three kinds of information

| Kind | Owner | Rule |
|---|---|---|
| **DECISION** (`D-xx`) | User | Never invented. If missing and required → ask via `AskUserQuestion`. If the user explicitly declines → store `UNDECIDED`. |
| **PROPOSAL** | Agent, until the user overrides it | A reversible, local choice the brief does not make. The agent writes its recommended option tagged `(proposal)` and lists it under that file's Open Decisions. No GAP, no question to the user. |
| **ELABORATION** | Agent | Designed freely by the owning agent (mechanics, systems, levels, UI flows, AI behaviours, asset lists, schedules). Tunable numbers are marked `(tunable)`; estimates `(est.)`. |

See `dispatch-rules.md` §1 for the full GAP-vs-PROPOSAL test. An elaboration that *hinges on* a missing decision is a **GAP** when it meets `dispatch-rules.md` §1's GAP conditions, otherwise a tagged `(proposal)`.

## Gate behaviour

1. Parse the user's opening message / attached file. Fill every `D-xx` you can find. Quote the user's words; do not paraphrase into a different meaning.
2. Ask only for **missing** fields. Batch ≤ 4 questions per `AskUserQuestion` call, grouped by section below. Always give the listed options; the tool adds "Other" automatically.
3. `AskUserQuestion` accepts at most 4 options per question ("Other" is added automatically). For a field whose option list is longer than 4: write the full option list into the question text, offer as the 4 options the values most consistent with what the user has already said (or, with no signal, the first 4 listed), and tell the user to type any other listed value via Other. For multi-select fields (D-04, D-22, D-30, D-38, D-39, D-40) set `multiSelect: true`; if more than 4 values are plausible, split the list across two questions in the same call. Never omit a listed option from the question text, and never pre-select a value on the user's behalf.
4. Ask **trigger** fields (marked ⚡) before their dependants. Skip dependants whose trigger is off.
5. Accept `UNDECIDED` when the user says so ("chưa biết", "skip", "để trống", "TBD"). Record it verbatim as `UNDECIDED`. Never substitute a default.
6. After all required fields are resolved, render the brief (see `brief-template.md`), show it, and ask one final confirmation: *Freeze this brief?* Only then proceed.
7. `D-01` (working title) may legitimately be `GENERATE` → the naming step runs (`pipeline.md` W1).

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
| D-09 | `scope` | Session length, then total content ambition — ask both parts | Size (session length): `Micro (<5 min sessions)`, `Small (5–15 min sessions)`, `Medium (15–45 min sessions)`, `Large (45+ min sessions)` • Content (ambition): `replay-driven (no authored content hours)`, `hours`, `~10 h`, `20–40 h`, `60 h+`, `live service` | 3,4,6,12 |
| D-10 | `team_budget` | Team size, timeline, budget tier | Solo, 2–5, 6–15, 16–50, 50+ • timeline months • budget tier: hobby / indie / AA / AAA, UNDECIDED | 3,12 |
| D-11 | `engine` | Engine / tech stack | Unity, Unreal, Godot, Phaser, Cocos, Custom, UNDECIDED | 9,11 |
| D-12 | `gdd_language` | Language to write the GDD in | Tiếng Việt, English, 中文 | all |
| D-13 | `reference_games` | 2–5 comparable titles and what to borrow / avoid from each | (free text; may be `none`) | 3,4,10,12 |
| D-14 | `output_dir` | Where to write the deliverable | `./deliverables/<slug>/GDD/<version>/` (default), (free text path) | pipeline |
| D-15 | `gdd_version` | Version tag for this GDD | `v0.1` concept, `v0.5` pre-production, `v1.0` production-ready | 2,12 |

`D-09` is one field with two parts. Store the confirmed value as `<size> · content: <ambition>`, e.g.
`Small (5–15 min sessions) · content: replay-driven`. Existing Depth rules that key on the size label
(Micro/Small/Medium/Large) keep working unchanged.

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
| D-30 | D-06 ∈ {F2P, Subscription, Hybrid} | `monetization_details` (multi) | Which mechanisms are acceptable? | Cosmetic IAP, Consumable IAP, Gacha/loot box, Battle pass, Rewarded ads, Interstitial ads, Remove-ads IAP, Subscription tier, Season pass, DLC/expansions | 4,12 |
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
| D-45 | profile = casual or hyper-casual | `kpi_targets` | CPI / D1 / D7 / playtime targets for this game (CPI is only relevant when `D-48 = Yes`; or leave undecided) | (free text — give a value per metric you care about, e.g. `CPI <your cap>, D1 <your floor>, D7 <your floor>, playtime <your floor>`; the kit supplies no default numbers), UNDECIDED | lite-4 |
| D-46 | profile = casual or hyper-casual | `ad_networks` | Ad mediation platform and ad networks to integrate | AppLovin MAX, ironSource, Google AdMob (mediation), LevelPlay, Custom/direct, UNDECIDED | lite-4, lite-5 |
| D-47 | profile = casual or hyper-casual | `build_size_target` | Target install/build size cap | (free text — state your own cap and the store/connection it must satisfy; the kit supplies no default), UNDECIDED | lite-5 |
| D-48 | profile = casual or hyper-casual | `paid_ua` | Will this game run paid user acquisition (CPI tests, ad creatives)? | Yes, No — organic only, UNDECIDED | lite-4, lite-5 |

## Casual Profile Preset

`--profile casual` and `--profile hyper-casual` do not relax the gate's core rule — **no value reaches `brief.md` without the user's explicit confirmation.** Instead of asking every Section A/B/C row individually, the orchestrator renders the proposed table below, shows it once, and asks the user to confirm it as-is, edit specific rows, or reject the whole preset and fall back to the full per-field questions. Only rows the user confirms (verbatim or edited) are written to `brief.md`; each such row is recorded with `Source: casual preset — confirmed by user`. An unconfirmed preset value is never used, never assumed, and never silently carried forward — if the user does not respond to a row, it is asked individually rather than defaulted.

`D-02` (pitch) is a hard requirement in every profile, including casual — the preset table below can never supply it. The gate still refuses to proceed without the user's own pitch text.

### Proposed values

Every cell below holds exactly the schema-valid option string(s) from Section A/B/C above — multi-select fields list more than one option, comma-separated, but never an "X or Y" alternative the user would still have to resolve.

| ID | Field | Hyper-casual preset | Casual preset |
|---|---|---|---|
| D-04 | platforms | iOS, Android | iOS, Android |
| D-05 | audience | Broad/all ages, casual | Broad/all ages, casual |
| D-06 | business_model | F2P + Ads | Hybrid (F2P: ads + IAP) |
| D-09 | scope | Micro (<5 min sessions) · content: replay-driven | Small (5–15 min sessions) · content: ~10 h⁵ |
| D-15 | gdd_version | v0.5 | v0.5 |
| D-20 | multiplayer | None (single-player) | None (single-player) |
| D-21 | narrative_weight | None (pure systems) | Light framing |
| D-22 | ai_agents | None¹ | Enemies² |
| D-23 | level_structure | Endless/arena³ | Level select (grid) |
| D-24 | liveops | None | Content updates only⁴ |
| D-30 | monetization_details | Rewarded ads, Interstitial ads, Remove-ads IAP | Rewarded ads, Interstitial ads, Remove-ads IAP, Consumable IAP |
| D-31 | monetization_ethics | No pay-to-win, No ads for kids | No pay-to-win, No ads for kids |
| D-39 | accessibility | Colour-blind modes, Difficulty options | Colour-blind modes, Difficulty options |

¹ Obstacle/hazard patterns are still designed in `2_Core Gameplay.md` §2.5 — they are level content, not AI.
² Simple movement patterns only, per `contracts-lite/lite-2.md` §2.5.
³ Edit to `Level select (grid)` if the pitch is stage-based.
⁴ Edit to `Seasons/events` if the pitch wants them.
⁵ Edit content to `replay-driven` when D-23 is Endless/arena.

### Always asked, never presumed

Regardless of profile, the following are still asked individually — a preset must never guess them: `D-02` (pitch), `D-03` (genre), `D-07` (art direction), `D-08` (tone), `D-11` (engine), `D-12` (gdd_language), `D-41` (rights holder), `D-37` (device floor), `D-48` (paid_ua — asked before D-45), `D-45` (kpi_targets), `D-46` (ad_networks), `D-47` (build_size_target) (asked, but `UNDECIDED` is accepted for D-11, D-37, D-41, D-48, D-45, D-46, D-47); and, additionally, `D-01` (working title — `GENERATE` accepted), `D-10` (team/timeline/budget — `UNDECIDED` accepted), `D-13` (reference games — `none` accepted), `D-14` (output dir — offer the default path), `D-38` (localization targets — `none` accepted), `D-40` (compliance — `none known` accepted), `D-43` (must-have features — `none` accepted), `D-44` (explicit exclusions — `none` accepted).

Section C triggers apply exactly as in the full gate: `D-35` is asked when `D-23 ∈ {Procedural, Endless}`, `D-36` when `D-24 ≠ None`, `D-42` when `D-11 ≠ UNDECIDED`, and `D-32`/`D-33`/`D-34` if an edited preset row makes their trigger fire (`D-20 ≠ None`, `D-21 ≥ Medium`, `D-22 ≠ None` respectively).

These fields are asked individually rather than left to the preset because the lite contracts consume them directly: `lite-1` derives §1.4 pillars from `D-43` and lists `D-44` under its "Explicitly out" exclusions; `lite-3`/`lite-4` consume `D-38`; `lite-4`/`lite-5` consume `D-40`; `lite-4` §4.6 uses `D-10`; `lite-4` §4.4–§4.6 and `lite-5` §5.5 consume `D-48`.

### Required-set — casual profile

For both `--profile casual` and `--profile hyper-casual`, the brief cannot freeze until these are resolved (not `UNDECIDED`): `D-02, D-03, D-07, D-08, D-12`, plus every row in the Proposed Values table above — each must be confirmed, edited, or explicitly rejected to `UNDECIDED` by the user (silence is not acceptance). `D-11, D-37, D-41, D-48, D-45, D-46, D-47` are still asked individually but may be left `UNDECIDED`: the lite contracts carry an explicit Depth rule for each (engine comparison table, `UNDECIDED` device floor, rights-holder placeholder, organic-only UA treatment, definitions-only KPIs, network-agnostic ad placement, no build-size target). The remaining fields from § Always asked, never presumed above — `D-01, D-10, D-13, D-14, D-38, D-40, D-43, D-44`, plus any Section C trigger fields their answers fire — may likewise be left `UNDECIDED`/`none`, but must have been asked: a field never asked is a gate failure, not an `UNDECIDED`. This required-set replaces the `D-15`-keyed table below only while a casual profile is active; the full profile's required-set table below is unaffected.

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
