# Finished Video Analysis

Use this reference for a flattened video such as MP4, MOV, MKV, or WebM. A finished render strongly proves what was visible and audible, but usually cannot prove how it was authored.

## Preserve and probe the source

- Keep the source read-only. Write proxies, extracted audio, frames, contact sheets, transcripts, and reports to the session workspace or another temporary analysis directory.
- Resolve the exact local source path and verify the file exists before analysis.
- Discover the available `ffprobe`, `ffmpeg`, transcript, image-inspection, and audio-analysis capabilities. Use the bundled media tools when provided by the runtime.
- Do not transcode over the source. Do not strip metadata, remux, normalize, or replace the user's file merely to inspect it.
- If decoding fails, try a read-only proxy to a new path only after preserving the error and source metadata. Report that pixel/audio conclusions come from the proxy.

A typical non-mutating technical probe is:

```bash
ffprobe -v error -show_format -show_streams -of json INPUT
```

Treat the command as a shape, not a fixed binary path. Quote user paths safely and use the runtime-provided executable.

## Technical inventory

Record:

- format/container, duration, file size, overall bitrate, tags, creation metadata, and chapters;
- video stream count, codec/profile/level, resolution, sample/display aspect, rotation, frame rate, variable/constant timing, pixel format, bit depth, chroma subsampling, color range, primaries, transfer, matrix, and HDR metadata;
- audio stream count, codec, sample rate, bit depth when exposed, channel count/layout, language, disposition, and bitrate;
- subtitle/data streams, language, format, forced/default disposition, and chapters;
- letterbox, pillarbox, baked borders, safe areas, watermarks, burnt-in captions, and platform recompression evidence;
- decode errors, missing timestamps, frame duplication/drop evidence, silence, clipped audio, and visible compression artifacts.

Technical metadata is not the style profile by itself. Use it to establish the timing, color, and audio domains for later measurement.

## Analyze the complete chronology

Do not learn a style from a thumbnail or a few evenly spaced frames. Build coverage in passes:

1. Review the complete duration chronologically through playback or a lightweight proxy.
2. Generate an initial low-density contact sheet to locate major sections, shot changes, text systems, and visual regimes.
3. Increase sampling around every suspected cut, transition, camera switch, B-roll boundary, title, animation, speed change, color change, and section boundary.
4. Inspect short frame sequences or proxy motion around dynamic events; one still cannot prove animation timing, easing, or transition type.
5. Inspect the beginning, middle, ending, and every exceptional section even when the edit is long.
6. Keep source timecodes and exact frame or presentation timestamps for all evidence.

For long sources, analyze bounded chronological windows and maintain an index so no interval is silently skipped.

## Transcript and semantic map

When speech carries the edit:

- obtain a fresh time-aligned transcript through available supported transcript tooling;
- preserve word or segment timing, language, speaker labels when genuinely available, pauses, interruptions, overlap, laughter, and uncertain words;
- align transcript positions to decoded media time, accounting for file start time and variable frame timing;
- divide speech into sentences, clauses, questions, answers, topics, examples, named entities, processes, statistics, emotional turns, jokes, sponsor copy, CTA, and silence;
- verify representative transcript boundaries against the media before using them as edit triggers.

For silent, musical, action-led, screen-recording, or visually led material, use a visual-first map. Do not generate a transcript merely to satisfy the workflow. For mixed material, combine both.

Speaker diarization is not identity proof. Label speakers consistently within the source and use names only when confirmed.

## Shot and transition detection

Use automatic scene-change candidates only as a first pass. Confirm them with adjacent frames and audio because flashes, exposure changes, screen content, whip motion, and graphics can cause false detections.

For each boundary classify:

- hard cut, jump cut, match cut, cut on action, cut on motion, invisible cut, or camera switch;
- cross dissolve, film dissolve, fade, dip to black/white, wipe, push, slide, zoom, blur, whip, flash, light leak, glitch, mask, morph, or custom transition;
- video-only change, audio-only change, J-cut, L-cut, pre-lap, post-lap, or synchronized audio/video boundary;
- transition start, midpoint, end, duration, direction, easing evidence, paired motion, and paired SFX/music accent;
- false boundary caused by on-screen animation, exposure, strobe, screen refresh, or occlusion.

Create a shot table with start/end, duration, visual class, camera cluster, framing, movement, subjects, text/graphics, audio state, and confidence. Compute duration distributions and cut-density curves by section; do not collapse them into one average.

## A-roll, B-roll, and semantic function

Classify each visible region as appropriate:

