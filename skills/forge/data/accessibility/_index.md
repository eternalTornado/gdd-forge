<!-- gdd-forge knowledge base · scavenged from BMad GDD Generator (MIT) · reference only: agents may cite facts from this file; nothing else counts as an external source -->
# Accessibility Standards — Index

Primary selector field: **D-39 `accessibility`** (multi: Colour-blind modes, Subtitles + captions, Remappable controls, Difficulty options, Screen-reader menus, Motion/photosensitivity options, None specified) — always asked, so always resolvable. Secondary fields: **D-04 `platforms`**, **D-40 `compliance`**, **D-05 `audience`** region.

| File | Selector rule |
|---|---|
| `standards.md` | **Always passed.** Baseline WCAG / ADA / Section 508 / EN 301 549 context applies independent of which specific D-39 commitments are made. |
| `platform-guidelines.md` | Dispatch the matching section(s) by D-04: iOS section when D-04 has `iOS`; Android section when D-04 has `Android`; Windows section when D-04 has `PC (Steam/Epic)`; Console section(s) when D-04 has `PlayStation`, `Xbox`, or `Switch`. |
| `disability-categories.md` | Dispatch whenever **D-39 ≠ `None specified`**. Sub-match by which D-39 items were chosen: Colour-blind modes → Color Blindness; Subtitles + captions → Hearing Disabilities; Remappable controls → Motor Disabilities; Screen-reader menus → Blindness/Low Vision; Motion/photosensitivity options → vestibular-sensitivity notes under Motor/Visual. |
| `best-practices.md` | Dispatch whenever **D-39 ≠ `None specified`** (design/development/testing/QA process integration). |
| `testing-tools.md` | Dispatch whenever **D-39 ≠ `None specified`** — needed once any accessibility commitment exists, to plan verification. |
| `legal-compliance.md` | Dispatch whenever **D-39 ≠ `None specified`**, OR D-40 `compliance` includes an age-rating/regional item. Match the Regional Requirements subsection against D-05's region / D-38 target markets. |
