# Graphic-accent construction recipes

These recipes define editable graphic structure and behavior. Use the installed public CutAgent SDK and CLI reference and live inspection for the exact node, mask, stroke, path, and animation identifiers available in the connected runtime.

## Arrow or pointer

Construct the shaft and arrowhead as one coherent mark or two grouped shapes:

```text
shaft shape ----\
                 Merge/group -> pointer Transform -> composite over footage
arrowhead shape-/
```

Keep shaft thickness and arrowhead proportions visually related. Set the pivot near the tail for a pointing swing or near the center for a simple placement move. Aim the tip at the target while leaving a small air gap so the icon or face remains visible.

For a draw-on, reveal the shaft from tail to tip, then reveal or pop the arrowhead just before completion. For a direct cue, animate the whole pointer a short distance along its pointing vector and settle once. Hold it still while the viewer identifies the target.

## Circle or highlight ring

Build a stroked ellipse or path on transparency and position it around the target:

```text
ring geometry -> color/softness -> ring Transform -> composite
```

Use an intentionally imperfect path only when the project's graphic language is hand-drawn; otherwise keep the ring clean. Reveal clockwise or in the direction implied by surrounding motion. A ring should enclose the target with breathing room, not touch or obscure it. For a pop, key scale from small to slightly large to exact rest while opacity arrives quickly.

## Underline or connector

Create a path whose visible length can grow from one endpoint:

```text
line path -> animated write/reveal -> optional end dot -> composite
```

Match underline width to the focal word rather than extending across the whole text block. Start under the reading origin and draw toward the reading direction. Keep a small gap below the glyphs so descenders remain clear. A connector between two objects should appear after both endpoints are visible.

## Star or burst punctuation

Use a simple editable star/burst silhouette and animate the group Transform:

```text
star geometry -> fill/outline -> Transform -> composite
```

Start invisible and small, reach one modest overshoot, then settle. Add a brief rotation only if it improves the pop. For several stars, vary scale and angle but keep the same stroke/fill logic; stagger them by a few frames around one beat. Freeze them during the reading hold or remove them quickly.

## Labeled callout

Build label content and pointer separately, merge them, then place the combined callout with one parent transform:

```text
backing shape -> label Merge --\
Text+ ------------------------- parent Transform -> composite
pointer ----------------------/
```

Fit the backing to the longest real label and preserve padding. Keep the pointer tip bound to the target while placing the label in nearby negative space. If the target moves, use the supported tracking workflow for target motion and add only a small deliberate label offset; do not hand-key a few positions and claim tracking.

## Cue timing and adaptation

Use four phases: hidden, reveal, hold, remove. Reveal just before or with the spoken reference. The hold should cover the noun and enough following context to locate the target. Remove the cue before a new target competes.

When delivery aspect ratio changes, reposition the group from the actual target and safe areas; do not reuse normalized coordinates blindly. When labels change, refit the backing and pointer before adjusting font size. Review the first visible frame, fully formed mark, settled hold, and last visible frame, then play through the spoken cue.
