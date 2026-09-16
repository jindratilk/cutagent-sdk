# CutAgent SDK 3.0.1 — source release status

The source includes the reviewed native SDK repairs integrated into CutAgent 3.0 on 2026-09-15. The standalone package uses AGPL-3.0-only; desktop application and private Creator Skills are not included.

The standalone package passed source inventory verification, build, strict TypeScript checks, runtime tests, and installation from an npm tarball, including setup/status/uninstall. npm registry publication is pending; use the source installation instructions until it is available.

The integrated upstream implementation was tested in an isolated macOS DaVinci Resolve Studio 21.1 instance: FCPXML import, three compiled Fusion layers with Unicode persistence after project reopen, clip-edge transitions, waveform synchronization with a known offset, nonzero-timecode multicam, clip-local markers and clip colors. These upstream native tests do not substitute for complete standalone package or Windows qualification.

Clip-local marker batching currently requires V1 clips with ordinary forward timing and matching source/timeline frame rates. Retimed clips are rejected. Waveform analysis exposes offset and unsigned drift span; this release does not provide a complete nondestructive clock-drift correction workflow through the SDK.

## DaVinci Resolve Free

The earlier Free handoff covers import, marker create/read/delete, transforms and H.264 output on its tested source. Its configured launcher binding, owned broker lifecycle, render admission and checkpoint fixes are retained. Current standalone runtime tests cover those integrations; a fresh live Free acceptance of this exact release remains outstanding.

## Platforms

Current standalone setup supports macOS. Windows setup and live qualification remain outstanding. Studio-only features require DaVinci Resolve Studio. Hosted AI services and private Creator Skills belong to the separate CutAgent desktop application.

## 3.0.1 focused patch

Preserves explicitly authored multicam offsets, uses native bounds for very short audio fade previews, tolerates only floating-point fade readback noise (at most 1e-8 frame), batches independent fade curves in one native database transaction, requests fresh post-mutation transition verification, and appends audio-only batches as audio. Transcript render preset cleanup restores the pre-existing preset catalog. Hosted transcription changes belong to the separate desktop runtime.

The upstream patch passed 449 targeted Python tests, 34 bridge tests and five SDK Fairlight tests. Its earlier real macOS DaVinci Resolve evidence includes the completed podcast run and an isolated six-edge transition verification without recovery. These are bounded existing observations, not a new full end-to-end or Windows acceptance of 3.0.1.

Known remaining case: native crossfade preview still uses the existing SQLite bounds for very short sample-addressed clips; this patch corrects individual fade preview only. That separate crossfade change has not been qualified here.
