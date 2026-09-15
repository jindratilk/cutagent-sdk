# Rendering

Use `project.render.export()` to create one new, managed, single-file output from an exact timeline revision. It configures single-clip delivery, enqueues and starts the owned job, waits for the native render, and independently verifies the resulting artifact. Use `project.render.queue` instead when the required jobs already exist in DaVinci Resolve's render queue.

Choose delivery properties from the receiving specification and the actual timeline. Confirm current platform, broadcaster, festival, client, or archive requirements before a consequential export; a current destination contract takes precedence over generic profile advice. Match timeline frame rate and resolution unless the request explicitly calls for standards conversion or scaling. Vertical delivery needs an intentionally reframed vertical timeline, not only vertical output dimensions. Keep SDR color intent and an already mixed audio program unchanged unless the delivery specification requires a conversion, HDR workflow, channel change, or loudness target.

## Export one verified file

Discover the exact format, codec, and resolution before requesting them. Availability varies with DaVinci Resolve version, edition, operating system, hardware, and installed encoder support; an `unknown_version` or unavailable discovery result is not permission to guess a label.

Take `snapshot` after the final timeline mutation. The export precondition is that exact timeline revision. Retain one idempotency key for the logical export and reuse it if dispatch has an uncertain outcome.

Given existing `sdk`, `project`, `timeline`, and fresh `snapshot` variables:

```ts
const width = 1920;
const height = 1080;
const discovery = await project.render.discovery();

if (discovery.formatSupport.availability !== "supported") {
  throw new Error("Render format discovery is unavailable.");
}

const format = discovery.formats.find(
  (entry) => entry.format.kind === "known" && entry.format.value === "mp4",
);
if (!format || format.codecSupport.availability !== "supported") {
  throw new Error("MP4 codec discovery is unavailable.");
}

const codec = format.codecs.find(
  (entry) => entry.codec.kind === "known" && entry.codec.value === "h264",
);
if (
  !codec ||
  codec.resolutionSupport.availability !== "supported" ||
  !codec.resolutions.some(
    (resolution) => resolution.width === width && resolution.height === height,
  )
) {
  throw new Error("MP4/H.264 at 1920x1080 is unavailable.");
}

const renderKey = sdk.idempotencyKey(); // persist this before dispatch when recovery matters
const operation = await project.render.export(
  {
    timeline,
    precondition: snapshot.revision,
    output: { baseName: "final-review" },
    settings: {
      format: "mp4",
      codec: "h264",
      width,
      height,
      exportVideo: true,
      exportAudio: true,
    },
  },
  { idempotencyKey: renderKey },
);

const terminal = await operation.wait();
if (terminal.status !== "succeeded") {
  throw new Error(
    `Render ${operation.operationId} ended as ${terminal.status}; inspect the terminal before retrying.`,
  );
}

const { artifact } = terminal.result;
if (
  artifact.media.width !== width ||
  artifact.media.height !== height ||
  artifact.media.videoCodec === null ||
  artifact.media.audioCodec === null
) {
  throw new Error("The verified artifact does not match the requested streams.");
}

await artifact.copyTo("/absolute/caller-owned/final-review.mp4");
```

`output.baseName` is a base name, not a destination path. CutAgent owns the temporary render destination and returns a sanitized artifact receipt. Copy the artifact to a new caller-owned path before `artifact.availableUntil`; `copyTo()` verifies size and SHA-256 and refuses to overwrite an existing file.

Omit `width`, `height`, or `frameRate` only when DaVinci Resolve's current/default value is intentional. If you specify dimensions, specify both. The result's `artifact.media` is independently probed technical metadata; compare every property that matters to the delivery.

## Render a range

The managed export defaults to the full timeline. A custom range uses record-domain frame offsets from the timeline start, with an exclusive end:

```ts
const range = { kind: "custom", startFrame: 0, endExclusiveFrame: 48 } as const;
```

Pass `range` in the export options. This renders the first 48 timeline frames even when the timeline starts at a nonzero timecode. Do not substitute absolute record frames, source frames, or Fusion composition time. See [Timing and targets](timing-and-targets.md) when translating an editorial interval.

## Start existing queue jobs

`project.render.queue` does not add, delete, reorder, or edit jobs. It can inspect the existing queue and start one job or several jobs together:

```ts
const page = await project.render.queue.list({ pageSize: 100 });
const selected = page.jobs.filter((job) => job.name.startsWith("Client review"));
if (selected.length === 0) throw new Error("No matching queued render jobs.");

const operation = await project.render.queue.start(selected, {
  idempotencyKey: sdk.idempotencyKey(),
});
const terminal = await operation.wait();
if (terminal.status !== "succeeded") {
  throw new Error(`Queue run ended as ${terminal.status}.`);
}
```

Pass intact job snapshots from the same queue revision; do not retain only their IDs or combine jobs from different pages/revisions. One call accepts at most 100 jobs. `job.refreshStatus()` deliberately fails stale if the queue structure changed or the job disappeared.

## Interpret completion and cancellation

`operation.wait()` returns a discriminated terminal state. A wait timeout or aborted wait stops only local polling; it does not stop the native render. Reattach to the durable operation or continue waiting. To request an actual stop, call `operation.requestCancellation()` and inspect the resulting authority state; cancellation is not confirmed merely because the request returned.

Before retrying any `partially_applied`, `verification_failed`, or `recovery_failed` terminal, inspect `possibleMutation`, `failure`, `verification`, and `recovery`. Render settings, a queue job, or a partial output may already exist. Follow [Errors and recovery](errors-and-recovery.md) rather than starting a second export with a new idempotency key.

A `succeeded` export proves that the correlated native job completed and that the returned bytes, digest, and reported streams passed technical verification. It does not prove the edit, grade, mix, captions, motion, or visual match is correct. Review representative frames and, for motion or time-varying work, multiple frames or playback; inspect or listen to audio when audio matters. See [Checking results](checking-results.md).

For a final-delivery review, include the first and final output frames plus representative interior frames. Compare an unexpected black, frozen, offline, or missing-effect boundary with the same timeline boundary before deciding whether it is intentional content or an export defect.

## Current semantic boundaries

- `project.render.export()` creates one file. Its accepted output families are QuickTime, MP4, MXF, Wave, and AIFF; its accepted codec families are H.264, H.265, ProRes, DNxHR, AV1, Linear PCM, AAC, and FLAC. Discovery may report additional formats such as DCP or image sequences, but that does not make them valid managed-export inputs.
- The semantic request covers format, codec, optional resolution and frame rate, video/audio enablement, full-timeline or custom range, and base name. It does not expose arbitrary native render-setting keys, destination directories, preset loading/saving, subtitle or burn-in configuration, bitrate/profile controls, alpha settings, or audio track routing.
- `project.render.presets()` lists names without loading them. `project.render.settings()` is a sanitized read; its revision describes that settings projection, not a timeline revision.
- For a delivery requirement outside this surface, consult the current installed command catalog through [CLI](cli.md) and confirm the exact command capability before use. Do not translate raw DaVinci Resolve labels into semantic SDK values or assume a CLI command provides managed artifact custody.

For connection, operation reattachment, and standalone imports, see [SDK](sdk.md).
