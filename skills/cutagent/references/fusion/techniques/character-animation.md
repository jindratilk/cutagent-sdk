# Animate text by character

Use a Text+ **Follower** when one authored animation should ripple through glyphs. A Follower is attached to Text+'s `StyledText` input, holds the editable text, and offsets the same local animation for successive text elements. It is the right primitive for letter-by-letter opacity, position, rotation, size, color, or shading changes.

This is not a typewriter substitution effect. The full string exists from the start; the Follower changes how each element is drawn over time. Use [text reveal](text-reveal.md) when the required effect is a Write On reveal or a clipping reveal.

## Build the Follower in Fusion

Right-click the Text+ **Styled Text** field and choose **Follower**, then work in the Modifiers tab. The Text+, Follower, and animated control have distinct jobs:

- Keep global typography on Text+: font, style, base size, tracking, alignment, layout box, and the main shading setup.
- Keep the editable copy in the Follower's text field. Text+'s `StyledText` is now connected to the Follower rather than holding a constant string.
- Key the changed property in the Follower's Text, Alignment, Transform, or Shading tab. A static value change in those tabs has no visible effect; the property must be animated.
- Use the Follower Timing tab to decide which characters are affected, their order, and how their local curves are offset.

Character Level Styling is a different modifier for static per-glyph exceptions. Do not assume it can be stacked with a Follower on the same `StyledText` connection. Prefer the Follower's shading controls for an animated color or opacity change, and test any combined modifier chain in the target DaVinci Resolve version.

## Choose the sequence deliberately

The Follower can process all characters or a selected range. Its character order can run left-to-right, right-to-left, inside-out, outside-in, random one-by-one, completely random, or from a manual curve. Spaces count as characters, so a multiword left-to-right sequence contains pauses unless that spacing is part of the design.

Delay type determines whether copy changes alter the total motion:

- **Between Each Character** offsets every next character by a fixed number of frames. More characters make the complete animation longer. With a 12-frame local curve and a two-frame delay, the four letters in `MOVE` start at frames 0, 2, 4, and 6; the last letter settles at frame 18.
- **Between First and Last Character** distributes the sequence across the chosen total span. Use it when translated or user-editable copy must finish in a stable amount of time.

DaVinci Resolve can apply Follower motion at character, word, or line level where the selected control exposes that grouping. Choose the element level before tuning the delay. First inspect the controls exposed by the installed Follower and export a representative setting; native parameter IDs and grouping controls are not stable enough to guess from Inspector labels. When exact grouping matters, one Text+ branch per word or line is the most explicit fallback: animate each branch's local Follower, then offset the branches in the composition. Do not treat spaces as reliable word delimiters for timing.

## Separate the local curve from the stagger

Author the motion of one element first. The Follower repeats that local curve and applies the timing offset. This separation makes timing predictable:

1. Put the first local key at the composition frame where the first character should begin.
2. Put the final local key where one character should settle.
3. Shape the curve in the Spline editor.
4. Add the Follower delay and confirm that the last affected character finishes before the composition ends.

The delay does not replace easing. Easing belongs to the animated property's spline. In a serialized setting, `BezierSpline.KeyFrames` uses composition-frame numbers as keys; `LH` and `RH` carry the left and right tangent coordinates. Do not add a timeline start frame to those keys. Avoid `Flags = { Linear = true }` when the intended curve uses eased handles.

Keep overshoot small for text. Large size, rotation, or Y-offset overshoot can make adjacent glyphs collide and can expose clipping in a tight layout box. Check the longest expected string, punctuation, spaces, and line breaks—not only the design copy.

## Minimal Follower setting

This setting keeps the base typography editable on `Text1`, keeps the copy editable on `Follower1.Text`, and fades each character over 12 local frames. It intentionally omits `Order` and `DelayType`, so the target DaVinci Resolve version supplies their defaults; confirm left-to-right and **Between Each Character** before relying on the 18-frame timing example. The horizontal tangent handles create a slow start and slow finish without a named easing preset.

```lua
{
    Tools = ordered() {
        Text1 = TextPlus {
            Inputs = {
                GlobalOut = Input { Value = 59, },
                Width = Input { Value = 1920, },
                Height = Input { Value = 1080, },
                UseFrameFormatSettings = Input { Value = 1, },
                StyledText = Input {
                    SourceOp = "Follower1",
                    Source = "StyledText",
                },
                Font = Input { Value = "Open Sans", },
                Style = Input { Value = "Regular", },
                Size = Input { Value = 0.08, },
                VerticalJustificationNew = Input { Value = 3, },
                HorizontalJustificationNew = Input { Value = 3, },
            },
            ViewInfo = OperatorInfo { Pos = { 0, 0 } },
        },
        Follower1 = StyledTextFollower {
            Inputs = {
                Delay = Input { Value = 2, },
                Text = Input {
                    Value = StyledText { Value = "MOVE", },
                },
                Opacity1 = Input {
                    SourceOp = "Follower1Opacity1",
                    Source = "Value",
                },
            },
        },
        Follower1Opacity1 = BezierSpline {
            KeyFrames = {
                [0] = { 0, RH = { 4, 0 }, },
                [12] = { 1, LH = { 8, 1 }, },
            },
        },
        MediaOut1 = MediaOut {
            Inputs = {
                Index = Input { Value = "0", },
                Input = Input { SourceOp = "Text1", Source = "Output", },
            },
            ViewInfo = OperatorInfo { Pos = { 220, 0 } },
        },
    },
}
```

