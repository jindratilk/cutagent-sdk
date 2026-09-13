# Audio

Treat audio as an edit with hierarchy, continuity, and delivery constraints—not as a final volume pass. Keep dialogue intelligible, preserve intentional ambience and perspective, and let music and effects support the cut without masking speech.

## Read the focused guidance when needed

- For J-cuts, L-cuts, split edits, audio-only placement, or any trim that can disturb sync, read [linked audio and J/L cuts](editing/linked-audio-and-jl-cuts.md).
- For loudness targets, dynamics, EQ, and final-level decisions, read [loudness and dynamics](audio/loudness-and-dynamics.md).
- For audio fades used as edit transitions, read [transitions](editing/transitions.md).

## Work from one coherent snapshot

Derive Fairlight objects from `timeline.snapshot()`. Track indexes are one-based. Clips, tracks, buses, and previews are bound to that exact timeline revision; do not mix objects from different snapshots or reuse them after another edit changes the timeline.

Build the mix in useful layers:

1. Fix edits, sync, missing handles, and abrupt boundaries.
2. Use clip gain for local level differences and clip fades for boundaries.
3. Use track mix for the shared level and pan of a role such as dialogue, music, or effects.
4. Apply tonal or dynamic processing only for a specific audible problem.
5. Normalize loudness against the actual delivery requirement after the mix is stable.

Do not use peak level as a substitute for perceived loudness. Likewise, do not normalize every clip independently when relative dynamics are intentional.

## Compose related changes once

This `cutagent-sdk --title "Set dialogue clip gain" script.mjs` module uses the supplied runner context to set every durable clip on audio track 1 to the same absolute clip gain in one plan:

```js
export default async function setDialogueClipGain({
  sdk,
  timeline,
  snapshot,
  progress,
}) {
  const fairlight = timeline.fairlight.from(snapshot);
  const dialogue = fairlight.track(1);
  const clips = dialogue.clips.filter(
    (clip) => clip.id !== null && clip.linkedItemIds !== null,
  );

  if (clips.length === 0) {
    throw new Error("Audio track 1 has no durable clips with proven link topology.");
  }

  const plan = sdk.defineFairlightGainBatch(
    fairlight,
    clips.map((clip) => ({ clip, gainDb: -3 })),
  );
  const retryKey = sdk.idempotencyKey();
  progress("Setting dialogue clip gain");
  const operation = await timeline.fairlight.apply(plan, {
    idempotencyKey: retryKey,
  });
  const terminal = await operation.wait();

  if (terminal.status !== "succeeded") {
    console.error({
      status: terminal.status,
      result: "result" in terminal ? terminal.result : undefined,
      failure: "failure" in terminal ? terminal.failure : undefined,
      recovery: "recovery" in terminal ? terminal.recovery : undefined,
    });
    throw new sdk.CutAgentSdkError(terminal.failure);
  }

  console.log({
    outcome: terminal.result.outcome,
    steps: terminal.result.steps,
    evidence: terminal.result.evidence,
  });
}
```

For different per-clip values, create previews such as `clip.gain(db)`, `clip.pan(value)`, `clip.fadeIn(duration)`, or `clip.fadeOut(duration)`, then pass the previews together to `fairlight.compose(...)`. Use `defineFairlightGainBatch`, `defineFairlightPanBatch`, `defineFairlightFadeInBatch`, `defineFairlightFadeOutBatch`, or `defineFairlightCrossfadeBatch` when their shared operation matches the edit. A crossfade pair must be adjacent on the same audio track.

## Respect current execution support

The current aggregate runtime executes clip gain, clip pan, clip fades and fade curves, track mix, exact clip effects, and track loudness normalization. Pan controls depend on the track's channel mapping, so preserve the observed pan when the runtime reports it as non-writable. Do not guess effect or preset identifiers.

Some typed preview builders describe planned surface area but are not currently executable through the aggregate plan: `routeTo(...)`, clip `eq(...)`, track `dynamics(...)`, `synchronize(...)`, and loudness normalization of a bus can fail before mutation with `CAPABILITY_NEGOTIATION_FAILED`. Check the installed version's declarations and capabilities before relying on them; do not invent a raw fallback.

Read `FairlightObserved<T>` state by checking `status`. An unavailable readback is not zero and is not permission to overwrite the setting with a guessed value.

## Verify proportionately

Inspect the terminal status before retrying. A non-success terminal may contain a partial result, per-step structural evidence, and recovery guidance; preserve that evidence, reattach through the operation ID or reference, and reuse the same idempotency key if the same logical mutation must be retried.

Structural readback proves settings and target identity, not that the mix sounds good. Audition representative boundaries and the loudest or most processed passages after consequential combined changes. Check dialogue clarity, clicks, masking, stereo placement, and true-peak or loudness compliance where relevant; do not require a fresh render for every minor gain adjustment.
