# CutAgent SDK

Use the TypeScript SDK for composable inspection and editing workflows. Prefer high-level domain objects; use typed actions only when no suitable semantic method exists. Use CutAgent CLI for a bounded one-off command or when reproducing and diagnosing a failure is clearer through the command interface.

## Choose the execution path

Write the edit as a context-driven module so the same file runs through either distribution. The standalone public package exports the SDK from `cutagent`; after starting its local runtime as described in [setup.md](setup.md), use a small launcher:

```js
import * as sdk from "cutagent";
import edit from "./replace-opening.mjs";

const client = await sdk.CutAgent.connect();
try {
  const project = await client.projects.current();
  const timeline = await project.timelines.current();
  const snapshot = await timeline.snapshot();
  await edit({
    sdk,
    client,
    project,
    timeline,
    snapshot,
    progress: (message) => console.log(message),
  });
} finally {
  await client.close();
}
```

Run the launcher with Node:

```sh
node run-edit.mjs
```

Inside the CutAgent-managed agent environment, run the shared edit module directly instead:

```sh
cutagent-sdk --title "Replace the opening shot" replace-opening.mjs
```

The module must export one default async function. The runner connects and supplies one `client`, current `project`, current `timeline`, initial immutable `snapshot`, the complete `sdk` namespace, and `progress(message)`. It imports the module only after connection preflight. Reuse this context instead of importing another package, reconnecting, or repeating initial setup. Call `progress()` only for truthful activity updates; progress does not prove completion. The script must await every operation it starts.

```js
export default async function replaceOpening({ sdk, client, project, timeline, snapshot, progress }) {
  const source = await project.mediaPool.assetByName("A001_C001.mov");

  const impact = await timeline.edit.previewOverwrite(snapshot, source, {
    at: sdk.timelineRecordOffset(snapshot, sdk.frames(240)),
    sourceRange: sdk.sourceRange(sdk.frames(0), sdk.frames(96)),
    videoTrack: sdk.trackIndex(1),
    audioTrack: sdk.trackIndex(1),
    linkedAudio: "include",
  });

  console.log(impact.summary);
  progress("Replacing the opening shot");

  const operation = await timeline.edit.overwrite(impact, {
    idempotencyKey: sdk.idempotencyKey(),
  });
  const stopProgress = operation.subscribe((state) => {
    if (state.status === "running" || state.status === "waiting") {
      console.log(state.progress.phase, state.progress.overallFraction ?? null);
    }
  });

  const terminal = await operation.wait();
  stopProgress();

  if (terminal.status !== "succeeded") {
    console.error({
      status: terminal.status,
      possibleMutation: terminal.possibleMutation,
      result: "result" in terminal ? terminal.result : undefined,
      recovery: "recovery" in terminal ? terminal.recovery : undefined,
    });
    throw new sdk.CutAgentSdkError(terminal.failure);
  }
  if (terminal.verification.outcome !== "passed") {
    throw new Error(`Overwrite verification was ${terminal.verification.outcome}.`);
  }

  progress("Verifying the updated timeline");
  const after = await timeline.snapshot();
  console.log({ operationId: operation.operationId, revision: after.revision });
}
```

The managed runner closes the client afterward and uses native process completion as the activity outcome. It performs no automatic post-script inspection. The example therefore previews the exact impact, waits for the durable terminal, requires passed SDK verification, and reads a fresh snapshot itself.

## Use the object model

Start from this hierarchy and load only the relevant domain reference:

```text
client
├── projects.current() → project
│   ├── mediaPool
│   ├── render
│   ├── multicams
│   └── timelines.current() → timeline
│       ├── snapshot()
│       ├── edit, items, markers, managed
│       ├── captions, transcript, voiceovers
│       ├── fusion, color, fairlight, multicam
│       └── retime
├── operations
├── workflows
├── actions
└── artifacts
```

Use the installed root declarations and TSDoc for exact signatures. Search the exported `.d.ts` or package source for a symbol rather than copying an inventory into the script. Deep imports other than declared package subpaths are unsupported.

For typed actions, choose the carrier from the installed action declaration, not from the verb in its name. `actions.read()` returns a semantic read result; `actions.start()` returns an operation handle that you must await. A method name alone does not establish whether its installed contract returns a result or an operation handle. `actions.invoke()` selects the semantic read or operation carrier from the contract, but its return type still differs accordingly. Actions assigned to the sanitized low-level read carrier require `actions.lowLevel.read()` and also return a handle. Do not change SDK internals or bypass types to make a call fit the wrong carrier.

