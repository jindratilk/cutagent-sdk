# Projects and Media

Read this when selecting a project, inspecting or organizing the Media Pool, importing or relinking media, editing metadata, deleting assets, or synchronizing production audio.

Keep project context, Media Pool observations, and mutation targets distinct. A Media Pool page is an immutable observation at one pool revision. Only an observation with a non-null durable `id` can become a mutation reference. Use its revision as the mutation precondition.

## Project context

The `cutagent-sdk` runner supplies `client`, `project`, `timeline`, and `snapshot` after checking the current context. Reuse them instead of reconnecting. `client.projects.context()` reports the current library, project, timeline, and project revision; `client.projects.current()` returns the exact current project.

Project changes use `context.projectRevision`, not a timeline or Media Pool revision. Create, open, restore, rename, change settings, or back up only when that revision is available, and give each mutation a caller-owned idempotency key. After a create, open, restore, library switch, or rename, reacquire the current project and context.

`projects.open()` requires an exact `ProjectReference` containing both durable `id` and name; never invent an ID from a name. PostgreSQL library identities are inspectable, but the current semantic SDK permits local create, open, backup, and restore only for Disk libraries.

## Inspect the Media Pool

`project.mediaPool.snapshot()` returns folders and assets in pages of at most 32 combined entries. `nextPage()` continues the same observation, returns `null` at the end, and fails with `STALE_REVISION` if the pool changes between pages.

Prefer `search()` for case-insensitive asset search across curated `name`, `metadata`, and `sourceFileName` fields. It does not search bins. `assetByName()` requires one exact display-name match and rejects zero or multiple matches.

Asset snapshots expose normalized kind, selection, source basename, duration, resolution, source frame-rate text, source start timecode, and curated metadata when DaVinci Resolve exposes them. `metadataAvailable: false` differs from an available empty list. Local source directories and arbitrary native metadata keys are not exposed. A snapshot with `id === null` is inspectable but cannot be passed to `mediaPool.asset()` or `mediaPool.bin()`.

## Reuse an existing asset

When the request identifies media already in the project, reuse the exact durable Media Pool asset instead of importing its source again or rebuilding a styled item. Preserve a compound clip, nested timeline, adjustment clip, title, generator, or Fusion-based asset as an opaque user-authored object unless the user asked to change its internals.

Do not choose the first same-name result. Narrow candidates with the fields the public snapshot exposes, such as kind, source basename, duration, resolution, and curated metadata; ask for a choice if those observations still do not establish one identity. Effects Library presets and Fusion `.setting` files are not Media Pool assets. Use the relevant title, generator, or Fusion-template route for those sources, then use [editing](editing.md) for timeline placement of a durable Media Pool asset.

## Import into an exact bin

Import all files for one destination with one `importMedia()` call. The semantic path accepts exact existing regular files, not a directory, symlink, URL, or guessed codec. Trust the returned asset identities instead of assuming every requested path produced an asset.

```js
// import-media.mjs — run with:
// cutagent-sdk --title "Import project media" /absolute/path/import-media.mjs
async function requireSuccess(handle) {
  const terminal = await handle.wait();
  if (terminal.status !== "succeeded") {
    console.error(terminal);
    throw new Error(`Operation ended as ${terminal.status}`);
  }
  return terminal;
}

async function readWholePool(pool) {
  const folders = [];
  const assets = [];
  let page = await pool.snapshot({ pageSize: 32 });
  const revision = page.revision;
  while (page) {
    folders.push(...page.folders);
    assets.push(...page.assets);
    page = await page.nextPage();
  }
  return { revision, folders, assets };
}

export default async function ({ sdk, project, progress }) {
  const pool = project.mediaPool;
  const observed = await readWholePool(pool);
  const bins = observed.folders.filter(
    (folder) => folder.name === "Selects" && folder.depth === 1,
  );
  if (bins.length !== 1) {
    throw new Error(`Expected one top-level Selects bin; found ${bins.length}`);
  }

  progress("Importing camera and production audio");
  const terminal = await requireSuccess(await pool.importMedia(
    {
      paths: ["/absolute/media/A001.mov", "/absolute/media/A001.wav"],
      destination: pool.bin(bins[0]),
    },
    { precondition: observed.revision, idempotencyKey: sdk.idempotencyKey() },
  ));

  console.log({ imported: terminal.result.assets, verification: terminal.verification });
}
```

Create a bin with `mediaPool.createBin({ name, parent? }, options)`; omit `parent` for the root. Refresh the pool before using the new bin in another mutation. A verified create may still return `folder.id === null`, which is not a durable destination.

## Organize and maintain assets

- The high-level object model does not yet expose clip moves. Use its typed escape hatch for one shared list operation: `client.actions.invoke("cutagent.action.media.move", { moves: [{ name: "A001.mov", target: "Selects" }, { name: "A001.wav", target: "Audio" }] }, { idempotencyKey: sdk.idempotencyKey() })`. Await the returned handle. This action targets clip and bin names, so preflight exact names and avoid ambiguity.
- `asset.relink({ path }, options)` relinks one durable asset to an exact replacement file.
- `asset.setMetadata(entries, options)` accepts unique curated keys. Read the installed `MediaPoolMetadataKey` union instead of guessing native labels.
- `mediaPool.delete(assetOrList, options)` performs one native deletion. Prefer the list form to looping deletes against one stale revision.
- `mediaPool.syncAudio(video, audioList, { method, appendTracks? }, options)` accepts same-project durable assets from one revision. `method` is `"waveform"` or `"timecode"`; `appendTracks` defaults to `true`.
- `asset.transcription({ useNestedClipTranscription? })` reads transcription already persisted by DaVinci Resolve; it does not start transcription. See [captions.md](captions.md) to create transcription or place captions.

Except for the low-level move action, these mutations require `{ precondition: observedRevision, idempotencyKey }`. A success makes old pool references stale. Before the next mutation, inspect only the target state needed for a fresh revision and references: prefer `assetByName()` or `search()` for an asset task, and traverse all pages only for hierarchy or inventory work.

## Verify and recover

Creating a handle is not success. Await `handle.wait()`. `succeeded` is required for complete success and includes the typed result plus verification; non-success terminals can retain a typed partial result, verification, or recovery evidence that must not be discarded. After an uncertain response, reuse the original idempotency key.

Structural readback is normally appropriate for Media Pool changes. Audio-sync readback proves the registered relationship, not perceptual quality; audition representative material before claiming it sounds synchronized. See [checking-results.md](checking-results.md) for evidence choice, [errors-and-recovery.md](errors-and-recovery.md) for terminal handling, [timing-and-targets.md](timing-and-targets.md) before timeline placement, and [multicam.md](multicam.md) when preparing camera angles.
