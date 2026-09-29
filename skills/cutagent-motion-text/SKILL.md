---
name: cutagent-motion-text
description: Create original editable animated typography, hook text, kinetic words, and short-form text treatments in DaVinci Resolve Fusion. Use when text needs designed motion beyond ordinary captions or a static title.
license: AGPL-3.0-only
---

# Motion text

Build the treatment from editable Text+, shape, mask, effect, and animation work. Purchased title packs may inform the vocabulary, but do not copy a supplied title or paste a preset and merely replace its wording.

## Design the reading state

Start with the frame in which the message is easiest to read. Reduce the copy to one focal phrase and, when needed, one supporting line. Decide which semantic unit should move independently:

- Animate the whole block for a clean title or lower third.
- Animate by line when the phrasing has two beats.
- Animate by word to emphasize a small number of ideas.
- Animate by character only for a brief expressive moment; constant character motion weakens reading.

Use type scale, weight, case, line breaks, and contrast to establish hierarchy before adding effects. For separate line nodes, confirm their top-to-bottom reading order in a native settled frame before adding stagger; do not assume screen-pixel Y and Fusion Y run in the same direction. Prefer a dependable installed font or a user-approved brand font. Lay out the longest real copy, not a short placeholder, and preserve phone-safe margins for vertical work.

## Choose one motion grammar

Match movement to the voice and meaning rather than cycling through unrelated effects.

- **Confident:** a fast directional slide, short deceleration, and firm hold.
- **Conversational:** a small scale or position settle with soft blur decay.
- **Urgent:** stepped or stop-motion timing, a brief flicker, or controlled shake.
- **Premium:** restrained tracking change, mask reveal, shine pass, or subtle gradient movement.
- **Playful:** one elastic overshoot or staggered word entrance, followed by a quiet hold.

Treat blur, glow, erosion, shine, or shake as secondary motion that supports the primary transform. Tie blur direction to travel, let a shine cross the letterforms once, and decay shake before the viewer must read. Avoid combining several high-energy treatments on the same phrase.

## Choreograph the phrase

Map the entrance, settled reading hold, and exit to the actual speech or musical beat. Lead a spoken keyword by a few frames when anticipation helps; otherwise land it on the word. Stagger only units whose order matters. Keep the hold long enough to read at delivery size, then make the exit shorter and less attention-grabbing than the entrance unless the exit motivates the next shot.

For reusable work, separate content, styling, layout, and motion controls. Make duration changes preserve the entrance and exit while the reading hold expands. Keep every visible layer connected to the composition output and keep the graph legible enough for another editor to revise.

## Local execution

Read `references/construction-recipes.md` when building the actual treatment. It gives original graph topologies and timing recipes for directional reveals, shine, layered hooks, and duration adaptation.

For local execution, read `cutagent-fusion` and inspect the installed SDK declarations, public CutAgent CLI command cards, and live capabilities for exact Text+, node, keyframe, and `.setting` operations.

Use exact SDK types, capabilities, identifiers, and mutation routes from the installed SDK declarations, public CutAgent CLI command cards, and live capabilities. Do not infer them from the names of creative effects in this skill.

## Review

Inspect the settled frame at delivery size for hierarchy, line breaks, glyphs, contrast, and safe margins. Inspect multiple frames across entrance, hold, and exit for clipping, pops, accidental overlaps, excessive blur, and a readable pause. Structural graph or keyframe readback proves editability and timing data; only a temporal preview or rendered excerpt proves how the motion feels.

Report the original text treatment created, the editable controls exposed, what was structurally verified, what was reviewed in motion, and any font or appearance uncertainty.
