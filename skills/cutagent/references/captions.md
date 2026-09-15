# Captions

Use this reference for native subtitle tracks, imported or generated subtitles, designed Text+ captions, and caption verification.

## Choose the caption representation

| Requirement | Representation | CutAgent SDK surface |
| --- | --- | --- |
| Editable, searchable, exportable captions | Native subtitle-track items | `timeline.captions.list()`, `importSrt()`, `export()`, `autoCreate()` |
| Branded typography, per-cue layout, or bespoke motion | Text+ clips on a video track | `timeline.captions.insertDesigned()` |
| Native subtitle semantics with a Fusion style applied to the subtitle track | DaVinci Resolve 20 subtitle-track Fusion template | No high-level SDK operation currently exposes this styling step |

Do not treat Text+ clips as subtitles. They do not appear in native subtitle readback or SRT/VTT/TTML export. If accessibility, localization, or sidecar delivery matters, retain a native subtitle track even when the visible design uses Text+.

When the representation is genuinely unclear, resolve the deliverable requirement first: semantic/exportable captions, designed on-screen graphics, or both.

## Preserve the timing domain

- `SubtitleItemSnapshot.recordRange` is an absolute, half-open timeline-record range.
- SRT, VTT, and TTML timestamps are relative to timeline content zero. A nonzero timeline start is not timestamp zero in the record domain.
- Use `timelineRecordRange(...)` for absolute placement. Use `transcriptRelativeRange(...)` only for offsets from transcript or timeline content zero.
- Use the inspected `TimelineSnapshot.frameRate` whenever converting frames, seconds, or timecode. Never substitute source-frame positions for timeline-record positions.
- After a timeline edit or retime, assume caption timing may need reconciliation. Do not reuse a stale transcript-to-record mapping.

## Native subtitle workflow

This runner-context snippet imports reviewed SRT text, waits for the durable operation, reads the new timeline revision, and serializes authoritative subtitle readback as VTT. The runner supplies `sdk`, the exact `timeline`, and its current `snapshot`.

```ts
const srt = `1
00:00:00,000 --> 00:00:01,500
Welcome to the edit.

2
00:00:01,700 --> 00:00:03,400
Let's make it clear.`;

const importOperation = await timeline.captions.importSrt({
  precondition: snapshot.revision,
  srt,
  ensureTrack: true,
  idempotencyKey: sdk.idempotencyKey(),
});
const imported = await importOperation.wait();
if (imported.status !== "succeeded") {
  throw new Error(`Subtitle import ended as ${imported.status}`);
}

const subtitles = await timeline.captions.list({
  precondition: imported.result.verification.revision,
});
const expectedText = ["Welcome to the edit.", "Let's make it clear."];
if (!expectedText.every((text) => subtitles.items.some((item) => item.text === text))) {
  throw new Error("Imported subtitle text was not present in authoritative readback");
}

const exportOperation = await timeline.captions.export({
  precondition: subtitles.revision,
  format: "vtt",
  allTracks: true,
  idempotencyKey: sdk.idempotencyKey(),
});
const exported = await exportOperation.wait();
if (exported.status !== "succeeded") {
  throw new Error(`Subtitle export ended as ${exported.status}`);
}

console.log({
  imported: imported.result.matchedEntries,
  readBack: subtitles.items.length,
  exported: exported.result.exportedEntries,
  sha256: exported.result.sha256,
  vtt: exported.result.content,
});
```

`importSrt()` accepts SRT content, not a file path. `ensureTrack` defaults to `true`. `export()` returns carrier-neutral text and a SHA-256 digest; it does not write a file. Choose either `track` or `allTracks`, never both. With neither supplied, export defaults to all subtitle tracks.

DaVinci Resolve can hold multiple native subtitle tracks, commonly one per language or use, but only one subtitle track is visible at a time. Check track enablement as well as item readback when a multilingual track appears absent.

For DaVinci Resolve speech analysis, call `timeline.captions.autoCreate()` with the exact snapshot revision, a fresh idempotency key, and only reviewed options: `language`, `preset`, `charsPerLine`, `lineBreak`, and `gap`. DaVinci Resolve's reference manual marks Create Subtitles from Audio as Studio-only; the current SDK inventory declares DaVinci Resolve 20.0 or later but does not claim verified Free-edition support. Treat capability negotiation as authoritative for the connected host.

The SDK method has no audio-track, marked-range, speaker, transcript, or destination-track selector. Inspect included audio and existing subtitles before starting, then list the resulting subtitles; do not infer the target track or generated text from `createdItems` alone.

## Designed Text+ workflow

`insertDesigned()` requires an existing video track, a `.setting` template already reachable by the runtime host, timed cues, and the complete segmentation policy. The target is a video track, not a subtitle track.

```ts
// The caller chooses a reviewed .setting file reachable by the runtime host.
const captionTemplatePath = "/absolute/path/to/reviewed-caption.setting";

const captionTrack = snapshot.videoTracks.find(
  (track) => track.clips.length === 0
    && snapshot.videoTracks.every(
      (other) => other.clips.length === 0 || other.index < track.index,
    ),
);
if (!captionTrack) {
  throw new Error("Create or choose an empty video track above occupied video tracks");
}

