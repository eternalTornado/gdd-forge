# Contract — 3_UX Art and Audio.md (lite profile)
Conventions and writing rules: `dispatch-rules.md`. Headings keep the English `3.` prefix; never delete a numbered heading.

- **Owner**: `gdd-ux-designer`
- **Reads**: brief `D-04, D-07, D-08, D-38, D-39`; `1_Concept.md` and `2_Core Gameplay.md` whole (mainly file 1 §1.4/§1.7/§1.8, file 2 §2.1/§2.3/§2.8).
- **tmpl**: `templates/lite/3-ux-art-audio.md` · **check**: `checklists/lite/lite-3-ux-audio.md` · **data**: `data/accessibility/` slices `D-39` selects; `data/platforms/mobile.md`
- **Owns**: screen inventory and flow (the home screen of every player choice), HUD/controls, FTUE, accessibility features, art style, asset list + naming convention, game feel, audio.
- **Budget**: file ≤ 1,900 words (`wc -w`, any language); per-section ceilings below — section ceilings are individual caps; the file ceiling binds.
- **Sections**:
  - §3.1 UX Principles (≤ 120) — 3–4 principles from §1.4 pillars, each testable against a screen decision.
  - §3.2 Screen Flow & Inventory (≤ 400) — flow list or mermaid, then a table (screen · purpose · key elements). Every player choice file 2 requires (item/skin, mode, account linking, every §3.5 toggle) has a home screen here, reachable from the menu and — where the loop needs it — the end-of-run screen. Typically 4–8 screens.
  - §3.3 HUD & Controls (≤ 150) — persistent HUD tied to §2.3 mechanics; input model per `D-04`.
  - §3.4 FTUE & Onboarding (≤ 150) — first §2.3 mechanic taught and how, tied to §2.8's first stage if one exists.
  - §3.5 Accessibility & Localisation (≤ 150) — map each `D-39` commitment to a concrete feature; state `D-38`'s language list and any text-expansion/font risk. `D-39 = "None specified"` → baseline-only, flagged in Open Decisions.
  - §3.6 Art Style Guide (≤ 200) — 2–3 visual pillars from `D-07`/`D-08`, shape language, palette philosophy, one lighting/mood line.
  - §3.7 Asset List & Naming Convention (≤ 350) — the naming pattern (2–3 examples) + a compact asset list (id · type · name · priority). The single canonical naming scheme for the whole lite set — `5_Tech Note.md` cites it, never redefines it.
  - §3.8 Game Feel & Juice (≤ 250) — feedback per event (hit, success, failure, reward) across shake, particles, haptics, audio stings.
  - §3.9 Audio Direction (≤ 150) — music style, SFX categories tied to §2.3, one paragraph on mix priorities.
  - Open Decisions — one bullet per `UNDECIDED` field, GAP, `(proposal)`. `D-39 = "None specified"` always appears. None → `None.`
- **Depth rule**: `D-20 ≠ None` → add a lobby/matchmaking line to §3.2. `D-39 = "None specified"` → §3.5 baseline-only.
- **Hard rules**: every screen in §3.2 traces to a §2.3 mechanic, a `D-04` platform requirement, or an explicit brief need. Every player choice file 2 requires has a home screen per above. Every screen or asset named anywhere in this file appears in §3.2/§3.7. Accessibility commitments come only from `D-39`. Never restate a gameplay rule or tunable — point to file 2's §. §3.7's naming convention is the only one for this GDD set.
