# Pattern Schema and Editorial Catalog

Read this reference for every analysis. Use it to turn observations into a portable, evidence-backed style profile.

## Pattern record

Store one record per materially distinct rule. Keep global defaults separate from scoped overrides.

```json
{
  "rule_id": "multicam.speaker-change.stable-turn",
  "domain": "multicam",
  "scope": {
    "program": "podcast",
    "section": "body",
    "platform": "long-form",
    "speaker_or_camera_role": "any"
  },
  "trigger": "a different speaker begins a stable turn",
  "conditions": ["turn is not a backchannel", "no protected reaction shot is active"],
  "action": "switch to the new speaker close-up",
  "timing": {
    "relationship": "after-trigger",
    "native_frames": null,
    "milliseconds": { "p10": 180, "p50": 260, "p90": 410 },
    "duration_or_hold": { "unit": "ms", "p50": 4600 }
  },
  "frequency": {
    "opportunities": 23,
    "occurrences": 19,
    "rate": 0.826
  },
  "sequence_context": ["previous angle usually listener or wide"],
  "exceptions": ["overlapping speech uses wide", "brief acknowledgement holds the current shot"],
  "negative_rules": ["do not switch twice inside the minimum hold"],
  "parameters": { "transition": "hard cut" },
  "evidence": [
    { "source": "reference.mp4", "timecode": "00:04:12.080", "kind": "measured-render" }
  ],
  "confidence": "high",
  "reproducibility": "supported-approximation",
  "application_priority": "high",
  "verification": "compare speaker onset, selected angle, and switch offset"
}
```

The example shape is normative; its values are illustrative only. Never reuse example values as defaults.

## Required fields and evidence labels

- `rule_id`: stable domain-oriented identifier.
- `domain`: one catalog domain below.
- `scope`: contexts in which the rule applies. Include program type, section, platform, aspect ratio, speaker/camera role, and other meaningful selectors.
- `trigger`: observable event that creates an opportunity.
- `conditions`: requirements that distinguish this rule from nearby cases.
- `action`: editorial response.
- `timing`: offset, duration, hold, or relative placement. Preserve native frames and normalized milliseconds.
- `frequency`: occurrences divided by qualifying opportunities. Add per-minute density only when useful; it is not a substitute for the conditional rate.
- `sequence_context`: preceding and following actions or repeated grammar.
- `exceptions`: positive alternate behavior in a special context.
- `negative_rules`: actions consistently avoided in qualifying contexts.
- `parameters`: exact or measured style values.
- `evidence`: source, sequence/timeline, timecode/range, extraction method, and observation kind.
- `confidence`: `high`, `medium`, `low`, or `unresolved`, justified by evidence rather than a fabricated score.
- `reproducibility`: `exact-supported`, `supported-approximation`, `manual-review`, or `blocked`.
- `application_priority`: importance to perceived style and target intent.
- `verification`: concrete structural, visual, or audio check.

Use these observation kinds:

- `exact-project`: direct active project/timeline/effect readback;
- `interchange-project`: value parsed from XML/FCPXML, AAF, EDL, OTIO, or another export;
- `measured-render`: pixels or audio measured from delivered media;
- `inferred-render`: likely relationship inferred from flattened media;
- `user-confirmed`: explicit user statement;
- `unresolved`: evidence is absent or conflicting.

## Confidence rules

- One occurrence is an observation, not a reusable style rule.
- Repetition in one local burst may be a montage pattern, not a global rule.
- A project parameter has high confidence only when it is active in the authoritative sequence/timeline and corroborated by output when output matters.
- A finished video can strongly prove visible timing, color, composition, and mixed audio behavior, but it cannot prove hidden implementation.
- Negative rules require a real opportunity set. Absence without relevant opportunities proves nothing.
- Contradictory contexts should become separate scoped rules instead of a lower-quality average.
- High confidence requires relevant coverage across the scope, consistent evidence, and no unresolved contradiction that would change application.

## Analysis coverage

Report:

