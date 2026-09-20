# Fusion `.setting` files

A `.setting` file is a declarative Fusion table that serializes tools, inputs, connections, modifiers, and flow layout. Treat it as native graph source, not JSON and not a general Lua script. Use the typed graph builder when its installed registry covers the graph; use a `.setting` when you need reviewed native serialization that the builder does not express. Managed `.setting` publication never authorizes FusionScript execution.

Use [Graph basics](graph-basics.md) for node and port decisions, [Coordinates and time](coordinates-and-time.md) for image and frame domains, and [Animation](animation.md) for modifiers and splines.

## Author the table

Put exactly one `Tools` collection in the top-level table. Use `ordered()` so tool order remains deterministic. Each key is an instance name and each constructor is the native tool type:

```lua
{
    Tools = ordered() {
        Canvas = Background {
            Inputs = {
                TopLeftRed = Input { Value = 0.04, },
                TopLeftGreen = Input { Value = 0.06, },
                TopLeftBlue = Input { Value = 0.10, },
                TopLeftAlpha = Input { Value = 1, },
            },
            ViewInfo = OperatorInfo { Pos = { 0, 0 } },
        },
        MediaOut1 = MediaOut {
            Inputs = {
                Index = Input { Value = "0", },
                Input = Input { SourceOp = "Canvas", Source = "Output", },
            },
            ViewInfo = OperatorInfo { Pos = { 220, 0 } },
        },
    },
}
```

`Canvas` and `MediaOut1` are instance names. `Background` and `MediaOut` are tool types. Input keys such as `TopLeftRed` are native input IDs, not translated Inspector labels. A connection names both the source instance (`SourceOp`) and its output (`Source`). Give every visible flow tool a distinct `ViewInfo` position; those coordinates affect node-editor layout, not the rendered image.

Use either `Value` or a source connection for one input. Keep every `SourceOp` resolvable, every instance name unique, and every visible branch connected to the intended `MediaOut`. Escape authored strings as Fusion table strings; do not interpolate unescaped user text into source. For Text+, font discovery, glyph coverage, and layout, read [Text and layout](text-and-layout.md).

## Keep time and assets portable

Keyframe and modifier times inside the document are Fusion composition frames. Timeline placement is a separate absolute record-frame domain, and the holder duration does not automatically retime fixed keyframes. Use duration-aware modifiers for templates intended to adapt to different edit lengths; otherwise author against the intended composition range and verify the actual duration. Do not convert timeline start timecode into Fusion keyframe numbers. See [Coordinates and time](coordinates-and-time.md).

Avoid machine-specific paths. Fusion's `Setting:` path map resolves beside a loaded `.setting` file and is useful for packaged templates with adjacent images, LUTs, or 3D assets. `client.artifacts.publishFusionSetting()` publishes only the setting document, not a sibling directory. Use `imageArtifactId` for a supported image placeholder, or follow [Templates](templates.md) when the deliverable needs bundled assets or installation in DaVinci Resolve's Effects Library.

## Inspect source before publication

The SDK publication call checks managed-ingress size and returns a digest receipt; it does not statically validate graph syntax. Use the current public CLI for an offline structural pass when authoring or revising source:

```sh
cutagent -j fusion setting validate ./lower-third.setting
cutagent -j fusion setting summary ./lower-third.setting --connections --animated
```

Static validation does not contact DaVinci Resolve and cannot prove that installed tools, fonts, media, or pixels will work. The optional `--runtime` validator creates a scratch timeline mutation; use it only when that separate native import test is warranted. Read the exact current command card before adding runtime options.

## Publish and insert with the SDK runner

The runner already supplies `sdk`, `client`, `timeline`, and the initial `snapshot`. The following module reads a setting placed beside the module, places it 48 frames after the observed timeline start, waits for the durable terminal, and refreshes the timeline state:

```js
import {readFile} from "node:fs/promises";

export default async function insertSetting({sdk, client, timeline, snapshot, progress}) {
  const settingUrl = new URL("./lower-third.setting", import.meta.url);
  const source = await readFile(settingUrl);
  const receipt = await client.artifacts.publishFusionSetting(source);
  const at = sdk.timelineRecordOffset(snapshot, sdk.frames(48));
  const targetTrack = snapshot.videoTrack(2);

  progress("Inserting the Fusion setting");
  const operation = await timeline.fusion.insertSettings(
    {
      settingArtifactId: receipt.artifactId,
      clipName: "Lower third",
      recordPosition: at,
      clipDuration: sdk.duration(sdk.frames(96)),
      videoTrackIndex: targetTrack.index,
    },
    {
      precondition: snapshot.revision,
      idempotencyKey: sdk.idempotencyKey(),
    },
  );

  const terminal = await operation.wait();
  if (terminal.status !== "succeeded") {
    console.error({
      operationId: operation.operationId,
      status: terminal.status,
      possibleMutation: terminal.possibleMutation,
      result: "result" in terminal ? terminal.result : undefined,
      recovery: "recovery" in terminal ? terminal.recovery : undefined,
    });
    throw new Error(`Fusion insertion ended as ${terminal.status}`);
  }
  if (
    terminal.verification.outcome !== "passed" ||
    terminal.verification.protectedStatePreserved === false
  ) {
    throw new Error(`Fusion insertion verification was ${terminal.verification.outcome}`);
  }

  const after = await timeline.snapshot();
  console.log({receipt, inserted: terminal.result.items, revision: after.revision});
}
```

Run it as:

```sh
cutagent-sdk --title "Insert lower third" insert-setting.mjs
```

Choose the target track and confirm the complete destination range is available before dispatch. `timelineRecordOffset(snapshot, frames)` preserves a nonzero timeline start; `timelineRecordPosition(frames(48), snapshot.frameRate)` would mean absolute record frame 48 instead.

`insertSettings()` accepts one insertion or an ordered array of 1–100 insertions. When several settings share the same observed revision, publish their sources and pass the complete ordered array once so CutAgent can use one operation and one verification boundary. Do not serialize repeated setup and single-item calls.

Optional per-item fields are `text`, `imageArtifactId`, `position`, `styleMarkdown`, and `boldStyle`. They act only where the imported document contains the corresponding supported placeholder. The insertion result does not report those substitutions, so do not infer that they applied from placement success.

## Verify only what the evidence proves

A successful insertion result identifies each new timeline item and verifies its requested record position, frame duration, video track, optional clip name, revision transition, and preservation of pre-existing timeline items. It does not prove the complete imported graph, installed dependencies, text/image substitutions, font rendering, appearance, or motion.

Use the returned `timelineItemId` and fresh revision for targeted composition readback. Inspect representative rendered frames for appearance; inspect more than one in-range frame or a temporal preview for animation. Follow [Preview and debugging](preview-and-debugging.md) for graph and visual checks and [Checking results](../checking-results.md) for terminal and recovery interpretation. If a non-success terminal reports possible or partial mutation, inspect its attached result and recovery state before any retry.

For an existing composition, do not use insertion as a replacement operation. Use the exact composition APIs described in [Scripting](scripting.md) or the typed graph replacement path in [Graph basics](graph-basics.md), according to the change required.
