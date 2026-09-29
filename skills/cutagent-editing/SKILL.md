---
name: cutagent-editing
description: Build or revise native DaVinci Resolve timelines with CutAgent SDK or CutAgent CLI. Use for clips, trims, linked audio, transitions, retiming, and exact placement.
license: AGPL-3.0-only
---

# Timeline editing

Identify the exact clip occurrence, track, timeline revision, source range, and record range before editing. A media name is not an occurrence identity. Keep source frames, timeline record frames, and Fusion composition frames separate; inspect actual frame rates and nonzero timeline starts before converting time. Preserve linked audio and protected neighboring material.

For inserts, trims, splits, moves, speed changes, or transitions, inspect enough surrounding context to understand the seam. Use the installed SDK preview and operation contract or the relevant public CutAgent CLI card. Check source handles and any overlap before transition or retime work. Refresh the timeline snapshot after mutations. Verify both edit structure and playback across changed boundaries; for speed or motion, inspect more than one frame.