- total source duration and analyzed duration;
- sequences/timelines/tracks inspected;
- chronological windows sampled;
- number of shots, edit points, speaker turns, text events, B-roll events, music regions, and qualifying opportunities;
- missing or offline media;
- opaque effects, plugins, templates, fonts, LUTs, or nested structures;
- portions skipped and why;
- whether a delivered reference render was available for corroboration.

## Technical and delivery profile

Inspect:

- container, codec, bitrate, bit depth, chroma subsampling, pixel format, and data levels;
- frame rate, timebase, variable versus constant frame rate, start timecode, drop-frame state, and duration;
- resolution, pixel aspect, display aspect, rotation, letterbox, pillarbox, crop, and safe areas;
- color primaries, transfer, matrix, working/output color spaces, HDR/SDR metadata, and tone-mapping evidence;
- audio codec, sample rate, bit depth, channels, layouts, loudness, true peak, and deliverable routing;
- subtitle/caption type, burn-in, sidecar, language, and styling;
- platform variants, reframes, duration variants, naming, watermarks, and export presets.

Learn which values are stable requirements and which are merely properties of one delivery.

## Narrative and macrostructure

Identify section boundaries, relative position, duration, trigger, entry, exit, and visual/audio treatment for:

- cold open, hook, title, intro, logo sting, setup, promise, and host/guest introduction;
- chapters, topic transitions, re-hooks, examples, demonstrations, montage, recap, and reveals;
- sponsor integrations, disclosures, citations, calls to action, conclusions, outro, teaser, and end screen;
- intentional black, silence, freeze, hold, breathing space, or long take;
- escalation and release of visual density, cut density, text density, music energy, and sound design.

Measure when the first cut, B-roll, title, caption, music entrance, SFX accent, and CTA occur. Compare absolute timing with normalized position because videos vary in length.

## Edit rhythm and continuity

Inspect:

- every edit point and shot duration;
- median, spread, useful percentiles, minimum, maximum, and outliers by section and shot role;
- cuts per minute and density curves rather than one global rate;
- hard cuts, jump cuts, match cuts, cut on action, cut on motion, invisible cuts, and deliberate discontinuity;
- J-cuts, L-cuts, pre-laps, post-laps, split edits, room-tone bridges, and dialogue overlaps;
- cut offset relative to word, sentence, speaker turn, pause, breath, gesture, action peak, camera motion, music event, or graphic accent;
- repeated rhythmic sequences such as short-short-long, burst-and-hold, or progressive acceleration;
- pause trimming, filler removal, false starts, sentence construction, reaction preservation, and comedic timing;
- source handles, take assembly, alternate audio, coverage cuts, and hidden dialogue surgery when project evidence exists;
- continuity of gaze, movement direction, screen position, lighting, background, action, and audio ambience;
- speed changes, freezes, reverse, retimes, optical-flow treatment, and transitions around retimes.

Separate editorial necessity from style. A cut caused by a corrupt frame is not a reusable rhythm rule.

## Shot selection and framing

Classify:

- establishing, wide, medium, close-up, extreme close-up, two-shot, over-the-shoulder, reaction, detail, insert, product, environment, screen, graphic, and text-only shots;
- camera, lens or crop identity when supportable;
- subject, action, emotion, informational role, visual complexity, movement, and production quality;
- headroom, lead room, eye line, look room, symmetry, rule of thirds, center framing, horizon, face size, and negative space;
- depth of field, background separation, foreground layers, lighting direction, and camera motion;
- shot-size progression, angle repetition, continuity pairings, and intentionally disruptive contrasts;
- preferred source ranges, action start/peak/end, handles, and rejected ranges when editable project evidence exists.

Learn both selection preferences and rejection patterns.

## B-roll grammar

For every B-roll opportunity and occurrence record:

- trigger type: named person, place, product, object, action, statistic, quotation, process, abstract concept, emotion, joke, topic change, or visual-staleness opportunity;
- semantic function: literal, process, contextual, emotional, metaphorical, product, archival, citation, screen recording, generated, transitional, or edit coverage;
- form: full-screen, overlay, picture-in-picture, split screen, matte, background, insert, still image, screen capture, or animated graphic;
- start/end, duration, lead or lag from trigger, return point, and whether it spans a word, clause, sentence, or topic;
- series length, shot-size order, internal pace, reuse, source category, and return-to-A-roll pattern;
- source audio, natural sound, dialogue continuation, music/SFX treatment, and audio transition;
- transform, pan, zoom, parallax, crop, border, shadow, corner radius, and transition;
- interaction with captions, lower thirds, citations, logos, and protected facial reactions;
- non-occurrences where B-roll was available but intentionally withheld.

