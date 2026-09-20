# Color

Use the Color APIs for grades, node structure, LUTs, gallery stills, Color groups, Power Windows, tracking, and shot matching. A clip's display color in the Edit page is metadata instead; change that with the timeline-item color API.

## Establish the grade context

- Confirm the intended input and output color spaces before adding a corrective LUT or transform. Do not compensate for an unknown color-management setup or apply a second input transform to already normalized footage.
- Put shared camera or scene treatment in an existing Color group when that is the project's convention; keep shot-specific balance and isolation on clip nodes.
- Treat node order as part of the image pipeline. Inspect the existing graph before choosing a node or adding one.

`timeline.color.current()` inspects DaVinci Resolve's exact current Color target, not an arbitrary timeline item. It returns the active clip and track, the one-based node graph, versions, current Color-group name, field availability, and mutation requirements. Pass `nodeStackLayerIndex` only when working in a specific node-stack layer.

The snapshot has two different preconditions:

- `revision` owns the Color state and node indexes.
- `timelineRevision` owns the clip and track observation.

Do not retain node indexes across a Color mutation. Read a fresh Color snapshot before the next dependent mutation. An unavailable optional readback means “not authoritatively exposed,” not an empty grade.

## Apply a bounded primary correction

Given the runner's existing `sdk` and `timeline`, target the first readable node of the current Color clip:

```ts
const color = await timeline.color.current();
const firstNode = color.nodeGraph.nodes[0];
if (!firstNode) throw new Error("The current Color target has no readable node.");

const preview = timeline.color.previewPrimary(color, firstNode.index, {
  contrast: 1.08,
  pivot: 0.45,
  temperature: 4,
});

const operation = await timeline.color.apply(preview, {
  idempotencyKey: sdk.idempotencyKey(),
});
const terminal = await operation.wait();
if (terminal.status !== "succeeded") {
  throw new Error(`Color operation ended with ${terminal.status}.`);
}
```

`previewPrimary` accepts only `contrast`, `pivot`, `temperature`, `tint`, `hue`, `colorBoost`, `midtoneDetail`, `shadows`, and `highlights`. Use the generated typed action namespace for another supported Color control; never invent a property dictionary.

The same preview/apply pattern supports:

- `previewAddNode`: append a serial node after the inspected tail. Parallel and layer topology are accepted only for an inspected single-node graph.
- `previewSetNodeLabel`: label one inspected node.
- `previewApplyGrade`: apply a `ColorAssetReference` (`assetId` and `fileId`) with alignment `none`, `source_timecode`, or `start_frame`.
- `previewAddEffect`: add only `gaussian_blur`, `sharpen`, or `film_grain` through this facade.

These previews are bound to the exact `timeline.color` facade and snapshot that created them. A copied or reconstructed preview is invalid.

## Use shared workflow requests

Color workflow helpers build requests for common operations. Execute mutation requests through `client.actions.invoke`, then wait for their durable results. For LUTs, supply installed catalog names, never filesystem paths. Use one plural action when several clips share the operation:

```ts
// `sdk`, `client`, `heroColor`, and `cutawayColor` already exist. Both snapshots are
// from the same project, timeline, and inspected timeline revision.
const input = {
  projectId: heroColor.projectId,
  timelineId: heroColor.timelineId,
  revision: heroColor.timelineRevision,
  items: [
    {
      timelineItemId: heroColor.clip.id,
      colorRevision: heroColor.revision,
      nodeStackLayerIndex: heroColor.nodeStackLayerIndex,
      nodeIndex: 2,
      lutName: "Film Looks/Warm",
      clear: false,
    },
    {
      timelineItemId: cutawayColor.clip.id,
      colorRevision: cutawayColor.revision,
      nodeStackLayerIndex: cutawayColor.nodeStackLayerIndex,
      nodeIndex: 1,
      lutName: "Camera/Neutral",
      clear: false,
    },
  ],
  failurePolicy: "stop",
} as const;

const operation = await client.actions.invoke(
  "cutagent.action.color.lut",
  input,
  { idempotencyKey: sdk.idempotencyKey() },
);
const terminal = await operation.wait();
if (terminal.status !== "succeeded") {
  throw new Error(`LUT operation ended with ${terminal.status}.`);
}
```

The plural LUT action accepts 1–128 unique clips in one operation. All snapshots must share the project, timeline, and `timelineRevision`; each node index remains bound to its own Color revision. Use `failurePolicy: "continue"` when independent targets may proceed after one failure, or `"stop"` when the set should stop at the first failure. `applyColorLut(snapshot, nodeIndex, lutName)` remains the concise request builder for one clip.

Other focused builders are:

- `assignColorGroup(snapshot, group)` for an existing project-scoped group.
- `grabColorStill(snapshot)` and `applyColorStill(snapshot, still, mode)` for project-scoped gallery assets.
- `createColorRectangle(snapshot, geometry)` for normalized rectangle geometry: center, width, height, optional softness, rotation, and composition index.
- `trackColorForward(snapshot, tracker)` for a tracker reference bound to the same clip and Color revision.
- `matchColorShot(snapshot, options)` for two private artifact references plus an exact reference frame and bounded match controls.

Opaque group, still, tracker, and artifact IDs must come from typed CutAgent reads or results. Do not manufacture them from display names.

## Check the result that matters

Operation creation is not completion. Inspect the terminal status and returned verification. If a result is partial or requests manual recovery, inspect current state before deciding whether to retry; reuse the same idempotency key when recovery guidance requires it.

Structural readback can prove the target, node graph, LUT name, or entity change. It cannot by itself prove that the grade looks correct. Use scopes and a representative frame for a static correction; review multiple frames for tracked windows or any change whose quality varies over time. Compare against the intended viewing transform, not an untagged screenshot.

For shared timing concepts, read [Timing and targets](timing-and-targets.md). For terminal-state interpretation, read [Checking results](checking-results.md) and [Errors and recovery](errors-and-recovery.md). If the requested mask or tracker belongs to a Fusion composition rather than the Color page, use [Fusion compositing and masks](fusion/compositing-and-masks.md) or [Fusion tracking](fusion/tracking.md).
