import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { build } from "esbuild";

const buildRoot = await mkdtemp(path.join(tmpdir(), "cutagent-fusion-settings-test-"));
const bundle = path.join(buildRoot, "fusion-settings.mjs");
await build({
  stdin: {
    contents: [
      'export * from "./src/fusion/runtime.ts";',
      'export { duration, frames, timelineRecordPosition } from "./src/value-types/time.ts";',
    ].join("\n"),
    resolveDir: fileURLToPath(new URL("../sdk/", import.meta.url)),
  },
  bundle: true,
  platform: "node",
  format: "esm",
  target: "node22.12",
  outfile: bundle,
  legalComments: "none",
});
const { createFusionCompositions, duration, frames, timelineRecordPosition } = await import(pathToFileURL(bundle).href);
test.after(async () => rm(buildRoot, { recursive: true, force: true }));

const PROJECT_ID = "project_fusion_settings_1234";
const TIMELINE_ID = "timeline_fusion_settings_1234";
const REVISION = "revision_fusion_settings_before_1234";
const ACTION_ID = "cutagent.action.fusion.insert_settings.batch";

function insertion(index) {
  return {
    settingArtifactId: `artifact_setting_${index}_1234`,
    clipName: `Graphic ${index}`,
    recordPosition: timelineRecordPosition(frames(index * 48)),
    clipDuration: duration(frames(24 + index)),
    videoTrackIndex: index + 1,
    position: { x: index / 10, y: -index / 10 },
    text: `Title ${index}`,
    imageArtifactId: `artifact_image_${index}_1234`,
    styleMarkdown: index % 2 === 0,
    boldStyle: index % 2 === 0 ? "Bold" : "Semibold",
  };
}

function runtime() {
  const calls = [];
  return {
    calls,
    generation: 1,
    async readAtGeneration() { throw new Error("unexpected read"); },
    async startAction(generation, actionId, input, resultSchema, options) {
      calls.push({ generation, actionId, input, options });
      const items = input.items.map((item, index) => ({
        timelineItemId: `timeline_item_inserted_${index}_1234`,
        clipName: item.clipName,
        recordPosition: item.recordPosition,
        clipDuration: item.clipDuration,
        videoTrackIndex: item.videoTrackIndex,
      }));
      const result = resultSchema.parse({
        actionId,
        insertedItems: {
          items,
          revision: {
            revisionBefore: input.revision,
            revisionAfter: "revision_fusion_settings_after_1234",
            changed: true,
          },
        },
      });
      return { actionId, result };
    },
  };
}

test("Fusion setting insertion normalizes one item and dispatches the plural native action once", async () => {
  const target = runtime();
  const fusion = createFusionCompositions(target, 1, PROJECT_ID, TIMELINE_ID);
  const handle = await fusion.insertSettings(insertion(1), {
    precondition: REVISION,
    idempotencyKey: "idempotency_fusion_settings_single_1234",
  });

  assert.equal(target.calls.length, 1);
  assert.equal(target.calls[0].actionId, ACTION_ID);
  assert.equal(target.calls[0].input.items.length, 1);
  assert.deepEqual(target.calls[0].input.items[0].recordPosition, {
    domain: "timeline_record",
    value: { kind: "frames", value: 48 },
  });
  assert.deepEqual(target.calls[0].input.items[0].clipDuration, {
    domain: "duration",
    value: { kind: "frames", value: 25 },
  });
  assert.equal(handle.result.items.length, 1);
  assert.equal(Object.isFrozen(handle.result.items), true);
});

test("Fusion setting insertion preserves ordered per-item templates, placement, and parameters in one dispatch", async () => {
  const target = runtime();
  const fusion = createFusionCompositions(target, 1, PROJECT_ID, TIMELINE_ID);
  const input = [insertion(1), insertion(2), insertion(3)];
  const handle = await fusion.insertSettings(input, {
    precondition: REVISION,
    idempotencyKey: "idempotency_fusion_settings_many_1234",
  });

  assert.equal(target.calls.length, 1);
  assert.deepEqual(
    target.calls[0].input.items.map(({ settingArtifactId, clipName, videoTrackIndex, text, imageArtifactId, position }) => (
      { settingArtifactId, clipName, videoTrackIndex, text, imageArtifactId, position }
    )),
    input.map(({ settingArtifactId, clipName, videoTrackIndex, text, imageArtifactId, position }) => (
      { settingArtifactId, clipName, videoTrackIndex, text, imageArtifactId, position }
    )),
  );
  assert.deepEqual(handle.result.items.map((item) => item.clipName), ["Graphic 1", "Graphic 2", "Graphic 3"]);
});

test("Fusion setting insertion rejects an empty list before transport", async () => {
  const target = runtime();
  const fusion = createFusionCompositions(target, 1, PROJECT_ID, TIMELINE_ID);
  await assert.rejects(
    () => fusion.insertSettings([], {
      precondition: REVISION,
      idempotencyKey: "idempotency_fusion_settings_empty_1234",
    }),
    /requires at least one item/,
  );
  assert.equal(target.calls.length, 0);
});

for (const explicitUndefined of [false, true]) {
  test(`Fusion text-only settings omit optional image data (explicit undefined: ${explicitUndefined})`, async () => {
    const target = runtime();
    const fusion = createFusionCompositions(target, 1, PROJECT_ID, TIMELINE_ID);
    const item = insertion(1);
    delete item.imageArtifactId;
    if (explicitUndefined) item.imageArtifactId = undefined;
    const handle = await fusion.insertSettings([item, { ...item, clipName: "Second title" }], {
      precondition: REVISION,
      idempotencyKey: "idempotency_fusion_text_only_1234",
    });
    assert.equal(target.calls.length, 1);
    assert.equal(handle.result.items.length, 2);
    assert.equal(Object.hasOwn(target.calls[0].input.items[0], "imageArtifactId"), false);
  });
}


test("Fusion setting insertion sends 1019 items in one operation", async () => {
  const target = runtime();
  const fusion = createFusionCompositions(target, 1, PROJECT_ID, TIMELINE_ID);
  const input = Array.from({ length: 1019 }, (_, index) => insertion(index + 1));
  const handle = await fusion.insertSettings(input, {
    precondition: REVISION,
    idempotencyKey: "idempotency_fusion_settings_large_1234",
  });
  assert.equal(target.calls.length, 1);
  assert.equal(target.calls[0].input.items.length, 1019);
  assert.equal(handle.result.items.length, 1019);
});