Measure density per minute and conditional coverage per opportunity. Do not infer that static duration alone triggers B-roll unless repeated opportunity evidence supports it.

## Multicam and speaker grammar

Record:

- camera/angle identity, speaker mapping, shot size, preferred use, and source offset when project evidence exists;
- speaker onset/offset, diarization confidence, lip movement, overlap, interruption, backchannel, laughter, silence, and reaction;
- selected angle and switch offset relative to each qualifying turn;
- minimum/typical/maximum hold, cooldown, rapid ping-pong suppression, and repeat-angle behavior;
- rules for close-up, side angle, wide, two-shot, listener/reaction, and digital punch-in;
- treatment of questions, answers, emotional turns, interruptions, overlaps, short acknowledgements, laughter, and pauses;
- anticipation of a speaker, delayed switches, reaction holds, wide-shot resets, and B-roll-covered switches;
- transition type, motion or scale change, and whether audio follows video;
- external microphone use, linked/embedded audio, and J/L relationships when project evidence exists.

Do not infer speaker-to-camera identity from filenames alone. In finished media, keep diarization and face/angle clustering explicitly inferential.

## Reframing, motion, and retiming

Inspect:

- position, scale, rotation, anchor/pivot, crop, opacity, blend/composite mode, corner radius, border, and shadow;
- static crop variants and digital punch-in levels by camera/section;
- animation start/end, delay, duration, keyframe count, easing, Bezier shape, overshoot, bounce, stagger, and motion blur;
- pan, tilt, push, pull, handheld simulation, stabilization, parallax, Ken Burns, object tracking, and cursor-following motion;
- speed, time remap, freeze, reverse, ramp segments, interpolation, optical flow, and action alignment;
- motion trigger: stressed word, topic change, beat, reveal, gesture, static-frame reset, or transition;
- reset behavior at cuts and maximum unchanged hold.

Distinguish captured camera motion from post-production movement when possible; keep it unresolved when flattened evidence cannot decide.

## Transitions

Record:

- hard cut, dissolve, dip, fade, wipe, push, slide, zoom, blur, whip, flash, light leak, glitch, mask, morph, or custom transition;
- video/audio scope, placement, duration, direction, alignment, easing, and handles;
- paired SFX, music accent, motion match, color flash, or graphic element;
- context: ordinary dialogue, time/location change, chapter, montage, sponsor, CTA, intro, or outro;
- frequency, opportunity rate, repetition, and negative rules;
- whether the apparent transition is a source-camera move, nested render, effect, or composited overlay when project evidence exists.

## Text, captions, and typography

Separate template families: hook text, captions, lower third, name/title, chapter card, quote, citation, callout, list, statistic, CTA, disclosure, logo, and watermark.

For each family inspect:

- exact text, capitalization, sentence case, punctuation, number formatting, emoji, abbreviation, spelling, and filler-word policy;
- font family or visual alternatives, style, weight, italic, width, size, tracking, kerning, line spacing, baseline, and alignment;
- line count, characters/words per cue, line breaks, orphan avoidance, reading speed, minimum duration, and pause/speaker boundary behavior;
- position, anchor, safe margins, padding, responsive layout, collision avoidance, and aspect-ratio variants;
- fill, gradient, active-word highlight, stroke layers, shadow, background box, blur, opacity, radius, and blend mode;
- animation in/hold/out, per-word or per-character treatment, delay, stagger, easing, bounce, motion blur, and write-on;
- speech lead/lag, word highlighting, phrase replacement cadence, and persistence across cuts or B-roll;
- template/preset identity, editable controls, missing fonts, and rasterized/baked limitations.

From finished video, report a likely font family or nearest alternatives, never an exact font without identifying evidence.

