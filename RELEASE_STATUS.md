# CutAgent SDK release status

The standalone package contains the TypeScript SDK and local CutAgent CLI runtime under AGPL-3.0-only. Install from source using the README. npm registry publication is not part of this source release.

## Platforms and verification

Current standalone setup supports macOS. Windows setup and live qualification remain outstanding. Studio-only features require DaVinci Resolve Studio. A fresh live DaVinci Resolve Free acceptance of this exact source remains outstanding.

Source inventory, build, strict TypeScript checks, runtime tests, and installed-package setup/status/uninstall are checked separately from live editing. Passing those checks does not establish complete native or cross-platform coverage.

## Current behavior and limitations

- Media Pool inspection tolerates unavailable metadata for file-less native generators. Media moves accept exact source paths or native media identities and reject ambiguous selectors before mutation.
- Multicam preserves explicitly authored offsets. Waveform analysis reports offset and unsigned drift span; complete nondestructive clock-drift correction is not provided through the SDK.
- Clip-local marker batching requires V1 clips with ordinary forward timing and matching source/timeline frame rates. Retimed clips are rejected.
- Individual audio fade preview uses native bounds for very short clips. Native crossfade preview still uses the existing SQLite bounds for very short sample-addressed clips and has not been qualified for that case.
- Hosted AI transcription, voice generation, and video generation require the separate CutAgent desktop app. They are not hosted services supplied by this standalone package.

No new full end-to-end, Windows, or live DaVinci Resolve acceptance is claimed by documentation or fixture maintenance.

Agent Knowledge and creative skills are not included in this release or its package. Earlier published versions are unchanged.
