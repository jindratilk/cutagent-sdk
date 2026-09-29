---
name: cutagent-apple-motion-graphics
description: Create original, editable Apple-inspired motion graphics in DaVinci Resolve Fusion for product stories, feature reveals, clean title sequences, device moments, and polished interface-led videos.
license: AGPL-3.0-only
---

# Apple-inspired motion graphics

Build a fresh composition from the message and supplied brand material. Aim for calm hierarchy, precise spacing, soft depth, and purposeful movement; do not import a purchased title or project and merely replace its text.

## Establish the visual system

Choose one focal idea per scene: a product benefit, interaction, number, object, or short phrase. Compose the settled hero frame first.

- Use a disciplined sans-serif hierarchy with few sizes and weights.
- Favor generous margins, strong alignment, and quiet negative space.
- Build panels from editable shapes, masks, backgrounds, and merges; use restrained radius, border, blur, glow, and shadow.
- Keep the palette small. Let one accent or image carry attention against neutral space.
- Treat icons, emoji, device imagery, photography, and wallpapers as content, not decoration.

Use supplied, licensed image or sound assets when they serve the brief, but author the layout, graph, timing, and controls anew. A Loader with a finished animation is baked media, not an editable reconstruction.

## Choreograph a product idea

Use motion to explain state change: enter, focus, select, expand, confirm, or resolve. Animate related elements as one system. A panel can establish first, content can follow, and a cursor or accent can complete the action. Keep entrances short enough to feel responsive and holds long enough to read.

Prefer smooth acceleration and settling over constant-speed sliding. Use overshoot only for an intentionally springy object. Keep scale and position pivots coherent so cards do not appear to drift. Exit by reversing the scene's logic or clearing attention for the next idea.

Build scenes in functional layers similar to a real product animation: a main background/composite, an adjustment or atmosphere layer, an animation layer for the current interaction, a separate text layer, an optional zoom/framing layer, and intentional SFX. This separation lets timing and copy change without dismantling the whole scene.

### Editable panel recipe

1. Create the backdrop from a Background node or an image branch. Use a Transform only when the source needs framing.
2. Make the panel with a Background masked by a rounded Rectangle. Duplicate that masked alpha below it for a soft, offset shadow; blur and reduce opacity rather than baking a shadow into artwork.
3. Keep icon proportions correct in the delivery frame: equal normalized X/Y dimensions are not equal pixel dimensions on a rectangular canvas. Compensate the aspect ratio for circles and square artwork. Merge an icon or image and one or two Text+ nodes inside the panel. Keep each element independent so spacing, copy, and emphasis remain editable.
4. Merge the complete panel over the backdrop, then feed a single output path to MediaOut. Place global zoom or finishing after the panel merge so the unit moves together.

For a scene of any duration, start with proportional phases: establish background and panel in the first 15–20%, introduce content by 30%, perform the interaction or emphasis around 35–60%, hold the resolved state through roughly 80–85%, then exit. Adapt the percentages to copy length and the real edit; never paste the source pack's keyframe times.

For a clean entrance, offset the panel a short distance and reduce its scale and opacity, then ease all three to the settled values. Bring text a few frames later with less travel than the panel. A soft highlight sweep or gradient may cross once after the panel settles; looping sheen usually cheapens the result.

Sound accents may reinforce a real interaction or completion. Use only assets whose rights fit the intended delivery, audition every placed sound, and keep it subordinate to dialogue and music.

## Author editable Fusion work

For local execution, read `cutagent-fusion`; check the installed SDK declarations, public CutAgent CLI command cards, and live capabilities for exact operations.

Create a connected, named graph whose Text+, geometry, images, masks, and keyframes remain editable. Group repeated visual roles consistently. Expose only controls an editor will reasonably change: copy, accent color, image, scale, and major timing offsets. Preserve the original graph source alongside any inserted timeline instance.

When a reference contains a gradient card, calendar, order confirmation, icon wall, or wallpaper reveal, reconstruct its function from primitives. Measure relative size, alignment, corner treatment, entrance order, and motion curve, then create a new graph with the current project's copy and imagery. Do not clone the reference node tree or reuse its branded screen as if it were original work.

## Select image assets

Use user supplied or locally licensed artwork for icons, screenshots, and textures. Inspect it at delivery size and import it through the installed CutAgent SDK or CutAgent CLI when it serves the edit. Build the motion and compositing locally in Fusion; record any source rights or editability limit.

## Review

Inspect the settled frame at delivery size for hierarchy, margins, glyphs, contrast, and cropping. Review entrance, focus action, hold, and exit in motion for pops, collisions, detached shadows, and unreadable overlap. Check alternate aspect ratios by recomposing rather than blindly scaling.

Report the original design choices, editable controls, external assets and fonts used, structural evidence, motion review, and any look or timing still awaiting approval.
