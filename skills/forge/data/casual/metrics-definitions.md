<!-- gdd-forge knowledge base · authored for the casual/hyper-casual lite profile · reference only: agents may cite definitions from this file; nothing else counts as an external source -->
<!-- CRITICAL: this file defines what each metric measures and how it is computed. It contains NO target or benchmark values. A target value belongs to brief:D-45 (kpi_targets) only — an agent that states a number here, or copies a number from here into a chapter as if it were a target, is fabricating. -->

# Casual Funnel — Metric Definitions

This file is the single source every lite-profile chapter must cite for KPI language (`4_Business and LiveOps.md` §4.4 above all). It defines terms so that "D1 retention" means the same thing in every file that uses it. It does not say what a good D1 number is — that is a business decision the user supplies via `D-45`, or leaves `UNDECIDED`.

## Acquisition & Cost

**CPI (Cost Per Install)** — total user-acquisition spend for a campaign or channel divided by the number of installs it produced. Measures how expensive it is to acquire one player, before any consideration of what that player is worth.

**IPM (Installs Per Mille)** — installs generated per 1,000 ad impressions of a marketing creative. Used to compare creative performance independent of the media buy's price; a higher IPM means the creative converts viewers to installs more efficiently.

**CTR (Click-Through Rate)** — clicks on an ad creative divided by impressions of that creative. Measures how compelling the creative is at prompting a tap, upstream of whether that tap becomes an install.

**CVR (Conversion Rate)** — installs (or store-page visits that complete install) divided by clicks on the ad creative that led to the store listing. Measures how well the store listing (icon, screenshots, description) closes what the ad creative opened.

## Retention & Engagement

**D1 / D7 / D30 Retention** — the percentage of players who install on day 0 and return to open the app again on exactly day 1 / day 7 / day 30 after install. Each is computed against the original day-0 cohort, not against the prior day's returning players. These three points are the standard curve read to judge whether a casual game's core loop and onboarding hold attention past the first session, the first week, and the first month.

**Session Length** — the duration of one continuous play session, from app open to app close/backgrounding. Usually reported as an average or median across a cohort.

**Sessions Per Day** — the count of distinct sessions a player opens in a single day, averaged across active players. Distinguishes a game played briefly many times a day (typical of hyper-casual) from one played once for longer (typical of casual with more meta).

**Playtime** — total time spent in the app by a player, summed across all sessions in a given period (per day, per week, or lifetime). Session Length × Sessions Per Day approximates daily Playtime.

## Monetisation

**ARPDAU (Average Revenue Per Daily Active User)** — total revenue (ads + IAP combined, unless split as below) on a given day divided by that day's daily active user count. The standard day-level blended monetisation metric for a live mobile game.

**Ad ARPDAU** — the ad-revenue-only component of ARPDAU: ad revenue for the day divided by daily active users that day. Reported separately from IAP revenue so the two monetisation levers (§4.2/§4.3 of `4_Business and LiveOps.md`) can be tuned independently.

**ARPU (Average Revenue Per User)** — total revenue over a period divided by the total number of users active at any point in that period (not just daily actives). A broader-window counterpart to ARPDAU.

**LTV (Lifetime Value)** — the total revenue a player is projected or observed to generate over their entire relationship with the game, typically modelled by extrapolating a retention/ARPDAU curve forward, or measured retrospectively for a cohort that has fully churned. LTV is always a modelled or measured figure tied to a specific cohort and time window — a bare "LTV" with no cohort/window stated is not a complete definition.

## Ad-Specific Supply Metrics

**eCPM (Effective Cost Per Mille)** — ad revenue earned per 1,000 ad impressions served, i.e. `(ad revenue / impressions) × 1000`. The unit ad networks and mediation platforms report fill and pricing in.

**Fill Rate** — the percentage of ad requests that successfully return a servable ad, out of all ad requests made. A low fill rate means placements in `4_Business and LiveOps.md` §4.2 are going unfilled (no revenue, and in the case of a rewarded placement, a broken player-facing promise) regardless of eCPM.

**Attach Rate** — the percentage of daily active users who engage with a given ad placement or feature at least once in a session (e.g. the share of DAU that watches at least one rewarded video that day). Distinguishes "the placement exists" from "players actually use it."

**Rewarded-Video Engagement Rate** — the percentage of times a rewarded-video offer is shown (or offered) that a player actually starts and completes it, out of all times the offer was presented. Narrower than Attach Rate: Attach Rate is per-DAU-per-day, Rewarded-Video Engagement Rate is per-offer-shown. A placement can have a high Attach Rate (many players see it once) but a low Engagement Rate (few actually complete the video each time it's offered), or vice versa — the two numbers answer different questions and should not be conflated in `4_Business and LiveOps.md` §4.2.

## How These Interact

These metrics form a chain, not a list: acquisition cost (CPI) only means something against what a player is worth (LTV) — LTV versus CPI is the standard go/no-go gate for scaling a user-acquisition campaign, independent of what either number actually is. Retention (D1/D7/D30) is the leading indicator that feeds an LTV model before enough time has passed to observe LTV directly. ARPDAU and Ad ARPDAU are the day-level inputs an LTV projection is built from. Fill Rate and eCPM determine how much of a placement's theoretical ad inventory actually converts to Ad ARPDAU, independent of how well `4_Business and LiveOps.md` §4.2 designed the placement itself. None of these relationships implies a number — whether a given CPI is "worth it" against a given LTV, or what counts as acceptable D1 retention, is exactly the decision `brief:D-45` exists to capture from the user, never to infer from this file.
