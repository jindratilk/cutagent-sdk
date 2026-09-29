# Adobe Premiere Pro Project Analysis

Use this reference for Adobe Premiere Pro projects and interchange exports. Keep the source read-only and treat the delivered reference render as the authority for final visible and audible output.

## Preferred inputs

Request or use the richest available combination:

1. The original `.prproj` or project package.
2. A Premiere-exported Final Cut Pro XML/FCPXML for timeline structure when the native project is not structurally readable.
3. AAF for detailed audio interchange when audio structure matters.
4. EDL for basic picture cut decisions when richer interchange is unavailable.
5. A reference render of the authoritative sequence.
6. Linked media, graphics, fonts, LUTs, MOGRTs, and plugin names when available and permitted.

Do not require every input. State how each missing input limits the profile. A reference render plus XML is usually more trustworthy for style reconstruction than an opaque `.prproj` alone.

## Safe intake

- Preserve the original file and work from a temporary copy for any decoding or extraction.
- Identify the file type, container, compression, and encoding before choosing a parser. Adobe Premiere Pro project serialization varies by version; do not assume that every `.prproj` is plain XML or that one decompression method applies universally.
- Parse only declarative project data. Do not execute scripts, extensions, macros, dynamic links, or third-party plugins found in the project.
- Keep absolute media paths, usernames, customer names, tokens, and private metadata out of the reusable style profile.
- Inventory missing/offline media, fonts, LUTs, MOGRTs, plugins, After Effects Dynamic Link compositions, and unsupported effects before interpreting absence in the render.
- Identify the intended master sequence from explicit user direction, project naming and activation evidence, export metadata, and the reference render. Do not pick the longest sequence automatically.

## Fallback when `.prproj` is opaque

If the native project cannot be decoded into reliable sequence, track, clip, component, and keyframe data:

1. Do not scrape printable strings and present them as a timeline.
2. Ask for a Premiere-exported XML/FCPXML from the intended sequence. Prefer this for clip placement, source ranges, nesting, transitions, and many motion/effect values.
3. Ask for AAF when clip-level audio edits, track layout, and mix handoff matter.
4. Accept EDL only as a cut-list fallback; mark missing graphics, nested structure, effects, keyframes, and most audio treatment as unresolved.
5. Use the reference render to recover visible text, compositing, transitions, color, and mixed audio behavior that interchange omits or flattens.

Do not claim complete project fidelity from an interchange format. Record the fields actually present.

## Normalize project time

- Read the sequence timebase, frame rate, start timecode, drop-frame state, and clip-specific rates.
- Convert project time units through the sequence's declared timing model. Do not hardcode one Adobe tick constant without verifying that the parsed field uses that unit.
- Preserve source in/out, sequence record in/out, media start, speed/time-remap mapping, and nested-sequence offsets separately.
- Convert cross-sequence comparisons to seconds or milliseconds while retaining native frame positions.
- Account for mixed-rate media, interpreted frame rates, still-image duration, speed changes, and nested sequences before measuring edit rhythm.

## Project and sequence structure

Extract:

- project/application version and project settings exposed by the file;
- bins, labels, naming conventions, metadata, source media, proxies, and offline state;
- all sequences, their names, settings, durations, start timecodes, and likely roles;
- master, alternate, social, vertical, trailer, teaser, clean, captioned, and archive variants;
- video, audio, caption, graphic, and adjustment-layer tracks;
- track order, names, enable/mute/lock/target state when available;
- nested sequences, subsequences, multicam sources, synchronized sequences, adjustment layers, and Dynamic Link items;
- markers, sequence markers, clip markers, label colors, comments, and review notes;
- disabled clips, hidden tracks, unused assets, alternate takes, and work-in-progress remnants.

Separate active master-sequence evidence from inactive or unused project elements.

## Clip and edit event map

For every active timeline item extract when available:

- stable project identifier, name, media reference, media type, track, and enable state;
- sequence record start/end/duration;
- source in/out/duration, media start, handles, and timecode;
- frame rate interpretation, speed, reverse, frame hold, time remapping, and interpolation;
- linked/grouped video and audio relationships;
- opacity, blend mode, transform, crop, stabilization, reframing, and intrinsic motion parameters;
- keyframes, interpolation, easing, Bezier handles, temporal/spatial continuity, and motion blur settings;
- clip, transition, master/source, track, and adjustment-layer effects;
- nested sequence identity and its local-to-parent time mapping;
- markers, labels, metadata, and comments.

Derive:

- shot durations and cut-density curves;
- hard cuts, gaps, overlaps, J-cuts, L-cuts, pre-laps, post-laps, and dialogue surgery;
- source reuse, take selection, alternate audio, jump-cut coverage, and handle preferences;
- action, speech, pause, music, and graphics relationships when corroborating media is available.

An item boundary alone does not prove a visible cut: upper tracks, opacity, nests, transitions, or disabled items may hide it. Compare the active composite with the reference render.

## A-roll, B-roll, and layer roles

Infer track roles from repeated content and compositing behavior, not track numbers alone. For every potential B-roll or overlay item record:

- whether it actually covers the active A-roll in the composite;
- semantic function and relation to transcript or topic;
- full-screen, overlay, picture-in-picture, split-screen, matte, screenshot, photograph, graphic, or screen-recording form;
- timing relative to the triggering word, clause, sentence, action, or section;
- source audio, natural sound, linked audio, fade, and dialogue continuation;
- transforms, crop, mask, border, shadow, opacity, transition, and effect stack;
- whether it covers a jump cut or supplies new information;
- whether the sequence returns to A-roll before the thought ends;
- reuse frequency and repeated shot-size sequences.

