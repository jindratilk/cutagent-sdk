# Tracked label

Use a 2D point track when a label must follow one compact feature. Use a planar track for a flat surface such as a sign or screen, and a 3D camera track only when the label must live in reconstructed scene space. Choose a feature with stable contrast, little deformation, and minimal occlusion or parallax.

## Build the native relationship

Keep tracking and label layout separate:

```text
footage ───────────────────────────────→ Tracker.Background
Text+ ──→ styling ──→ offset Transform ─→ Tracker.Foreground
                                          Tracker (Match Move) ──→ MediaOut
```

Track the footage first, inspect the path across the whole range, then set the Tracker operation to Match Move and feed the label branch into its foreground. Put the label's visual offset before the Tracker. Moving the tracker point to position the label changes the measured feature and can weaken the track.

Give important tools stable names such as `LabelText`, `LabelOffset`, and `ObjectTrack`. This lets later SDK edits address the intended input without depending on DaVinci Resolve's automatically numbered names. Read [Fusion tracking](../tracking.md) for tracker choice and analysis, [Text and layout](../text-and-layout.md) for the label design, and [Coordinates and time](../coordinates-and-time.md) before translating positions or frames.

## Retitle an existing tracked composition

Preserve the graph and change only the known Text+ input. This runner module expects exactly one timeline item named `Product Callout` and one Fusion composition on that item:

```js
export default async function retitleTrackedLabel({ sdk, timeline, snapshot, progress }) {
  const matches = snapshot.videoTracks
    .flatMap((track) => track.clips)
    .filter((clip) => clip.name === "Product Callout");

  if (matches.length !== 1 || matches[0].id === null) {
    throw new Error("Expected one durable Product Callout timeline item.");
  }

  const compositions = await timeline.fusion.forTimelineItem(
    matches[0].id,
    snapshot.revision,
  );
  if (compositions.length !== 1) {
    throw new Error("Expected exactly one Fusion composition on Product Callout.");
  }

  progress("Updating the tracked label");
  const operation = await timeline.fusion.setText(
    {
      target: compositions[0],
      toolName: "LabelText",
      inputName: "StyledText",
      text: "Aperture control",
    },
    {
      precondition: compositions[0].timelineRevision,
      idempotencyKey: sdk.idempotencyKey(),
    },
  );

  const terminal = await operation.wait();
  if (
    terminal.status !== "succeeded" ||
    terminal.verification.outcome !== "passed"
  ) {
    console.error(terminal);
    throw new Error(`Tracked-label update ended as ${terminal.status}.`);
  }
}
```

`setText` accepts one update or a list of updates in one native operation. Use the list form when several labels come from the same observed timeline revision; do not reconnect or repeat project selection for every label.

## Use supplied motion samples carefully

CutAgent can write an exact keyframe to a known Fusion input through the typed action `cutagent.action.fusion.keyframe.set`. This is useful when trustworthy point coordinates already exist. It is not motion analysis. The action accepts one keyframe, uses a Fusion source-frame position, and advances the composition revision; chain the returned `revisionAfter` into the next sample rather than reusing the original precondition.

The current generated applicability for this action is unresolved across the release matrix. Attempt it only when the connected runtime admits `fusion.mutation`; stop on `CAPABILITY_UNAVAILABLE`. Do not replace that failure with an untyped script or a guessed `.setting` mutation.

## Current automation boundary

The reviewed `fusionGraph()` registry currently exposes neither `Tracker` nor `MediaIn`, and it has no input with verified animation support. Its `animate()` method therefore cannot author this technique today. Applying a graph built only from the reviewed registry would replace the existing composition and discard its tracking relationship.

The typed `cutagent.action.fusion.tracker.add` action creates an inline Tracker scaffold and sets its initial pattern center. It does not run forward or reverse analysis, configure Match Move, attach the label, or prove track quality. Do not report a tracked label from that action alone.

Until those capabilities gain reviewed public contracts, automate either a text change in an already tracked composition or keyframes from supplied motion samples. Leave new native analysis as an explicit unresolved step.

## Verify the motion

Check structural readback for the exact composition, tool, input, and keyframes. Then inspect frames near the start, middle, end, direction changes, fast motion, and any occlusion. A single frame cannot prove tracking. Review playback or a rendered excerpt before claiming that the label follows the object, and distinguish a technically attached label from one whose offset, scale, contrast, or occlusion treatment looks convincing. Read [Preview and debugging](../preview-and-debugging.md) and [Checking results](../../checking-results.md) for evidence selection.
