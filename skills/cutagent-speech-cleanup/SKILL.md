---
name: cutagent-speech-cleanup
description: Tighten spoken-word edits while preserving meaning, personality, breaths, reactions, and natural rhythm. Use for podcasts, interviews, talking heads, tutorials, or social videos with pauses, fillers, false starts, repeats, or setup talk.
license: AGPL-3.0-only
---

# Speech cleanup

Edit for clarity, not maximum cut count. The speaker should sound like their best natural take, not like a transcript with every imperfection removed.

## Choose the pace

Use **Natural** for intimate interviews and documentary speech, **Balanced** for most creator and educational work, and **Fast** for concise ads or short-form. Treat those labels as rhythm intentions, not fixed pause thresholds.

Map the complete relevant transcript in bounded chronological windows. Mark long pauses, fillers, abandoned starts, corrections, repeated ideas, failed takes, setup talk, and transcript gaps. Carry incomplete thoughts across window boundaries so no passage is skipped or judged twice.

## Make contextual decisions

Review every candidate with the words, breath, reaction, and picture immediately around it. Classify it as remove, shorten, keep, or manual review.

- Preserve repetition used for emphasis, humor, emotion, or rhetoric.
- Keep transitional words when they organize the thought.
- Prefer the complete corrected take when intent is unambiguous.
- Retain space after a question, topic turn, emotional beat, or punchline.
- Vary pauses according to syntax and performance; identical gaps sound mechanical.
- Keep enough room around words to preserve consonants, tails, breaths, and room tone.

Use acoustic silence analysis only where the transcript has no reliable speech coverage, and inspect for laughter, breathing, music, or off-mic speech before cutting.

## Protect continuity

Check the picture around every proposed edit. Move a boundary, preserve more pause, or use an available cutaway when a cut creates a distracting gesture, pose, expression, or camera discontinuity. Do not retain irrelevant speech merely to avoid a jump cut when a truthful visual cover exists.

For local execution, read `cutagent-captions`, `cutagent-editing`, `cutagent-verification`; check the installed SDK declarations, public CutAgent CLI command cards, and live capabilities for exact operations.

## Review

Review all uncertain joins plus representative beginning, middle, and end sections. Confirm meaning is unchanged, no word edge is clipped, breaths and room tone feel natural, speaker handoffs remain intelligible, and picture continuity holds. Structural readback proves the edit plan landed; audition proves the speech still sounds human.

Report the pacing intention, removed/shortened/kept decisions, duration change, visual covers, listening evidence, and manual-review passages.
