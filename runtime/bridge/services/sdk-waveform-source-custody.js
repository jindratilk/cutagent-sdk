import crypto from "node:crypto";
import {open, lstat, realpath} from "node:fs/promises";
import path from "node:path";

const sha256 = (value) => crypto.createHash("sha256").update(value).digest("hex");
function identity(stat) {
  return {device: stat.dev.toString(), inode: stat.ino.toString(), size: stat.size.toString(), modifiedNanoseconds: stat.mtimeNs.toString(), changedNanoseconds: stat.ctimeNs.toString()};
}
function sameIdentity(left, right) {
  return JSON.stringify(identity(left)) === JSON.stringify(identity(right));
}

/** Private preparation only; this does not register a new trusted filesystem root.
 * Every accepted path must resolve to one exact source in the captured project.
 * Activation requires an independent CLI-side custody verifier.
 */
export async function captureWaveformProjectSources({liveInspectionService, projectId, paths}) {
  if (typeof projectId !== "string" || !projectId || !Array.isArray(paths) || paths.length !== 2
    || paths.some((file) => typeof file !== "string" || !path.isAbsolute(file))
    || new Set(paths).size !== paths.length) throw new Error("Waveform source custody requires two distinct absolute project-source paths.");
  let offset = 0, revision = null, poolDigest = null;
  const matches = new Map(paths.map((file) => [file, []]));
  do {
    const page = await liveInspectionService.readWithMutationGuard({operation: "mediaPool.page", projectId, offset, pageSize: 32, expectedRevision: revision, search: null});
    const state = page.privateMediaPoolState;
    if (!state || !Array.isArray(state.entries) || !state.poolDigest || page.value?.project?.id !== projectId
      || typeof page.value.revision !== "string" || !page.value.revision) throw new Error("Waveform source custody has no exact private pool readback.");
    revision ??= page.value.revision;
    poolDigest ??= state.poolDigest;
    if (page.value.revision !== revision || state.poolDigest !== poolDigest) throw new Error("Waveform source pool changed during preparation.");
    for (const entry of state.entries) {
      if (entry.entryKind === "asset" && matches.has(entry.sourcePath)) matches.get(entry.sourcePath).push(entry);
    }
    const next = page.value.nextOffset;
    if (next !== null && (!Number.isSafeInteger(next) || next <= offset)) throw new Error("Waveform source pool pagination is invalid.");
    offset = next;
  } while (offset !== null);
  const result = [];
  for (const file of paths) {
    const candidates = matches.get(file);
    if (candidates.length !== 1 || !candidates[0].id || !candidates[0].nativeId || !["audio", "video"].includes(candidates[0].kind)) throw new Error("Waveform source is missing or ambiguous in the exact project.");
    const entry = candidates[0];
    const before = await lstat(file, {bigint: true});
    if (!before.isFile() || before.isSymbolicLink() || await realpath(file) !== file) throw new Error("Waveform source must be an exact regular file without symlink traversal.");
    const handle = await open(file, "r");
    try {
      if (!sameIdentity(before, await handle.stat({bigint: true}))) throw new Error("Waveform source identity changed during admission.");
    } finally { await handle.close(); }
    const after = await lstat(file, {bigint: true});
    if (!after.isFile() || after.isSymbolicLink() || !sameIdentity(before, after) || await realpath(file) !== file) throw new Error("Waveform source path changed during preparation.");
    // This read-only operation binds a live project source, not an uploaded
    // content-addressed artifact. Never scan hundreds of GB of video for custody.
    // Change time also rejects in-place writes that restore size and mtime.
    const fileIdentity = identity(before);
    const sourceIdentityDigest = `sha256:${sha256(JSON.stringify([
      "waveform-project-source-v1", file, ...Object.values(fileIdentity),
    ]))}`;
    result.push({
      stableId: `artifact_${sha256(file).slice(0, 32)}`, resolvedPath: file, sourceIdentityDigest,
      revision: `revision_${sha256(`${file}${sourceIdentityDigest}`).slice(0, 32)}`,
      allowedRootId: "exact_project_media_source", sourceProjectId: projectId,
      sourceMediaPoolItemId: entry.id, sourceNativeId: entry.nativeId,
      sourceMediaPoolRevision: revision, sourcePoolDigest: poolDigest, sourceFileIdentity: fileIdentity,
    });
  }
  if (new Set(result.map((item) => `${item.sourceFileIdentity.device}:${item.sourceFileIdentity.inode}`)).size !== result.length) throw new Error("Waveform sources refer to the same file identity.");
  return result;
}

/** Narrow private callback: no caller-chosen paths or arbitrary media reads. */
export async function readCapturedWaveformSources({request, captured, payload, liveInspectionService}) {
  const sources = captured.privateContext?.waveformSources;
  if (request.actionId !== "cutagent.action.audio.waveform_offset" || !Array.isArray(sources) || sources.length !== 2
    || payload.operation !== "audio.waveform.sources" || payload.projectId !== request.identities.projectId
    || payload.timelineId !== request.identities.timelineId || !["current", "verify"].includes(payload.phase ?? "current")
    || Object.keys(payload).some((key) => !["operation", "projectId", "timelineId", "phase", "mediaPoolItemIds"].includes(key))
    || JSON.stringify(payload.mediaPoolItemIds) !== JSON.stringify(sources.map((source) => source.sourceMediaPoolItemId))) {
    throw new Error("Waveform source callback escaped captured project-media custody.");
  }
  const rows = await liveInspectionService.resolvePreparedTimelineMedia({projectId: request.identities.projectId, mediaPoolItemIds: payload.mediaPoolItemIds});
  if (!Array.isArray(rows) || rows.length !== sources.length || rows.some((row, index) => {
    const source = sources[index];
    return row.mediaPoolItemId !== source.sourceMediaPoolItemId || row.nativeId !== source.sourceNativeId
      || row.sourcePath !== source.resolvedPath || row.revision !== source.sourceMediaPoolRevision
      || row.poolDigest !== source.sourcePoolDigest || !["video", "audio"].includes(row.kind);
  })) throw new Error("Waveform source changed after exact project-media admission.");
  return {operation: payload.operation, value: rows};
}
