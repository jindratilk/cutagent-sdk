---
name: cutagent
description: Inspect, edit, composite, mix, caption, color, and render DaVinci Resolve projects through the CutAgent SDK or CLI. Use for CutAgent automation, existing-timeline work, or authoring a CutAgent skill; skip for general video advice that does not operate DaVinci Resolve.
---

# CutAgent

Use CutAgent to operate DaVinci Resolve through either the SDK or CLI. Prefer semantic SDK objects in scripts; use current CLI commands when clearer. Do not infer methods from adjacent capabilities.

Target the exact current project, timeline, and snapshot revision. Refresh the snapshot after a mutation before making a dependent change. Inspect partial or uncertain results before retrying.

Read only the references that match the request.

## Choose the workflow

- For installation, connection, editions, or first use, read [Setup](./references/setup.md).
- For SDK imports, runner context, time values, or operations, read [SDK usage](./references/sdk.md).
- For terminal commands or JSON envelopes, read [CLI usage](./references/cli.md).
- For a new project or timeline, read [Create a video](./references/create-video.md).
- For an existing timeline, read [Edit an existing video](./references/edit-existing.md).
- For positions, ranges, frame rates, tracks, handles, or snapshot targets, read [Timing and targets](./references/timing-and-targets.md).
- For failures, timeouts, disconnects, or partial application, read [Errors and recovery](./references/errors-and-recovery.md).
- For structural, visual, motion, render, or audition checks, read [Checking results](./references/checking-results.md).

## Route by domain

- Projects, timelines, Media Pool, import, metadata, relink, or sync: [Projects and media](./references/projects-and-media.md).
- Cuts, inserts, overwrites, trims, moves, markers, or properties: [Editing](./references/editing.md).
- Variable speed, freeze, reverse, or retime curves: [Speed ramps](./references/editing/speed-ramps.md).
- Edit transitions: [Transitions](./references/editing/transitions.md).
- Inspector transforms or clip keyframes: [Transforms and keyframes](./references/editing/transforms-and-keyframes.md).
- Linked picture and sound, split edits, or J/L cuts: [Linked audio and J/L cuts](./references/editing/linked-audio-and-jl-cuts.md).
- Fairlight editing and mixing: [Audio](./references/audio.md).
- Metering, normalization, loudness, compression, or limiting: [Loudness and dynamics](./references/audio/loudness-and-dynamics.md).
- Color inspection, corrections, nodes, LUTs, stills, groups, or tracking: [Color](./references/color.md).
- Multicam creation, switching, or flattening: [Multicam](./references/multicam.md).
- Subtitles, designed Text+ captions, transcription, or cue layout: [Captions](./references/captions.md).
- Generated video or voice assets: [Generation](./references/generation.md).
- Render discovery, settings, queue state, codecs, or artifacts: [Rendering](./references/rendering.md).

## Route Fusion work

- Any Fusion composition: [Fusion](./references/fusion/REFERENCE.md).
- Nodes, ports, connections, or typed graphs: [Graph basics](./references/fusion/graph-basics.md).
- Native Lua-table `.setting` documents: [Setting files](./references/fusion/setting-files.md).
- Keyframes, splines, easing, or tangents: [Animation](./references/fusion/animation.md).
- Text+, fonts, glyphs, sizing, or layout: [Text and layout](./references/fusion/text-and-layout.md).
- Multi-frame checks, graph diagnostics, or broken imports: [Preview and debugging](./references/fusion/preview-and-debugging.md).

When creating or revising reusable CutAgent agent instructions, read [Skill authoring](./references/skill-authoring.md).