A `TimelineSnapshot` is a coherent, immutable observation. Its clips, tracks, node indexes, and revision-bound previews describe that exact state. After a successful mutation, obtain a fresh timeline snapshot or domain readback before planning the next change. Never retarget a stale object by display name, reuse an impact against a changed revision, or assume the current playhead and selection still identify the intended object.

Track indexes are one-based. Timeline record positions, source positions, durations, and Fusion frames are distinct domains. Preserve the snapshot's nonzero timeline start and the source asset's own rate. Read [timing-and-targets.md](timing-and-targets.md) before doing time conversion, mixed-rate work, source trims, retiming, or Fusion animation.

## Preview and apply mutations

Use this shape for semantic writes:

1. Read the exact project, timeline, snapshot, and source objects.
2. Build validated value types such as `frames()`, `sourceRange()`, `timelineRecordOffset()`, and `trackIndex()`.
3. Call the domain's `preview…` method and inspect affected and protected state.
4. Apply that issued preview with a caller-owned idempotency key.
5. Keep the operation reference, observe or wait for its terminal, and inspect any partial result before deciding what to do next.
6. Require the proof appropriate to the claim and refresh state before the next mutation.

Where declarations provide a list overload, preview the list from one shared snapshot and submit the returned impacts in one operation. Do not emulate this by repeatedly reconnecting, reselecting the project, or inventing a batch method. Single-item methods and list overloads are not universal; check the current declaration for the chosen operation.

For multi-step work that needs checkpoint-backed recovery, use `client.workflows.checkpointed()`. It is serial and exposes its actual step and recovery outcomes; it is not an atomic transaction across DaVinci Resolve operations.

## Handle durable operations safely

`wait()` and `subscribe()` poll locally. Their timeout or `AbortSignal` stops only the local wait or subscription; it does not cancel the server-side operation. Use `requestCancellation()` when cancellation is intended, then wait for a confirmed terminal state.

Retain `operation.ref` in memory and use `client.operations.reattach(operation.ref)` to preserve its action-specific result type. For recovery across a process restart, persist the opaque operation ID, validate it with `operationId()`, and reattach it; the result then requires runtime discriminator narrowing. Reattachment observes the existing operation and must not replay the mutation.

Retain the original idempotency key when retrying the same logical mutation after a lost response. Do not create a new key or repeat the call until the operation and live state have been inspected.

Terminal states are deliberately distinct: `succeeded`, `failed`, `cancelled`, `partially_applied`, `verification_failed`, and `recovery_failed`. Non-success terminals can still contain a partial semantic `result`, verification evidence, or recovery state. Inspect those fields before recovery. A thrown `CutAgentSdkError` exposes `error.failure`, including the stable `code`, `retrySafe`, optional `retrySafetyProof`, `possibleMutation`, `readbackRequired`, operation correlation, and `recoveryGuidance`. Retry only when the returned contract proves it safe. Read [errors-and-recovery.md](errors-and-recovery.md) for recovery decisions.

## Use typed actions sparingly

`client.actions` is the reviewed typed escape hatch for capabilities without a high-level domain object. Use `read()` for semantic reads and `start()` or `invoke()` according to the action's generated lifecycle contract. Mutation actions may require an idempotency key and return a durable handle. `client.actions.lowLevel.read()` is only for explicitly listed read-only actions without a semantic result projection.

In a standalone script, import exact action IDs and input/result types from `cutagent/actions`; do not invent action names, command strings, input fields, or result shapes. Capability presence in declarations does not prove that the connected platform, DaVinci Resolve edition, project storage, or runtime currently admits it. Treat the connected runtime's result as live truth and handle `CAPABILITY_UNAVAILABLE` without falling back to an untyped mutation.

Use [cli.md](cli.md) when an exact CutAgent CLI command is a better fit or when cross-interface reproduction will clarify a failure. Both interfaces reach the same protected execution foundation; direct CLI use is not a way around SDK targeting, authorization, or verification requirements.

## Match proof to the result

SDK verification proves only the modalities named in its `verification.evidence`. Structural readback does not prove visual quality; a rendered frame does not prove motion; one frame does not prove an animation; and process success does not prove audio quality. Use fresh structural reads, representative multi-frame exports, rendered-file inspection, or audition as the requested outcome requires. Read [checking-results.md](checking-results.md) before making completion claims.

Load domain guidance for the work itself: [projects-and-media.md](projects-and-media.md), [editing.md](editing.md), [captions.md](captions.md), [fusion/REFERENCE.md](fusion/REFERENCE.md), [color.md](color.md), [audio.md](audio.md), [multicam.md](multicam.md), or [rendering.md](rendering.md).
