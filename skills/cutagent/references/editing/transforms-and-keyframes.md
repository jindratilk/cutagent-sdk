# Transform clips and animate Inspector properties

Use `timeline.items.setProperties()` for static Inspector values. Use the typed clip-keyframe actions when a supported numeric Inspector property must change over time. These surfaces target video timeline items from one immutable snapshot; they do not animate Fusion tool inputs.

Read [timing and targets](../timing-and-targets.md) before deriving frames. Use [speed ramps](speed-ramps.md) for retime curves and [Fusion animation](../fusion/animation.md) for node-input animation.

## Set static Inspector values

`timeline.items.setProperties()` accepts one change or an ordered list of changes in one durable operation. Prefer the list form when several clips come from the same snapshot. Each clip may receive different values.

Supported properties are `zoomX`, `zoomY`, `positionX`, `positionY`, `rotation`, `anchorX`, `anchorY`, `pitch`, `yaw`, `flipX`, `flipY`, `opacity`, `cropLeft`, `cropRight`, `cropTop`, `cropBottom`, `distortion`, and `dynamicZoomEase`. The last value accepts `linear`, `in`, `out`, or `inout`. `opacity` is bounded from 0 to 100. Do not pass DaVinci Resolve's internal property names or an arbitrary property dictionary.

This managed-runner module assumes the supplied `sdk`, `timeline`, and `snapshot` variables:

```js
export default async function setFraming({ sdk, timeline, snapshot }) {
  const track = snapshot.videoTrack(1);
  const [wide, close] = track.clips;
  if (!wide || !close) throw new Error("Expected two clips on V1.");
  if (track.locked !== false) throw new Error("V1 is not authoritatively unlocked.");

  const operation = await timeline.items.setProperties([
    {
      clip: wide,
      properties: { zoomX: 1.08, zoomY: 1.08, positionX: -24 },
    },
    {
      clip: close,
      properties: { rotation: 1.5, cropRight: 12, opacity: 92 },
    },
  ], { idempotencyKey: sdk.idempotencyKey() });

  const terminal = await operation.wait();
  if (terminal.status !== "succeeded") {
    throw new sdk.CutAgentSdkError(terminal.failure);
  }
  if (terminal.verification.outcome !== "passed") {
    throw new Error(`Transform verification was ${terminal.verification.outcome}.`);
  }

  console.log(terminal.result.items);
}
```

The operation reads every target before and after the mutation, checks the requested values, preserves existing keyframe curves and composite mode, and compares protected timeline state. It rejects duplicate targets, non-video items, stale clip snapshots, unknown linked-item topology, and empty or unsupported property sets.

`positionX` and `positionY` are the SDK's static names for DaVinci Resolve's Pan and Tilt controls. Keyframe actions use the native public property names `Pan` and `Tilt` instead.

## Add clip Inspector keyframes

Use `sdk.timelineActionContext(snapshot)` to bind the project, timeline, revision, exact clip range, durable item identity, and linked-item topology. A keyframe `recordFrame` is an absolute frame in the timeline-record domain, not a clip-relative offset and not a source frame. Derive it from the selected clip's observed record range. Timelines commonly have a nonzero start.

The keyframe actions support `Pan`, `Tilt`, `ZoomX`, `ZoomY`, `Rotation`, `Pitch`, `Yaw`, `Opacity`, `CropLeft`, `CropRight`, `CropTop`, and `CropBottom`. Interpolation is `linear`, `bezier`, `ease_in`, or `ease_out`.

Each keyframe mutation changes the timeline revision. The current action accepts one keyframe, so reacquire the snapshot and rebuild the target before adding the next point. This example creates and reads back a two-point Pan animation without reconnecting or reselecting the project:

