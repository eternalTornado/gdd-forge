# Guidance — 7_Interface.md (full profile)

## Contract notes
- Ch 9 reads your §7.5 and §7.11 directly, and ch 10 reads your §7.4 and §7.11 — keep those sections concrete enough for another agent to cite verbatim. §7.11 also defines the GDD's canonical asset naming convention (consistency rule 5) — ch 10 §10.8 adopts and extends it, ch 9 §9.5 inherits it — so state the pattern once, literally, with 2–3 examples.
- You are dispatched in W4, alongside ch 6 only — ch 8 and ch 10 come later, in W5. You read only ch 3, ch 4, and ch 5 §5.8, none of which are being written concurrently with you.

## Working order
1. Read `brief.md` — D-04 (platforms, drives control maps), D-20 (multiplayer, gates lobby/social screens), D-38 (localisation targets), D-39 (accessibility commitments).
2. Read ch 3 §3.7 (Game Flow) and §3.8 (Look & Feel); ch 4 §4.4 (mechanics catalogue, for HUD/feedback needs) and §4.9 (options/save/replay); ch 5 §5.8 (dialogue delivery system, for cutscene/subtitle UI). Do not read other sections.
3. Read the template `07-interface.md`; reproduce §7.1–§7.11 plus Open Decisions.
4. Draft UX Principles (§7.1) from the pillars implied in ch 3 first — every later screen and control decision should trace back to one of these principles.
5. Build the Information Architecture flow (§7.2) next, then the Screen Inventory (§7.3) — add multiplayer screens per the Depth rule if D-20 ≠ None, and confirm the two sections list the same screens.
6. Write HUD & Visual System (§7.4), Control System (§7.5), and Camera & Feedback (§7.6) together — all three describe the same moment-to-moment feedback loop from different angles.
7. Write Audio Direction (§7.7) as its own full sub-section — in this GDD structure, audio lives here, not in a separate chapter.
8. Map D-39 accessibility commitments one-to-one to concrete features in §7.9 using the `data/accessibility/` slices you were given; if D-39 = "None specified," write baseline-only and add to Open Decisions per the Depth rule.
9. Self-check against `ch07-ui-ux.md` and `ch07-audio.md`.

## Anti-fabrication — chapter specifics
The dispatch rules (`dispatch-rules.md`, path in your dispatch prompt) apply — do not restate them, apply them. What follows is what those rules mean for this chapter specifically.

1. Platform list (D-04, drives control schemes), multiplayer existence (D-20, drives social screens), localisation targets (D-38), and accessibility commitments (D-39) are decisions.
2. Screen layout details, HUD element placement, specific camera feedback rules, audio asset categories — all elaboration.
3. No external facts beyond the `data/accessibility/` and `data/platforms/` slices you were given.
4. Reuse ch 3 §3.10 terms for UI labels where they overlap (currency names, mechanic names).
5. The D-39 baseline-only flag belongs in the Open Decisions box when triggered.
6. A screen with no gameplay or platform justification is scope creep. Every screen in the inventory should trace to a mechanic (ch 4), a platform requirement (D-04), or a multiplayer need (D-20) — not personal taste for "a nice settings screen."
7. A screen you invent still needs a stated purpose. Elaboration on layout and flow is free; a screen that exists for no traceable reason at all is scope the brief never asked for.

Examples for this chapter:
- DECISION: accessibility commitments = decision (D-39) — you cannot promise a screen-reader menu if D-39 doesn't list it; that becomes an Open Decision, not a feature.
- DECISION: platform list (D-04) determines which control schemes exist at all — don't add a gamepad scheme for a mobile-only D-04.
- ELABORATION: exact HUD icon placement, specific camera shake values on hit feedback = elaboration `(tunable)`; screen transition style; audio bus naming; the specific wording of a UX principle.

## Domain guidance
- Every Screen Inventory row needs purpose, entry/exit, key elements, and notes — a screen with no stated exit condition is a dead end for implementers.
- UX Principles (§7.1) should be genuinely testable against a screen ("never more than two taps to the core loop") rather than generic maxims ("keep it simple") that any game could claim.
- Information Architecture (§7.2) as a mermaid state diagram should match the Screen Inventory table exactly — no screen in one without the other.
- HUD & Feedback (§7.4, §7.6): describe feedback per channel (visual, audio, haptic where relevant) for hit/success/failure — a mechanic from ch 4 §4.4 with no feedback channel is incomplete.
- Control System (§7.5): one input map per D-04 platform, and note remapping support explicitly tied to D-39 — don't assume remapping is available if it isn't a stated commitment.
- Audio Direction (§7.7) needs four things at minimum: music style and adaptive layering, SFX categories, VO/dialogue delivery (tied to ch 5 §5.8's mechanism), and mix priorities — treat this as seriously as the visual UI, not an afterthought paragraph.
- For audio asset naming, favor a simple prefix convention (music/SFX/VO) and note loop points and platform quality tiers qualitatively — exact bitrates belong to ch 9/10 asset pipelines, not here.
- Accessibility (§7.9): map every D-39 item to a named feature ("colour-blind modes" → "deuteranopia/protanopia palette toggle in Settings > Display") — a vague restatement of the brief field is not a design.
- Localisation Considerations (§7.10): call out text expansion risk for any D-38 language known to run long, and RTL only if a relevant language is targeted.
- Control System (§7.5) should note platform-specific input conventions (back-button behaviour on Android, controller glyph conventions on console) rather than a single generic scheme reused across every platform in D-04.
- The UI & Audio Asset Inventory (§7.11) defines the naming pattern every later asset table adopts (ch 10 §10.8 extends it, ch 9 §9.5 and ch 13 §C inherit it): state it once as a literal pattern with 2–3 examples, choose prefixes broad enough to cover art assets too (CHR_, ENV_, PROP_, VFX_, UI_, SFX_, MUS_ …), and follow it in every row.
- When D-20 ≠ None, don't forget the un-glamorous screens: matchmaking wait state, disconnect/reconnect handling, and post-match summary — these are the ones implementers most often discover missing.
- Camera & Feedback (§7.6): state the camera model (fixed, follow, player-controlled) as a rule, then describe feedback channels per event type — a camera description with no feedback rules attached is incomplete.
- Common failure pattern: an accessibility section that restates D-39's option labels verbatim instead of naming the actual UI feature that implements each one — implementers need a feature name, not a repeated brief field.
- Help, Tutorialisation & Onboarding UI (§7.8) should name where each mechanic from ch 4 §4.4 is first taught on-screen — an onboarding section with no mapping to the mechanic order in ch 4 §4.4 is disconnected (ch 6 §6.3 is written in parallel with you and follows the same order) from the rest of the design.

## PATCH mode notes
- Do not restructure the Information Architecture diagram or Screen Inventory unless the patch requires it — both must stay in lockstep with each other even after a patch.
- Touch only the named `G-<ch>-<n>` placeholder(s) and directly dependent screens/rows (e.g., accessibility features added once D-39 resolves).
