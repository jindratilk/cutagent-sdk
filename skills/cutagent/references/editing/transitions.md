# Transitions

Use a transition to bridge one exact edit seam. Keep straight cuts when the transition adds no editorial meaning. Use a dissolve for continuity or a change in time, Smooth Cut only to conceal a compatible jump, and a Fusion transition only when the requested style justifies it.

## Choose the right operation

- Use `cutagent.action.edit.transition.add` for one video, audio, or linked video-and-audio seam.
- Use `cutagent.action.edit.transition.batch` for one or many video seams in one operation. Its input accepts either one transition object or an array; do not loop over repeated single-operation setup.
- Use Fairlight clip fades for a fade to or from silence. `defineFairlightCrossfadeBatch()` composes a fade-out and fade-in on adjacent audio clips; it does not create overlapping media or a native transition object. See [Audio](../audio.md) and [Linked audio and J/L cuts](linked-audio-and-jl-cuts.md).
- Build a custom handoff in Fusion when a native Edit transition cannot express it. See [Fusion](../fusion/REFERENCE.md).

The installed action declarations and schemas are authoritative for accepted fields and transition names. Do not assume every transition visible in DaVinci Resolve's Effects Library is accepted by these actions.

## Bind the exact seam

Transition inputs use absolute timeline-record frames, not offsets from zero. Derive `editFrame` from the incoming clip in the same immutable snapshot; this remains correct when the timeline starts at a nonzero timecode. See [Timing and targets](../timing-and-targets.md).

The outgoing and incoming clips must be adjacent on the same track, and their boundary must equal `editFrame`. Preserve complete linked-audio custody even for `scope: "video"`: include every linked audio target reported for both video clips. The runtime rejects stale, ambiguous, cross-track, or incomplete targets.

This snippet assumes the runner already supplied `{sdk, client, project, timeline, snapshot}`:

```js
const recordFrame = (position) => {
  if (position.value.kind !== "frames") {
    throw new Error("Transition targets require exact frame-domain record positions.");
  }
  return position.value.value;
};

const ownerOf = (clip) => {
  const tracks = snapshot.tracks.filter((track) => track.clips.includes(clip));
  if (tracks.length !== 1) throw new Error("Clip ownership is missing or ambiguous.");
  return tracks[0];
};

const audioTarget = (clip) => {
  const track = ownerOf(clip);
  if (track.type !== "audio" || clip.id === null || clip.linkedItemIds === null) {
    throw new Error("Audio transition target lacks a durable identity or complete link topology.");
  }
  return {
    id: clip.id,
    snapshotId: clip.snapshotId,
    mediaPoolItemId: clip.mediaPoolItemId,
    name: clip.name,
    trackType: "audio",
    trackIndex: track.index,
    recordStartFrame: recordFrame(clip.recordRange.start),
    recordEndFrame: recordFrame(clip.recordRange.endExclusive),
    linkedItemIds: clip.linkedItemIds,
  };
};

const videoTrack = snapshot.videoTrack(1);
const seams = videoTrack.clips.slice(1).flatMap((incoming, index) => {
  const outgoing = videoTrack.clips[index];
  return recordFrame(outgoing.recordRange.endExclusive) ===
    recordFrame(incoming.recordRange.start)
    ? [{outgoing, incoming}]
    : [];
});

const matches = seams.filter(({incoming}) => incoming.name === "Scene B");
if (matches.length !== 1) throw new Error("Expected one exact Scene B edit seam.");
const seam = matches[0];
const context = sdk.timelineActionContext(snapshot);

const linkedAudio = [
  ...snapshot.linkedItems(seam.outgoing),
  ...snapshot.linkedItems(seam.incoming),
].filter((clip) => ownerOf(clip).type === "audio");
const linkedAudioTargets = [...new Map(
  linkedAudio.map((clip) => [clip.id, audioTarget(clip)]),
).values()];

const operation = await client.actions.start(
  "cutagent.action.edit.transition.add",
  context.input({
    outgoing: context.videoTarget(seam.outgoing),
    incoming: context.videoTarget(seam.incoming),
    linkedAudioTargets,
    editFrame: recordFrame(seam.incoming.recordRange.start),
    transitionType: "cross-dissolve",
    durationFrames: 12,
    placement: "both",
    scope: "video",
  }),
  {idempotencyKey: sdk.idempotencyKey()},
);

const terminal = await operation.wait();
if (terminal.status !== "succeeded") throw terminal.failure;
if (terminal.verification.outcome !== "passed") {
  throw new Error("Transition structural verification did not pass.");
}
```

Use `scope: "linked"` only when both video clips have exactly one reciprocal, adjacent audio companion pair at the same seam. A linked Cross Dissolve requests the video transition and its audio companion. Use `scope: "audio"` with exact audio neighbors for an audio transition object; use `scope: "video"` to leave linked audio unchanged.

## Apply several video transitions together

Build every entry from the same snapshot and submit one batch. Batch transitions are video-only, but each entry still carries the linked audio identities that the runtime must preserve.

```js
const transitions = seams.map(({outgoing, incoming}) => Object.freeze({
  outgoing: context.videoTarget(outgoing),
  incoming: context.videoTarget(incoming),
  linkedAudioTargets: [...new Map([
    ...snapshot.linkedItems(outgoing),
    ...snapshot.linkedItems(incoming),
  ].filter((clip) => ownerOf(clip).type === "audio")
    .map((clip) => [clip.id, audioTarget(clip)])).values()],
  editFrame: recordFrame(incoming.recordRange.start),
  transitionType: "cross-dissolve",
  durationFrames: 12,
  placement: "both",
}));

if (transitions.length === 0) throw new Error("No adjacent video seams selected.");
const operation = await client.actions.start(
  "cutagent.action.edit.transition.batch",
  context.input({transitions}),
  {idempotencyKey: sdk.idempotencyKey()},
);
const terminal = await operation.wait();
if (terminal.status !== "succeeded") throw terminal.failure;
if (terminal.verification.outcome !== "passed") {
  throw new Error("Transition batch structural verification did not pass.");
}
```

The batch result preserves ordered per-seam outcomes. Inspect them before deciding whether any further action is appropriate; an existing matching transition may be reported as a verified no-op.

## Duration, placement, and handles

`durationFrames` is a positive whole-frame duration in the timeline frame domain. At one edit seam:

- `placement: "start"` starts the transition at the seam.
- `placement: "end"` ends the transition at the seam.
- `placement: "both"` centers it on the seam. Prefer an even duration when symmetric halves matter.

A transition needs usable source material beyond the visible outgoing and incoming edit boundaries. Exact `sourceRange` and `retimeSource.availableRange` values can expose an obvious lack of spare media when present, but they are not a transition-specific handle preview. The prepared-action preflight does not prove sufficient handles. Choose a conservative duration and treat live rejection as no mutation unless the terminal reports possible or partial mutation. Do not trim clips automatically just to make a transition fit.

The native `TimelineItem.AddTransition` route requires DaVinci Resolve 21.1. Current SDK applicability metadata does not independently certify OS, architecture, transport, or Free/Studio support, so let live capability admission decide and do not claim broader compatibility from source inspection alone.

## Verify the result

The transition actions require structural readback of the created transition identity, track, start, duration, and placement while preserving ordinary timeline items and linked audio. That proves structure, not appearance or sound.

For an editorially consequential seam, inspect motion across multiple frames or play/render through it. Audition linked or audio-only transitions. A single still cannot prove a transition, and a successful process exit cannot prove the visual match. Follow [Checking results](../checking-results.md). A successful transition invalidates the snapshot revision used above, so obtain a fresh snapshot before a later mutation on that timeline.
