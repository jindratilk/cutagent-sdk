# Preserve linked audio and make J/L cuts

Treat link topology and timing as separate facts. A native link tells DaVinci Resolve which timeline items belong together; it does not prove that their record or source ranges match. Inspect both before editing, then state explicitly whether the operation should preserve, include, or exclude linked audio.

Use [timing and targets](../timing-and-targets.md) for record/source domains and nonzero timeline starts. Use [checking results](../checking-results.md) when interpreting an operation terminal.

## Inspect the relationship

Read linked companions from the same coherent `TimelineSnapshot`:

```js
const video = snapshot.videoTrack(1).clips[0];
if (!video) throw new Error("V1 has no clip to inspect");

const companions = snapshot.linkedItems(video);
const audioIds = new Set(
  snapshot.audioTracks.flatMap((track) => track.clips.map((clip) => clip.id)),
);
const linkedAudio = companions.filter((clip) => clip.id && audioIds.has(clip.id));

console.log({
  video: {id: video.id, recordRange: video.recordRange.toJSON()},
  linkedAudio: linkedAudio.map((clip) => ({
    id: clip.id,
    recordRange: clip.recordRange.toJSON(),
    sourceRange: clip.sourceRange?.toJSON() ?? null,
  })),
});
```

`linkedItemIds === null` means topology was not authoritatively available; it does not mean “unlinked.” `snapshot.linkedItems()` also requires reciprocal, uniquely resolvable identities and fails closed otherwise. Do not infer a relationship from matching names, Media Pool items, or co-timed ranges.

## Choose the linked-audio policy

- `previewInsert()` and `previewOverwrite()` require `linkedAudio: "include" | "exclude"`. `include` also requires an explicit one-based `audioTrack`; `exclude` places video only.
- `previewInsertAudio()` places an audio-only source range on one existing audio track. It neither creates a video item nor links the new item to picture.
- `previewTrim()` requires `linkedAudio: "preserve" | "exclude"`. `preserve` trims an authoritatively linked video/audio group together. `exclude` trims only the selected video and protects the linked audio and reciprocal relationship; this is the primitive for picture-only split edits.
- `timeline.items.previewMove()` defaults to preserving linked audio for a record-time move. Pass `linkedAudio: "exclude"` only when the audio is intentionally meant to stay at its current record position.

The semantic SDK currently has no dedicated method to create or dissolve an arbitrary native link group. If the relationship itself must change, use the exact version-matched `clip link` or `clip unlink` command described through [the CLI reference](../cli.md), then read both sides back. Do not confuse linking with waveform synchronization; use Media Pool synchronization for sync work.

## Move a picture cut without moving the audio cut

A J-cut introduces the incoming audio before its picture. An L-cut shows the incoming picture while the outgoing audio continues. Starting from an aligned A/V cut, move only the picture edit:

| Split edit | Outgoing video tail | Incoming video head | Audio cut |
| --- | --- | --- | --- |
| J-cut | extend by `n` | trim inward by `n` | unchanged |
| L-cut | trim inward by `n` | extend by `n` | unchanged |

The following is an executable `cutagent-sdk --title ... script.mjs` module. The runner supplies `{sdk, client, project, timeline, snapshot, progress}`. It uses the first adjacent pair on V1 only as a concrete selection example; select the intended cut from inspected identities in real work.

```js
export default async function ({sdk, timeline, snapshot, progress}) {
  const kind = "J"; // Change to "L" for the opposite split.
  const amount = 12;
  const [outgoing, incoming] = snapshot.videoTrack(1).clips;
  if (!outgoing?.id || !incoming?.id) {
    throw new Error("Select two durable adjacent video clips on V1");
  }
  if (outgoing.recordRange.endExclusive.toString() !== incoming.recordRange.start.toString()) {
    throw new Error("The selected picture clips do not share one edit point");
  }

  const linkedAudioBefore = new Map();
  for (const picture of [outgoing, incoming]) {
    const audio = snapshot.linkedItems(picture).filter((candidate) =>
      snapshot.audioTracks.some((track) =>
        track.clips.some((clip) => clip.snapshotId === candidate.snapshotId),
      ),
    );
    if (audio.length === 0 || audio.some((clip) => !clip.id)) {
      throw new Error(`Picture clip ${picture.name} lacks durable linked audio`);
    }
    for (const clip of audio) {
      linkedAudioBefore.set(clip.id, JSON.stringify({
        recordRange: clip.recordRange.toJSON(),
        sourceRange: clip.sourceRange?.toJSON() ?? null,
      }));
    }
  }

  const inward = sdk.frames(amount, snapshot.frameRate);
  const outward = sdk.frames(-amount, snapshot.frameRate);
  const trims = kind === "J"
    ? [
        {clip: outgoing, options: {tail: outward, linkedAudio: "exclude"}},
        {clip: incoming, options: {head: inward, linkedAudio: "exclude"}},
      ]
    : [
        {clip: outgoing, options: {tail: inward, linkedAudio: "exclude"}},
        {clip: incoming, options: {head: outward, linkedAudio: "exclude"}},
      ];

  const impacts = await timeline.edit.previewTrim(snapshot, trims);
  if (impacts.some((impact) =>
    impact.linkedAudio.behavior !== "exclude" || !impact.linkedAudio.topologyProven
  )) {
    throw new Error("The preview did not prove picture-only trim topology");
  }

  progress(`Creating a ${kind}-cut at the selected edit`);
  const operation = await timeline.edit.trim(impacts, {
    idempotencyKey: sdk.idempotencyKey(),
  });
  const terminal = await operation.wait();
  if (
    terminal.status !== "succeeded" ||
    terminal.verification.outcome !== "passed" ||
    terminal.verification.protectedStatePreserved !== true
  ) {
    throw new Error(JSON.stringify(terminal));
  }

  const fresh = await timeline.snapshot();
  for (const [audioId, before] of linkedAudioBefore) {
    const audio = fresh.audioTracks
      .flatMap((track) => track.clips)
      .find((clip) => clip.id === audioId);
    if (!audio) throw new Error(`Linked audio ${audioId} disappeared`);
    const after = JSON.stringify({
      recordRange: audio.recordRange.toJSON(),
      sourceRange: audio.sourceRange?.toJSON() ?? null,
    });
    if (after !== before) throw new Error(`Linked audio ${audioId} changed`);
    fresh.linkedItems(audio);
  }

  console.log(terminal.result.results);
}
```

Positive `head` or `tail` values move that edge inward; negative values extend it outward. Extensions require real source handles. Preview can therefore reject a stale target, missing handles, an ambiguous or unreadable link group, an occupied result range, a locked track, or a source/timeline boundary that cannot be represented exactly. Review both returned impacts before dispatch.

This operation moves a cut; it does not judge dialogue cadence or hide a visual discontinuity. Audition across the edit and play the picture through the overlap. Structural readback can prove ranges, identities, links, and protected state, but only temporal review can establish that the split sounds natural and the picture cut lands well.

## Current boundaries

- Semantic trim is video-primary. It can trim linked A/V together or trim picture while preserving audio, but it does not expose an audio-primary split-edit method.
- A one-sided picture-only trim can open a gap. For a normal J/L cut between adjacent clips, adjust both neighboring video edges as one plural preview, as above.
- A plural preview groups independently configured trims into one operation; it does not make overlapping or contradictory impacts valid.
- Link topology must be observable in the current snapshot. Capability metadata or a successful earlier operation does not substitute for current reciprocal readback.
- The checks above verify structure. They do not claim that this exact example was executed or auditioned in the user's current DaVinci Resolve project.
