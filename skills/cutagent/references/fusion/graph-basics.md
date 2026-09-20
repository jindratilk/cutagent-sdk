# Fusion graph basics

Use the typed graph builder when you need to replace one existing Fusion composition with a graph made entirely from the installed verified registry. The graph is a directed flow: a tool's output feeds another tool's input, and every authored branch must reach a declared `MediaOut`.

`applyGraph()` replaces the complete graph of one exact composition. It is not an incremental node-add operation. Do not use a generator-only graph on a footage composition and expect the source image to survive.

## Build from verified facts

Start with `sdk.fusionGraph()`. Chain the returned immutable builder through:

- `node(instanceName, nodeType, initialInputs?)` to add a uniquely named tool;
- `set(instanceName, inputId, value)` to change a literal input;
- `connect(sourceName, outputId, targetName, inputId)` to add an exact registry-verified connection;
- `output(instanceName)` to declare a `MediaOut` result;
- `compile()` to validate and produce a pure `FusionGraphRequest` without dispatching a mutation.

Read `sdk.FUSION_REGISTRY` or the installed declarations when choosing node, input, and output identifiers. Do not infer that two ports connect merely because their captured data-type labels match. Use `sdk.diagnoseFusionConnection()` for a read-only explanation of whether the exact pair is verified.

Compilation rejects unknown nodes or inputs, wrong literal types and observed bounds, duplicate node names, two sources connected to one input, unverified connections, cycles, missing required inputs, non-`MediaOut` outputs, and nodes with no path to an output.

The builder is immutable. Keep chaining or assign each returned builder:

```js
// Wrong: node() returns a new builder; this leaves `graph` empty.
const graph = sdk.fusionGraph();
graph.node("title", "TextPlus", { StyledText: "Launch day" });
```

## Replace one title graph

The `cutagent-sdk` runner supplies `sdk`, `client`, `project`, `timeline`, and `snapshot`. This executable module selects one uniquely named timeline item, requires a durable item identity and exactly one Fusion composition, compiles a title graph, previews its complete impact, then waits for verified structural readback.

```js
export default async function ({ sdk, timeline, snapshot, progress }) {
  const candidates = snapshot.videoTracks
    .flatMap((track) => track.clips)
    .filter((clip) => clip.name === "Launch Title");

  if (candidates.length !== 1) {
    throw new Error(`Expected one Launch Title item; found ${candidates.length}`);
  }
  const targetClip = candidates[0];
  if (!targetClip || targetClip.id === null) {
    throw new Error("The target has no durable timeline-item identity");
  }

  const compositions = await timeline.fusion.forTimelineItem(
    targetClip.id,
    snapshot.revision,
  );
  const composition = compositions.at(0);
  if (compositions.length !== 1 || !composition) {
    throw new Error(`Expected one Fusion composition; found ${compositions.length}`);
  }

  const graph = sdk.fusionGraph()
    .node("title", "TextPlus", {
      StyledText: "Launch day",
      Size: 0.08,
    })
    .node("output", "MediaOut")
    .connect("title", "Output", "output", "Input")
    .output("output")
    .compile();

  const impact = composition.previewApply(graph);
  console.log({
    target: impact.target.name,
    effects: impact.intendedEffects,
    protectedState: impact.protectedState,
  });

  progress("Replacing the exact Fusion title graph");
  const operation = await composition.applyGraph(graph, {
    precondition: composition.revision,
    idempotencyKey: sdk.idempotencyKey(),
  });
  const terminal = await operation.wait();

  if (terminal.status !== "succeeded") {
    console.error({
      status: terminal.status,
      code: terminal.failure.code,
      possibleMutation: terminal.failure.possibleMutation,
      recovery: terminal.failure.recoveryGuidance,
    });
    throw terminal.failure;
  }
  if (
    terminal.verification.outcome !== "passed" ||
    terminal.result.protectedStatePreserved !== true ||
    terminal.result.readback.graphDigest !== terminal.result.appliedGraphDigest
  ) {
    throw new Error("Fusion graph structural verification did not pass");
  }

  console.log({
    graphDigest: terminal.result.readback.graphDigest,
    nodes: terminal.result.readback.nodes,
    connections: terminal.result.readback.connections,
  });
}
```

Run it with a descriptive activity title:

```sh
cutagent-sdk --title "Replace Launch Title Fusion graph" graph.mjs
```

Use a new snapshot and reacquire the composition after any successful change; its timeline and composition revisions are now stale. Reuse an idempotency key only for the identical semantic request. After an uncertain, partial, verification-failed, or recovery-failed terminal, inspect the returned `possibleMutation`, `verification`, and `recovery` fields and re-read the current composition before deciding whether another mutation is safe.

## Current boundaries

- The typed graph builder accepts only nodes, literal inputs, and exact connection pairs present in its generated registry. The current registry is deliberately smaller than Fusion's full node catalog.
- The current registry has no `MediaIn`, so the typed builder cannot yet express an inline source-footage graph. Use this example for a title or generator composition, not as a footage-preserving effect chain.
- No current registry input is marked as proven animatable. Do not infer `.animate()` support from an input merely appearing numeric; read [animation](animation.md) for an activated animation route.
- Typed graph inspection and application currently require an activated desktop-managed runtime. Plugin-managed connections fail before dispatch with `RUNTIME_UNAVAILABLE`.
- Registry activation records current node and connection evidence; it does not by itself prove graph mutation support across every platform, DaVinci Resolve edition, or transport. Treat the connected runtime's capability and operation result as authoritative.
- Successful graph application proves exact structural readback and preservation of the protected state reported in the result. It does not prove typography, framing, visual quality, or motion. Review representative rendered frames, and use a temporal preview for animation claims; see [preview and debugging](preview-and-debugging.md).

For coordinate and composition-frame semantics, read [coordinates and time](coordinates-and-time.md). For `.setting` authoring or FusionScript rather than the typed builder, read [setting files](setting-files.md) or [scripting](scripting.md).