const operation = await timeline.captions.insertDesigned({
  precondition: snapshot.revision,
  template: { kind: "runtime_path", path: captionTemplatePath },
  trackIndex: captionTrack.index,
  cues: [
    { text: "Design", timing: sdk.transcriptRelativeRange(sdk.seconds(0), sdk.seconds(0.42)) },
    { text: "for", timing: sdk.transcriptRelativeRange(sdk.seconds(0.42), sdk.seconds(0.68)) },
    { text: "real", timing: sdk.transcriptRelativeRange(sdk.seconds(0.68), sdk.seconds(1.02)) },
    { text: "readers.", timing: sdk.transcriptRelativeRange(sdk.seconds(1.02), sdk.seconds(1.55)) },
  ],
  segmentation: {
    unit: "words",
    target: 4,
    preferredMin: 2,
    preferredMax: 5,
    hardMax: 6,
    maxCharactersPerLine: 36,
    maxLines: 2,
    preferredCps: 17,
    hardCps: 21,
    minimumDurationSeconds: 0.8,
    pauseThresholdSeconds: 0.4,
  },
  idempotencyKey: sdk.idempotencyKey(),
});
const terminal = await operation.wait();
if (terminal.status !== "succeeded") {
  throw new Error(`Designed-caption insertion ended as ${terminal.status}`);
}

const after = await timeline.snapshot();
const changedTrack = after.videoTracks.find(
  (track) => track.index === terminal.result.trackIndex,
);
if (!changedTrack || changedTrack.clips.length <= captionTrack.clips.length) {
  throw new Error("Designed captions were not present on the requested track");
}
console.log(terminal.result);
```

Keep transcript-relative cues non-negative, nonempty, ordered, and non-overlapping. The segmentation object is intentional editorial policy; choose it for language, format, pace, and reading speed instead of copying the example values blindly.

## Transcript source

`timeline.transcript.create()` is a durable hosted operation bound to one exact timeline revision. In the standalone public package, hosted transcription is unavailable and returns `HOSTED_SERVICE_REQUIRES_CUTAGENT_APP`; the CutAgent app provides the account-managed route.

Treat transcription as potentially billed work. Retain the original idempotency key and operation identity across an uncertain response. Resume retained work with the returned job identity; never set `newJob: true` as an automatic retry. A delivered transcript proves what was rendered for that job, not that the live timeline has remained unchanged.

## Verify the result

Use evidence proportional to the representation:

- Native subtitles: compare expected text, track, and absolute record ranges through `captions.list()`. Review exported SRT/VTT/TTML when textual delivery matters.
- Auto captions: review wording, language, punctuation, line breaks, timing, gaps, overlaps, and dialogue coverage. Overlapping dialogue across audio tracks deserves special attention.
- Designed Text+: confirm exact target-track placement and inspect representative first, middle, boundary, longest, multiline, and non-ASCII cues in rendered frames. Check the actual font, glyph fallback, wrapping, safe area, contrast, subject occlusion, and template parameters.
- Animated captions: inspect multiple frames across entrance, hold/highlight, and exit. One frame cannot prove motion or synchronization.
- Final delivery: verify whether captions must remain selectable/exportable, burn in, embed, or ship as a sidecar; timeline presence alone does not prove the render setting or output artifact.

Operation success and structural readback do not prove typography or motion. Visual review does not replace semantic subtitle readback.

## Recover without duplication

- On `STALE_REVISION`, refresh the exact timeline snapshot, then rebuild the request from the new revision.
- On `CAPABILITY_UNAVAILABLE`, keep the requested result in view and choose a supported native, Text+, or CutAgent CLI route; do not invent an SDK method.
- On `VERIFICATION_FAILED`, `RECOVERY_FAILED`, timeout, disconnect, or any failure with `possibleMutation` other than `none`, inspect current subtitle tracks and the designed-caption video track before retrying. Reuse the original idempotency key for the same logical attempt.
- A local wait timeout or abort stops only the caller's wait. Reattach through `client.operations` before deciding whether new work is necessary.

For bounded inspection or file export, CutAgent CLI may be the more direct route:

```sh
cutagent --json timeline subtitle list --track 1
cutagent --json timeline subtitle export /absolute/path/captions.vtt --format vtt --track 1
```

Read the JSON envelope through `ok`, `data`, `error`, and `meta`. Inspect partial state before repeating any CLI mutation. There is no evidence-backed blanket preference for SDK or CutAgent CLI caption creation; choose by current capability, composability, latency, and verification needs.

## Related editing knowledge

- If a speed change can alter speech-to-picture timing, read [speed ramps](editing/speed-ramps.md).
- If designed captions need animated layout or parameter motion, read [transforms and keyframes](editing/transforms-and-keyframes.md).
- If transcript-driven cutting must preserve linked audio or create J/L cuts, read [linked audio and J/L cuts](editing/linked-audio-and-jl-cuts.md).
- If intelligibility or delivery level is part of caption QA, read [loudness and dynamics](audio/loudness-and-dynamics.md).
