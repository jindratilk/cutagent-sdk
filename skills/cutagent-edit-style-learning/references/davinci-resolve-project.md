# DaVinci Resolve project evidence

Use this reference for a live project, `.drp`, `.dra`, `.drt`, exported timeline, or project database. Analyze through the supported public SDK or CutAgent CLI. Read the relevant public CutAgent technical skill and installed command reference for exact operations, selectors, capability boundaries, recovery, and verification.

## Choose the richest safe source

Prefer an already open authoritative project when available. It exposes active timeline structure, Fusion, Color, Fairlight, and render state without importing anything.

Importing a `.drp`, restoring a `.dra`, or adding an interchange timeline changes project state. Do that only when the requested analysis authorizes it, after recording the original project and timeline and checking name collisions. Use an isolated destination when practical, verify the imported identity, analyze without editing the reference, and restore the original context. Never overwrite or delete a same-named project as incidental cleanup.

Treat `.drt`, FCPXML, AAF, EDL, and OTIO as partial evidence. They may omit or flatten Fusion, grades, effects, captions, multicam state, and Fairlight routing. A delivered render remains the authority for what was visible and audible.

## Identify the authoritative timeline

Inventory final, master, approved, social, vertical, trailer, clean, captioned, source, selects, sync, multicam, test, and archived timelines. Use user direction, current activation, naming, settings, and delivered-render evidence together. Do not choose the longest timeline automatically.

Record the timeline's frame rate, start timecode, resolution, duration, tracks, locks, visibility, mute state, markers, and settings. Keep timeline record positions distinct from media source positions and Fusion composition frames.

## Build the composited event map

For every relevant video, audio, and subtitle track, record item identity, active state, record range, source range, linked media, speed, transitions, generators, titles, adjustment clips, Fusion clips, compounds, nested timelines, multicam items, and offline media.

Map what is actually visible. A cut on V1 may be covered by B-roll, Text+, Fusion, an adjustment clip, or another upper-track item. A present item, effect, or track is not style evidence when it is disabled, hidden, disconnected, or outside the delivered range.

Derive:

- visible shot boundaries, duration distributions, density by section, J/L relationships, and dialogue surgery;
- shot-size and camera sequences, source reuse, handles, action alignment, transitions, and purposeful discontinuity;
- B-roll function, entrance and return timing, audio treatment, and interaction with captions or graphics;
- exact active transforms, keyframes, retimes, effects, and repeated parameters when exposed.

Use a fresh transcript when speech drives the edit. Align speaker, pause, sentence, and topic events with the record-domain map.

## Inspect domain structure

### Multicam

Establish true camera and speaker roles from visual evidence, not angle number or filename. Measure switch timing, holds, reactions, wide resets, overlap, interruption, laughter, backchannels, and cases where the edit deliberately does not switch. Distinguish real angles, digital crops, B-roll, screens, and graphics.

### Fusion and Text+

For every visible composition, record composition identity, node roles, topology, MediaOut path, text ownership, layout, images, masks, keyframes, expressions, modifiers, and missing dependencies. Separate reusable title families and their editable controls. A graph can prove structure but not appearance; compare final pixels and temporal behavior.

### Color

Inspect the active grade version and active node path by camera, scene, lighting condition, and subject. Record correction versus look responsibilities, color management, LUT/DCTL or OFX dependencies, qualifiers, windows, tracking, texture, and deliberate exceptions. Ignore inactive versions and disabled nodes. Use matched frames and scopes to establish output behavior.

### Fairlight

Map track roles, source channels, linked state, clip and track levels, fades, pan, routing, buses, EQ, dynamics, automation, voice processing, music, sound effects, ambience, and silence when available. Stored values are structural evidence; audition is required for claims about clarity, continuity, musical fit, or mix quality.

### Titles, captions, markers, and delivery

Separate native subtitles from designed Text+ captions. Record title families, typography, safe-area behavior, animation, marker conventions, delivery settings, and transformations between horizontal, vertical, captioned, clean, trailer, or language variants.

## Turn project facts into style rules

Use `pattern-schema.md`. Give active, repeated behavior corroborated by output the strongest confidence. Downgrade inactive timelines, ambiguous duplicate items, incomplete media, opaque plugins, missing fonts or LUTs, stored audio without audition, and graph values without visible output.

For application, load the relevant public CutAgent technical skill. Map learned rules to target opportunities, not reference timestamps. Preserve the reference and work only on the authorized target or an appropriate reversible copy.

## Report limitations

State which timelines and tracks were covered; which fields were exact, measured, inferred, or unavailable; which output was visually reviewed or auditioned; which dependencies were missing; whether the original context was restored; and which learned rules remain blocked or approximate.
