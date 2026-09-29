---
name: cutagent-object-animation
description: Create original editable entrance, hold, and exit animation for logos, cutouts, screenshots, cards, UI panels, and other visual objects in DaVinci Resolve Fusion. Use when an object needs purposeful motion rather than a stock preset.
license: AGPL-3.0-only
---

# Object animation

Animate the meaning and weight of the object with an editable Fusion construction. Existing effect packs may be studied for motion principles, but do not apply a purchased preset as the result or disguise template substitution as original work.

## Establish the object and its job

Identify the object's final position, scale, orientation, anchor, and relationship to the footage. Decide whether it is the focal subject, supporting evidence, or a brief annotation. Build the clean settled frame first, including any matte, shadow, border, or backing shape that must travel with it.

Choose a motion path that has a reason:

- Enter from the side associated with the source or previous point of attention.
- Move toward the subject being explained, not across it arbitrarily.
- Use scale for emphasis or depth, rotation for character, and translation for spatial continuity.
- Keep screen captures and UI cards stable enough to inspect; save stronger motion for their container or callout.

## Build a three-part motion phrase

Author a distinct entrance, hold, and exit. Keep the entrance and exit compact, with a stretchable middle hold when the object may be retimed. Direction pairs can create different meanings: same-direction entrance and exit continues momentum; opposite directions makes the object arrive, present, and leave; an entrance-only treatment lets it remain as part of the scene.

Shape the motion according to perceived weight. A heavy card needs slower acceleration and little rebound. A lightweight icon can overshoot once. A cutout can use a small position-and-scale settle. Do not add bounce by default.

When added energy is appropriate, derive secondary deformation from velocity: stretch slightly along fast travel, compress briefly on a motivated impact, then return to neutral at rest. Motion blur should follow the main move. A short shake or irregularity may accent impact, but it should decay quickly and never make the hold unstable.

Keep the complete object rig together. If several layers form one object, animate a shared parent transform instead of allowing borders, shadows, and labels to drift apart. Expose only controls an editor can use safely, such as direction, travel distance, duration, overshoot, and secondary-motion strength.

## Local execution

Read `references/construction-recipes.md` when constructing the rig. It describes parented object topology, entrance/hold/exit keys, velocity-linked deformation, and duration-safe adaptation.

For local execution, read `cutagent-fusion`; check the installed SDK declarations, public CutAgent CLI command cards, and live capabilities for exact operations.

Take exact SDK methods, graph identifiers, input contracts, keyframe semantics, and capability boundaries from those references. Keep the creative plan here and the technical contract there.

## Review

Inspect the first fully settled frame for placement, scale, edge quality, transparency, and layer cohesion. Review the full entrance and exit at speed, plus slow inspection around impact and rest. Look for clipped travel, empty edges, wobble during the hold, detached shadows, unwanted scale breathing, and motion that fights the footage.

Use structural readback to confirm the intended graph and animation data. Use a temporal preview or rendered excerpt to judge weight, continuity, and the absence of pops. Report the original motion phrase, editable controls, verified structure, perceptual review, and any untested format or duration variant.
