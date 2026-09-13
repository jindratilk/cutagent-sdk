# Fusion text and layout

Read this when creating or changing Text+, choosing a layout mode, handling fonts or glyphs, or diagnosing text that is clipped, missing, misaligned, or visually different on another machine.

Keep text content, styling, layout, and animation as separate decisions. Inspect the exact composition and text owner before changing any of them.

## Choose the mutation boundary

- For wording changes in a known existing composition, use `timeline.fusion.setText()` with the exact composition, tool name, and input name. Pass one update or an ordered list to the same operation.
- For a template that deliberately exposes header/body fields, use `timeline.fusion.updateNestedText()`. Inspect every returned item because a plural operation can report mixed success.
- For a new or fully owned dedicated composition, build the complete graph with `fusionGraph()` and apply it through that composition's `applyGraph()` method.
- For reusable typography with character-level styling, modifiers, or a text-box setup not represented by the typed graph, publish a reviewed `.setting` with `client.artifacts.publishFusionSetting()` and insert it with `timeline.fusion.insertSettings()`.

`applyGraph()` replaces the complete target composition graph. Do not use a title-only graph as a patch for a composition whose existing MediaIn, masks, effects, or other branches must survive.

## Model Text+ correctly

`StyledText` is the usual Text+ string input. It may instead be driven by a modifier such as character-level styling. When an input has a source connection, change the text at the actual owning tool/input rather than writing an unused literal under the connection.

Treat these controls independently:

- `Font` selects a family; `Style` selects one of that family's installed faces. Do not infer a style name from a numeric weight.
- `Size` controls type scale. Long copy, multiline copy, fallback glyphs, and different font metrics can all change fit.
- `Center` positions the layout anchor in normalized image coordinates. `{0.5, 0.5}` is the image center; positive Y runs upward in the viewer coordinate domain.
- Horizontal and vertical justification arrange lines inside the layout. Anchor/alignment controls determine how the resulting text block grows around its position. Moving `Center` is not the same as changing justification.
- Point layout grows from an anchor and suits short display text. Text+ Frame layout supplies a rectangle for alignment; its current controls also expose text-box wrapping and clipping. MultiText separately names its bounded mode Text Box. Do not guess a numeric layout enum in serialized source—derive it from the installed registry or an exported known-good setting.
- `UseFrameFormatSettings` delegates image dimensions to the composition format. Explicit `Width` and `Height` alone do not override that delegation.

Lay out the longest expected copy at its most visible frame before adding animation. Preserve a deliberate safe margin, and test the real delivery aspect ratio; equal normalized width and height do not describe equal pixel dimensions in a widescreen frame.

## Build a typed title graph

This runner-context snippet only compiles a graph request. It deliberately leaves `Font` and `Style` unset so the composition does not depend on an unverified installed face.

```js
const titleGraph = sdk.fusionGraph()
  .node("title", "TextPlus", {
    StyledText: "A precise title",
    Size: 0.075,
    Center: [0.5, 0.5],
    Red1: 0.96,
    Green1: 0.98,
    Blue1: 1,
    Alpha1: 1,
  })
  .node("output", "MediaOut")
  .connect("title", "Output", "output", "Input")
  .output("output")
  .compile();
```

Use identifiers from the installed `FUSION_REGISTRY`; Inspector labels are not graph IDs. Compilation proves schema, input-type, output-path, and registry-verified connection constraints. It does not prove font availability, line fit, rendered appearance, or motion.

Before applying this graph, resolve one exact dedicated composition and preview the replacement:

```js
const impact = composition.previewApply(titleGraph);
const operation = await composition.applyGraph(titleGraph, {
  precondition: composition.revision,
  idempotencyKey,
});
```

This is a snippet given existing `composition` and `idempotencyKey` variables. Read [SDK usage](../sdk.md) for connection, operation waiting, and terminal-result handling.

## Change one exact existing text input

The `cutagent-sdk` runner supplies the values used below. This module updates a uniquely named timeline item whose graph is already known to contain `Title.StyledText`. Replace those two graph identifiers only after inspecting the target composition. It rejects ambiguous names and items without durable identity.

