# Timing and targets

Use this reference when choosing a timeline position, selecting source media, or identifying an existing track or clip for a write.

## Keep time domains explicit

| Intent | SDK value | Meaning |
| --- | --- | --- |
| Place or find something on a timeline | `TimelineRecordPosition` / `TimelineRecordRange` | Absolute record coordinate on that timeline |
| Choose frames from media | `SourcePosition` / `SourceRange` | Coordinate within the source asset |
| Express a length | `Duration` | Non-negative length, not a position |
| Author a keyframe in the typed Fusion graph | `FusionFrame` | Composition-frame coordinate; do not substitute record or source frames |

Construct these values with `timelineRecordPosition()`, `timelineRecordRange()`, `sourcePosition()`, `sourceRange()`, `duration()` and `fusionFrame()`. Do not pass plain objects that merely resemble them. SDK ranges are half-open: the start is included and `endExclusive` is not. Adjacent ranges therefore meet without sharing a frame.

Use the exact rate observed from the relevant object. `snapshot.frameRate` owns timeline-record values; a clip's or Media Pool asset's source rate owns source values. They can differ. If the source rate is unavailable, do not silently substitute the timeline rate for frame-accurate source work.

Represent fractional rates exactly, for example `frameRate(30_000, 1_001, 30)`. A semicolon denotes drop-frame numbering and is valid only for supported drop-frame rates; a colon denotes non-drop-frame numbering. Timecode changes labels, not playback speed.

`seconds()` preserves decimal values to microsecond precision. Converting seconds to frames can be inexact, especially at fractional rates. Prefer an explicit frame boundary when the edit is frame-specific. Otherwise choose `floor`, `ceil`, or `nearest_ties_to_even` deliberately and pass that rounding policy to the operation or conversion; omission fails instead of rounding silently.

## Offset from the observed timeline start

Do not assume record frame zero is the first timeline frame. Timelines commonly start at a nonzero timecode, and the start can be changed per timeline. Use `timelineRecordOffset()` for a frame offset from the observed start:

```js
export default async function ({sdk, timeline, snapshot}) {
  const at = sdk.timelineRecordOffset(snapshot, sdk.frames(240));
  const video = snapshot.videoTrack(1);
  const clip = video.clipAt(at);

  console.log({
    timelineId: timeline.id,
    revision: snapshot.revision,
    position: at.toString(),
    track: {type: video.type, index: video.index, name: video.name},
    clip: {id: clip.id, snapshotId: clip.snapshotId, name: clip.name},
  });
}
```

This is a complete module for the `cutagent-sdk` runner; it uses the runner's already connected `sdk`, `timeline`, and `snapshot` context.

`timelineRecordPosition(frames(240), snapshot.frameRate)` means absolute record frame 240. It does **not** mean 240 frames after `snapshot.start`. Likewise, a timecode such as `01:00:10:00` is an absolute displayed record coordinate when constructed with the timeline's exact rate.

## DaVinci Resolve targets from one coherent snapshot

Use the exact current project and timeline supplied by the runner or explicitly resolved by your program, then select tracks and clips from one immutable snapshot. Track indexes are 1-based by DaVinci Resolve convention.

`clipAt()` uses a record-domain position and requires exactly one covering item. Preserve `TARGET_NOT_FOUND` and `AMBIGUOUS_TARGET`; do not turn either into "use the first clip." A name is display metadata and may repeat. When selecting by metadata, filter the snapshot, apply the requested track/range constraints, and require the intended cardinality before proceeding.

Use the exact `ClipSnapshot` and `TrackSnapshot` objects returned by that snapshot in semantic previews. Their snapshot identities and `snapshotRevision` prevent a write from drifting to a similar object. `clip.id === null` means DaVinci Resolve did not prove a durable item identity; such a clip can be inspected but cannot be used by mutations that require durable identity.

For generic Actions, create `timelineActionContext(snapshot)` and use its `input()`, `videoTarget()`, `bladeTarget()`, or `videoRetimeTarget()` helpers instead of hand-building identity and revision fields. The retime helper uses verified available source handles and the source origin; the currently trimmed source range alone may be insufficient for a ramp. See [speed ramps](editing/speed-ramps.md).

## Preserve relationships and revision authority

Treat linked audio as topology, not as clips that happen to share a name or range. Use `snapshot.linkedItems(clip)` only when DaVinci Resolve exposes authoritative reciprocal links, and choose the operation's explicit `preserve`, `include`, or `exclude` policy. If topology is unavailable, do not guess.

Inspect every impact preview before dispatch. A preview binds the resolved targets, protected neighbors, affected tracks and timeline revision; do not reconstruct it or apply it through a different action. When an API accepts a list, pass all independently configured items to that plural overload so CutAgent can evaluate and execute the shared operation coherently. Do not loop serial writes or invent a batch method.

After a mutation changes the timeline revision, call `timeline.snapshot()` before preparing a dependent preview or target. Keep the existing project and timeline handles for ordinary timeline mutations; avoid broad repeated setup reads. DaVinci Resolve `client.projects.current()` and its current timeline again after the context-changing methods `client.projects.create()`, `client.projects.open()`, `client.projects.restore()`, `client.projects.libraries.open()`, or `client.projects.libraries.restore()`. Refresh a Media Pool page or asset only after an operation changes its revision/custody or when the next operation needs fields you have not read. Whenever you resolve a new context, compare durable project and timeline identities with the intended targets rather than accepting a matching name.

For operation failures, uncertain completion or stale revisions, follow [failure and recovery guidance](errors-and-recovery.md). For mapping timeline, source and composition frames, read [Fusion coordinates and time](fusion/coordinates-and-time.md); for keyframe operations, read [Fusion animation](fusion/animation.md). A timeline frame and a Fusion composition frame are not interchangeable.
