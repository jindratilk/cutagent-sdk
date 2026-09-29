---
name: cutagent-color-grading
description: Design and review color correction, shot matching, local light shaping, and creative looks in DaVinci Resolve. Use for exposure, white balance, log normalization, cinematic palettes, product color, skin tone, or grade continuity.
license: AGPL-3.0-only
---

# Color grading

Build a stable image before building a look. Correction should remain credible with the creative layer bypassed, and every creative decision should have a visible purpose.

## Establish the scene

Identify the source type, viewing target, repeated-source or multicam relationships, lighting changes, and hero moments. Do not guess a camera transform from a broad gamut tag or a flat-looking frame. When the source profile is uncertain, compare a conservative interpretation rather than forcing a log conversion.

Capture same-position before frames for hero, middle, late, lighting-change, and match-critical shots. Read `references/professional-workflow.md` for the detailed colorist order and review rubric. Read `references/asset-selection.md` only when considering a LUT, PowerGrade, DCTL, grain, overlay, texture, preset, or reference still.

## Build the grade

Work in passes:

1. Normalize known camera material into the intended viewing pipeline.
2. Set exposure and highlight/shadow separation from scopes plus image meaning.
3. Balance neutrals and skin without removing motivated color from the lighting.
4. Shape contrast and color density; avoid using saturation as the first cure for a flat image.
5. Match adjacent shots by shared anchors before styling them independently.
6. Add a reducible creative palette and local light shaping only where they improve hierarchy.
7. Add texture or finishing effects last.

Separate responsibilities so the technical base, creative look, local shaping, and finish can be reviewed or reduced independently. Omit a layer when it has no job. Empty nodes and labels are not creative work.

For local execution, read `cutagent-color`, `cutagent-sdk`, `cutagent-cli`, `cutagent-verification`, `cutagent-fusion`; check the installed SDK declarations, public CutAgent CLI command cards, and live capabilities for exact operations.

## Review twice

Compare after frames to the exact before positions. Check skin, neutrals, important brand colors, shadow noise, highlight rolloff, gamut, local-mask edges, and shot-to-shot continuity. If the comparison reveals a visible issue, make a focused correction and review that change. Stop when the requested look and continuity are achieved.

Reject a grade that is merely stronger, that hides a mismatch behind a heavy look, or that uses different positions for before/after proof. A static frame cannot prove tracked work over time.

Report the color-management assumption, grade scope, creative palette, local decisions, matched before/after evidence, second-pass changes, and any unverified visual branch.
