# Speed ramps

A speed ramp changes the mapping between timeline playback time and source-media time. For a cut-centered ramp, accelerate the outgoing clip into the cut and decelerate the incoming clip away from it. Use a constant-speed retime for one uniform change, a whole-clip freeze or reverse for those effects, and a transition when the clips have no usable source handles.

CutAgent's native speed-ramp action currently authors one exact adjacent cut on one video track. It is not a general keyframe editor and it does not accept a list of cuts.

## Shape the ramp around the edit

- Choose the cut from the edit's action or beat, then choose outgoing and incoming ramp durations in **timeline frames**. An `18`-frame side is 0.75 seconds at 24 fps but 0.6 seconds at 30 fps.
- Speeds are multipliers: `1` is normal speed and `6.5` is 650%. A conventional cut ramp is `1 → peak` on the outgoing side and `peak → 1` on the incoming side.
- `linear`, `normal_s`, and `sharp_s` describe the curve family. Treat the preset name as a starting shape, not proof that the motion reads well.
- Accelerating a clip consumes source frames faster. The current trim is not the same as the media available beyond that trim. Build targets with `timelineActionContext(snapshot).videoRetimeTarget(clip)` so the action receives the authoritative available source range, source-frame rate, and fractional source origin when DaVinci Resolve reports them. Do not lower the peak speed merely to conceal a wrong source range.
- Mixed-rate ramps use record frames for placement and each clip's own source rate for sampling. Never convert both sides with the timeline rate. See [timing and targets](../timing-and-targets.md).

Before authoring, establish that the position is one exact adjacent cut, both clips are on the same unlocked video track, both have durable IDs and source authority, and neither overlaps the cut. Read `timeline.retime.read(clip)` if either side may already be retimed; its points map record frames to source frames, so a changing source-frame delta is the speed change.

## Author an unlinked cut with the managed SDK runner

This complete runner module accepts a timeline-relative cut offset and deliberately rejects linked A/V. The linked case needs the complete reciprocal audio topology; use the CLI route below instead of submitting an incomplete `linkedAudioTargets` list.

```js
function frameOf(position) {
  if (position.value.kind !== "frames") {
    throw new Error("Expected an exact frame-domain record position.");
  }
  return position.value.value;
}

export default async function rampUnlinkedCut({ sdk, client, timeline, snapshot, progress }) {
  const cutOffsetFrames = 240;
  const videoTrackIndex = 1;
  const rampFrames = 18;
  const peakSpeed = 6.5;

  const track = snapshot.videoTrack(videoTrackIndex);
  if (track.locked !== false) {
    throw new Error(`V${videoTrackIndex} is locked or its lock state is unknown.`);
  }

  const cut = sdk.timelineRecordOffset(snapshot, sdk.frames(cutOffsetFrames));
  const beforeCut = sdk.timelineRecordOffset(snapshot, sdk.frames(cutOffsetFrames - 1));
  const outgoing = track.clipAt(beforeCut);
  const incoming = track.clipAt(cut);
  const cutFrame = frameOf(cut);

  if (
    frameOf(outgoing.recordRange.endExclusive) !== cutFrame ||
    frameOf(incoming.recordRange.start) !== cutFrame
  ) {
    throw new Error("The requested position is not one adjacent V-track cut.");
  }
  if (snapshot.linkedItems(outgoing).length || snapshot.linkedItems(incoming).length) {
    throw new Error("This module accepts only an unlinked video cut.");
  }

  const action = sdk.timelineActionContext(snapshot);
  progress("Applying the speed ramp");
  const operation = await client.actions.start(
    "cutagent.action.clip.speed_ramp",
    action.input({
      outgoing: action.videoRetimeTarget(outgoing),
      incoming: action.videoRetimeTarget(incoming),
      linkedAudioTargets: [],
      protectedNeighbors: [],
      linkedMedia: "preserve",
      cut,
      outDuration: sdk.duration(sdk.frames(rampFrames)),
      inDuration: sdk.duration(sdk.frames(rampFrames)),
      outStartSpeed: 1,
      outEndSpeed: peakSpeed,
      inStartSpeed: peakSpeed,
      inEndSpeed: 1,
      curve: "sharp_s",
      reverseIncoming: false,
    }),
    { idempotencyKey: sdk.idempotencyKey() },
  );

  const terminal = await operation.wait();
  if (terminal.status !== "succeeded") {
    console.error({
      status: terminal.status,
      possibleMutation: terminal.possibleMutation,
      result: "result" in terminal ? terminal.result : undefined,
      recovery: "recovery" in terminal ? terminal.recovery : undefined,
    });
    throw terminal.failure;
  }
  if (terminal.verification.outcome !== "passed") {
    throw new Error(`Speed-ramp verification was ${terminal.verification.outcome}.`);
  }

  const after = await timeline.snapshot();
  const outgoingAfter = after.videoTrack(videoTrackIndex).clips.find(
    (clip) => clip.id === outgoing.id,
  );
  if (!outgoingAfter) throw new Error("The outgoing clip is absent after the ramp.");

  const curve = await timeline.retime.read(outgoingAfter);
  console.log({ operationId: operation.operationId, curve });
}
```

