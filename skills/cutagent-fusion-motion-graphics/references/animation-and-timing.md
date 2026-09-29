# Animation and timing

Read this when animating a Fusion scene. Design what the viewer should notice and when; use keyframes to express that sequence.

## Time domains

Separate timeline record frames, clip-local offsets, and Fusion composition frames. Inspect the composition range and clip placement; do not assume all three begin at zero. At 24 fps, a five-second zero-based composition contains frames 0–119. A key at 120 is outside that visible range. The frame-export commands' `Nf` inputs are timeline-relative offsets, while explicit timecode includes the timeline start. Translate clip-local samples through placement; do not add the timeline start twice.

Write a short timing table before generating keys: element, entrance start/end, reading hold, exit start/end. At a given frame rate, convert seconds to integer composition frames once. Scale phase durations when changing length instead of blindly stretching every hold and easing segment. Preserve enough time to read the actual text.

## Scalar animation: BezierSpline

BezierSpline animates a number. Connect it to `Merge.Blend`, `Transform.Size`, a verified scalar rotation input, or another discovered numeric input. It does not emit a 2D point. A scalar spline wired directly to `Transform.Center` is the wrong type. Blackmagic's [Fusion scripting guide](https://documents.blackmagicdesign.com/UserManuals/Fusion8_Scripting_Guide.pdf) distinguishes numeric splines from point paths.

```lua
TitleFade = BezierSpline {
    KeyFrames = {
        [0] = { 0, RH = { 4, 0 } },
        [12] = { 1, LH = { 8, 1 }, RH = { 38, 1 } },
        [90] = { 1, LH = { 64, 1 }, RH = { 96, 1 } },
        [108] = { 0, LH = { 102, 0 } },
    },
}
```

Connect with `Blend = Input { SourceOp = "TitleFade", Source = "Value", }` on a Merge. Key indices are frames. Each first value is the scalar at that frame. `LH` and `RH` are absolute time/value handle coordinates, not CSS control points or offsets. The 0→12 segment above uses horizontal endpoint tangents. Keep handle times inside their segment and ordered so time does not fold back on itself. Explicit equal-valued keys create a reading hold. Do not combine an intended eased segment with contradictory `Linear` flags.

Choose curves by meaning: a fast approach and slow settle communicates arrival; a restrained overshoot communicates elasticity; constant velocity suits a mechanical sweep. Keep opacity in 0–1, keep size positive, and avoid applying spring overshoot to constrained values. For an overshoot, add a small excursion and a settling key rather than random oscillations across the entire clip. Blackmagic documents spline handle editing in the [Fusion tool reference](https://documents.blackmagicdesign.com/UserManuals/Fusion9_Tool_Reference.pdf).

## Point animation: XYPath

For independently animated X/Y position, use a point-producing XYPath with scalar curves on its X and Y inputs. This structure is observed in native exported scenes:

```lua
CardPath = XYPath {
    Inputs = {
        X = Input { Value = 0.5, },
        Y = Input { SourceOp = "CardY", Source = "Value", },
    },
    ViewInfo = OperatorInfo { Pos = { 0, 180 } },
}
CardY = BezierSpline {
    KeyFrames = {
        [0] = { 0.42, RH = { 8, 0.42 } },
        [24] = { 0.5, LH = { 16, 0.5 } },
    },
}
```

The owning Transform uses `Center = Input { SourceOp = "CardPath", Source = "Value", }`. For a curved spatial trajectory or path-following design, discover/capture the native PolyPath structure instead of pretending two scalar keys define a curved path. Keep spatial shape and progress along that shape separate.

## Choreography and editability

Animate a shared card transform after assembling fill, accent, and label. Reveal text a few frames after its supporting shape. Keep connectors attached to moving endpoints, or build and animate their parent group. Stagger repeated items by shifting a reusable phase schedule, while retaining one coherent reading order. Avoid simultaneous movement of every visual layer.

For a line draw, distinguish the curve geometry from reveal progress. A PolylineMask stroke can use its native length control when verified. If that input fails visually, reveal a fully drawn line with an animated mask. Validate the endpoint and partial-draw states; final geometry alone does not prove write-on behavior.

SDK `animate` records exact values at integer `fusionFrame(...)` times; its current public contract does not assert interpolation or expose Bezier handles. Do not invent `easing`, `spring`, or tangent parameters. Use a supported native `.setting` route when exact spline shape is required. Read `cutagent-fusion` and the installed SDK declarations for the current execution contract.

Inspect a short preview when the claim concerns smoothness, spring character, camera movement, or attached elements. Static beginning/middle/end samples can miss pops or a long dead interval.
