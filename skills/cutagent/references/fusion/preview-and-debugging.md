# Preview and debug Fusion

Fusion has several kinds of “preview,” and they prove different things. Use the cheapest check that can falsify the current hypothesis, then move toward pixels and time only when the claim requires them.

| Check | What it proves | What it does not prove |
| --- | --- | --- |
| `compile()` and `diagnoseFusionConnection()` | The request fits the installed registry and graph rules | DaVinci Resolve accepted it or produced an image |
| `composition.previewApply(graph)` | The exact target, replacement scope, precondition, graph digest, and protected state | Any live mutation or rendered result |
| Successful `applyGraph()` terminal | The graph matched exact structural readback and protected state was preserved | Typography, framing, visible pixels, or motion quality |
| One exported timeline frame | Final timeline appearance at one record position | Animation, interpolation, playback, or audio |
| Sampled frames, contact sheet, or preview export | Change across selected timeline positions | Full-rate playback or audiovisual delivery quality |

An upstream node shown in a Fusion viewer is also not the final output. DaVinci Resolve viewers can display any node. Compare the suspect node with the final `MediaOut`, or inspect an exported timeline frame, before concluding that the composition output is correct.

## Inspect the replacement without changing DaVinci Resolve

The runner supplies the connected objects. This script resolves one exact timeline item and composition, compiles a small graph offline, and prints the live impact contract. It does not call `applyGraph()` and does not mutate DaVinci Resolve.

```js
export default async function ({ sdk, client, project, timeline, snapshot, progress }) {
  if (snapshot.projectId !== project.id || snapshot.timelineId !== timeline.id) {
    throw new Error("The supplied snapshot does not belong to the supplied project and timeline");
  }

  const clips = snapshot.videoTracks
    .flatMap((track) => track.clips)
    .filter((clip) => clip.name === "Launch Title" && clip.id !== null);

  if (clips.length !== 1) {
    throw new Error(`Expected one durable Launch Title item; found ${clips.length}`);
  }

  progress("Reading the exact Fusion composition");
  const compositions = await timeline.fusion.forTimelineItem(
    clips[0].id,
    snapshot.revision,
  );
  const composition = compositions.find((candidate) => candidate.index === 1);
  if (!composition) throw new Error("Fusion composition index 1 was not found");

  const graph = sdk.fusionGraph()
    .node("title", "TextPlus", { StyledText: "Launch day", Size: 0.08 })
    .node("output", "MediaOut")
    .connect("title", "Output", "output", "Input")
    .output("output")
    .compile();

  const impact = composition.previewApply(graph);
  console.log(JSON.stringify({
    target: {
      projectId: impact.target.projectId,
      timelineId: impact.target.timelineId,
      timelineItemId: impact.target.timelineItemId,
      compositionId: impact.target.id,
      compositionIndex: impact.target.index,
      compositionName: impact.target.name,
    },
    precondition: impact.precondition,
    graphDigest: impact.graphDigest,
    intendedEffects: impact.intendedEffects,
    protectedState: impact.protectedState,
    minimumEvidence: impact.minimumEvidence,
  }, null, 2));

  // `client` remains runner-owned; do not reconnect or close it here.
}
```

Run it with:

```sh
cutagent-sdk --title "Preview Launch Title Fusion replacement" preview.mjs
```

Treat the printed target and `replace_*` effects as a review gate. `applyGraph()` replaces the complete graph in that exact composition; it is not an incremental patch. Follow [graph basics](graph-basics.md) for the mutation and terminal-handling pattern.

## Debug graph construction before transport

`FusionGraphValidationError` means the request failed before any transport or DaVinci Resolve mutation. Fix the graph instead of re-reading live state. Common causes are an unknown node or input, an unverified connection, two sources occupying one input, a cycle, a missing `MediaOut`, a disconnected branch, or invalid literal data.

When a connection is rejected, inspect the exact pair:

```js
const connection = sdk.diagnoseFusionConnection(
  { node: "TextPlus", port: "Output" },
  { node: "MediaOut", port: "Input" },
);

console.log(connection);
if (!connection.acceptedByGraphBuilder) {
  throw new Error(`Connection evidence is ${connection.status}`);
}
```

Matching data-type labels are only a clue. `typeLabelRelation: "same"` is not compatibility evidence unless `status` is `verified_pair`. Do not cast around the registry gate.

The current checked-in registry exposes no input with observed animation support. A numeric input is therefore not evidence that `.animate()` is available. Use the supported `.setting` or scripting route when keyframes are required; see [animation](animation.md).

## Interpret the live result accurately

After `applyGraph()`, branch on the typed terminal state before doing more work:

