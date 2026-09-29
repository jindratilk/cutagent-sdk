---
name: cutagent-motion-transitions
description: Design original editable motion transitions and energetic shot handoffs in DaVinci Resolve. Use when an edit seam needs a directional, scale, rotation, elastic, or distortion-based transition rather than a straight cut or standard dissolve.
license: AGPL-3.0-only
---

# Motion transitions

Make the handoff arise from the two shots and the edit's momentum. Build an editable transition or paired clip treatment; do not substitute a purchased effect and change only its duration or exposed controls.

## Decide whether the seam should move

Keep the cut when motion adds no meaning. Use a custom transition when it reinforces a location change, energetic beat, graphic match, camera direction, or deliberate interruption. Study the outgoing and incoming frames together: subject position, dominant edge, camera motion, luminance, and available negative space should determine the transition axis and energy.

Choose one primary handoff:

- **Directional travel:** both shots appear to continue through the same screen-space vector.
- **Push and replace:** the outgoing frame yields as the incoming frame occupies its space.
- **Scale handoff:** zoom toward a compatible detail or pull back to reveal a new context.
- **Rotational handoff:** use only when circular movement, a spin, or the graphic language supports it.
- **Impact handoff:** a short elastic or bounce response lands on a beat.

## Shape continuity

Place the fastest movement over the seam and give both sides compatible velocity. Build anticipation only when the shot has room for it. An elastic response should overshoot once and settle; a bounce should visibly contact a boundary or beat rather than float. Keep the subject readable immediately before and after the handoff.

If using directional squash or stretch, derive it from speed and return to neutral at rest. Keep distortion strongest around the seam, not throughout both shots. Pair motion blur with travel and check edge behavior so the frame does not expose transparent borders. Do not use zoom, rotation, displacement, shake, and glow together unless the brief deliberately calls for a chaotic break.

Design timing in frames relative to the actual cut and delivery frame rate. Start with a compact interval, then adjust from playback. Confirm that source handles or the chosen Fusion construction can support the intended overlap; do not silently trim story content to force the effect.

## Local execution

Read `references/construction-recipes.md` when authoring the handoff. It gives original paired-branch topologies for directional, scale, rotation, and impact transitions, plus seam-centered timing and edge treatment.

For local execution, read `cutagent-editing`, `cutagent-fusion`; check the installed SDK declarations, public CutAgent CLI command cards, and live capabilities for exact operations.

Use the exact supported SDK or CutAgent CLI route from the installed SDK declarations, public CutAgent CLI command cards, and live capabilities. Preserve linked audio and surrounding clips according to the transition contract; creative intent is not permission to alter them.

## Review

Review the outgoing lead-in, seam, incoming settle, and linked sound as one passage. Inspect several frames around the cut for edge exposure, flashes, duplicate-looking frames, subject jumps, overlong blur, and distortion that remains after the motion stops. Play at normal speed to judge rhythm, then inspect slowly only to diagnose defects.

Structural evidence should confirm the correct seam, duration, graph or transition data, and preserved neighbors. Only playback or a rendered excerpt can prove continuity and feel. Report the transition concept, exact seam affected, editable controls, structural verification, temporal review, and any unresolved handle or audio concern.
