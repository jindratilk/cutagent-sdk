# Motion-transition construction recipes

Use these as original motion models, not preset files. Select the exact supported transition or Fusion construction from the installed public CutAgent SDK and CLI reference after inspecting the seam and available source.

## Paired directional push

Create an outgoing and incoming image branch and give them one shared screen-space axis:

```text
outgoing source -> outgoing Transform --\
                                           Merge/composite -> output
incoming source -> incoming Transform --/
```

Before the seam, the outgoing branch travels toward its exit edge while the incoming branch begins just beyond the opposite edge. At the seam they share compatible velocity; after it the incoming branch decelerates into exact rest. Keep the apparent gap between frames closed. If the sources overlap, choose the foreground order from scene logic and soften or mask only the overlap that would otherwise double an important subject.

Use the source bounds to calculate travel distance. Motion blur can hide small discontinuities but must not substitute for matching the axes. Inspect corners at peak travel for transparent exposure.

## Scale handoff

Choose one visual anchor—a face, wheel hub, product detail, doorway, or graphic shape—that plausibly connects the shots. Animate outgoing scale and center toward that anchor. Begin the incoming shot at a compatible scale and center, then settle to its natural framing:

```text
outgoing: natural framing -> enlarged anchor
incoming: matching enlarged anchor -> natural framing
```

Cross the seam near the closest visual match. Avoid a pure center zoom when the subject is off-center; it creates a lateral jump. Keep the zoom range small enough to preserve image quality unless a deliberate abstract blur covers the closest point.

## Rotational handoff

Rotate both branches around a motivated pivot. Pair rotation with modest translation or scale so the corners remain covered. Keep angular direction continuous across the seam. A full spin is rarely necessary; use only enough rotation to carry the eye from the outgoing circular motion into the incoming direction.

If the incoming shot must be upright immediately, finish most rotation before its key subject needs to be read. Add one small elastic settle only when the music or visual language supports it.

## Elastic impact and directional deformation

Separate the primary motion from the response:

```text
source -> primary Transform -> optional velocity deformation -> blur -> output
```

The primary transform reaches the seam or final position first. The response overshoots once, crosses rest, and converges quickly. Increase damping to shorten ringing; adjust oscillation rate only enough to make one response visible. Do not expose mathematical controls if the editor would be better served by labeled strength and duration controls.

For directional deformation, stretch along the travel axis and compress across it near peak speed, then return to 1:1 at rest. Keep faces and interface content recognizable. If a supported native expression route is unavailable, author a few deliberate keys around peak velocity rather than asserting a live velocity link.

## Seam-centered timing

Think in five events:

```text
setup -> acceleration -> seam/peak speed -> incoming settle -> rest
```

Place the seam near peak speed for a continuous transition, or at impact for a beat-driven cut. Start with a short duration appropriate to the frame rate, then adjust by playback and source handles. When shortening, remove anticipation and secondary oscillation before compressing the essential outgoing and incoming motion into an unreadable flash.

Review a few frames before setup, every frame around the seam when diagnosing flashes, and several frames after rest. Also play the passage with sound at normal speed; slow scrubbing exaggerates defects that may be invisible while hiding rhythm problems.
