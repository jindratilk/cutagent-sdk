# Generated voice and video

Use this reference when the user asks for AI-generated narration or video. These are hosted, billable creation services. They create media files; they do not place those files in a DaVinci Resolve timeline.

## Choose the available route

In a signed-in CutAgent desktop chat, use CutAgent CLI for current hosted generation:

- `audio voice-list` and `audio voice-generate` create an MP3 voiceover.
- `video generate` creates an MP4 video and attaches it to the active chat.

The public SDK voice catalog is active, but `client.voice.generate()` is currently release-gated and terminates with `CAPABILITY_UNAVAILABLE` before usage is reserved. There is no current semantic SDK video-generation method. Do not replace the working app CLI route with either unavailable SDK path.

Hosted generation is unavailable to a standalone agent that has no signed-in CutAgent desktop context; video generation additionally requires an active CutAgent chat. Do not ask for provider keys or account tokens. When the user supplies an existing generated file, continue with [projects and media](projects-and-media.md) to import it and [audio](audio.md) when it is voice or other sound.

## Generate voiceover

Find a current voice ID rather than inventing one. Search account voices first; search the public library only when the account has no suitable voice:

```sh
cutagent -j audio voice-list --source account --search "warm narrator" --limit 10
cutagent -j audio voice-list --source library --language en --use-case social_media --sort trending --limit 10
```

Review the returned voice name, description, language, accent, and rate information. Preserve the selected `voice_id`. Exclude custom-rate voices unless their additional cost is intentional.

Choose a new destination and validate it without contacting the hosted service:

```sh
cutagent -j --dry-run audio voice-generate \
  --voice-id voice_123456 \
  --text "This is where the story changes." \
  --output "$PWD/story-turn.mp3"
```

Then run the same request without `--dry-run`:

```sh
cutagent -j audio voice-generate \
  --voice-id voice_123456 \
  --text "This is where the story changes." \
  --output "$PWD/story-turn.mp3"
```

Omit voice settings to use the selected voice's stored defaults. Override them only for a deliberate delivery change:

- `--stability`, `--similarity-boost`, and `--style` accept values from 0 through 1.
- `--speaker-boost` controls an additional similarity pass.
- `--speed` accepts 0.7 through 1.2.
- `--seed` requests best-effort repeatability; it does not guarantee identical audio.
- Repeat `--pronunciation-dictionary DICTIONARY_ID[:VERSION_ID]` up to three times for known pronunciations.
- Use previous/next text or request IDs when adjacent generated segments need continuity.
- Use `--text-normalize auto|on|off` only when the spoken treatment of numbers or symbols needs control. Language-specific normalization is currently useful for Japanese and may add latency.

Text is trimmed and must contain 1–10,000 characters. Write names, abbreviations, dates, and numbers as they should be spoken. Generation may still vary, so audition the complete result.

Success returns `output_path`, `size_bytes`, the actual `voice_id`, applied settings, seed, rate multiplier, character count, available usage, and a provider request ID. Confirm `ok: true`, use the returned path rather than reconstructing it, and check that the MP3 is nonempty. The command's file verification proves a retained download, not pronunciation, tone, timing, or mix quality.

Without `--force`, an existing destination fails before billable work. Use `--force` only when replacing that exact file is intended. On failure, inspect the JSON error before retrying; do not change voice, text, settings, seed, or destination while treating a retry as the same request.

## Generate video

Describe visible subject and action, setting, composition or camera movement, light, and intended mood. Put essential constraints in the prompt; the command exposes only prompt, resolution, ratio, duration, and seed.

Validate the request first:

```sh
cutagent -j --dry-run video generate \
  --prompt "One continuous slow aerial move above a misty pine forest at sunrise, wide cinematic composition, soft amber light" \
  --resolution 1080P \
  --ratio 16:9 \
  --duration 5 \
  --seed 42
```

Then submit the same settings:

```sh
cutagent -j video generate \
  --prompt "One continuous slow aerial move above a misty pine forest at sunrise, wide cinematic composition, soft amber light" \
  --resolution 1080P \
  --ratio 16:9 \
  --duration 5 \
  --seed 42
```

The current command accepts:

- a prompt of 1–5,000 characters;
- `720P` or `1080P` resolution;
- `16:9`, `9:16`, `1:1`, `4:3`, `3:4`, `4:5`, `5:4`, `9:21`, or `21:9` ratio;
- an integer duration from 3 through 15 seconds;
- an optional seed from 0 through 2,147,483,647.

Resolution and duration affect hosted cost. A fixed seed can improve similarity between attempts but does not make generation deterministic. Do not invent image inputs, reference-video inputs, negative prompts, audio controls, model selection, prompt extension, shot-type, watermark, or other provider parameters that the command does not expose.

The command waits for the hosted job and downloads its result into the active chat. Success returns `status: "succeeded"`, `output_path`, `artifact_id`, `size_bytes`, actual settings, model, and available usage. A submitted job, task ID, or polling response is not success. If the command yields while still running, continue the same terminal session; do not submit a second job. If it fails or times out, read the error and preserve the same settings while recovering the pending job.

## Place and check generated media

Generation and timeline editing are separate stages. Use the exact returned path.

For generated voice, `audio voice-place` provides exact audio-only placement when the project, timeline, unlocked track, and absolute record frame are already known:

```sh
cutagent -j audio voice-place "$PWD/story-turn.mp3" \
  --track 1 \
  --absolute-record-frame 86400
```

Its result is only partial structural proof. Inspect the target audio track and audition the placed clip before approval.

For generated video, import `output_path`, resolve the resulting Media Pool item, then use the semantic SDK editing APIs or `media append` with an explicit target. Do not select by an ambiguous filename. Check several representative frames and play the relevant interval: a single frame cannot prove motion, continuity, or temporal artifacts.

Continue with [checking results](checking-results.md) for visual and audio evidence, [errors and recovery](errors-and-recovery.md) for failed or uncertain operations, and [SDK guidance](sdk.md) when composing placement with other edits.
