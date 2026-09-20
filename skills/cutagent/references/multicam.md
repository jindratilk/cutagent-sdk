# Multicam editing

Keep one synchronized native multicam clip as the source of truth. Make program cuts by switching its stable angle identities in timeline record time; do not rebuild camera sync at every cut.

Use [projects and media](projects-and-media.md) to select or import camera sources and [timing and targets](timing-and-targets.md) for nonzero timeline starts, mixed frame rates, and record-time conversion.

## Prepare the sources

- Give every camera a deliberate angle label. Do not infer editorial identity from source order when camera, angle, or reel metadata is available.
- Prefer shared timecode when production supplied reliable jam sync. Use sound when the recordings share usable reference audio; use matching markers or intentional In/Out points when those are the real synchronization anchors.
- Check the sync at several separated moments, including near the end. One frame can show alignment at one instant but cannot reveal drift.
- Decide which audio should remain the program bed before cutting. Picture-only switches usually preserve a dedicated recorder or chosen reference angle; linked switches intentionally change picture and audio together.

`project.multicams.previewCreate()` currently requires at least two durable video assets from one coherent Media Pool revision. Its semantic input exposes `name`, source-to-angle bindings, `syncMode`, and an optional `timelineName`. It does not expose every option in DaVinci Resolve's New Multicam Clip dialog, including reference-audio selection, DaVinci Resolve 21's All Angles audio, and full-clip-extents controls. Do not invent SDK fields for those options.

## Create a native multicam clip

This managed-runner module creates a two-camera multicam clip and a timeline. Replace the asset names, labels, sync mode, and destination names with inspected project values.

```js
export default async function createInterviewMulticam({ sdk, project, progress }) {
  const cameraA = await project.mediaPool.assetByName("Camera A.mov");
  const cameraB = await project.mediaPool.assetByName("Camera B.mov");

  const impact = project.multicams.previewCreate({
    name: "Interview Multicam",
    sources: [
      { asset: cameraA, angleLabel: "Wide" },
      { asset: cameraB, angleLabel: "Close" },
    ],
    syncMode: "timecode",
    timelineName: "Interview Program",
  });
  console.log(impact.summary);
  progress("Creating the synchronized multicam clip");

  const operation = await project.multicams.create(impact, {
    idempotencyKey: sdk.idempotencyKey(),
  });
  const terminal = await operation.wait();
  if (terminal.status !== "succeeded") {
    console.error({
      operationId: operation.operationId,
      status: terminal.status,
      possibleMutation: terminal.possibleMutation,
      result: "result" in terminal ? terminal.result : undefined,
      recovery: "recovery" in terminal ? terminal.recovery : undefined,
    });
    throw terminal.failure;
  }
  if (terminal.verification.outcome !== "passed") {
    throw new Error(`Multicam verification was ${terminal.verification.outcome}.`);
  }

  console.log({
    multicam: terminal.result.multicam.name,
    angles: terminal.result.multicam.angles.map((angle) => angle.label),
    timeline: terminal.result.timeline?.name ?? null,
  });
}
```

Omit `timelineName` when only the Media Pool multicam asset should be created. The successful result contains the verified `multicam` snapshot and either the created timeline identity or `null`. Before a dependent step, reacquire the current project and timeline rather than assuming a newly created timeline became current.

## Inspect and switch angles

DaVinci Resolve a multicam asset through the Media Pool, then call `project.multicams.inspect(asset)`. Use `multicam.angle(label)` to obtain an angle from that exact snapshot. Labels must resolve uniquely; keep the returned angle object rather than constructing an ID or matching an array position.

Build switch positions from a fresh timeline snapshot. `timelineRecordOffset()` preserves a nonzero timeline start, and the switches must be strictly increasing after conversion to record frames.

```ts
// Given `sdk`, `project`, `timeline`, and a fresh `snapshot` from the managed runner:
const asset = await project.mediaPool.assetByName("Interview Multicam");
const multicam = await project.multicams.inspect(asset);

const impact = await timeline.multicam.previewSwitch(
  multicam,
  [
    { at: sdk.timelineRecordOffset(snapshot, sdk.frames(0)), angle: multicam.angle("Wide") },
    { at: sdk.timelineRecordOffset(snapshot, sdk.frames(144)), angle: multicam.angle("Close") },
  ],
  { scope: "video" },
);

const operation = await timeline.multicam.switch(impact, {
  idempotencyKey: sdk.idempotencyKey(),
});
const terminal = await operation.wait();
if (terminal.status !== "succeeded") {
  throw terminal.failure;
}
if (terminal.verification.outcome !== "passed") {
  throw new Error(`Multicam switch verification was ${terminal.verification.outcome}.`);
}
console.log({ changedSegments: terminal.result.changedSegments });
```

