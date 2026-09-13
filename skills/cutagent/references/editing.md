# Edit timeline clips

Make editorial decisions from one coherent `TimelineSnapshot`. Its tracks and clips are immutable observations tied to `snapshot.revision`; they are not permanent handles. Track indexes are one-based, clip ranges are half-open, and source-media time is distinct from timeline-record time.

Use [timing and targets](timing-and-targets.md) when converting timecode, seconds, frames, or timeline-relative offsets. Use [projects and media](projects-and-media.md) when importing or selecting source assets.

## Choose the editing surface

- Use `timeline.edit.previewInsert()` / `insert()` for video-rooted insertion, with an explicit linked-audio policy. Use `previewInsertAudio()` for an audio-only Media Pool asset on an existing audio track.
- Use `timeline.edit.previewOverwrite()` / `overwrite()` when the source range should replace material in an exact record range.
- Use `timeline.edit.previewTrim()` / `trim()` for explicit head or tail changes. Use `previewRemove()` / `remove()` for non-ripple removal of exact occurrences.
- Use `timeline.items.previewMove()` / `move()` to reposition existing video items, optionally preserving linked audio. Use `setDuration()`, `enable()`, `disable()`, `setColor()`, and `setProperties()` for their focused item changes.
- Use `timelineActionContext(snapshot)` with the [typed generic action API](sdk.md) for an exact blade. Look up the installed `cutagent.action.edit.blade` input rather than reconstructing a raw command.
- Use `timeline.managed` only when the task intentionally owns a whole timeline or bounded region declaratively. Do not use it to rewrite unrelated manual work.

For speed changes and retime curves, read [speed ramps](editing/speed-ramps.md). For edit-point transitions, read [transitions](editing/transitions.md). For Inspector transforms or animated properties, read [transforms and keyframes](editing/transforms-and-keyframes.md). For linked dialogue audio, split edits, and J/L cuts, read [linked audio and J/L cuts](editing/linked-audio-and-jl-cuts.md). For loudness, dynamics, and mix processing rather than picture editing, read [loudness and dynamics](audio/loudness-and-dynamics.md).

## Preview the resolved impact

Semantic edit and move previews do not mutate. Review their resolved record range, affected tracks and items, linked-audio behavior, protected items, collisions, and blockers before dispatch. A preview belongs to the exact client generation, timeline facade, and revision that issued it; do not reuse it after reconnecting or refreshing state.

Use plural overloads for several independently configured inserts, overwrites, trims, removals, moves, property changes, or duration changes. They create one shared operation while retaining per-item results. Do not repeatedly rebuild the same project and timeline context merely to operate on each item.

## Insert a short sequence

This `cutagent-sdk` runner snippet uses the supplied `sdk`, `project`, `timeline`, and `snapshot` variables. It inserts two video-only source ranges in one operation. Adapt asset names, source handles, positions, and tracks to inspected media and the user's authorized scope.

```ts
const wide = await project.mediaPool.assetByName("wide.mov");
const close = await project.mediaPool.assetByName("close.mov");

const impacts = await timeline.edit.previewInsert(snapshot, [
  {
    source: wide,
    options: {
      at: sdk.timelineRecordOffset(snapshot, sdk.frames(240)),
      sourceRange: sdk.sourceRange(sdk.frames(48), sdk.frames(144)),
      videoTrack: sdk.trackIndex(1),
      linkedAudio: "exclude",
    },
  },
  {
    source: close,
    options: {
      at: sdk.timelineRecordOffset(snapshot, sdk.frames(336)),
      sourceRange: sdk.sourceRange(sdk.frames(24), sdk.frames(96)),
      videoTrack: sdk.trackIndex(1),
      linkedAudio: "exclude",
    },
  },
]);

const key = sdk.idempotencyKey();
const operation = await timeline.edit.insert(impacts, { idempotencyKey: key });
const terminal = await operation.wait();
if (terminal.status !== "succeeded") {
  throw new Error(JSON.stringify(terminal.failure));
}
console.log(terminal.result.results);
```

`timelineRecordOffset(snapshot, frames(n))` adds `n` to the timeline's authoritative start, which may be nonzero. `sourceRange()` addresses frames in each source asset, not frames on the destination timeline. When source and timeline rates differ, choose boundaries the preview can represent exactly; use explicit rounding only when that loss of precision is intentional.

Keep the idempotency key for the lifetime of the dispatch. If the response is uncertain, reattach or inspect before retrying; never invent a new key to repeat an operation whose outcome is unknown.

## Continue after a mutation

After a successful mutation, refresh only the observations the next dependent edit needs. A new preview needs a fresh timeline snapshot and fresh snapshot-bound clip or track targets. Reacquire the project, timeline facade, or Media Pool asset only when the operation invalidated it or the runtime reports identity or revision drift. Do not pass old clips, tracks, impacts, or action contexts into a preview for a new revision.

Use proportionate evidence. A fresh timeline readback usually establishes a structural edit; transitions, motion, and pacing benefit from representative temporal or visual review because a successful process or one still frame cannot prove them. Follow [checking results](checking-results.md) for proof choices and [errors and recovery](errors-and-recovery.md) for stale revisions, partial results, or uncertain operations.
