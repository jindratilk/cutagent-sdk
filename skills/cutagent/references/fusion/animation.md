# Animate Fusion inputs

Use Fusion keyframe actions on an existing composition. Their typed value contract can carry numbers, text, Booleans, points, and small numeric arrays, but that transport shape does not prove a particular Fusion input supports native animation. Address the composition by durable timeline-item identity and one-based composition index. Inspect the actual tool and input IDs before writing; display labels, guessed names, and the current playhead are not stable targets.

## Keep time domains separate

Fusion keyframe actions take `sourcePosition(frames(n))`. Here, `n` is the integer frame shown in the Fusion composition's own time ruler. It is not a timeline-record frame, a timeline-relative offset, a duration, or necessarily a zero-based clip offset.

Read the exact composition and its source range before choosing keys. A nonzero timeline start does not shift Fusion keyframes, and mixed source/timeline rates do not justify converting a record-frame number directly into a Fusion frame. Use [coordinates and time](coordinates-and-time.md) when the mapping is not already known from the composition.

## Inspect, key, and read back

Use `client.actions.read()` for `fusion.tool.list`, `fusion.tool.inputs`, `fusion.tool.get`, `fusion.comp.current`, and `fusion.keyframe.list`. Use `client.actions.start()` for keyframe writes. `keyframe.set` creates or replaces the value at one frame; `keyframe.add` currently has the same single-frame behavior. There is no list overload, so carry the returned `revisionAfter` into the next write instead of rediscovering the project and timeline for every key.

This runner module animates a verified Text+ `Center` point input on one exact composition. The inspected point value is represented by the numeric array `[x, y, z]`; do not assume that shape for an input whose observed type differs. The module reuses the supplied context, and the second mutation carries the first mutation's returned revision. Adapt the clip selection, tool ID, input ID, frames, and values from inspection rather than treating these names as universal.

```js
export default async function animateTitle({
  sdk,
  client,
  project,
  timeline,
  snapshot,
  progress,
}) {
  const item = snapshot.videoTrack(2).clips.find(
    (clip) => clip.name === "Lower Third",
  );
  if (!item?.id) throw new Error("The target needs a durable timeline-item ID");

  const [composition] = await timeline.fusion.forTimelineItem(
    item.id,
    snapshot.revision,
  );
  if (!composition) throw new Error("The item has no Fusion composition");

  const target = {
    projectId: project.id,
    timelineId: timeline.id,
    timelineItemId: item.id,
    compositionIndex: composition.index,
  };
  const inputs = await client.actions.read("cutagent.action.fusion.tool.inputs", {
    ...target,
    toolName: "Text1",
  });
  if (!inputs.inputs.some((input) => input.id === "Center")) {
    throw new Error("Text1.Center was not found on the exact composition");
  }

  let revision = composition.revision;
  for (const [frame, value] of [
    [0, [0.5, 0.54, 0]],
    [119, [0.5, 0.5, 0]],
  ]) {
    progress(`Setting Text1.Center at Fusion frame ${frame}`);
    const operation = await client.actions.start(
      "cutagent.action.fusion.keyframe.set",
      {
        ...target,
        revision,
        toolName: "Text1",
        inputName: "Center",
        sourcePosition: sdk.sourcePosition(sdk.frames(frame)),
        value,
      },
      {idempotencyKey: sdk.idempotencyKey()},
    );
    const terminal = await operation.wait();
    if (
      terminal.status !== "succeeded" ||
      terminal.verification.outcome !== "passed"
    ) {
      console.error(terminal);
      throw new Error(`Keyframe write ended as ${terminal.status}`);
    }
    revision = terminal.result.keyframe.revision.revisionAfter;
  }

  const readback = await client.actions.read("cutagent.action.fusion.keyframe.list", {
    ...target,
    toolName: "Text1",
    inputName: "Center",
  });
  const midpoint = await client.actions.read("cutagent.action.fusion.tool.get", {
    ...target,
    toolName: "Text1",
    inputName: "Center",
    sourcePosition: sdk.sourcePosition(sdk.frames(60)),
  });
  console.log({ keyframes: readback.keyframes, midpoint: midpoint.toolValue.value });
}
```

Treat `keyframe.list` as structural evidence for exact keyed frames and values. Also read at least one in-between frame with `fusion.tool.get`. For motion, timing, or easing claims, review playback or a rendered excerpt across the affected interval; one still cannot prove animation.

## Delete without widening the change

Use `fusion.keyframe.delete` to remove one exact frame. It verifies that the requested key disappeared without changing the remaining keyframe set. Use `fusion.keyframe.clear` only when every key on that input should be removed. Clear converts the input to a constant using its value at the composition's current time, so record the full original key list and the intended retained value first.

After either operation, inspect the terminal result and verification, then list keys and sample values again. A failed or uncertain terminal may follow a mutation; follow [checking results](../checking-results.md) and inspect current state before retrying.

## Know the current curve limits

The public keyframe actions do not accept interpolation modes, easing presets, spline types, or tangent handles. For a constant input, the runtime inspects its native data type before writing the first key: a `Point` input receives an `XYPath`, while other currently supported scalar inputs receive a Bézier spline. For an already animated input, it writes through the existing animation connection. This modifier choice is an implementation requirement for native type compatibility, not a caller-selectable curve mode. Therefore, two successful keyframe writes prove keyed values, not a particular curve shape or tangent layout.

The typed graph builder also exposes `animate()` and `fusionFrame()`, but the current verified public registry marks no inputs as animatable. Calls such as `fusionGraph().node("title", "TextPlus").animate("title", "Size", ...)` are intentionally rejected by the current type contract. Do not cast around that gate or describe graph-authored animation as available. Use the exact keyframe actions for existing compositions; for reviewed native curve data or modifier structure, read [setting files](setting-files.md) and [scripting](scripting.md) without inventing an executable raw path.

## Use the CLI only for an active composition

For a bounded one-off change, the CLI can inspect and key the currently active Fusion composition:

```sh
cutagent fusion tool list --json
cutagent fusion tool inputs Text1 --json
cutagent fusion keyframe list Text1 Size --json
cutagent --dry-run fusion keyframe set Text1 Size 0 0.05 --json
cutagent fusion keyframe set Text1 Size 0 0.05 --json
cutagent fusion keyframe set Text1 Size 24 0.09 --json
cutagent fusion keyframe list Text1 Size --json
cutagent fusion tool get Text1 Size --time 12 --json
```

These commands have no timeline-item or composition selector. Use them only after opening and confirming the intended composition. CLI value parsing is limited to numbers or strings, and the commands do not set interpolation or tangents. Prefer the typed SDK for durable targeting and point or array values.
