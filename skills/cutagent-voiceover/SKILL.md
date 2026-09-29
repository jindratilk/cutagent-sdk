---
name: cutagent-voiceover
description: Select, edit, and place locally supplied narration or voiceover takes in DaVinci Resolve. Use for explainers, ads, accessibility narration, dubbing, or a recorded voice track.
license: AGPL-3.0-only
---

# Local voiceover

Work from recorded or user supplied audio files. This skill does not generate a synthetic voice or call a voice provider. If the user has only a script, prepare a performance brief and request a recorded file or use a local tool that is already available and explicitly chosen for the task.

## Direct and select

Confirm the approved script, language, pronunciation, speaker role, pace, and emotional tone. Compare available takes by listening to the complete sentence in context. Note difficult names, numbers, abbreviations, and language changes. Do not choose a take solely from its filename or waveform.

## Place and mix

Identify the exact timeline and intended narration range. Trim the selected take at natural phrase boundaries, preserve breaths that support the performance, and synchronize it to picture without stretching speech unnecessarily. Put narration on a named audio track and avoid doubled scratch or reference audio. Read `cutagent-audio` and `cutagent-editing` for local execution; use the installed CutAgent SDK or CutAgent CLI for exact operations.

Listen to the result with music and effects, then inspect the rendered passage. Report the source take, timing decisions, any missing pronunciation or recording fix, and what was actually auditioned.