- talking head, interview close-up, medium, wide, two-shot, reaction, over-the-shoulder, detail, product, environment, establishing, action, screen recording, screenshot, photograph, archive, stock, meme, animation, graphic, text-only, or mixed composite;
- likely A-roll, B-roll, transition insert, overlay, picture-in-picture, split screen, matte, background, or full-screen graphic.

For every B-roll event measure:

- start/end, duration, series length, shot-size progression, transform/motion, transition, and reuse;
- relation to transcript word, clause, sentence, topic, named entity, action, emotion, joke, process, statistic, quotation, or edit discontinuity;
- lead/lag from the likely trigger and return point to A-roll;
- whether dialogue continues, natural sound enters, music changes, or SFX accents the boundary;
- interaction with captions, titles, citations, logos, and visible facial reactions;
- semantic role: literal, process, contextual, emotional, metaphorical, product, archival, citation, screen, transitional, or coverage.

Build the opportunity denominator from all comparable semantic events. Do not conclude that every named entity triggers B-roll when only one does.

## Camera and multicam inference

When the video contains interviews or podcasts, use available visual and speech evidence to cluster recurring angles:

- background, framing, subject identity, wardrobe, lighting, camera position, crop, and lens perspective;
- close-up, side angle, wide, two-shot, reaction, listener, screen, B-roll, and digital punch-in roles;
- face visibility, lip movement, speaker diarization, and transcript turn timing when supported;
- near-identical crops that may be digital variants of one source rather than separate cameras.

For every qualifying speaker event record active angle, previous/following angle, switch offset, hold, cooldown, reaction behavior, and whether B-roll hides the switch. Analyze stable turns, short acknowledgements, interruptions, overlap, laughter, silence, questions, answers, emotional reactions, and wide-shot resets separately.

Keep camera identity, speaker identity, and causal switching rules marked `inferred-render` unless independent evidence confirms them. A flattened mix cannot prove external microphone mapping or audio-follow-video state.

## Text and typography from pixels

Use OCR as a candidate generator, then verify the visible frames. Separate hook, caption, lower-third, chapter, quote, citation, statistic, callout, CTA, disclosure, logo, and watermark families.

For every event measure:

- exact visible text, capitalization, punctuation, number treatment, emoji, line breaks, words/characters, and correction confidence;
- frame/time start and end, speech lead/lag, persistence across cuts, and cue replacement cadence;
- bounding box, anchor, alignment, margins, safe area, line count, relative size, and responsive behavior;
- fill/gradient, stroke layers, shadow, background box, radius, padding, opacity, blur, and active-word highlight;
- animation start/hold/end, transform/opacity/blur change, per-word/per-character behavior, stagger, easing, overshoot, bounce, and motion blur.

Estimate font family through visible glyph shape only when a matching capability or comparison set is available. Report a likely family or nearest alternatives, weight, width, and defining visual traits. Do not claim an exact font, font file, MOGRT, Text+ setting, or template from rasterized pixels alone.

## Motion, reframing, and retiming

Use short frame sequences, tracked landmarks, and optical-flow evidence when available to measure:

- digital position, scale, rotation, crop, opacity, and anchor-like movement;
- punch-in levels, pans, tilts, pushes, pulls, parallax, Ken Burns, handheld simulation, camera shake, stabilization, and object/cursor following;
- animation onset, duration, hold, easing, overshoot, bounce, stagger, motion blur, and reset behavior;
- speed-up, slow motion, freeze, reverse, speed ramp, interpolation artifacts, duplicated frames, and action alignment;
- trigger relationship to speech stress, gesture, reveal, topic change, music event, text, B-roll, or static-frame reset.

Do not decide that a move is keyframed rather than captured in-camera unless the evidence distinguishes them. The transferable rule may be the visible motion profile, not the hidden implementation.

## Graphics and compositing

Inspect visible:

- lower thirds, cards, panels, frames, logos, bugs, watermarks, progress bars, charts, maps, arrows, circles, underlines, scribbles, icons, and device mockups;
- picture-in-picture, split screen, screen replacement, keying, masks, mattes, blur/redaction, tracked elements, background removal, shadows, glows, borders, and corner radii;
- layer ordering from occlusion, entrance/exit timing, shared motion, and repeated layout;
- palette, spacing, grid, iconography, illustration, and template families;
- intro/outro, chapters, citations, sponsor elements, disclosures, CTA, and end-screen systems.

Infer only the visible composite and temporal behavior. Node graphs, layer count, effect names, plugins, and hidden controls remain unresolved unless another project source provides them.

## Color and image finishing

Sample representative frames by camera, scene, lighting, subject, and section. Use waveform, RGB parade, vectorscope, histogram, and pixel measurements when supported. Analyze:

