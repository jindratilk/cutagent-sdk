# Text reveal

Use Text+ **Write On** when letters should appear in text order. It reveals typeset glyphs; it does not trace a handwritten stroke. For a block, line, or directional wipe independent of character order, reveal an already typeset Text+ branch with an animated mask instead; see [Compositing and masks](../compositing-and-masks.md). Read [Text and layout](../text-and-layout.md) before choosing fonts or line breaks, and [Animation](../animation.md) for spline timing.

## Author a Write On setting

Drive the Text+ `End` input from `0` to `1` while leaving `Start` at `0`. Keep the final value at `1` for the reading hold. The following setting is a transparent 72-frame title; the reveal finishes on composition frame 18.

```lua
{
    Tools = ordered() {
        Title = TextPlus {
            Inputs = {
                GlobalOut = Input { Value = 71, },
                Width = Input { Value = 1920, },
                Height = Input { Value = 1080, },
                UseFrameFormatSettings = Input { Value = 1, },
                StyledText = Input { Value = "Replace me", },
                Font = Input { Value = "Arial", },
                Style = Input { Value = "Bold", },
                Size = Input { Value = 0.1, },
                Center = Input { Value = { 0.5, 0.5 }, },
                Red1 = Input { Value = 1, },
                Green1 = Input { Value = 1, },
                Blue1 = Input { Value = 1, },
                Alpha1 = Input { Value = 1, },
                Start = Input { Value = 0, },
                End = Input { SourceOp = "RevealEnd", Source = "Value", },
            },
            ViewInfo = OperatorInfo { Pos = { 0, 0 } },
        },
        MediaOut1 = MediaOut {
            Inputs = {
                Index = Input { Value = "0", },
                Input = Input { SourceOp = "Title", Source = "Output", },
            },
            ViewInfo = OperatorInfo { Pos = { 220, 0 } },
        },
        RevealEnd = BezierSpline {
            KeyFrames = {
                [0] = { 0, RH = { 6, 0 } },
                [18] = { 1, LH = { 12, 1 } },
            },
        },
    },
}
```

Treat `GlobalOut = 71` and the 72-frame insertion duration as one design. If the duration changes, move the reveal and hold keys deliberately rather than stretching blindly. Text+ follows its configured reading and line direction; review multiline, vertical, or right-to-left copy rather than assuming a left-to-right result. Use an installed face and style, then check the real glyph coverage and line wrap.

## Publish and insert it

In a `cutagent-sdk` runner module, keep the setting string above in `TEXT_REVEAL_SETTING`. The runner already supplies `sdk`, `client`, `timeline`, and the initial `snapshot`:

```js
export default async function addTextReveal({ sdk, client, timeline, snapshot }) {
  const setting = await client.artifacts.publishFusionSetting(TEXT_REVEAL_SETTING);

  const operation = await timeline.fusion.insertSettings(
    {
      settingArtifactId: setting.artifactId,
      clipName: "Text reveal",
      recordPosition: sdk.timelineRecordOffset(snapshot, sdk.frames(240)),
      clipDuration: sdk.duration(sdk.frames(72)),
      videoTrackIndex: 2,
      text: "A clear idea",
    },
    {
      precondition: snapshot.revision,
      idempotencyKey: sdk.idempotencyKey(),
    },
  );

  const terminal = await operation.wait();
  if (terminal.status !== "succeeded") {
    console.error({
      status: terminal.status,
      result: "result" in terminal ? terminal.result : undefined,
      recovery: "recovery" in terminal ? terminal.recovery : undefined,
    });
    throw new sdk.CutAgentSdkError(terminal.failure);
  }
  if (terminal.verification.outcome !== "passed") {
    throw new Error(`Insertion verification was ${terminal.verification.outcome}.`);
  }

  console.log({
    operationId: operation.operationId,
    inserted: terminal.result.items,
    verification: terminal.verification.evidence,
  });
}
```

`text` requests replacement of the setting's direct `StyledText` payload during insertion, so do not also attach a `StyledTextCLS` owner unless character-level styling is intentional. Placement verification alone does not prove that substitution; inspect the inserted composition. For several reveals from the same coherent snapshot, publish each distinct setting once and pass an ordered insertion list to `insertSettings`; do not repeat project setup or invent a batch method.

The typed `fusionGraph()` builder currently exposes Text+ and its `Start`/`End` inputs, but the shipped registry does not mark them as animatable. Do not cast around that evidence gate or claim that `.animate("title", "End", ...)` works. A native setting spline is the supported authoring route for this technique. See [Setting files](../setting-files.md) for serialization boundaries.

## Check the reveal

Insertion verification proves placement and structural readback, not pacing, glyph rendering, or the direction of the reveal. Inspect at least one frame before the first key, one during the transition, and one during the full-text hold; use a short playback or preview when judging smoothness. Confirm the actual font, line breaks, clipping, contrast, and that neighboring tracks remain unchanged. A single final frame proves only the settled title. Read [Preview and debugging](../preview-and-debugging.md) for evidence choices.
