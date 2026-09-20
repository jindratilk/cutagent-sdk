# Fusion templates

Use a Fusion template when a title, generator, effect, or transition should be reusable from the Edit or Cut page. A template is a `.setting` macro with a deliberate image-flow contract and a small set of published Inspector controls. It is not merely any Fusion composition saved to disk.

For the serialized graph format, read [setting files](./setting-files.md). For exact node connections, read [graph basics](./graph-basics.md). For Text+ controls and font behavior, read [text and layout](./text-and-layout.md).

## Choose the template contract

Match the graph boundary to the Effects Library category:

| Template | Image-flow contract | Typical published controls |
| --- | --- | --- |
| Title | Generates text/graphics; no source-image input | Styled Text, font, style, size, color |
| Generator | No image input; one image output | Colors, seed, scale, speed |
| Effect | Normally one image input and one output; a deliberate multi-layer effect may expose more inputs | Effect strength, mask, blend, look controls |
| Transition | Two image inputs and one image output | Only the few controls an editor should vary |

Select every internal tool the macro needs. Publish only controls that remain meaningful outside the node graph; their selection and order define the Edit-page Inspector. For an effect with several source layers, expose each required MediaIn `Layer` control. Expose a MediaIn `ClipName` control when the template needs an Edit-page media drop zone.

Do not treat Inspector labels as SDK graph identifiers. The template author chooses the public UI labels, while Fusion tool and input IDs remain the structural targeting contract.

## Make duration behavior intentional

Fixed Fusion keyframes keep their composition-frame timing when an editor changes the template duration. They do not automatically scale to the new Edit-page length.

- Use an Anim Curves modifier when the whole animation should scale with the clip or transition duration. Its Duration source follows the edit length; its Transition source also follows the Edit-page transition curve.
- Use a Keyframe Stretcher for a title whose entrance and exit timing should remain fixed while the middle hold expands or contracts.
- Keep fixed keyframes only when a fixed composition-frame schedule is part of the design.

Verify at more than one duration and inspect multiple frames. A correct first or last frame does not prove that a transition adapts or that a title's hold region stretches. See [animation](./animation.md) and [preview and debugging](./preview-and-debugging.md).

## Insert a reviewed `.setting`

Publish the source through `client.artifacts.publishFusionSetting()`, then insert it with `timeline.fusion.insertSettings()`. The complete runner example lives in [setting files](./setting-files.md). Pass one insertion or one ordered array; items that share the observed timeline revision belong in the same operation.

Use `sdk.timelineRecordOffset(snapshot, sdk.frames(n))` for a position relative to the observed timeline start. `recordPosition` is absolute timeline-record time, while animation inside the template uses Fusion composition frames. Track indexes are one-based.

Optional insertion fields such as `text`, `imageArtifactId`, `position`, `styleMarkdown`, and `boldStyle` work only when the reviewed template implements the corresponding supported placeholder. A successful insertion result verifies each new item's identity, record position, duration, track, optional clip name, revision transition, and preservation of pre-existing timeline items. It does not report or prove those optional substitutions, the complete imported graph, fonts, pixels, or motion.

## Update a known nested text template

Use `updateNestedText()` only for a template whose contract contains nested header/body text clips. Supply the nested clip names when the template contract defines them; otherwise the runtime may have to infer roles from nested clip order. For ordinary Text+ inputs on one composition, use `timeline.fusion.setText()` instead.

```js
export default async function ({ sdk, timeline, snapshot, progress }) {
  const matches = snapshot.videoTracks
    .flatMap((track) => track.clips)
    .filter((clip) => clip.name === "Feature Callout");
  const item = matches[0];
  if (matches.length !== 1 || !item || item.id === null) {
    throw new Error("Expected one durable Feature Callout item");
  }

  const compositions = await timeline.fusion.forTimelineItem(
    item.id,
    snapshot.revision,
  );
  if (compositions.length !== 1) {
    throw new Error(`Expected one Fusion composition; found ${compositions.length}`);
  }

  progress("Updating the callout template text");
  const operation = await timeline.fusion.updateNestedText(
    {
      timelineItemId: item.id,
      compositionIndex: compositions[0].index,
      header: "Faster review",
      body: "Compare the exact result before delivery.",
      headerClipName: "Header",
      bodyClipName: "Body",
      boldStyle: "Bold",
    },
    {
      precondition: snapshot.revision,
      idempotencyKey: sdk.idempotencyKey(),
    },
  );

  const terminal = await operation.wait();
  if (terminal.status !== "succeeded") {
    console.error(terminal);
    throw new Error(`Nested text update ended as ${terminal.status}`);
  }
  if (terminal.result.failureCount !== 0) {
    console.error(terminal.result.results);
    throw new Error("At least one nested template update failed");
  }
  console.log(terminal.result.results);
}
```

For several known template items from the same revision, pass one ordered update array. Inspect every result row instead of treating the operation's terminal state as proof that every item changed; a successful row reports whether its header and body were actually updated. Reacquire only state invalidated by the returned revision before preparing another mutation.

Case conversion, doubled header spacing, and `boldStyle` are explicit template-specific transformations. Do not enable them as generic typography defaults. Validate the actual font face, glyphs, line breaks, and longest copy as described in [text and layout](./text-and-layout.md).

## Package reusable assets

Use Fusion's `Setting:` path map for assets stored beside a loaded `.setting`, such as images, LUTs, and 3D files. Keep those relative references inside the package. `publishFusionSetting()` publishes only the setting bytes; it does not publish an adjacent asset directory.

For Effects Library distribution, use the direct CLI template-management surface described in [CLI usage](../cli.md). The current semantic SDK has no high-level scaffold, install, uninstall, icon, asset-directory, or DRFX packaging facade. Preserve the standard bundle hierarchy under `Edit/Titles`, `Edit/Generators`, `Edit/Effects`, or `Edit/Transitions`. A custom icon is a same-basename PNG beside the `.setting`; Blackmagic recommends 104 × 58 pixels. Use the lowercase `.drfx` extension for cross-platform packages.

File creation or installation proves only the filesystem result. Confirm that DaVinci Resolve discovers the intended category and that an inserted instance exposes the intended controls. For final proof, inspect the graph, render representative frames, and review the affected interval when the template moves.

Blackmagic's [Fusion 21 Reference Manual](https://documents.blackmagicdesign.com/UserManuals/FusionManual.pdf) describes macro publication, template categories, duration modifiers, drop zones, icons, and DRFX bundles. Use the installed SDK declarations and live capabilities for the current CutAgent contract; method presence alone is not proof of support on every DaVinci Resolve edition, platform, or runtime path.
