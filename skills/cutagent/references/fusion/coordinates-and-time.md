# Fusion coordinates and time

Read this when placing Fusion elements, converting pixel measurements, choosing a keyframe frame, or translating between a timeline item and its composition.

## Keep the domains separate

| Value | Meaning |
| --- | --- |
| Fusion image point | A tool-input value such as `Center`. The graph builder represents an observed `Point` or `Point2D` as `[x, y]`. |
| Flow position | The node's location in the Fusion Flow editor. It affects graph layout, not the rendered image. |
| Timeline record position | A location on the edit timeline. The timeline can start at a nonzero frame or timecode. |
| Source position | A location in the clip's source media. Trims and retiming can make this differ from record time. |
| Fusion composition frame | The frame used to evaluate a composition input or animation. `fusionFrame(n)` brands this domain; it does not convert from record or source time. |

Never pass a timeline record frame or source frame to `fusionFrame()` merely because all three are numbers. Do not add the timeline start timecode to a Fusion frame. DaVinci Resolve the exact timeline item and composition first, then use the time domain required by the selected SDK operation. See [timing and targets](../timing-and-targets.md) for record and source value types.

## Place image-space points

For ordinary 2D position controls, Fusion uses resolution-independent coordinates with the lower-left at `[0, 0]`, the upper-right at `[1, 1]`, and the image center at `[0.5, 0.5]`. Convert measurements taken from a top-left pixel origin before supplying them:

```ts
// Runner snippet: sdk is already supplied.
function pointFromTopLeftPixels(
  x: number,
  y: number,
  width: number,
  height: number,
): [number, number] {
  if (width <= 0 || height <= 0) throw new RangeError("Image dimensions must be positive.");
  return [x / width, 1 - y / height];
}

const titleCenter = pointFromTopLeftPixels(1536, 216, 1920, 1080);

const graph = sdk.fusionGraph()
  .node("title", "TextPlus", {
    StyledText: "North by northwest",
    Center: titleCenter,
    Size: 0.08,
  })
  .node("output", "MediaOut")
  .connect("title", "Output", "output", "Input")
  .output("output")
  .compile();
```

This compiles and validates a graph request; it does not mutate the live composition. Apply a complete replacement only when replacing the complete graph is intended. Follow [graph basics](graph-basics.md) for exact composition selection, preview, apply, and terminal result handling.

Treat the selected input's registry definition as authoritative. A `Point` tuple is not necessarily a screen position: pixel aspect, gamut, pivots, and other controls also use point-shaped data. Likewise, `Width`, `Height`, and `Size` are input-specific values, not a universal pixel unit. On Merge and Transform, reference-size settings change the Inspector's displayed Center values, while scripting still retrieves the internally stored normalized value.

Use the dimensions of the image or reference frame that owns the control, not an assumed delivery resolution. Creator tools can inherit a composition frame format or carry explicit width, height, and pixel-aspect inputs. Mixed-resolution branches therefore need rendered inspection at the output, especially when exact margins or circles matter.

Do not confuse image points with object-shaped options on other SDK methods. The graph IR uses `[x, y]` for a registry `Point`; operations such as image replacement and setting insertion use their declared `{x, y}` option shapes. Let TypeScript and the installed declarations enforce the distinction instead of casting between them.

## Choose Fusion frames deliberately

`fusionFrame(value)` accepts a safe integer in the composition frame domain. It does not carry a frame rate, a timeline start, a source offset, or a proof that the frame lies inside the live composition's global or render range. Fusion itself can represent sub-frame time, but this typed graph value cannot; do not round a required sub-frame position without deciding that loss of precision is acceptable.

Fusion composition attributes distinguish current time, global start/end, and render start/end. A clip-attached composition may not share the edit timeline's absolute frame numbers, and a trimmed or retimed clip may not share its visible record offset with its source position. Inspect live bounds and use the operation's declared time type instead of deriving one domain from another by unverified arithmetic.

The typed graph builder accepts keyframes only for inputs whose installed registry evidence marks them animatable. Keyframe times must be unique and strictly ascending. It records exact values at integer frames but does not promise interpolation, easing, Bezier handles, or motion-path shape.

The current checked-in registry exposes no input with observed animation support, so this plausible code is intentionally rejected:

```ts
sdk.fusionGraph()
  .node("title", "TextPlus")
  .animate("title", "Size", {
    kind: "keyframes",
    keyframes: [
      {time: sdk.fusionFrame(0), value: 0.05},
      {time: sdk.fusionFrame(24), value: 0.09},
    ],
  });
```

Do not cast around that gate. When exact scalar splines, point paths, handles, or interpolation are required, use a supported `.setting` or scripting route described in [animation](animation.md), [setting files](setting-files.md), and [scripting](scripting.md). Blackmagic's scripting model uses a numeric Bezier spline for number inputs and a Path for point inputs; those are different data types.

## Verify what the claim requires

After a live change, read back the exact composition, tool input, and keyframe times. Check the relevant global/render bounds and confirm that unrelated tools and compositions were preserved. A static frame can verify position at that frame; it cannot prove animation, interpolation, or behavior across a retimed clip. Sample the beginning, middle, end, and motion extremes when making a temporal claim, then follow [checking results](../checking-results.md) for the required evidence level.
