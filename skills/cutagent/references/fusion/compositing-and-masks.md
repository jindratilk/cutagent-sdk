# Fusion compositing and masks

Use this reference for 2D layer order, alpha, mattes, and masks. A branch changes the picture only when it reaches the composition's `MediaOut`; attach each mask to the node whose operation it should limit.

## Build the image path deliberately

A `Merge` combines one background and one foreground. The background defines the output frame, the foreground is composited over it, and `EffectMask` limits the merge operation. Keep those roles explicit:

```text
base image ───────────────→ Merge.Background
foreground with alpha ───→ Merge.Foreground ─→ Merge.Output ─→ MediaOut.Input
optional mask ────────────→ Merge.EffectMask
```

Attach a mask earlier when it owns a source shape or a single effect. For example, `EllipseMask.Mask → Background.EffectMask` turns a Background into an elliptical element before that element enters a Merge. Attach the same mask to `Merge.EffectMask` only when the intended result is to limit the complete foreground-over-background operation.

Do not confuse image alpha with an effect mask. Foreground alpha participates in the normal over composite; an `EffectMask` limits the node receiving it. A transparent generator canvas uses `Background.TopLeftAlpha = 0`, while an opaque shape branch normally uses alpha `1`. For alpha-channel extraction, matte replacement, multiple mask shapes, or keying, use nodes and connections that the current registry actually exposes; do not approximate them with unrelated ports.

## Author the supported masked composite

This runner-context example replaces one exact composition with a transparent canvas and a soft elliptical foreground. It reuses the supplied `sdk`, `timeline`, and `snapshot`; it does not reconnect or repeat runner setup.

```js
export default async function ({ sdk, timeline, snapshot, progress }) {
  const matches = snapshot.videoTrack(1).clips.filter(
    (clip) => clip.name === "Graphic holder" && clip.id !== null,
  );
  if (matches.length !== 1) {
    throw new Error(`Expected one durable Graphic holder on V1; found ${matches.length}.`);
  }

  const compositions = await timeline.fusion.forTimelineItem(
    matches[0].id,
    snapshot.revision,
  );
  if (compositions.length !== 1) {
    throw new Error(`Expected one Fusion composition; found ${compositions.length}.`);
  }
  const composition = compositions[0];

  const graph = sdk.fusionGraph()
    .node("canvas", "Background", { TopLeftAlpha: 0 })
    .node("shape", "Background", {
      TopLeftRed: 0.95,
      TopLeftGreen: 0.24,
      TopLeftBlue: 0.12,
      TopLeftAlpha: 1,
    })
    .node("shapeMask", "EllipseMask", {
      Center: [0.5, 0.5],
      Width: 0.58,
      Height: 0.26,
      SoftEdge: 0.015,
    })
    .node("merge", "Merge")
    .node("out", "MediaOut")
    .connect("shapeMask", "Mask", "shape", "EffectMask")
    .connect("canvas", "Output", "merge", "Background")
    .connect("shape", "Output", "merge", "Foreground")
    .connect("merge", "Output", "out", "Input")
    .output("out")
    .compile();

  console.log(composition.previewApply(graph));
  progress("Applying the masked Fusion composite");
  const operation = await composition.applyGraph(graph, {
    precondition: composition.revision,
    idempotencyKey: sdk.idempotencyKey(),
  });
  const terminal = await operation.wait();
  if (terminal.status !== "succeeded") throw terminal.failure;
  if (terminal.verification.outcome !== "passed") {
    throw new Error(`Fusion verification was ${terminal.verification.outcome}.`);
  }

  const after = await timeline.snapshot();
  const [readback] = await timeline.fusion.forTimelineItem(matches[0].id, after.revision);
  if (!readback) throw new Error("The applied composition is absent from readback.");
  console.log({ operationId: operation.operationId, graphDigest: readback.graphDigest });
}
```

`compile()` performs local schema, input, connection, cycle, output-path, and registry-digest checks; it does not mutate DaVinci Resolve. `previewApply()` describes a full graph replacement, including protected surrounding state. `applyGraph()` requires the exact observed composition revision and returns a durable operation. Do not use it as an append-node API or apply it to a composition whose existing branches must survive unless the replacement graph deliberately contains them.

## Respect the current typed boundary

The current generated registry exposes `Background`, `EllipseMask`, `Merge`, `MediaOut`, `TextPlus`, `Transform`, and a small 3D set. It does not expose `MediaIn`, `RectangleMask`, `PolylineMask`, `Bitmap`, `MatteControl`, or `ChannelBooleans`, and it contains no input currently marked animatable. Consequently:

- Use the typed graph above for a graph composed entirely from registered nodes and exact registered connections.
- Do not replace a live-footage composition with this graph: without `MediaIn`, the typed request cannot preserve that image branch.
- Use [Setting files](setting-files.md) for a graph requiring other native nodes, freeform masks, mask combinations, or existing media inputs. Use [Animation](animation.md) for animated mask geometry and [Tracking](tracking.md) for a mask driven by tracked motion.
- Consult the installed `FUSION_REGISTRY` or `diagnoseFusionConnection()` when a port pair is uncertain. Equal captured data-type labels do not prove a connection, and a verified native pair may have different labels.

Registry activation is evidence-bound. The bundled registry was captured on one macOS arm64 DaVinci Resolve Studio 21.0.0.47 environment; it is not proof of Windows, DaVinci Resolve Free, or another DaVinci Resolve version. Let the connected runtime fail closed when the active environment is unsupported instead of casting around the builder or inventing a fallback mutation.

## Check the result at the claimed level

Graph apply currently requires and reports structural readback and protected-state verification. Its result can truthfully contain no rendered evidence, with rendered, semantic, and temporal review marked `not_run`. That proves the accepted graph structure, not the intended pixels.

For a static mask, inspect a representative frame over a contrasting background and check the boundary, softness, alpha, and foreground/background order. For an animated or tracked mask, inspect several meaningful times or a temporal preview; one frame cannot prove motion or tracking. Read [Preview and debugging](preview-and-debugging.md) for those checks and [Coordinates and time](coordinates-and-time.md) before interpreting normalized mask geometry or Fusion frame values.