Run it as described in [the SDK reference](../sdk.md), for example:

```sh
cutagent-sdk --title "Ramp the cut at frame 240" speed-ramp.mjs
```

`timelineRecordOffset()` makes frame 240 relative to the timeline's actual start; it is not absolute record frame 240. `videoRetimeTarget()` also rejects stale, identity-poor, or source-ambiguous clip objects before the action is sent.

## Preserve linked A/V through the CLI planner

For an ordinary linked picture-and-production-audio cut, let the supported CLI route discover and validate the complete reciprocal link topology. Use an explicit one-based video track when several tracks cut at the same position. A bare frame count is relative to the timeline start.

```sh
cutagent --json --dry-run clip speed-ramp \
  --cut-at 240f \
  --track 1 \
  --out-frames 18 \
  --in-frames 18 \
  --peak-speed 6.5x \
  --curve sharp-s
```

Inspect the dry-run result for the outgoing and incoming IDs, record ranges, available source ranges, and every linked audio target. If it names the intended topology, rerun the same command without `--dry-run`. This CLI route currently requires a Disk project library. For deliberate J/L cuts or audio-only timing changes, use [linked audio and J/L cuts](linked-audio-and-jl-cuts.md) rather than forcing the video-ramp topology.

Adjustment blur is optional decoration, not a repair for invalid source sampling. Establish and verify the retime graph first; add blur only when the visual design calls for it.

## Use custom curves only from measured evidence

The action's optional `curveControl` accepts separate outgoing and incoming controls. Each side may use a `preset` with easing and Bezier handles, or `explicit_points`. Explicit point coordinates are record/output seconds and source seconds after frame conversion; handles are deltas in those same domains. Raw interpolation codes are DaVinci Resolve data, not portable style names. Preserve points and codes read from a known-good reference or deliberately calculated map—do not guess them from percentages.

DaVinci Resolve exposes both a Retime Speed curve and a Retime Frame curve. The former represents relative speed; the latter represents source-frame mapping over timeline playback. CutAgent readback reports the time map, so reason about source progression rather than expecting Inspector speed percentages alone.

## Prove timing, continuity, and quality

The action terminal and SDK verification establish structural facts such as the written time map and preservation of protected state. After success:

- read both clips with `timeline.retime.read()` from a fresh snapshot and inspect point order, record/source ranges, reversal, freeze state, and curve data;
- preview or export a short multi-frame interval spanning both sides of the cut to judge acceleration, deceleration, continuity, and the edit beat;
- audition linked sound for sync, pitch, discontinuities, and whether the editorial intent should instead be a J/L cut;
- inspect slow or complex-motion portions for interpolation artifacts.

DaVinci Resolve's Nearest mode drops or duplicates frames, Frame Blend dissolves adjacent frames, and Optical Flow synthesizes frames through motion estimation. Optical Flow can be smooth for linear motion but can artifact when objects cross or camera motion is unpredictable. Choose the clip's Retime Process and motion-estimation mode from the footage, then review moving frames; neither structural readback nor a single still proves motion quality. See [checking results](../checking-results.md).

If the operation returns a non-success terminal, keep its operation identity and inspect `possibleMutation`, partial `result`, `recovery`, and fresh retime readback before deciding whether a retry is safe. Never redispatch the logical edit under a new idempotency key merely because the local wait failed.