```js
export default async function ({ sdk, timeline, snapshot, progress }) {
  const matches = snapshot.videoTracks
    .flatMap((track) => track.clips)
    .filter((clip) => clip.name === "Lower third");

  const item = matches[0];
  if (matches.length !== 1 || !item || item.id === null) {
    throw new Error("Expected one durable timeline item named Lower third");
  }

  const compositions = await timeline.fusion.forTimelineItem(
    item.id,
    snapshot.revision,
  );
  const composition = compositions[0];
  if (compositions.length !== 1 || !composition) {
    throw new Error("Expected exactly one Fusion composition on Lower third");
  }

  progress("Updating the Lower third text");
  const operation = await timeline.fusion.setText(
    {
      target: composition,
      toolName: "Title",
      inputName: "StyledText",
      text: "A precise lower third",
    },
    {
      precondition: snapshot.revision,
      idempotencyKey: sdk.idempotencyKey(),
    },
  );

  const terminal = await operation.wait();
  if (terminal.status !== "succeeded" || terminal.result === undefined) {
    throw new Error(`Text update ended as ${terminal.status}`);
  }

  const update = terminal.result.textUpdates.updates[0];
  if (
    update?.verified !== true ||
    update.toolName !== "Title" ||
    update.inputName !== "StyledText" ||
    update.text !== "A precise lower third" ||
    terminal.result.textUpdates.revision.changed !== true
  ) {
    throw new Error("Text update readback did not match the request");
  }

  console.log(update);
}
```

The operation result verifies the requested tool/input/text correlation and reports whether the composition revision changed. It does not prove that the title is legible or inside frame.

For several text nodes observed at the same timeline revision, pass their updates as one array to `setText()`. Do not repeat setup and dispatch serial mutations unless later updates genuinely depend on earlier readback.

## Character-level styling and glyphs

Character-level styling is structured text, not Markdown stored in `StyledText`. Preserve the modifier and its range data when changing copy. If changed string length invalidates styling ranges, rebuild or deliberately remove those ranges; do not assume they retarget semantically.

DaVinci Resolve 21 expands Text+ font, color-font, bitmap-font, and emoji support, but a font can still contain only a subset of the requested glyphs. A regular font may fall back to the configured emoji font; an emoji-only font does not provide Latin letters in the reverse direction. Verify the actual font family, face, glyph coverage, and fallback on every delivery platform.

The current typed public graph registry is the authority for builder support. Do not infer that a GUI-visible Text+ or MultiText control is accepted by `fusionGraph()`. Use an exported known-good `.setting` or the exact supported interface when the registry does not contain the required node, input, data type, or connection.

## Verify layout and appearance

After a text or layout change:

1. Confirm the exact timeline item, composition index, text owner, input name, resulting text, and output path by native readback.
2. Inspect a full-resolution frame at the principal reading state. Check margins, line breaks, alignment, contrast, clipping, font substitution, missing glyphs, and transparent edges.
3. Test the longest realistic copy and every required script, emoji, or special character. A short Latin placeholder is not a font or overflow test.
4. If any text, layout, reveal, or transform is animated, inspect multiple meaningful frames and a short motion preview. One frame cannot prove temporal behavior; read [Fusion animation](./animation.md).
5. Keep structural, visual, and temporal outcomes separate. A successful operation or changed graph digest is not a visual review.

## Recurring failures

- **Text is unchanged:** inspect whether `StyledText` is connected to a modifier and update the real owner.
- **Text is missing:** check the output path, enabled shading element, alpha, clip bounds, font face, and glyph coverage before changing position.
- **Only one line moves as expected:** distinguish line justification from the block anchor and `Center`.
- **Paragraph overflows:** use a verified Text Box layout and wrapping setup, then test the longest copy; shrinking type is not the only remedy.
- **Layout differs by resolution:** reconcile composition format, aspect ratio, normalized coordinates, and any explicit generator dimensions.
- **Graph compilation rejects animation:** the builder accepts animation only for inputs whose current live registry marks `animatable: true`. Do not bypass that evidence with an invented cast; use the supported route described in [Fusion animation](./animation.md).
- **A batch partly fails:** inspect the terminal status and per-item results before retrying. Reuse an idempotency key only for the identical semantic request.

Keep Fusion frame time distinct from timeline record time and source time when choosing review frames; see [timing and targets](../timing-and-targets.md).
