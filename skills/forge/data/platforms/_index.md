<!-- gdd-forge knowledge base · scavenged from BMad GDD Generator (MIT) · reference only: agents may cite facts from this file; nothing else counts as an external source -->
# Platform Specifications — Index

Selector field: **D-04 `platforms`** (multi-select). Options per `brief-schema.md`:
iOS, Android, PC (Steam/Epic), PlayStation, Xbox, Switch, Web (HTML5/WebGL), VR (Quest/PSVR), AR, Mini-program (WeChat/Zalo).

| File | Selector rule |
|---|---|
| `mobile.md` | Dispatch when D-04 contains `iOS` or `Android`. |
| `pc.md` | Dispatch when D-04 contains `PC (Steam/Epic)`. |
| `console.md` | Dispatch when D-04 contains `PlayStation`, `Xbox`, or `Switch`. |
| `web.md` | Dispatch when D-04 contains `Web (HTML5/WebGL)`. |
| `vr-ar.md` | Dispatch when D-04 contains `VR (Quest/PSVR)` or `AR`. |
| `selection-criteria.md` | **Always passed.** Platform-agnostic decision criteria (audience, technical, business, dev-resource trade-offs) — needed to justify whichever D-04 platforms were picked, or to help weigh options if D-04 is still open. |

Note: `Mini-program (WeChat/Zalo)` has no dedicated slice in this knowledge base — none of the six files above match on that value alone.
