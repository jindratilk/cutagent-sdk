---
name: cutagent-text-behind-object
description: Design editable text that passes behind a person, product, vehicle, building, or other foreground subject in DaVinci Resolve. Use for depth-aware titles, hooks, labels, and typography integrated into live-action footage.
license: AGPL-3.0-only
---

# Text behind an object

Treat the effect as spatial typography, not a masking trick. The text must remain readable in the scene while the foreground occlusion creates convincing depth.

## Compose the settled frame

Choose a shot where the subject crosses a useful text area and has enough separation from the background. Decide the focal words, line breaks, scale, placement, color, and whether the typography belongs to the environment or deliberately contrasts with it.

Build three editable layers:

1. the original plate;
2. native Text+ or a fully editable Fusion title;
3. a foreground-only duplicate or alpha layer above the text.

Place the text so some letters remain readable outside the occluder. Avoid hiding the key word, punctuation, or the only distinctive letterform. Let the subject interrupt the text enough to establish depth, but not enough to turn the message into a puzzle.

## Choose the matte

Read `references/tutorial-analysis.md` before choosing the isolation method. Use a tracked subject matte for people and irregular moving objects. Use original geometric Fusion masks only for simple, predictable silhouettes. The bundled ellipse and rounded-rectangle assets are editable scaffolds for those simple cases, not substitutes for a real subject matte.

When authoring a custom Fusion version, keep the original media as visible RGB and use the matte only to control alpha. Build a complete connected graph from the shot's actual subject and timing; do not copy a purchased title/template and merely replace the words.

For local execution, read `cutagent-fusion`, `cutagent-verification`; check the installed SDK declarations, public CutAgent CLI command cards, and live capabilities for exact operations.

## Refine motion and edges

Track the complete interval in which the subject crosses the type. Refine hair, hands, thin objects, motion blur, and edge softness only where they affect the illusion. Match the foreground duplicate's scale and color to the plate exactly. Avoid broad feathering that makes the subject glow.

## Review

Inspect early, middle, late, and maximum-overlap frames, then play the crossing. Compare all layers on, foreground isolated, and foreground disabled at one key frame. The foreground-only view must contain the intended subject rather than a bright detail or background blob.

Reject text leaks, matte flashes, edge chatter, scale mismatch, duplicate-layer pops, unreadable copy, or a result proven from only one frame. Report the typography design, matte route, editable graph/assets, representative evidence, and any edge that still needs manual refinement.
