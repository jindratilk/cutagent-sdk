# Motion-text construction recipes

These are original construction patterns, not serialized presets. Translate them into the exact supported nodes, inputs, and animation route described by the installed public CutAgent SDK and CLI reference and confirmed by live inspection.

## Directional word or line reveal

Build one editable text branch per semantic unit, not per glyph:

```text
Text+ -> unit Transform -> optional directional blur -> unit Merge
```

Lay out every unit in its final reading position first. Animate the unit Transform from a small offset into that position while opacity rises. Point the blur along the travel axis and animate its strength from visible to zero slightly before the transform settles. If the words must emerge from behind a boundary, add a stationary mask at the reveal edge; move the text through the mask instead of moving mask and text together.

Use a normalized entrance window of roughly the first 15-25% of the clip as a starting range, then tune by speech. For a two-line phrase, start line two only after line one has established its direction; use a short overlap rather than waiting for a complete settle. Keep every transform, blur, and opacity value neutral throughout the reading hold.

When copy changes, adjust the Text+ content and line layout first. Recalculate only the stagger and hold; do not scale a long phrase down until it technically fits if a better line break preserves hierarchy.

## Tracking or scale emphasis

For a restrained premium title, animate one typographic property and one supporting transform:

```text
Text+ with tracking/size animation -> small position or opacity settle -> output
```

Begin slightly wider or tighter than the settled tracking and converge slowly during the entrance. Keep the range subtle enough that letters never collide or become disconnected. If size also changes, use a small scale delta and a stable anchor so the phrase does not drift. This works best on a short phrase with generous negative space.

## Shine constrained to letterforms

Build the base text and highlight separately:

```text
base Text+ ---------------------------------> Merge -> output
soft bright band -> traveling Transform --\
text alpha/matte --------------------------- effect mask for the band
```

Use the text's alpha as the highlight boundary so the band cannot brighten the background. Angle the band to cross multiple letter stems, soften its edges, and move it completely across once. Keep the base readable without the shine. The pass should occupy only part of the settled hold and should not loop unless the brief explicitly asks for continuous signage.

## Layered hook with an accent word

Use separate branches for supporting copy, focal words, and small accents, then merge them before a shared parent transform:

```text
support Text+ --\
focal Text+ ---- layered Merges -> shared Transform -> output
shape accents --/
```

The focal word may use one stronger treatment—scale overshoot, brief flicker, outline reveal, or blur slide—while supporting copy uses a simpler entrance. Animate the shared parent only for a final small settle; large parent motion makes the internal hierarchy feel detached from speech.

For flicker, use a deliberately short irregular sequence that ends fully on. For shake, animate strength rather than leaving noise active during the hold. For stepped or stop-motion movement, use a small number of purposeful poses and hold each pose cleanly; random frame-to-frame jitter is not the same style.

## Duration model

Define four conceptual boundaries in composition time:

```text
start -> entrance end -> exit start -> end
```

Keep the designed entrance before `entrance end` and the designed exit after `exit start`. Stretch the interval between them for longer copy or speech. On short titles, reduce stagger before reducing the readable hold. On long titles, extend the clip and middle hold before slowing the entrance into a float.

Curve handles should create a fast readable arrival and a quiet settle. Use overshoot on only the focal layer. Review sampled frames around the first visible state, peak blur or overshoot, settled state, start of exit, and final disappearance, then review the complete phrase at speed.
