---
name: cutagent-screen-camera-pip-sync
description: Synchronize a screen recording with a camera or webcam and design an editable picture-in-picture layout. Use for screencasts, tutorials, product demos, courses, streams, and social edits with a facecam overlay.
license: AGPL-3.0-only
---

# Screen and camera PiP

Keep the screen readable, the presenter present, and the synchronization invisible. The facecam should clarify the experience without covering the interface it is meant to explain.

## Establish the sources

Identify the exact screen, camera, and primary microphone. Use waveform sync when trustworthy shared audio exists; otherwise require a shared clock, visual event, or confirmed start relationship. Do not infer synchronization from similar filenames or durations.

Choose the useful common range and one programme-audio source. Avoid doubled screen, webcam, and external-mic scratch audio.

## Design the layout

Inspect the real screen content before choosing a corner. Place the camera where it avoids menus, captions, notifications, cursor targets, and demonstrated controls. Start near a safe corner, then adapt per section when important UI moves.

Size for facial expression at the delivery scale without dominating the screen. Keep edge margins optically even, crop distracting camera edges, and use a subtle corner radius only when it fits the visual language. For vertical delivery, recompose the screen first and then place the camera within the new hierarchy.

Use `assets/rounded-camera-pip.setting` only as a small editable Fusion scaffold for a simple rounded camera branch. For a custom shape, border, shadow, entrance, or responsive layout, author an original connected graph from the brief; do not import a purchased template and merely replace its text or media.

For local execution, read `cutagent-editing`, `cutagent-fusion`, `cutagent-audio`, `cutagent-verification`; check the installed SDK declarations, public CutAgent CLI command cards, and live capabilities for exact operations.

## Add motion sparingly

Let the PiP enter when the presenter becomes useful and leave when the screen needs full attention. Use a short, readable move with restrained easing; avoid perpetual bouncing or zooming. If the facecam changes corners, motivate the move with the screen content and keep it clear of the cursor path.

## Review

Inspect representative frames across every PiP section and a short playback around entrances, exits, and corner changes. Confirm screen content remains legible, the camera is visible, the outside of the mask is transparent, edges do not show a black rectangle, and synchronization stays stable early and late.

Report the sources, sync authority, audio choice, PiP scope and placement, editable graph treatment, and visual/temporal evidence.
