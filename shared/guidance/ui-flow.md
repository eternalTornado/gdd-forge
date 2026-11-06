# Guidance — UI flow systems

Screens, navigation, HUD, onboarding.

- Start from the player choices other systems require: every choice needs a home screen. A choice with no screen is a gap you created.
- One screen inventory table: screen · purpose · entry · exit · key elements. A screen with no exit is a dead end.
- Walk the flow backward from the end of a run or session to every home screen; it is the fastest way to find an unreachable choice.
- A screen with no gameplay, platform or business reason is scope creep; cut it.
- Never mention a screen or HUD element in passing: if it is not a row, it does not exist yet.
- Point to the owning system for any rule or number (→ <file> §Rules) instead of restating it.
- UX principles must be testable against a screen ("never more than two taps to the core loop"), not maxims.
- Onboarding: name where each core mechanic is first taught, in the order the mechanics docs make learnable.
- Accessibility: map each D-39 commitment to a named feature ("colour-blind palette toggle in Settings"), never restate the commitment's label.
- For multiplayer, do not forget waiting, disconnect/reconnect and post-match screens.
