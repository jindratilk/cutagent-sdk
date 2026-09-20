# Loudness and dynamics

Use loudness normalization to meet an explicit delivery target. Use dynamics to reshape level variation or control peaks and low-level noise. They are different operations: a dynamics setting is not loudness-compliance evidence, and peak normalization is not programme-loudness normalization.

Start from a fresh timeline snapshot and derive targets through `timeline.fairlight.from(snapshot)`. Fairlight tracks are one-based. Keep every preview in a plan bound to the same project, timeline, client generation, and snapshot revision.

## Normalize one exact track

The current verified SDK route measures the complete occupied range of one enabled audio track, calculates a track-fader correction, renders the same isolated range again, and verifies both Integrated LUFS and true peak. `truePeakDbtp` is a ceiling, not a second level target.

Choose values from the actual delivery specification. For example, EBU R 128 uses -23 LUFS and a production maximum of -1 dBTP; do not treat that as a universal streaming, theatrical, podcast, or broadcaster preset.

```js
export default async function normalizeDialogue({ sdk, timeline, snapshot, progress }) {
  const fairlight = timeline.fairlight.from(snapshot);
  const dialogue = fairlight.track(1);

  const change = fairlight.normalizeLoudness(dialogue, {
    integratedLufs: -23,
    truePeakDbtp: -1,
  });
  const plan = fairlight.compose([change]);
  const replayKey = sdk.idempotencyKey();
  progress("Measuring and normalizing dialogue loudness");
  const operation = await timeline.fairlight.apply(plan, {
    idempotencyKey: replayKey,
  });
  const terminal = await operation.wait();

  if (terminal.status !== "succeeded") {
    console.error({
      operationId: terminal.operationId,
      possibleMutation: terminal.possibleMutation,
      failure: terminal.failure,
      result: "result" in terminal ? terminal.result : undefined,
      recovery: "recovery" in terminal ? terminal.recovery : undefined,
    });
    throw new sdk.CutAgentSdkError(terminal.failure);
  }

  if (
    terminal.verification.outcome !== "passed" ||
    terminal.result.outcome === "partial" ||
    terminal.result.recovery.manualRecoveryRequired
  ) {
    console.error({
      operationId: terminal.operationId,
      result: terminal.result,
      verification: terminal.verification,
    });
    throw new Error("Track loudness result requires review");
  }

  const measuredStep = terminal.result.steps.find(
    (step) => step.change.kind === "loudness",
  );
  console.log(measuredStep?.change);
}
```

Read the measured before/after values from the successful terminal step. A later snapshot may still report `track.state.loudness` as unavailable; do not replace the operation receipt with guessed meter state.

The route fails before mutation when it cannot prove the exact track, occupied range, frame rate, fader state, or isolated rendered source. It also rejects a correction that would violate the true-peak ceiling or require processing beyond the verified fader route. Do not silently loosen the ceiling or switch targets. Rebalance the mix or apply the requested dynamics through the supported path below, then derive a fresh Fairlight snapshot and normalize again.

Normalize each track at most once in a plan. Do not combine `track.mix(...)` and `normalizeLoudness(...)` for the same track because both would own its final fader. Other same-revision clip changes can share the plan; the runtime performs loudness normalization after them so the final measurement covers their effect.

The public type also accepts a `FairlightBus`, but current runtime support is track-only. Main-output or named-bus normalization fails closed before mutation. Do not fall back to the similarly named public CLI loudness commands: they do not provide this SDK route's exact target binding and measured verification.

## Author dynamics deliberately

`track.dynamics(...)` describes a closed compressor, gate, and limiter state. Supply all three processors; it is not a partial patch.

```ts
// Given `fairlight` from a fresh snapshot:
const dialogue = fairlight.track(1);
const dynamicsPreview = dialogue.dynamics({
  compressor: { enabled: true, thresholdDb: -18, ratio: 3 },
  gate: { enabled: false, thresholdDb: -45, ratio: null },
  limiter: { enabled: true, thresholdDb: -1, ratio: null },
});
```

Thresholds are decibels. Ratios are dimensionless and must be between 1 and 100 when present; use `null` only for a processor without a ratio. The public dynamics model does not expose attack, hold, release, knee, make-up gain, or wet/dry mix. Do not invent those fields or claim a preset-equivalent sound from threshold and ratio alone.

Choose settings by listening to representative passages and checking gain reduction, transient handling, noise between phrases, and level consistency. A compressor reduces the range above its threshold; a gate attenuates low-level material; a limiter prevents peaks from exceeding its threshold. Aggressive settings can pump, breathe, clip word endings, amplify noise through downstream gain, or flatten intentional dynamics.

The semantic dynamics builder is present so a plan can express the intended closed state, but the aggregate SDK runtime currently rejects that change before mutation. Do not call `fairlight.apply()` with a dynamics preview as though support were established.

For a dynamics change that must be completed now, use the supported exact-track CLI route instead. It reads or patches the active timeline's one-based audio track, preserves unspecified parameters, closes and reopens the Disk project for the write, and verifies the same sequence, track identity, and requested values after reopen.

```sh
cutagent fairlight dynamics read --track 1 --json
cutagent fairlight dynamics set --track 1 --comp-enable --comp-threshold -18 --json
```

Read before writing and change only the controls the mix requires. The CLI exposes compressor threshold, enable, knee, mix, and a normalized native `comp-ratio` control; gate threshold/enable; and limiter threshold/enable. Do not pass a displayed compression ratio such as `3:1` to `--comp-ratio`: that option uses a 0–100 native control scale. Attack, hold, release, make-up gain, gate range, and sidechain routing are not writable through this command. Use a manual Fairlight workflow when those controls are essential, then audition and measure the result.

## Verify the audible result

Structural readback proves the requested control state or measured loudness result, not that the mix sounds good. Audition the affected programme in context and render/analyze the actual deliverable when compliance matters. Confirm channel layout, duration, Integrated LUFS, maximum true peak, silence, clipping, and any audible pumping or gating artifacts.

For SDK wait, cancellation, partial results, reattachment, and safe retry semantics, follow [SDK workflow](../sdk.md), [Checking results](../checking-results.md), and [Errors and recovery](../errors-and-recovery.md). See [Audio](../audio.md) for the surrounding mix workflow.

Primary standards: [ITU-R BS.1770-5](https://www.itu.int/rec/R-REC-BS.1770-5-202311-I) and [EBU R 128](https://tech.ebu.ch/publications/r128).
