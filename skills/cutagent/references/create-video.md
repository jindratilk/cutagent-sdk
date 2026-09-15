# Create a video

Build a new video as an explicit timeline assembly: choose the project and format, resolve source assets, create the timeline, place exact source ranges at exact record positions, then verify the resulting structure and the creative result. Keep source time, timeline-record time, and the timeline's nonzero start distinct.

Use the current project unless the request explicitly calls for a new one. Read [projects and media](projects-and-media.md) before importing, relinking, or synchronizing sources, and [timing and targets](timing-and-targets.md) before mixed-rate or timecode-based assembly.

If a newly created project has no timeline, create its first empty timeline with `cutagent -j timeline create "Main" --width 1920 --height 1080 --fps 24` before the SDK workflow. The current prepared SDK timeline-create route can fail with `NO_TIMELINE_OPEN` in a timeline-free project. The SDK example below starts from an existing current timeline; it creates a separate output timeline.

## Choose the creation path

- Use the typed `cutagent.action.timeline.create` action for an empty timeline or when name, width, height, or frame rate must be explicit. It currently has no high-level `project.timelines.create()` equivalent.
- Use `timeline.edit.previewInsert()` and `insert()` to assemble deliberate source subranges and tracks. Their list overloads preview and apply several placements through one shared operation.
- For a simple Media Pool stringout where clip names and their order are sufficient, the current `media create-timeline` CLI command can be shorter. Do not use it when exact bins, source ranges, tracks, gaps, or record positions matter.
- Import an existing DRT, OTIO, XML, AAF, or EDL through the installed timeline-import contract rather than rebuilding it as a guessed sequence.

Decide the timeline frame rate before cutting. A source frame number belongs to that asset's rate; it is not automatically a record frame at the timeline rate. Treat ranges as half-open: `endExclusive` is the first frame not used.

## Assemble an empty timeline

This managed-runner module creates a 1920×1080, 24 fps timeline and inserts two linked picture-and-sound excerpts. Replace asset names and source-frame decisions with inspected media. `timelineRecordOffset()` keeps the placements correct when the timeline starts at a nonzero record frame. The runner supplies `sdk`, `client`, and the current `project`; read [SDK usage](sdk.md) for invocation and standalone connection.

```js
export default async function createVideo({ sdk, client, project, progress }) {
  const context = await client.projects.context();
  if (context.projectRevision.status !== "available") {
    throw new Error("The current project has no mutation revision.");
  }

  const createOperation = await client.actions.start(
    "cutagent.action.timeline.create",
    {
      projectId: project.id,
      revision: context.projectRevision.revision,
      name: "Launch Film",
      width: 1920,
      height: 1080,
      frameRate: 24,
    },
    { idempotencyKey: sdk.idempotencyKey() },
  );
  const created = await createOperation.wait();
  if (created.status !== "succeeded" || created.verification.outcome !== "passed") {
    throw new Error(JSON.stringify(created));
  }

  // Creation changes the current timeline. Resolve only that invalidated context.
  const timeline = await project.timelines.current();
  if (timeline.id !== created.result.timeline.timelineId) {
    throw new Error("The created timeline is not the current timeline.");
  }
  const snapshot = await timeline.snapshot();
  snapshot.videoTrack(1);
  snapshot.audioTrack(1);

  const sourceRate = sdk.frameRate(24, 1);
  const wide = await project.mediaPool.assetByName("wide.mov");
  const close = await project.mediaPool.assetByName("close.mov");

  const impacts = await timeline.edit.previewInsert(snapshot, [
    {
      source: wide,
      options: {
        at: sdk.timelineRecordOffset(snapshot, sdk.frames(0)),
        sourceRange: sdk.sourceRange(sdk.frames(48), sdk.frames(192), sourceRate),
        videoTrack: sdk.trackIndex(1),
        audioTrack: sdk.trackIndex(1),
        linkedAudio: "include",
      },
    },
    {
      source: close,
      options: {
        at: sdk.timelineRecordOffset(snapshot, sdk.frames(144)),
        sourceRange: sdk.sourceRange(sdk.frames(24), sdk.frames(120), sourceRate),
        videoTrack: sdk.trackIndex(1),
        audioTrack: sdk.trackIndex(1),
        linkedAudio: "include",
      },
    },
  ]);

  progress("Assembling the new timeline");
  const insertOperation = await timeline.edit.insert(impacts, {
    idempotencyKey: sdk.idempotencyKey(),
  });
  const inserted = await insertOperation.wait();
  if (inserted.status !== "succeeded" || inserted.verification.outcome !== "passed") {
    throw new Error(JSON.stringify(inserted));
  }

  const after = await timeline.snapshot();
  const v1 = after.videoTrack(1).clips;
  if (v1.length !== 2 || v1[0]?.name !== "wide.mov" || v1[1]?.name !== "close.mov") {
    throw new Error("The assembled V1 sequence does not match the intended order.");
  }
}
```

The source ranges total 144 and 96 frames, so the second placement starts at timeline offset 144 without a gap. For mixed source rates, give each cut its own authoritative `FrameRate` and choose source boundaries that are exactly representable on the timeline. Do not label record offsets as source handles or reuse the creation revision for later edits.

If files are not yet in the Media Pool, first read `project.mediaPool.snapshot()`, call `importMedia()` with that pool revision and one idempotency key, and await its terminal result. Then refresh the Media Pool observation and match the returned imported IDs to the source assets used for placement; the stable project facade does not need to be reacquired. Do not assume a successful file probe means DaVinci Resolve imported a usable codec.

## Continue the build

After a mutation, refresh the snapshot, impact, or other revision-bound target needed by the next dependent change. Keep stable project and timeline facades when their identities remain valid. Use one list overload for related placements from one snapshot; do not serialize repeated setup around every clip or invent a batch method that is absent from the declarations.

- For additional inserts, overwrites, trims, clip moves, or track structure, read [editing](editing.md).
- For variable speed or freeze/reverse work, read [speed ramps](editing/speed-ramps.md).
- For edit-point transitions, read [transitions](editing/transitions.md).
- For static framing and animated Inspector properties, read [transforms and keyframes](editing/transforms-and-keyframes.md).
- For sync-sensitive dialogue, separate audio placement, or J/L cuts, read [linked audio and J/L cuts](editing/linked-audio-and-jl-cuts.md).
- For loudness, EQ, compression, limiting, or mix proof, read [loudness and dynamics](audio/loudness-and-dynamics.md).
- For export settings, codec discovery, queue state, and delivered-file checks, read [rendering](rendering.md).

## Verify the video

Inspect the mutation terminal before any retry. A non-success terminal may still contain partial results, verification evidence, or recovery state; an uncertain mutation must not be replayed with a new idempotency key.

Use a fresh timeline snapshot to verify timeline identity, rate, tracks, clip order, record ranges, source ranges, and reciprocal linked items. Then review the proof required by the creative claim: representative frames for layout, a temporal preview across cuts, transitions, ramps, and animation, and an audition for synchronization and mix quality. One still cannot prove motion, and process success or structural readback cannot prove the finished video looks or sounds right.