The source shape above passed CutAgent's offline structural inspector: all three connections resolve, the spline is used, and MediaOut is connected. That check does not load DaVinci Resolve. Before treating a hand-authored setting as production-ready, import it into the target DaVinci Resolve version or start from a setting exported by that version. For a different order, delay type, affected range, transform, or shading element, change the control in Fusion and preserve the exported native input IDs; do not guess numeric enum values.

## Publish and insert with the SDK

The current typed Fusion graph registry has no input marked animatable, so `fusionGraph().animate(...)` cannot express this modifier and spline honestly. Publish the reviewed setting and insert it through the managed setting API. This runner module uses the supplied `sdk`, `client`, `timeline`, `snapshot`, and `progress` objects; it does not reconnect or rediscover project state.

```js
export default async function insertFollowerTitle({
  sdk,
  client,
  timeline,
  snapshot,
  progress,
}) {
  const settingSource = String.raw`{
    Tools = ordered() {
      Text1 = TextPlus {
        Inputs = {
          GlobalOut = Input { Value = 59, },
          Width = Input { Value = 1920, }, Height = Input { Value = 1080, },
          UseFrameFormatSettings = Input { Value = 1, },
          StyledText = Input { SourceOp = "Follower1", Source = "StyledText", },
          Font = Input { Value = "Open Sans", },
          Style = Input { Value = "Regular", }, Size = Input { Value = 0.08, },
          VerticalJustificationNew = Input { Value = 3, },
          HorizontalJustificationNew = Input { Value = 3, },
        },
        ViewInfo = OperatorInfo { Pos = { 0, 0 } },
      },
      Follower1 = StyledTextFollower {
        Inputs = {
          Delay = Input { Value = 2, },
          Text = Input { Value = StyledText { Value = "MOVE", }, },
          Opacity1 = Input { SourceOp = "Follower1Opacity1", Source = "Value", },
        },
      },
      Follower1Opacity1 = BezierSpline {
        KeyFrames = {
          [0] = { 0, RH = { 4, 0 }, },
          [12] = { 1, LH = { 8, 1 }, },
        },
      },
      MediaOut1 = MediaOut {
        Inputs = {
          Index = Input { Value = "0", },
          Input = Input { SourceOp = "Text1", Source = "Output", },
        },
        ViewInfo = OperatorInfo { Pos = { 220, 0 } },
      },
    },
  }`;

  const receipt = await client.artifacts.publishFusionSetting(settingSource);
  const targetTrack = snapshot.videoTrack(2);

  progress("Inserting the Follower title");
  const operation = await timeline.fusion.insertSettings(
    {
      settingArtifactId: receipt.artifactId,
      clipName: "Follower title",
      recordPosition: sdk.timelineRecordOffset(snapshot, sdk.frames(0)),
      clipDuration: sdk.duration(sdk.frames(60)),
      videoTrackIndex: targetTrack.index,
    },
    {
      precondition: snapshot.revision,
      idempotencyKey: sdk.idempotencyKey(),
    },
  );

  const terminal = await operation.wait();
  if (
    terminal.status !== "succeeded" ||
    terminal.verification.outcome !== "passed" ||
    terminal.verification.protectedStatePreserved === false
  ) {
    console.error(terminal);
    throw new Error(`Follower insertion ended as ${terminal.status}`);
  }

  const inserted = terminal.result.items[0];
  const after = await timeline.snapshot();
  const compositions = await timeline.fusion.forTimelineItem(
    inserted.timelineItemId,
    after.revision,
  );
  console.log({receipt, inserted, compositions});
}
```

Run the module with `cutagent-sdk --title "Insert Follower title" insert-follower-title.mjs`. `timelineRecordOffset` respects a nonzero timeline start. The setting's frames 0 and 12 remain local Fusion composition frames.

For several titles observed at the same revision, publish each source and pass one ordered array to `insertSettings()` rather than starting serial single-item operations. The method accepts 1–100 insertions. A batch is not atomic: if it does not succeed, inspect its terminal result and recovery state before retrying so earlier insertions are not duplicated.

## Verify structure and motion

A successful insertion verifies the requested item placement, duration, track, revision change, and preservation of unrelated items. It does not prove Follower behavior, the selected shading element, font availability, easing, or rendered pixels.

Use the returned timeline-item identity and fresh revision to inspect the composition. Confirm this chain:

```text
Follower1Opacity1.Value -> Follower1.Opacity1
Follower1.StyledText    -> Text1.StyledText
Text1.Output            -> MediaOut1.Input
```

Then review frames 0, 6, 12, and 18 for the example, plus normal-speed playback. Those samples cover the first glyph's start and finish and the last glyph's start and finish. Check spaces, punctuation, line wrapping, clipping, glyph collisions, and the longest editable copy. Read [setting files](../setting-files.md) for offline inspection and managed insertion, [animation](../animation.md) for current keyframe limits, and [preview and debugging](../preview-and-debugging.md) for evidence appropriate to appearance and motion claims.