```js
export default async function animatePan({ sdk, client, timeline, snapshot }) {
  const initial = snapshot.videoTrack(1).clips[0];
  if (!initial?.id) throw new Error("The target clip has no durable identity.");
  const targetId = initial.id;
  let current = snapshot;

  const findTarget = () => {
    const clip = current.videoTracks
      .flatMap((track) => track.clips)
      .find((candidate) => candidate.id === targetId);
    if (!clip) throw new Error("The target clip is absent from the current snapshot.");
    return clip;
  };

  const addPanKeyframe = async (offset, value, interpolation) => {
    const clip = findTarget();
    const start = clip.recordRange.start.value;
    const end = clip.recordRange.endExclusive.value;
    if (start.kind !== "frames" || end.kind !== "frames") {
      throw new Error("The clip lacks an exact frame-domain record range.");
    }
    const recordFrame = start.value + offset;
    if (recordFrame < start.value || recordFrame >= end.value) {
      throw new Error("The requested keyframe is outside the visible clip range.");
    }

    const action = sdk.timelineActionContext(current);
    const operation = await client.actions.start(
      "cutagent.action.clip.keyframe.add",
      action.input({
        target: action.videoTarget(clip),
        property: "Pan",
        recordFrame,
        value,
        interpolation,
      }),
      { idempotencyKey: sdk.idempotencyKey() },
    );

    const terminal = await operation.wait();
    if (terminal.status !== "succeeded") {
      throw new sdk.CutAgentSdkError(terminal.failure);
    }
    if (terminal.verification.outcome !== "passed") {
      throw new Error(`Keyframe verification was ${terminal.verification.outcome}.`);
    }
    current = await timeline.snapshot();
  };

  await addPanKeyframe(0, -40, "ease_out");
  await addPanKeyframe(24, 40, "ease_in");

  const clip = findTarget();
  const action = sdk.timelineActionContext(current);
  const readback = await client.actions.read(
    "cutagent.action.clip.keyframe.get",
    action.input({ target: action.videoTarget(clip), property: "Pan" }),
  );
  console.log(readback.keyframes);
}
```

Use `cutagent.action.clip.keyframe.set_interpolation` to change interpolation at one existing `recordFrame`, and `cutagent.action.clip.keyframe.delete` to remove one point. Both are mutation actions: supply the same exact target shape through a fresh action context, wait for the durable terminal, and require passed verification. `keyframe.get` is a direct semantic read and does not take an idempotency key.

Adding a `ZoomX` or `ZoomY` keyframe can preserve the paired zoom curve when the axes were previously linked. If asymmetric scaling is intentional, inspect both curves rather than assuming one-axis authoring left the other unchanged.

## Respect the surface boundaries

- A static transform is not an animation. It updates the clip's Inspector state while preserving its existing keyframe curves.
- The clip-keyframe CRUD surface does not keyframe anchor, flip, distortion, or Dynamic Zoom framing. `dynamicZoomEase` changes only the supported static Inspector value; it does not author or enable Dynamic Zoom's start and end boxes.
- `keyframe.get` may read `RetimeFrame`, but the clip-keyframe write actions do not accept it. Author speed changes through the dedicated retime surface in [speed ramps](speed-ramps.md).
- Fusion keyframes address a Fusion tool input at a source-domain position. Do not feed a timeline record frame to a Fusion action; use [Fusion coordinates and time](../fusion/coordinates-and-time.md) and [Fusion animation](../fusion/animation.md).
- DaVinci Resolve can retain active keyframes beyond a clip's current edit points after trimming. Before replacing or deleting a curve, read it and distinguish hidden retained points from visible in-range points.

## Verify motion

The transform and keyframe terminals provide structural readback: exact values or curve points, the resulting timeline revision, protected-state preservation, and verification evidence. That proves persisted structure, not the look or timing of the motion.

Read the curve after authoring, then review at least the start, an interior frame, and the end of the animated interval. Use a short temporal preview when easing and continuity matter. One exported frame cannot prove motion. Follow [checking results](../checking-results.md) for proportionate visual proof and [errors and recovery](../errors-and-recovery.md) before retrying a partial or uncertain mutation.