- exposure, black/white points, contrast, pivot-like behavior, shadow/highlight detail, clipping, and highlight rolloff;
- white balance, tint, skin hue/luminance/saturation, product color, neutrals, and camera matching;
- saturation, saturation by luminance, palette, hue relationships, split tone, warm/cool separation, and scene exceptions;
- local contrast, subject/background separation, vignette, bloom, glow, halation, diffusion, grain, sharpening, denoise, chromatic aberration, and compression artifacts;
- shot-to-shot consistency, deliberate mood changes, day/night/interior/exterior rules, and transition grades.

Distinguish measurements from interpretations. `Cinematic`, `clean`, `social`, `broadcast`, `pastel`, and `film-like` are summaries; the profile must retain measurable rules beneath them.

Do not infer exact LUTs, Color Page nodes, Lumetri values, color management, input transforms, qualifiers, windows, or noise-reduction settings from a finished render. Metadata may narrow possibilities but does not prove the grading pipeline.

## Audio and music from the final mix

Inspect each stream and the complete mixed program. Measure when supported:

- integrated, short-term, and momentary loudness; loudness range; true peak; peak-to-loudness relationship; noise floor; silence; and clipping;
- dialogue level consistency, spectral balance, high-pass character, sibilance, compression, limiting, gating, denoise artifacts, reverb, and stereo placement;
- music cue boundaries, level under dialogue, ducking depth, attack/release shape, phrase/section alignment, reuse/looping, transitions, cadence, and silence;
- natural sound, ambience, room tone, continuity, foley, whooshes, impacts, risers, pops, stingers, text accents, zoom accents, and transition SFX;
- J/L relationships, dialogue edits, breaths, pauses, overlaps, interruptions, and acoustic discontinuities.

Automatic source separation may help locate dialogue, music, and effects but is not ground truth. Label separated-stem conclusions as inferred, verify against the original mix, and never claim exact original stems, plugin chains, EQ values, bus routing, or automation.

Waveforms and loudness data cannot prove intelligibility, musical taste, emotional fit, or artifact-free processing. Perform genuine listening when available or request user audition.

## Narrative and platform grammar

Align transcript, shot, text, graphics, color, music, and SFX tables to identify:

- cold open, hook, title, setup, chapters, re-hooks, examples, reveal, sponsor, recap, CTA, conclusion, outro, teaser, and end screen;
- first cut, B-roll, title, caption, music entrance, SFX, and CTA;
- changes in edit, B-roll, text, motion, music, and SFX density by section;
- horizontal/vertical/square framing, safe areas, hook replacement, caption resize, reordering, pacing, CTA, and duration when multiple exports exist.

Do not infer a general platform rule from one export. Compare multiple variants or obtain user confirmation.

## Pattern inference from flattened evidence

For each candidate rule:

1. Define the trigger opportunity from transcript, shot, speaker, music, motion, or narrative events.
2. Count occurrences and non-occurrences.
3. Measure offsets and distributions.
4. Split distinct contexts.
5. Record alternative behavior and negative rules.
6. Preserve timecoded examples.
7. Mark visible measurements `measured-render` and hidden relationships `inferred-render`.

Examples of valid finished-video conclusions:

- high confidence: captions appear 80-140 ms before the corresponding spoken phrase in 34 of 37 qualifying cues;
- medium confidence: most stable speaker turns switch to the matching close-up after a short delay, based on diarization and lip movement;
- unresolved: the close-up may be a separate camera or a digital crop;
- invalid: the editor used a specific multicam switch command with a 250 ms setting.

## Applying to DaVinci Resolve

- Import the reference video into the target project only when it helps comparison and the user permits that project change. Keep it off the program output or on a clearly isolated reference timeline/track.
- Do not scene-detect, blade, grade, relink, or process the only reference item as a substitute for read-only file analysis.
- Build the style profile first, then apply supported rules to a duplicated target timeline through current CutAgent workflows.
- Use exact visible timing and measured parameters when transferable. Choose supported approximations for hidden implementation only when the user accepts them.
- Compare matched target frames, motion previews, loudness evidence, and representative renders against reference examples. Similar metadata alone is not style parity.

## Report limitations

Explicitly list every consequential unknown:

- hidden layers and source ranges;
- original takes and unused media;
- camera versus digital crop;
- exact fonts, templates, transitions, effects, plugins, LUTs, grade topology, and color transforms;
- audio stems, microphone mapping, plugin chains, buses, and automation;
- causal trigger versus observed correlation;
- skipped ranges, decode/proxy differences, transcription uncertainty, diarization uncertainty, and unavailable listening.

Connect each limitation to affected rules and their application strategy.
