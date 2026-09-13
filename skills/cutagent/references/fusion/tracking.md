# Fusion tracking

Choose the tracker from the motion being solved, not from the element being attached:

- Use `Tracker` for a small, distinctive 2D feature. One pattern can drive position; rotation, scale, stabilization, and corner positioning require multiple suitable patterns.
- Use `PlanarTracker` for a textured flat surface whose perspective changes, such as a sign, screen, wall, or license plate. Its track can drive a Planar Transform, corner pin, steady/unsteady workflow, or stabilization.
- Use `CameraTracker` when camera motion and parallax must produce a virtual 3D camera and point cloud. Moving subjects, weak detail, motion blur, rolling shutter, and insufficient parallax can invalidate the solve.
- Use `SurfaceTracker` for a deforming surface such as cloth or skin. Define one surface's bounds and mesh, track it, then choose the required warp or stabilized/rewarped result.

Do not substitute a point track for a perspective-changing plane, or a camera solve for a locked-off shot with no parallax. Color-page Power Window tracking is a different domain; use [Color](../color.md) when the target is a Color grade rather than a Fusion composition.

## Prepare the analysis

Identify the exact timeline item and Fusion composition before changing the graph. Pick a reference frame where the feature or plane is clear, large enough, and not occluded. Treat that frame as Fusion source time, not timeline record time; a nonzero timeline start, clip trim, retime, or mixed source/timeline rates can make the same integer name different frames. Read [Coordinates and time](coordinates-and-time.md) when converting between these domains.

For a point track, place the pattern over a high-contrast, distinctive feature that keeps its shape. Keep the pattern tight around useful pixels and make the search area large enough for the feature's frame-to-frame motion. For stabilization, choose patterns on the same rigid depth plane. For a planar track, draw the region on the chosen reference frame, exclude independently moving detail, and use an occlusion mask when needed. For a camera solve, mask moving objects and supply trustworthy lens/sensor information when available. For a surface track, keep the bounds on one deforming surface; changing its bounds or mesh invalidates existing tracking data.

## Add the currently supported point-tracker scaffold

The typed action `cutagent.action.fusion.tracker.add` targets one exact composition. It adds one standard `Tracker`, sets its first pattern center with normalized image coordinates, inserts it inline before `MediaOut`, and verifies the created tool, `PatternCenter1`, and connection change. It does **not** run tracking.

This managed-runner example reuses the supplied `sdk`, `client`, `project`, `timeline`, and `snapshot` values:

```js
export default async function addPointTracker({ sdk, client, project, timeline, snapshot }) {
  const matches = snapshot.videoTracks
    .flatMap((track) => track.clips)
    .filter((clip) => clip.name === "Interview A");
  if (matches.length !== 1) {
    throw new Error("Expected exactly one target clip");
  }

  const clip = matches[0];
  if (clip.id === null) {
    throw new Error("Target clip has no durable identity");
  }
  const compositions = await timeline.fusion.forTimelineItem(clip.id, snapshot.revision);
  if (compositions.length !== 1) {
    throw new Error("Expected exactly one Fusion composition on the target clip");
  }

  const operation = await client.actions.start(
    "cutagent.action.fusion.tracker.add",
    {
      projectId: project.id,
      timelineId: timeline.id,
      revision: snapshot.revision,
      timelineItemId: clip.id,
      compositionIndex: compositions[0].index,
      patternCenter: { x: 0.42, y: 0.58 },
    },
    { idempotencyKey: sdk.idempotencyKey() },
  );

  const terminal = await operation.wait();
  if (terminal.status !== "succeeded") {
    throw new Error(`Tracker setup ended with ${terminal.status}`);
  }
  console.log(terminal.result.tracker);
}
```

The action accepts one composition, not a list. Do not invent a batch form or add several trackers speculatively. Acquire a fresh snapshot before a dependent revision-bound mutation.

## Continue only through an exposed capability

The current public SDK has no Fusion action for starting point or planar analysis, configuring pattern/search size, choosing adaptive or operation mode, creating a Planar Transform, solving/exporting a camera track, or defining/tracking a Surface Tracker mesh. The typed Fusion graph registry also does not currently expose any tracker node type, so `fusionGraph()` cannot author these workflows. Do not use generic tool-input writes or raw Fusion requests to guess hidden control IDs.

If the requested result needs one of those operations, report the exact unsupported step and preserve the scaffold for interactive completion or a future documented capability. If the user only wants DaVinci Resolve's default clip stabilizer rather than a Fusion track, the separate `cutagent.action.clip.stabilize` action is the relevant route; it exposes no mode, crop, smoothing, strength, or re-analysis controls.

## Verify the track and its use

Separate setup, analysis, and downstream use:

- The tracker-add terminal can prove that the node, first pattern center, and inline connection were retained. It cannot prove a motion path.
- After analysis, inspect tracked centers or generated track data across the required source-frame range. Check for drift, jumps, occlusion failures, and whether the whole intended range was analyzed in the correct direction.
- Inspect the connection or operation that consumes the track: offset position for following motion, steady/unsteady outputs for stabilization workflows, the Planar Transform or corner pin for planar work, the exported camera/point cloud for a camera solve, or the selected surface-warp result.
- Review representative frames around the start, reference, difficult motion or occlusion, and end. Then review playback or a rendered excerpt. A single still cannot prove tracking quality, stabilization, deformation, or a camera solve.

Use [Animation](animation.md) for resulting keyframes and motion paths, [Preview and debugging](preview-and-debugging.md) for graph and frame checks, and [Checking results](../checking-results.md) before claiming the shot is complete.
