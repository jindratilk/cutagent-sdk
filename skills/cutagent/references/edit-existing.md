# Edit an existing timeline

Use the current timeline as the source of truth. Preserve its story, track organization, sync, and unrelated work; make the smallest coherent change that satisfies the request.

## Choose the editing surface

- Use `timeline.edit` for semantic insert, overwrite, trim, and non-ripple removal. DaVinci Resolve an impact preview from one fresh snapshot, then apply that exact preview.
- Use `timeline.items` to move clips, change duration, enable or disable clips, set clip colors, or apply supported Inspector properties. Its shared operations accept one clip or a list where the installed types expose both forms.
- Use the CutAgent CLI for a supported one-off command or when its current reference documents a capability that the object model does not expose. Check the installed types or command reference instead of guessing a method.
- For retiming, read [speed ramps](editing/speed-ramps.md). For edit transitions, read [transitions](editing/transitions.md). For static transforms or animated framing, read [transforms and keyframes](editing/transforms-and-keyframes.md).
- For split edits and sync-sensitive dialogue work, read [linked audio and J/L cuts](editing/linked-audio-and-jl-cuts.md). For level, loudness, or dynamics work, read [loudness and dynamics](audio/loudness-and-dynamics.md).

CutAgent's semantic insert is a non-ripple placement into a preflight-confirmed empty target range; any conflict rejects the edit. Do not confuse it with DaVinci Resolve's GUI Insert Edit, which pushes later material. Choose overwrite when the new source range should replace an occupied record range without extending the timeline. A remove preview is also non-ripple; use a separately documented ripple route only when closing a gap is intended.

## Keep time and identity explicit

Treat timeline record positions, source-media ranges, and Fusion time as different domains. Build record positions from the snapshot's actual start, and express source ranges in source frames. Ranges are half-open: the end is the first excluded frame. Do not assume record frame zero, a `01:00:00:00` start, or matching source and timeline frame rates.

Snapshot clips, tracks, links, and previews are revision-bound. Compose related targets from one snapshot and submit the supported plural operation once. After a mutation, refresh only the state needed for the next dependent decision: take a new timeline snapshot when clip layout may have changed, and reacquire broader project or media references only when the operation could invalidate them. If a terminal result is ambiguous, inspect or reattach the same operation; do not replay it under a new idempotency key.

Preserve linked audio unless the editorial goal deliberately changes sync. A move or trim that excludes linked audio can create a split edit, but it should be an intentional J/L-cut decision rather than an incidental side effect.

## Apply a shared move

This runner script moves two exact video clips together while preserving their linked audio. Replace the clip and destination choices with targets selected from the user's timeline. The runner supplies one connected `timeline`, its current `snapshot`, the SDK namespace, and progress reporting.

```js
export default async function ({ sdk, timeline, snapshot, progress }) {
  const [first, second] = snapshot.videoTrack(1).clips;
  if (!first || !second) throw new Error("Expected two source clips on V1.");

  const previews = await timeline.items.previewMove([
    {
      item: first,
      destination: {
        track: snapshot.videoTrack(2),
        start: sdk.timelineRecordOffset(snapshot, sdk.frames(240)),
        linkedAudio: "preserve",
        collisionPolicy: "reject",
      },
    },
    {
      item: second,
      destination: {
        track: snapshot.videoTrack(2),
        start: sdk.timelineRecordOffset(snapshot, sdk.frames(360)),
        linkedAudio: "preserve",
        collisionPolicy: "reject",
      },
    },
  ]);

  const blocked = previews.flatMap((preview) => preview.blockers);
  if (blocked.length > 0) {
    throw new Error(blocked.map((item) => item.summary).join("; "));
  }

  progress("Moving two clips with linked audio");
  const operation = await timeline.items.move(previews, {
    idempotencyKey: sdk.idempotencyKey(),
  });
  const terminal = await operation.wait();
  if (terminal.status !== "succeeded") throw terminal.failure;
  console.log({ result: terminal.result, verification: terminal.verification });
}
```

## Verify the edit, not only the call

Match verification to the claim. Use the operation's ordered result and refresh the affected region when structural evidence is still needed; do not inspect every clip by default. Review a short preview across cuts, transitions, ramps, or animated moves when timing and continuity matter because a single frame cannot prove motion. Inspect representative frames for visual changes and audition sound-quality claims. If a list operation partially fails, retain the successful results and retry only unresolved targets from fresh state.
