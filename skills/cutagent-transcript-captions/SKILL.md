---
name: cutagent-transcript-captions
description: Turn a fresh timeline transcript into readable native subtitles, designed Text+ captions, or both. Use for accessibility captions, SRT-style delivery, burned-in social captions, branded on-screen text, or transcript-led emphasis.
license: AGPL-3.0-only
---

# Transcript captions

Make each cue effortless to read at the speed and scale of the final video. Preserve semantic subtitles when accessibility or localization matters; use Text+ when typography and motion are part of the edit.

## Choose the representation

- Use native subtitles for searchable, editable, exportable language tracks.
- Use designed Text+ captions for branded typography, per-cue composition, emphasis, or motion.
- Use both when the video needs a visible design and a semantic sidecar/localization source.

For local execution, read `cutagent-captions`, `cutagent-fusion`; check the installed SDK declarations, public CutAgent CLI command cards, and live capabilities for exact operations.

## Segment for meaning

Work from a fresh transcript of the actual target timeline. Break on speaker changes, completed thoughts, clause boundaries, and meaningful pauses. Keep tightly connected grammar together and avoid orphaning one word. Every spoken token should appear once unless the user explicitly requests editorial paraphrase.

Choose cue length from the frame size, type scale, language, speech pace, and design. Prefer one line for fast social captions; use two lines only when the composition and reading rhythm benefit. Give short cues enough screen time to register and split dense cues before shrinking the type into illegibility.

## Design the system

Create a small visual grammar: base style, emphasis style, speaker treatment when needed, safe area, and motion rule. Emphasize only words that carry meaning; highlighting every noun or every spoken word produces noise.

Use `assets/text-plus-caption-clean.setting` as a plain editable starting graph when it fits. For a distinctive treatment, author an original `.setting` or supported Fusion graph with deliberate typography, boxes, masks, and native keyframes. Do not take a purchased template, replace its text, and call that original caption design.

Motion should help the eye acquire the cue. A subtle rise, scale settle, wipe, or word emphasis is usually enough. Leave the cue readable before animating it away.

## Review

Review the complete cue plan before insertion, then inspect beginning, middle, end, fastest speech, longest line, speaker change, and difficult name. Check spelling, timing, line breaks, safe margins, contrast, occlusion, repeated/missing words, and animation holds. Structural readback proves cues and ranges; representative frames and playback prove legibility and motion.

Report the representation, segmentation logic, style system, cue count, language/name issues, and structural/visual/temporal evidence.
