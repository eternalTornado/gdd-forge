# Checklist ch04-mechanics — Gameplay and Mechanics
Applies to: 4_Gameplay and Mechanics.md · Used by: gdd-mechanics-designer (self-check) and gdd-reviewer.

## Core & Meta Loop
- [ ] ME-01 Core Loop (§4.1) is written as 30-second → 5-minute → session loop, each a numbered cycle naming the player's verb
- [ ] ME-02 Meta Loop & Progression (§4.2) names the unlock structure, currencies, and at least one retention hook tied to D-09
- [ ] ME-03 World Rules & Physics (§4.3) states what is always true (movement, collision, time, death/failure) before any mechanic detail

## Mechanics Catalogue
- [ ] ME-04 Every mechanic entry in §4.4 has intent, rules, inputs, outputs, edge cases, and a tunables table
- [ ] ME-05 Every mechanic cites the pillar (ch3 §3.2) it serves
- [ ] ME-06 Systems Interaction Map (§4.5) is a mermaid graph connecting mechanics to systems to resources
- [ ] ME-07 Objectives, Challenge & Puzzle Structure (§4.6) is described separately from the Mechanics Catalogue

## Balance & Economy
- [ ] ME-08 Balance Framework (§4.10) describes target curves qualitatively and names which tunables drive them
- [ ] ME-09 No single mechanic or strategy is described as dominant without a stated counter or cost
- [ ] ME-10 Economy (§4.7) lists sources and sinks in a table
- [ ] ME-11 If D-06 is F2P/hybrid, monetised sinks are marked and use only mechanisms listed in D-30
- [ ] ME-12 Risk vs reward is stated for at least the core loop's central choice

## Multiplayer & Options
- [ ] ME-13 §4.8 is present only if D-20 ≠ None; if D-20 = None, §4.8 is exactly the one-line Depth-rule statement
- [ ] ME-14 If present, §4.8 names modes, match flow, fairness approach, and scale from D-32
- [ ] ME-15 Game Options, Saving & Replay (§4.9) states the difficulty model and save model

## Genre conventions (apply the matching block)
- [ ] ME-16 Action RPG (if D-03 matches): combat responsiveness, progression choices, skill trees, equipment upgrade path, and resource management (health/mana/stamina) are each addressed
- [ ] ME-17 Strategy (if D-03 matches): resource management decisions, unit/faction balance, information presentation, and win-condition variety are each addressed
- [ ] ME-18 Casual/Puzzle (if D-03 matches): immediately-understandable core mechanic, gradual difficulty progression, and session length fit for D-09 are each addressed
- [ ] ME-19 Simulation (if D-03 matches): system cause-and-effect is stated as logical/consistent, and complexity introduction is gradual
- [ ] ME-20 Multiplayer (if D-20 ≠ None): match fairness, progression parity across players, and disconnection/reconnection handling are each addressed

## Feature List
- [ ] ME-21 Feature list table (§4.11) has id, feature, pillar, priority, and depends-on columns filled for every row

## Anti-fabrication
- [ ] ME-22 No monetised sink uses a mechanism absent from brief D-30
- [ ] ME-23 No multiplayer scale, mode, or platform appears that is not derivable from D-20/D-32
- [ ] ME-24 No balance number is stated as fixed fact; all target numbers are tagged (tunable) or (est.)

## Consistency rules
- [ ] ME-25 [Rule 2] Every feature in §4.11 traces to a pillar in ch3 §3.2
- [ ] ME-26 [Rule 1] Terms used for mechanics/systems match the Glossary in ch3 §3.10 (no unexplained synonyms)