Use the event map plus transcript and render evidence to distinguish purposeful B-roll from full-screen A-roll camera changes.

## Multicam and podcast structure

When Premiere multicam information is present, extract:

- multicam source sequence and nested program sequence;
- camera/angle labels, ordering, source media, sync basis, and offsets;
- active camera selection over time;
- audio-follow-video state and selected audio sources when exposed;
- program-sequence cuts, nested segment timing, transitions, and digital punch-ins;
- external microphone tracks and sync relationships.

Correlate speaker turns with active camera changes and measure switch offsets, holds, reaction shots, wide-shot resets, overlap behavior, backchannels, interruptions, laughter, and switch suppression. If active-camera state is absent or flattened, infer it from the reference render and label it `inferred-render`.

## Motion, transitions, and effects

Inspect each active component/effect in render order:

- Motion/Transform position, scale, rotation, anchor, crop, opacity, and composite mode;
- static punch-in variants and animated moves;
- keyframe timing, interpolation, easing, overshoot, bounce, and repeated curves;
- speed, time remapping, freeze, reverse, and ramp behavior;
- stabilization, blur, glow, sharpen, distort, keying, masking, tracking, and plugin effects;
- transition name, video/audio scope, duration, alignment, direction, parameters, and handles;
- adjustment-layer effects and their affected ranges;
- nested effects and rendered/baked effects.

Map proprietary or missing plugin effects by observable output and timing, not guessed parameter equivalence.

## Essential Graphics, MOGRT, titles, and captions

For each graphic family inspect when exposed:

- graphic/template identity and editable properties;
- source text, font, style, weight, size, tracking, line height, alignment, and position;
- fill, stroke, shadow, background, padding, radius, gradient, opacity, and blend;
- responsive design, pinning, safe areas, and aspect-ratio variants;
- keyframes, animation in/hold/out, per-word or per-character treatment, easing, and motion blur;
- caption track format, cue text, timing, line breaks, reading speed, and styling;
- lower-third, hook, chapter, quote, citation, CTA, disclosure, logo, and watermark families.

MOGRTs and Dynamic Link items may expose only controls, references, or a flattened result. Preserve visible measurements from the render and mark hidden graph behavior unresolved. A missing font must produce a nearest-match requirement, not a false exact match.

## Lumetri and color

Inspect active source/master, clip, nested-sequence, track, and adjustment-layer color treatment:

- input LUT, Basic Correction, Creative Look, curves, color wheels, HSL Secondary, vignette, masks, tracking, and effect opacity;
- order of multiple Lumetri instances and non-Lumetri effects;
- sequence working color space, media color overrides, tone mapping, HDR/SDR settings, and export color tags;
- camera-specific corrections, scene matching, skin treatment, local corrections, creative look, texture, and output transform evidence.

Use matched reference-render frames and scopes to confirm active output. The presence of an input LUT or Lumetri instance is not proof that it controls the delivered look if it is disabled, overridden, nested, or absent from the exported range.

## Audio structure and mix

Inspect when present:

- clip/channel mapping, sync, source channels, linked media, roles, and track layout;
- clip gain, volume, pan, fades, crossfades, keyframes, Essential Sound settings, and clip effects;
- track mixer levels, pan, routing, submixes, master treatment, inserts, sends, and automation;
- dialogue cleanup, EQ, de-essing, compression, limiting, reverb, noise reduction, music ducking, SFX, ambience, and silence;
- music cue boundaries, edits, loop/reuse, phrase alignment, and dialogue relationship;
- sequence loudness and delivered mixed loudness.

AAF may preserve useful edit and track information without preserving the audible result of every plugin or routing decision. Corroborate with the reference render and label opaque processing.

## Export and variant analysis

Extract or infer:

- export presets, format, codec, resolution, frame rate, bitrate mode, audio settings, captions, color tags, and naming;
- horizontal, vertical, square, clean, captioned, teaser, ad, and platform-specific sequences;
- transformation rules between variants: reframe, text resize, safe-area shift, hook replacement, pacing, B-roll density, CTA, duration, and loudness.

Do not treat every sequence as a delivered variant. Require reference render, export metadata, naming plus active evidence, or user confirmation.

## Evidence reconciliation

For each learned field report whether it came from:

- active native project structure;
- interchange export;
- linked media inspection;
- reference-render pixels/audio;
- user confirmation;
- inference.

Use the reference render to invalidate stale or non-visible project state. Use project structure to explain how a visible pattern was authored only when the active path is traceable.

## Applying the learned profile in DaVinci Resolve

- Do not attempt to open `.prproj` directly in DaVinci Resolve.
- If timeline translation is required, use a user-approved XML/FCPXML, AAF, EDL, or other supported interchange route and inspect the imported timeline before editing.
- Treat the interchange import as source reconstruction, not proof of Premiere parity. Check media relinks, clip timing, nests, multicam, transitions, speed changes, graphics, captions, color, and audio.
- Rebuild unsupported Premiere-specific graphics, effects, grades, and audio treatments through current supported CutAgent workflows on a duplicate DaVinci Resolve timeline.
- Compare the reconstruction and styled target with matched frames and representative audio from the authoritative render.

## Report limitations

Name every important opaque or missing area, including unreadable project serialization, missing media, unavailable Dynamic Link content, third-party plugins, MOGRT internals, fonts, LUTs, audio routing, inactive variants, and absent reference render. Do not downgrade these to generic warnings; connect each limitation to the rules it weakens or blocks.
