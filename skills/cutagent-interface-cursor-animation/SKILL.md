---
name: cutagent-interface-cursor-animation
description: Create editable cursor-led interface animations in DaVinci Resolve Fusion for software demos, screen recordings, product walkthroughs, tutorials, and UI callouts.
license: AGPL-3.0-only
---

# Interface cursor animation

Make the cursor explain the interaction. Its path, state, and emphasis should reveal what changes in the interface, not wander decoratively over the screen.

## Map the interaction

Review the screen recording or interface frames and list the meaningful states: starting view, target control, hover or focus, click or drag, interface response, and settled result. Keep only actions needed to understand the task.

Choose the correct cursor state for the action—pointer, text, grab, resize, crosshair, or another supplied state. Prefer supplied cursor artwork for a standard pointer; construct polygon geometry only when a custom silhouette is needed, and check that its outline is closed and does not cross itself. A Unicode arrow in Text+ can render as a colored emoji or change shape with font fallback. Place the pointer tip on its target and keep its body away from the control label. If the recording already contains a baked cursor, avoid a doubled pointer: use it as-is, crop or rebuild the interface when feasible, or state that clean replacement is blocked.

## Design readable motion

Place cursor anchors at real interface targets. Travel directly with a gentle ease, brief deceleration before precise clicks, and no unexplained loops. Long moves may arc around important content; short moves should remain efficient.

Build click feedback from editable geometry: a quick scale compression, small ring, tint, or focus pulse synchronized to the UI response. Keep it local to the click; a broad glow that washes out the label weakens the interaction. Use drag motion with clear pickup, continuous travel, and release. Let scrolling move the interface while the cursor remains plausibly attached to its control.

Use zooms and callouts sparingly. Establish the full interface before pushing in, keep the target inside a safe readable region, and return or cut only after the viewer has understood the result. Maintain consistent cursor scale relative to the interface across reframes.

### Editable interaction recipe

Build one clear branch per responsibility:

1. Feed the screen recording or still interface through its own Transform for crop and camera move.
2. Feed a transparent cursor image through a separate Transform. Animate that Transform's center along a short path whose points correspond to real controls.
3. Create click feedback from a colored Background masked by an Ellipse. Animate its scale outward while opacity falls, then merge it below the cursor.
4. Build callouts from a rounded Rectangle-masked Background plus Text+ and merge them as a grouped branch. Animate the group, not each shadow and label independently.
5. Merge interface, focus treatment, click feedback, callout, and cursor in that order before MediaOut so the pointer stays visible without covering the label it explains.

Express choreography relative to the action. Use roughly 45–60% of a cursor move to travel, 10–15% to settle over the target, 5–10% for press feedback, and the remaining time for the interface response and reading hold. Shorten travel before shortening the response hold. For a drag, add distinct press, attached travel, release, and result states instead of one continuous glide.

Use few path points. Add one control point only when the route must avoid a label or describe a real curved gesture. Ease out of the starting point and into the target; do not smooth through a click position because that makes the cursor appear to miss it.

## Build an editable composition

For local execution, read `cutagent-fusion`, `cutagent-editing`; check the installed SDK declarations, public CutAgent CLI command cards, and live capabilities for exact operations.

Author cursor states, path keyframes, click feedback, zoom framing, and masks as editable Fusion elements or a reusable `.setting`. Name tools by role and preserve the clean source screen recording. Supplied cursor artwork may be used as a visual input; do not copy a purchased animation graph and rename its labels.

Choose distinct cursor artwork for general, drag-and-drop, link/status, zoom, selection, screenshot, and resize states when needed. Change state only when the underlying control would change the real cursor. Do not cycle cursor images for visual variety.

## Select image assets

Use user supplied or locally licensed artwork for icons, screenshots, and textures. Inspect it at delivery size and import it through the installed CutAgent SDK or CutAgent CLI when it serves the edit. Build the motion and compositing locally in Fusion; record any source rights or editability limit.

## Review

Review the whole interaction at normal playback speed and at the intended delivery size. Check that the cursor reaches the exact target before activation, click feedback coincides with the response, drags remain attached, text stays legible, and no zoom causes motion sickness or hides context.

Structural keyframes do not prove readable motion. Report the interaction states, cursor assets, original animation structure, temporal review performed, and any baked-cursor or interface-response limitation.
