---
name: cutagent-edit-style-learning
description: Analyze Adobe Premiere Pro projects, DaVinci Resolve projects, or finished videos to learn conditional editorial rules and apply them to a new edit without blindly copying the reference.
license: AGPL-3.0-only
---

# Edit style learning

Learn an editorial grammar, not a LUT, preset, average cut length, or superficial look. Express each transferable behavior as: in context `X`, trigger `Y` usually leads to action `Z`, with measured timing, exceptions, confidence, and evidence.

## Choose evidence by source

Read only the source-specific reference needed:

- `references/adobe-premiere-project.md` for Adobe Premiere Pro projects or interchange exports;
- `references/davinci-resolve-project.md` for live projects, `.drp`, `.dra`, `.drt`, or timeline exports;
- `references/finished-video.md` for flattened video;
- `references/pattern-schema.md` when recording or applying the learned profile.

Use editable project state to learn exact active structure and parameters. Use the delivered render to establish what was actually visible and audible. Treat inactive versions, unused sequences, disabled layers, opaque effects, and filenames as weak evidence.

## Build an evidence map

Cover the complete relevant reference chronologically. Align transcript and speaker events, visible shot boundaries, camera roles, B-roll, text, graphics, motion, transitions, music, effects, color, and sound. Keep source, record, composition, and delivery time domains distinct.

For each candidate pattern:

1. Define qualifying opportunities, including non-occurrences.
2. Record trigger, action, timing, duration, frequency, context, and sequence position.
3. Split hook/body, dialogue/montage, platform, speaker, camera, and energy contexts before aggregating.
4. Identify exceptions and negative rules.
5. Label exact project facts, measured render behavior, inference, and unresolved details separately.

One occurrence is an observation. Promote a rule only when repetition, active project structure, or user confirmation supports it. Do not claim causation from coincidence or infer a hidden graph, plugin, font, camera, or audio chain from flattened output.

## Create a portable style profile

Summarize the highest-impact rules for narrative structure, rhythm, shot choice, B-roll, multicam, reframing, typography, motion, transitions, graphics, color, music, sound design, and finishing. Keep global defaults separate from scoped overrides. Give every rule evidence examples, confidence, reproducibility, application priority, and a concrete verification method.

When sources disagree, prefer the user's new-edit direction, then the delivered output, active master state, repeated related work, and finally inactive material. Preserve meaningful conflicts instead of averaging them away.

## Apply judgment, not timestamps

Map the profile onto real opportunities in the target content. Resolve conflicts in this order: user requirements; integrity, intelligibility, sync, legality, and delivery constraints; story and performance; high-confidence rules; low-confidence preferences.

Plan from macro to micro: structure and pacing, A-roll or multicam, B-roll, reframing and transitions, text and graphics, color, then audio. Use the focused Creative Skill for a domain pass when available; the learned profile supplies its constraints.

For local execution, read `cutagent-editing`, `cutagent-verification`; check the installed SDK declarations, public CutAgent CLI command cards, and live capabilities for exact operations.

## Compare the result

Check both whether the edit changed and whether it follows the learned rule. Compare target opportunities, applied rule IDs, exceptions, representative static frames, motion passages, and audible passages. Similar metadata is not style parity; a still cannot prove movement; stored settings cannot prove a mix.

Report analyzed coverage, highest-impact rules, applied and skipped rules, approximations, unavailable assets, consequential unknowns, source preservation, evidence reviewed, and remaining user judgment.