Use `scope: "video"` to preserve program audio, `"audio"` to change audio only, or `"linked"` when both should follow the selected angle. A switch creates program segments at the requested record positions; it is not a source-time trim.

For speaker-led edits, `planPodcastMulticamSwitches(frameRate, segments, speakerAngles)` converts ordered, non-overlapping, speaker-labelled `TimelineRecordRange` values into stable switch points and coalesces consecutive segments mapped to the same angle. It does not create a transcript, judge reactions, resolve overlapping speakers, or prove that the chosen camera is visually useful. Review the plan, then pass `plan.switches` to `previewSwitch()`. Prefer video-only scope when a continuous master recording should survive the picture cut.

Do not describe this deterministic helper, or the separate `cutagent multicam smart-switch` CLI workflow, as DaVinci Resolve AI Multicam SmartSwitch. DaVinci Resolve's AI feature is a distinct Studio feature.

## Refine picture and audio separately

Cut for intelligibility first, then refine shot duration, reactions, eyelines, continuity, and jump-cut coverage. Avoid rapid alternation merely because speaker labels change. Keep a useful wide angle for overlaps, silence, uncertain speaker attribution, or visual resets.

When picture and audio edit points should diverge, read [linked audio and J/L cuts](editing/linked-audio-and-jl-cuts.md). For edit-point effects, read [transitions](editing/transitions.md); a transition does not repair a bad angle choice or broken sync. Perform loudness and dynamics work after the program structure is stable; read [loudness and dynamics](audio/loudness-and-dynamics.md).

## Flatten only for a defined downstream need

Keep multicam wrappers while alternate-angle changes remain likely. Flatten when downstream grading, interchange, or delivery requires ordinary source clips.

Use `timeline.multicam.previewFlatten(multicam, { scope, gradePolicy })`, inspect its summary, then apply that exact preview with `flatten()`. `scope` is `"video"`, `"audio"`, or `"both"`. Use `gradePolicy: "copy_multicam"` when the wrapper grade should follow the active source clips; use `"retain_angle"` when the selected source-angle grades should remain. Complex Color metadata can require separate review.

Flattening removes alternate-angle switching from the affected timeline items. Retain an unflattened timeline or approved version before flattening when reversibility matters. After success, reacquire the timeline and its items; old snapshots and previews are stale.

## Respect current capability boundaries

The high-level semantic surface is `project.multicams.inspect()`, `previewCreate()` / `create()`, and `timeline.multicam.previewSwitch()` / `switch()` plus `previewFlatten()` / `flatten()`. Search the installed declarations instead of guessing angle-reorder, source-replacement, match-frame, SmartSwitch, or timing-recovery methods on these objects.

The current verified semantic switch and flatten route requires a contiguous multicam-only program beginning at the timeline start on affected track 1. Mixed target content is rejected with `CAPABILITY_UNAVAILABLE` before mutation. Do not move or delete unrelated clips merely to force the route. Use the exact current CLI reference only when its documented target and verification contract fits the requested operation; otherwise report the limitation.

## Verify the edit

- After creation, inspect the returned multicam structure and confirm source membership, labels, and enabled state. Play or render samples near the beginning and end to check sync and drift.
- After switching, require a successful terminal with passed verification, inspect `changedSegments`, and read a fresh timeline revision. Review motion across representative cut points and confirm the intended video/audio scope.
- After flattening, confirm the affected wrappers became the intended ordinary source items and inspect the chosen grade policy. Verify that unrelated tracks and clips remain unchanged.
- Audition dialogue across cuts for phase, doubled audio, gaps, room-tone jumps, and unintended angle-audio changes. Structural readback alone cannot prove a clean listen.
- On any non-success terminal, inspect `possibleMutation`, partial `result`, `verification`, and `recovery` before retrying. Reattach or reuse the same idempotency key after an uncertain response; do not dispatch the logical mutation again with a new key.

See [SDK](sdk.md) for managed-runner structure and durable operation handling, [checking results](checking-results.md) for proof selection, and [errors and recovery](errors-and-recovery.md) for stale revisions and partial outcomes.

Primary DaVinci Resolve references: [DaVinci Resolve 21 New Features Guide](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_21_New_Features_Guide.pdf), [The Editor's Guide to DaVinci Resolve 20](https://documents.blackmagicdesign.com/UserManuals/DaVinci-DaVinci Resolve-20-Editors-Guide.pdf), and [Blackmagic Design multicam overview](https://www.blackmagicdesign.com/products/davinciresolve/edit).
