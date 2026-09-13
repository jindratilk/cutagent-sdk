# Errors and recovery

Use this reference when a CutAgent call throws, an operation stops without `succeeded`, a script loses its connection, or the observed project state is uncertain.

## Preserve authority before acting

Keep the operation handle, its `ref` or `operationId`, and the idempotency key used to start the mutation. Observe that operation before starting another edit. A script process ending, a connection closing, or a local wait timing out does not prove that the underlying operation stopped.

Treat these as separate outcomes:

- Calls can throw `CutAgentSdkError` before a handle is returned or while observing or controlling an existing operation. It carries a validated `failure` object.
- Local argument and value validation commonly throws `TypeError` before dispatch.
- `operation.wait()` returns every authoritative terminal, including `failed`, `cancelled`, `partially_applied`, `verification_failed`, and `recovery_failed`; it does not turn those terminals into thrown exceptions.
- An `AbortError` or `TimeoutError` from `wait()` stops only local polling. It neither cancels nor rolls back the operation.

## Interpret structured failure truth

Branch on `failure.code` or `failure.kind`, never on message text. Use the installed SDK declarations for the complete current code catalog.

Read these fields together:

- `retrySafe` is the authority's retry decision. When true, `retrySafetyProof` states whether safety comes from pre-execution rejection, a read-only request, or an idempotent replay bound to the original key and operation.
- `possibleMutation` describes project-state risk. Any value other than `none` requires conservative handling.
- `readbackRequired` means inspect current authoritative state before another mutation.
- `recovery` and `recoveryGuidance` describe the next supported actions; `recoveryOutcome` records whether recovery was already attempted.
- `requestId`, `operationId`, `workflowId`, `executionId`, and `incidentId` are correlation evidence. Retain them in diagnostics.
- `usage` reports account-usage disposition; do not infer it from whether the edit succeeded.

Do not infer “no change” from an underlying native error. DaVinci Resolve documents that some grouped setting calls may keep earlier settings when a later setting fails. Prefer the SDK's `possibleMutation`, partial result, recovery, and fresh readback over process output or assumptions about native return values.

## Reattach after an interrupted wait

The following is a standalone helper. It retries observation once, not the mutation:

```ts
import {
  type CutAgentClient,
  type OperationHandle,
  type PublicActionId,
  type TerminalOperationSnapshot,
} from "cutagent";

export async function waitOrReattachAfterTimeout<TResult, TAction extends PublicActionId>(
  client: CutAgentClient,
  operation: OperationHandle<TResult, TAction>,
): Promise<TerminalOperationSnapshot<TResult, TAction>> {
  try {
    return await operation.wait({ timeoutMs: 60_000 });
  } catch (error) {
    if (!(error instanceof DOMException) || error.name !== "TimeoutError") {
      throw error;
    }

    const reattached = await client.operations.reattach(operation.ref, {
      timeoutMs: 20_000,
    });
    return reattached.wait({ timeoutMs: 60_000 });
  }
}
```

Reattachment through `operation.ref` preserves the action-specific result type. Reattachment by raw `operationId` is available when only persisted identity remains, but returns a runtime-discriminated result rather than a caller-selected generic.

## Handle a terminal without hiding partial work

Given an existing `terminal` returned by `waitOrReattachAfterTimeout`:

1. On `succeeded`, inspect `terminal.verification`. Match proof to the claim: structural readback can prove topology, while motion, appearance, and sound may require rendered, visual, or auditioned evidence.
2. On `failed`, inspect `terminal.failure`, any retained `result`, and optional `recovery` before deciding what remains.
3. On `cancelled`, require `terminal.cancellation.state === "confirmed"`. A prior `cancellation_requested` state is nonterminal and does not imply rollback.
4. On `partially_applied`, inspect the retained result, verification evidence, and recovery state before touching affected objects. Do not replay the whole edit.
5. On `verification_failed`, assume the edit may exist but the claimed result was not proven. Reinspect the exact target and protected surroundings.
6. On `recovery_failed`, stop automated mutation. Preserve recovery evidence and follow the declared manual-recovery guidance.

If `failure.retrySafe` is false, do not repeat the mutation. If it is true, preserve the stated proof. For `idempotent_replay`, keep observing the named operation and reuse the exact idempotency key if replay is directed. A fresh key creates a new request rather than safely observing or replaying the old one.

Unsafe retry pattern, shown as a snippet with existing `applyEdit` and `input` variables:

```ts
try {
  await applyEdit(input);
} catch {
  await applyEdit(input); // May duplicate an edit whose first outcome is unknown.
}
```

## Recover at the right scope

Use a checkpoint-backed workflow for genuinely multi-step edits that need shared recovery truth. It is not an atomic transaction: cancellation does not roll back completed steps, and its result can report `partially_applied`, `checkpoint_restored`, `compensated`, `restore_failed`, or `manual_recovery_required`. Do not wrap a single semantic mutation in a workflow merely to add ceremony.

Use direct CutAgent CLI reproduction when the exact mature command or readback is the clearest diagnostic route. Load its current command card first, keep the same project and timeline identities, and begin with inspection when mutation state is possible or unknown. CLI process success is not a substitute for SDK terminal and verification evidence.

For domain-specific recovery, continue only with the relevant reference:

- For source-handle, retime, or speed-curve failures, read [speed ramps](editing/speed-ramps.md).
- For transition placement or handle failures, read [transitions](editing/transitions.md).
- For transform or animation readback, read [transforms and keyframes](editing/transforms-and-keyframes.md).
- For linked audio, split edits, or J/L-cut drift, read [linked audio and J/L cuts](editing/linked-audio-and-jl-cuts.md).
- For loudness, dynamics, or audition failures, read [loudness and dynamics](audio/loudness-and-dynamics.md).

Inspect only the affected scope and protected surroundings needed to resolve uncertainty. Do not turn recovery into mandatory per-clip inspection when the operation and its bounded readback already establish the result.
