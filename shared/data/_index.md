# Knowledge base — which files each document gets

The skill passes data files to a dispatch by document type, then narrows each topic with that topic's
own `_index.md` selector rules (which key on `decisions.md` values). An unused data file in a prompt is
an invitation to cite facts nobody asked for, so pass only what this table selects.

| Document | Files |
| --- | --- |
| `concept` | `game-design-patterns.md` |
| `mechanics`, `progression`, `level`, `enemy-behavior` | `game-design-patterns.md` |
| `economy` | `monetization/` per its `_index.md`; `casual/metrics-definitions.md` when D-06 includes ads |
| `ui-flow` | `platforms/` per its `_index.md` (by D-04); `accessibility/` per its `_index.md` (by D-39, D-04) |
| `narrative`, `presentation` | `cultural/` per its `_index.md` (by D-05 region) |

Files here were scavenged from the BMad Expansion Pack — Game GDD Generator (MIT, WangHaiSheng) and
rewritten; `casual/` was written for gdd-forge.
