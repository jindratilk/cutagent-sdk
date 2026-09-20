# Fusion particles

Use native Fusion particles for editable rain, smoke, sparks, dust, trails, swarms, and other effects whose elements share simulated motion. For a few independently animated shapes, an ordinary Fusion graph is usually easier to direct and verify.

Read [Setting files](setting-files.md) for the executable publication and insertion workflow, [Coordinates and time](coordinates-and-time.md) for Fusion-frame timing, and [3D](3d.md) when particles join a 3D scene.

## Choose the supported authoring route

Author a complete Fusion `.setting`, publish it with `client.artifacts.publishFusionSetting()`, and place it with `timeline.fusion.insertSettings()`. This preserves the native node graph for later editing.

The current typed `fusionGraph()` registry does not contain particle nodes. It cannot compile `pEmitter`, `pRender`, particle forces, or their connections. Do not infer support from similar port labels or pass particle names into the typed builder. `validateAdvancedFusionRawRequest()` and its deprecated alias only validate a description; they do not execute or insert a setting.

For a small change to an existing particle composition, inspect the installed action declarations and live Fusion tool metadata before using a typed `fusion.tool.*` action. Tool types, input names, and port names are native identifiers, not labels to guess. Prefer a complete setting when creating or substantially replacing the system.

## Build the particle system

A visible system needs this flow:

```text
pEmitter -> optional particle modifiers -> pRender
```

Connect `pRender` to the rest of the composition as a 2D image, or use its 3D output in a `Merge3D` scene. Decide the 2D/3D route before finalizing the setting. Use `pMerge` to combine multiple emitters; it is not the ordinary image `Merge` node.

Set the controls that determine the result explicitly:

- `Number` is the number of new particles born per frame. Animate it back to zero for a finite burst.
- `Lifespan` is measured in Fusion frames. Leave enough time after emission stops for the tail to decay. Use variance intentionally rather than as a substitute for art direction.
- Set `Random Seed` to a fixed value so the same setting and frame produce the same population. Do not rely on the Randomize button for repeatable output.
- Use velocity, emission angles, and their variances to establish direction before adding forces. Add `pDirectionalForce`, `pFriction`, `pTurbulence`, `pVortex`, collision, avoidance, or spawning only when each has a clear role.
- Use particle sets when a force or condition should affect only selected emitters.
- Choose an emission region deliberately. Bitmap and mesh regions require the corresponding input; surface and volume emission create different distributions. A bitmap particle style also requires an image with useful alpha.
- Shape appearance over life: size, color, opacity/fade, spin, and blur usually need a readable birth, body, and death phase.

Keep the first version economical. High birth rate, long lifespan, subframe calculation, image particles, depth output, glow, and motion blur multiply render cost. Increase them only after the motion and silhouette work at a lower density.

## Account for simulation history

Particle state depends on earlier frames. A random seek can show the wrong population when intervening frames were not calculated. Configure `pRender` pre-roll for the intended review and render path. Use pre-generated frames when smoke, fog, rain, or another continuous system must already be established on its first visible frame.

Keep timeline record placement, clip duration, and Fusion composition frames separate. A timeline may have a nonzero start time, while particle lifespan and keyframes remain in the composition's frame domain. Follow [Coordinates and time](coordinates-and-time.md) instead of converting by intuition.

## Place the authored setting

Follow [Setting files](setting-files.md) to validate, publish, and insert the particle graph. Choose the timeline offset, video track, and holder duration from the inspected snapshot. The holder must cover the intended emission, established motion, and decay; it does not automatically retime fixed particle keyframes.

`insertSettings()` accepts one placement or an ordered list of 1–100 placements that share the observed revision. After success, use the returned timeline-item identity and a fresh timeline revision for `timeline.fusion.forTimelineItem()` when composition-presence readback matters. Do not treat placement verification as particle-graph or image verification.

## Verify the effect

The successful insertion receipt and fresh composition reference prove placement and the presence of a Fusion composition. They do not prove that the authored particle nodes lowered as intended or that the effect looks right.

Inspect the native graph when exact node, connection, seed, or control readback matters. Review several frames spanning emission, established motion, and decay. Include the first visible frame to catch missing pre-generation, and compare sequential playback with sampled seeks to expose pre-roll problems. Check alpha edges, occlusion, scale, density, collisions, and motion blur in the final composite—not only against a black viewer background.

A still cannot prove particle motion, timing, or simulation stability. Render and review the relevant interval before claiming the effect complete. See [Checking results](../checking-results.md) for proof levels and [Errors and recovery](../errors-and-recovery.md) before retrying an uncertain insertion.
