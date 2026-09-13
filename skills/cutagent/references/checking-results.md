# Check results and evidence

Use this reference after an SDK mutation, workflow, render, or other durable operation. Check the typed terminal state before interpreting domain-specific output. Process exit, progress text, a returned object, or a changed revision alone does not prove the requested result.

## Read the terminal truth

Await the operation once and branch on `terminal.status`:

- `succeeded`: inspect `terminal.result` and `terminal.verification`. Treat the result as complete only when the verification outcome and evidence support the claim you intend to make.
- `failed`: read `failure.possibleMutation`, `failure.readbackRequired`, `failure.retrySafe`, and `failure.recovery` before deciding what to do next. A failure may still follow a mutation.
- `cancelled`: cancellation is confirmed, but changes completed before cancellation may remain. Inspect any attached verification or recovery state.
- `partially_applied`: preserve successful items, inspect the returned partial result and recovery, and continue only from current state. Do not replay the whole batch.
- `verification_failed`: assume the mutation may have happened. Reconcile authoritative state before another write.
- `recovery_failed`: stop automated mutation and follow the reported manual-recovery guidance.

`verification.outcome` and evidence modality answer different questions. `passed` reports the verification decision; `readback`, `structural`, `file`, `rendered`, `visual`, and `auditioned` describe what was observed. `manual_review_required`, `partial`, `failed`, or `not_performed` must not be summarized as verified success.

Inside a `cutagent-sdk` runner script, use this fragment after creating `operation`. It records the terminal without turning every non-`passed` outcome into the same error:

```ts
const terminal = await operation.wait();

console.log({
  operationId: terminal.operationId,
  status: terminal.status,
  result: "result" in terminal ? terminal.result : undefined,
  verification: "verification" in terminal ? terminal.verification : undefined,
  failure: "failure" in terminal ? terminal.failure : undefined,
  recovery: "recovery" in terminal ? terminal.recovery : undefined,
});

if (
  terminal.status === "succeeded" &&
  terminal.verification.outcome === "manual_review_required"
) {
  progress("The native change finished; reviewing the requested result");
}
```

A `wait()` timeout or aborted wait stops only local polling. Keep the original `operationId` and idempotency key, then refresh or reattach that operation; do not dispatch a replacement mutation with a new key.

## Match evidence to the claim

Use the smallest evidence set that proves the requested outcome and protects nearby work:

| Claim | Useful evidence |
| --- | --- |
| Clip, track, marker, transition, link, or range changed as requested | SDK result plus structural/readback evidence for the affected region and relevant protected neighbors |
| Inspector, grade, Fusion input, or audio parameter changed | Exact parameter readback; add representative visual or audition evidence only when claiming perceptual quality |
| Motion, animation, transition timing, or retime feels correct | Structural/keyframe or curve readback plus temporal playback or a rendered excerpt; a still frame cannot prove motion |
| Final picture or mix is good | Representative visual review or an audition of the relevant passage; numeric state alone is insufficient |
| Deliverable is complete | Render terminal, file identity and media metadata, then playback of the exported picture and sound |

Do not render after every local parameter change. Conversely, do not claim appearance, pacing, intelligibility, loudness quality, or delivery readiness from structural readback alone.

Inspect one coherent affected region rather than re-reading every clip individually. For plural operations, use the ordered per-item results and inspect only failures, ambiguous targets, protected neighbors, or items whose requested outcome is not already proven. A fresh timeline snapshot is useful before a dependent edit or when terminal evidence is insufficient; repeated matching session and revision reads add no proof.

The snapshot supplied by `cutagent-sdk --title ... script.mjs` is the pre-script snapshot. Before another revision-bound action, refresh the timeline snapshot and create a new action context. Reacquire the current project or timeline only when its identity may have changed; do not repeat unchanged setup reads.

## Use domain-specific checks

- For speed curves and source handles, read [editing/speed-ramps.md](editing/speed-ramps.md).
- For transition placement, overlap, and temporal review, read [editing/transitions.md](editing/transitions.md).
- For Inspector transforms and animation, read [editing/transforms-and-keyframes.md](editing/transforms-and-keyframes.md).
- For linked sound, split edits, and J/L cuts, read [editing/linked-audio-and-jl-cuts.md](editing/linked-audio-and-jl-cuts.md).
- For loudness, dynamics, meters, and audition evidence, read [audio/loudness-and-dynamics.md](audio/loudness-and-dynamics.md).

## Report precisely

State separately what changed, what the runtime verified, what you reviewed visually or by audition, and what remains unresolved. Include stable operation or incident identifiers when they help recovery. Do not expose private traces or substitute a successful process exit for the operation terminal.