- `succeeded`: require passed structural verification, matching applied/readback graph digests, and `protectedStatePreserved: true`.
- `failed` or `cancelled`: inspect `possibleMutation`, `readbackRequired`, retry safety, recovery, and any attached result.
- `partially_applied`, `verification_failed`, or `recovery_failed`: assume the live state may differ from the original snapshot. Reconcile the exact composition before another mutation.

A local `wait()` timeout or abort stops polling, not the server action. Keep the operation ID and original idempotency key and reattach or refresh the operation. Do not submit a replacement mutation merely because the local wait ended.

The current graph-apply implementation returns exact nodes, connections, animated-input count, and graph digests, but its visual fields remain unreviewed: `renderedEvidence` is empty and rendered, semantic, and temporal review outcomes are `not_run`. Structural success must therefore be reported as structural success, not as “the title looks correct.”

See [check results and evidence](../checking-results.md) for the shared operation rules.

## Collect final-pixel and temporal proof

Choose timeline-record positions after mapping the composition frames you care about; do not pass a Fusion-local frame to a timeline command. See [coordinates and time](coordinates-and-time.md).

For a static claim, export one representative final timeline frame:

```sh
mkdir -p "$PWD/fusion-proof"
cutagent timeline frame-export \
  --at 01:00:05:12 \
  --output "$PWD/fusion-proof/final.png"
```

Replace the example timecode with a valid record position from the active timeline. The output parent must already exist. Open the image and inspect the final composite, not merely the file’s existence.

For motion, sample the beginning, middle, end, and any extrema or boundary frames. A contact sheet makes omissions and discontinuities easy to spot:

```sh
cutagent timeline frame-export batch \
  --frames "01:00:05:00,01:00:05:12,01:00:06:00" \
  --out-dir "$PWD/fusion-proof/frames" \
  --prefix title \
  --contact-sheet "$PWD/fusion-proof/contact-sheet.png"
```

Use `cutagent timeline preview-export` when ordered sampled playback is more informative. It creates a silent slideshow from stills, not a real-time audiovisual render, so it cannot prove smooth full-rate timing, audio sync, or delivery readiness. If the response reports offline media, resolve that before judging the effect.

Fusion’s render range controls interactive playback, caches, and previews. Frames outside it may not play even when they can be scrubbed. A blank or frozen preview can therefore be a range problem rather than a graph problem. Compare composition/global/render bounds with the timeline positions you sampled.

`cutagent fusion comp render --wait` renders a composition range and is useful for configured Saver output. It is not the right tool for one verification still, and its frame range is composition-local rather than timeline-record time.

## Isolate `.setting` and scripting failures

For a `.setting` file, separate static parsing from live import and final output:

```sh
cutagent fusion setting inspect "$PWD/title.setting"
cutagent clip fusion list "Launch Title" --track 2 --record-frame 150
cutagent clip fusion export 1 "$PWD/fusion-proof/readback.setting" \
  --clip "Launch Title" --track 2 --record-frame 150
```

Replace the example track and record frame with selectors that identify the intended item. Static inspection can find malformed or unsupported-looking content without changing DaVinci Resolve, but it cannot prove that DaVinci Resolve imports the file or that `MediaOut` renders visible pixels. After a live import, list compositions again, export the exact resulting composition by its one-based index, and compare the readback with the intended setting. Then inspect final timeline pixels.

For raw FusionScript, read the exact tool list and exact input at an explicit composition time. Omitting time is only safe for an unanimated input. Useful native inspection concepts include `Composition.GetToolList()`, `Operator.GetInput(id, time)`, render/global attributes, and whether the composition is currently rendering. Use [scripting](scripting.md) for current CutAgent routes and safety boundaries.

## Symptom triage

| Symptom | First useful check |
| --- | --- |
| Graph will not compile | Read the validation error; diagnose the exact rejected connection |
| Dispatch fails before an operation exists | Check runtime/capability availability and the exact composition revision |
| Operation succeeds but output is blank | Inspect final `MediaOut`, render range, generator/media availability, and an exported timeline frame |
| Intermediate node looks correct but timeline does not | Compare that node with `MediaOut`; inspect the path and final timeline pixels |
| One frame is right but animation is wrong | Check keyframe/readback time domains, then sample multiple record positions |
| `.setting` inspects but will not import | Treat inspection as syntax evidence only; inspect unsupported tools/inputs and live import diagnostics |
| Retry is tempting after timeout or verification failure | Reattach the operation or read back the exact composition before any new write |

Keep reports explicit: state what was compiled, what DaVinci Resolve structurally read back, which final frames were visually reviewed, which time span was sampled, and what remains unproved.
