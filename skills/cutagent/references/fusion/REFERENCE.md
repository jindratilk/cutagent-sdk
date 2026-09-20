# Fusion

Use Fusion for node-based compositing, motion graphics, masks, tracking, particles, and 3D work. A DaVinci Resolve timeline item can own more than one Fusion composition. Address the item by its durable identity, then choose among the observed one-based composition indexes; never target by clip name alone.

## Read the relevant detail

- For node flow, complete-graph replacement, and the typed builder, read [graph basics](./graph-basics.md).
- For Merge ordering, alpha, and masks, read [compositing and masks](./compositing-and-masks.md).
- For Text+, fonts, glyphs, sizing, and layout, read [text and layout](./text-and-layout.md).
- For keyframes and modifiers, read [animation](./animation.md). For timeline record time versus Fusion composition time, read [coordinates and time](./coordinates-and-time.md).
- For tracking, read [tracking](./tracking.md). For particles or 3D scenes, read [particles](./particles.md) or [3D](./3d.md).
- For reusable Edit-page titles, generators, effects, and transitions, read [templates](./templates.md).
- For `.setting` graphs, read [setting files](./setting-files.md). For exact tool/input inspection or FusionScript boundaries, read [scripting](./scripting.md).
- For frame sampling and visual diagnosis, read [preview and debugging](./preview-and-debugging.md).

Technique references cover [text reveals](./techniques/text-reveal.md), [character animation](./techniques/character-animation.md), and [tracked labels](./techniques/tracked-label.md).

## Resolve the composition first

The `cutagent-sdk` runner supplies `{ sdk, client, project, timeline, snapshot, progress }`. Reuse that coherent snapshot. Require one durable item, then inspect its compositions at the same revision:

```js
const matches = snapshot.videoTracks
  .flatMap((track) => track.clips)
  .filter((clip) => clip.name === "Lower Third");

if (matches.length !== 1 || matches[0].id === null) {
  throw new Error("Expected one durable Lower Third timeline item");
}

const compositions = await timeline.fusion.forTimelineItem(
  matches[0].id,
  snapshot.revision,
);
console.log(compositions.map(({ id, index, name, revision, graphDigest }) => ({
  id, index, name, revision, graphDigest,
})));
```

An empty list means the observed item has no addressable composition. If several exist, select by returned identity, index, and name together. After a mutation changes the relevant revision, refresh only the state needed for the next revision-bound operation.

## Choose the smallest correct mutation boundary

- Use `composition.applyGraph()` for a composition you fully own. It replaces the complete graph; it is not a patch. Build and preview it as shown in [graph basics](./graph-basics.md).
- Use `timeline.fusion.setText()` for known exact text tool/input identifiers. Use `updateNestedText()` for templates that deliberately expose nested header/body clips. Both accept one item or an ordered list; see [text and layout](./text-and-layout.md) and [scripting](./scripting.md).
- Use `timeline.fusion.replaceImages()` for one or many exact composition/image-artifact pairs. Inspect every result row because the plural operation can partially succeed.
- Use `timeline.fusion.insertSettings()` for one or an ordered list of managed `.setting` artifacts. Timeline placement uses timeline-record positions, while keys inside the graph use Fusion composition frames. See [setting files](./setting-files.md).
- Use typed low-level actions or the direct [CLI reference](../cli.md) when the semantic surface does not express the operation. `validateAdvancedFusionRawRequest()` and deprecated `advancedFusionRaw()` only validate descriptions; neither executes a script nor imports a graph.

Exact Fusion instance and input IDs are not Inspector labels. Inspect them or rely on a known template contract; do not assume every Text+ instance is `Text1` or every text owner is `StyledText`.

## Know the current typed-graph boundary

The installed `FUSION_REGISTRY` is the authority for builder node types, literal inputs, and exact connection pairs. Matching captured data-type labels do not prove that two ports connect. `FusionGraphBuilder.animate()` only accepts inputs marked `observed.animatable: true`; the current shipped registry marks none, so use the inspected keyframe actions described in [animation](./animation.md).

Semantic Fusion composition reads and typed graph application run through the local SDK runtime: `standalone_local` in the public package and `desktop_managed` inside CutAgent. A `plugin_managed` connection currently returns `RUNTIME_UNAVAILABLE` before dispatch. Do not fabricate composition references to bypass it.

Structural readback proves graph structure, not appearance. Inspect representative output frames after material visual changes, and more than one frame for motion, tracking, particles, or transitions. Follow [preview and debugging](./preview-and-debugging.md) for proportionate review.
