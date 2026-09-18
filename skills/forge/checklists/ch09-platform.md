# Checklist ch09-platform — Platform Compatibility
Applies to: 9_Technical.md · Used by: gdd-tech-designer (self-check) and gdd-reviewer.

## Platform Targets
- [ ] PL-01 Target Platforms & Hardware Floor (§9.1) lists exactly the platforms in D-04, no more, no fewer
- [ ] PL-02 Device floor (§9.1) states D-37 verbatim when resolved, or marks it UNDECIDED
- [ ] PL-03 Certification/compliance requirements (§9.8) are named per platform present in D-04

## Platform conventions (apply the matching block(s) for D-04)
- [ ] PL-04 Mobile (if D-04 includes iOS/Android): touch control precision, interruption handling (calls/notifications), and battery/network considerations are each addressed
- [ ] PL-05 PC/Console (if D-04 includes PC/PlayStation/Xbox/Switch): input remapping, large-screen UI scaling, and platform feature integration (achievements/cloud saves) are each addressed
- [ ] PL-06 Web (if D-04 includes Web): load-time expectations, cross-browser compatibility, and no-plugin operation are each addressed
- [ ] PL-07 VR/AR (if D-04 includes VR/AR): comfort/motion-sickness mitigation and safety-boundary handling are each addressed

## Compliance
- [ ] PL-08 Platform store/certification guidelines relevant to D-04 are named, not asserted generically
- [ ] PL-09 Age rating and regional compliance targets (D-40) are listed with the platforms they apply to

## Cross-platform
- [ ] PL-10 Cross-platform play or account linking is addressed only if plausible given D-04/D-20, otherwise marked Open Decision

## Anti-fabrication
- [ ] PL-11 No platform-specific feature (e.g. a specific console's controller feature) is claimed for a platform absent from D-04
- [ ] PL-12 No certification or store-policy claim is made without citing the `data/platforms/` slice you were given or brief.md

## Consistency rules
- [ ] PL-13 [Rule 7] No platform, compliance, or hardware value appears that is absent from D-04/D-37/D-40
- [ ] PL-14 [Rule 1] Platform terminology matches the Glossary in ch3 §3.10
- [ ] PL-15 Every platform block applied is one actually present in D-04 (no unused block left in the document)