## Graphics, compositing, and visual effects

Inspect:

- lower thirds, bugs, logos, frames, panels, cards, split screens, picture-in-picture, device mockups, screen replacements, progress bars, charts, maps, arrows, circles, underlines, scribbles, and cursor highlights;
- layer order, matte, mask, feather, tracking, keying, background removal, blur/redaction, blend, shadow, glow, and depth;
- repeated graphic systems, spacing, grid, palette, corner treatment, iconography, illustration, and brand behavior;
- intro/outro packages, chapter transitions, citations, disclaimers, and reusable templates;
- graph topology, inputs, expressions, modifiers, animation curves, and media dependencies when editable project data exposes them;
- plugin, template, font, logo, image, or license dependencies and supported fallbacks.

## Color and image finishing

Inspect by camera, scene, lighting condition, subject, and section:

- input/working/output color spaces, transforms, LUTs, DCTLs, display transforms, and metadata;
- exposure, white balance, tint, black point, white point, contrast, pivot, shadow/highlight detail, and highlight rolloff;
- saturation, vibrance, saturation by luminance, hue relationships, palette, split tone, and color separation;
- skin hue, luminance, saturation, consistency, subject/background separation, and product-color fidelity;
- curves, secondaries, qualifiers, windows, tracking, local corrections, vignettes, and relighting evidence;
- noise reduction, sharpening, grain, halation, bloom, glow, diffusion, chromatic aberration, lens effects, and texture;
- shot matching, camera matching, scene consistency, purposeful exceptions, and transition grades;
- grade topology and responsibility-separated nodes/layers when project evidence exists.

Use scopes and matched frames. A broad adjective such as `cinematic` is a summary, not a transferable rule.

## Dialogue, Fairlight, music, and sound design

Inspect:

- source/channel mapping, sync, linked audio, microphone identity, track roles, routing, buses, and stem availability;
- clip gain, track gain, automation, fades, crossfades, panning, stereo width, mono compatibility, and ambience continuity;
- noise floor, denoise, voice isolation, EQ, high-pass/low-pass, de-essing, compression, gate, limiter, saturation, reverb, and dialogue leveling;
- breath, pause, filler, false-start, overlap, interruption, room-tone, and sentence-splice treatment;
- integrated/short-term/momentary loudness, loudness range, dialogue range, true peak, and section-level changes;
- music role, cue boundaries, phrase/section alignment, beat or transient evidence, ducking depth, attack/release, transitions, cadence, and silence;
- SFX type, layer count, trigger, lead/lag, level, stereo placement, tail, repetition, and pairing with text, B-roll, transitions, zooms, or CTA;
- natural sound, ambience, foley, risers, impacts, whooshes, pops, stingers, and intentional absence.

Do not claim to have heard or separated elements when only filenames, waveforms, metadata, or imperfect stem inference are available.

## Platform and format variants

Compare:

- horizontal, square, vertical, and cropped versions;
- long-form, short-form, trailer, teaser, ad, and cutdown versions;
- hook replacement, shot reordering, pace, caption density, text size, safe areas, reframing, CTA, music, loudness, and duration;
- platform-specific graphics, branding, disclaimers, watermarks, end cards, and export settings.

Learn transformation rules between variants rather than treating each export as an unrelated style.

## Negative rules and exceptions

Explicitly look for:

- speaker changes that do not switch cameras;
- named entities that do not receive B-roll;
- beats that do not receive cuts;
- jump cuts deliberately left visible;
- captions omitted during graphics, B-roll, or sensitive moments;
- long shots intentionally protected;
- sections without music or sound effects;
- camera angles avoided for a speaker or topic;
- transition types present in the project but absent from delivery;
- grade or effect treatments restricted to one scene;
- maximum tolerated repetition, density, duration, or motion;
- asset, readability, continuity, emotion, or platform conditions that override the normal rule.

## Style profile summary

End with:

- five to ten highest-impact transferable rules;
- section and format overrides;
- assets required for exact reproduction;
- supported approximations;
- blocked or unresolved features;
- rules intentionally excluded because evidence was insufficient;
- recommended application order;
- per-rule verification plan.
