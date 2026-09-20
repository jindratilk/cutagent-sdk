# Fusion scripting

Read this when translating FusionScript concepts into CutAgent SDK operations, inspecting tools and inputs, or deciding whether a requested raw script is executable through the public SDK.

## Use the exact object chain

Fusion's native scripting model is `timeline item -> composition -> tool -> input/output`. CutAgent preserves that targeting without exposing live native handles:

- Start from a durable timeline-item ID observed in `snapshot`. A snapshot-only ID or clip name is not a safe mutation target.
- DaVinci Resolve compositions with `timeline.fusion.forTimelineItem(itemId, snapshot.revision)`. Composition indexes are one-based and each returned reference carries its own revision and graph digest.
- Address tool instances and inputs by their observed names. A tool type such as `TextPlus` does not imply that its instance is named `Text1`, and an Inspector label does not necessarily equal the scripting input ID.
- Before another revision-bound Fusion mutation on this timeline, take a new snapshot and resolve only the composition references you still need. Never invent or copy a revision from another item.

Native Fusion distinguishes inputs from attributes. Inputs carry values or connections and can vary at composition-frame times; attributes describe object state and are not all writable. One input accepts at most one connected output, while an output may feed several inputs. Treat these facts as vocabulary for interpreting readback, not as permission to call native FusionScript directly.

## Inspect, then update through one native operation

This runner snippet uses the supplied `{sdk, client, project, timeline, snapshot}` variables. It finds one durable clip, resolves exactly one composition, confirms two Text+ tool instances and their real `StyledText` inputs, then submits both changes as one ordered native operation.

```ts
const clip = snapshot.videoTracks
  .flatMap((track) => track.clips)
  .find((candidate) => candidate.name === "Opening graphic");

if (!clip?.id) {
  throw new Error("Opening graphic has no durable timeline-item identity");
}
const itemId = clip.id;

const compositions = await timeline.fusion.forTimelineItem(
  itemId,
  snapshot.revision,
);
if (compositions.length !== 1) {
  throw new Error(`Expected one Fusion composition, found ${compositions.length}`);
}
const composition = compositions[0];

const toolRead = await client.actions.read(
  "cutagent.action.fusion.tool.list",
  {
    projectId: project.id,
    timelineId: timeline.id,
    timelineItemId: itemId,
    compositionIndex: composition.index,
  },
);

const desired = new Map([
  ["Title", "A clear idea"],
  ["Subtitle", "Built in Resolve"],
]);

const updates = await Promise.all(
  [...desired].map(async ([toolName, text]) => {
    const tool = toolRead.tools.find(
      (candidate) => candidate.name === toolName && candidate.type === "TextPlus",
    );
    if (!tool) throw new Error(`Missing TextPlus tool: ${toolName}`);

    const inputRead = await client.actions.read(
      "cutagent.action.fusion.tool.inputs",
      {
        projectId: project.id,
        timelineId: timeline.id,
        timelineItemId: itemId,
        compositionIndex: composition.index,
        toolName: tool.name,
      },
    );
    if (!inputRead.inputs.some((input) => input.id === "StyledText")) {
      throw new Error(`${tool.name} has no StyledText input`);
    }
    return {
      target: composition,
      toolName: tool.name,
      inputName: "StyledText",
      text,
    };
  }),
);

const operation = await timeline.fusion.setText(updates, {
  precondition: snapshot.revision,
  idempotencyKey: sdk.idempotencyKey(),
});
const terminal = await operation.wait();

if (terminal.status !== "succeeded") {
  throw new Error(`Fusion text update ended as ${terminal.status}`);
}
console.log(terminal.result.textUpdates);
```

`setText` accepts one update or a non-empty list. Prefer the list form when all targets come from the same observed timeline revision: it shares setup, preserves order, and returns one revision transition. Inspect every per-item result for plural operations that permit partial success; do not blindly retry the full list after an uncertain or partial outcome. See [errors and recovery](../errors-and-recovery.md).

## Choose the supported authoring surface

- Build or replace a complete typed graph with the registry-backed builder described in [graph basics](graph-basics.md). `composition.applyGraph(...)` replaces that exact composition graph; it does not append nodes to the existing graph.
- Publish and insert a caller-authored `.setting` through managed artifact custody as described in [setting files](setting-files.md).
- Use `timeline.fusion.replaceImages`, `setText`, or `updateNestedText` for their focused operations. Each accepts one item or a list; do not loop separate calls over targets observed at one revision.
- Load [animation](animation.md) for composition-frame timing, keyframes, modifiers, and expressions. Fusion composition frames are not timeline record frames; use [coordinates and time](coordinates-and-time.md) when translating between them.

Do not treat `advancedFusionRaw()` or `validateAdvancedFusionRawRequest()` as execution. They only validate a release-gated request description; neither lowers, dispatches, or mutates it. The public SDK currently has no general raw `fusion_script` executor. Do not bypass that boundary with native handles or private runtime routes.

## Registry and compatibility limits

Use the installed `sdk.FUSION_REGISTRY` and generated SDK declarations for exact node types, input IDs, output IDs, captured metadata, and provenance. The graph builder accepts only connection pairs with recorded native readback. Matching data-type labels do not prove compatibility, and differing labels do not prove incompatibility.

The current registry exposes no input marked `animatable: true`, so the typed graph builder's `.animate()` method has no currently admitted input. Use the supported `.setting` animation route rather than casting around this gate. Registry capture provenance is narrower than every supported DaVinci Resolve/platform combination; inspect the live capability and registry metadata instead of generalizing from one capture.

The semantic composition carrier is unavailable in a `plugin_managed` SDK distribution and fails before dispatch with `RUNTIME_UNAVAILABLE`. Select an available desktop-managed or standalone-local route rather than attempting to reconstruct native scripting access.

## Prove the claim you make

A successful graph apply proves exact structural readback and protected-state preservation. Its current `renderedReview`, `semanticReview`, and `temporalReview` fields may truthfully be `not_run`; process success and a graph digest do not prove appearance or motion. For a text update, confirm the returned update rows and revision transition, then refresh the affected timeline state before another revision-bound mutation.

Use [preview and debugging](preview-and-debugging.md) for rendered frames and temporal review. Inspect more than one frame when claiming animation, and inspect representative frames for Text+ font, glyph, wrapping, and placement claims.
