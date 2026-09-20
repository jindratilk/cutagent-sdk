# Author Creative Skills

Create or revise a Creative Skill only when the user asks to save reusable CutAgent behavior. A Creative Skill supplies editorial judgment, visual or sonic direction, and a specialized DaVinci Resolve workflow. It does not replace Agent Knowledge or prove that its workflow has run successfully.

## Define reusable behavior

Write for several realistic requests, not one project's names, paths, timecodes, or current selection. State the intended viewing result, the choices the agent should make, the scope it should preserve, and the evidence that would support completion. Give the agent room to use professional judgment where several edits could satisfy the request.

Include guidance that corrects a recurring mistake or supplies useful, non-obvious domain knowledge. Use editorial guidance when several outcomes are valid, parameterized command or SDK patterns when one route is preferred, and a deterministic script only for a fragile repeated transformation. Do not turn discoverable runtime facts into fixed skill policy.

Put all activation language in the frontmatter `description`; the body is read only after activation. Use a precise lowercase hyphenated name and a description that distinguishes the workflow from neighboring skills.

```markdown
---
name: interview-story-cut
description: Shape a long-form interview into a concise story-led edit while preserving the speaker's meaning. Use for interview selects, narrative restructuring, or pacing passes driven by spoken content.
---

# Interview story cut

Preserve the speaker's meaning while removing repetition and weak setup.

## Editorial approach

Identify the central claim, arrange only the context needed to understand it, and prefer complete thoughts over mechanically short clips. Keep intentional pauses when they add emphasis.

## Execution

Inspect the current audible timeline and transcript. Propose a bounded story order, apply it to the authorized range, then re-check continuity at each changed edit point.

## Completion

Report the retained story beats, material removed or moved, continuity checks performed, and any passage that still needs editorial review.
```

Keep technical facts in their maintained source. For SDK execution and exact symbols, read [SDK usage](sdk.md). For timeline structure, read [editing](editing.md) and [timing and targets](timing-and-targets.md). Load [Fusion](fusion/REFERENCE.md), [audio](audio.md), [color](color.md), [captions](captions.md), or [rendering](rendering.md) only when the Creative Skill actually uses that domain. Use [checking results](checking-results.md) for the proof appropriate to the claimed outcome and [errors and recovery](errors-and-recovery.md) for partial or uncertain operations.

Do not copy SDK declarations, CutAgent CLI catalogs, Fusion registries, capability lists, error inventories, or edition claims into the skill. Those facts are version-matched Agent Knowledge and live-runtime concerns. A Creative Skill may explain why and when a technique serves its creative result, then direct the executing agent to the relevant technical reference.

## Add resources only when they earn their context

Keep the reusable path in `SKILL.md`. Add a resource when it prevents repeated rediscovery or keeps a conditional branch out of the main instructions:

- Put detailed variants, style language, examples, and decision rubrics in `references/`.
- Put deterministic text helpers in `scripts/`. Export the individual script into the session workspace before running it; activation does not execute resources.
- Put text templates or other text assets consumed by the workflow in `assets/`.

Point to each resource from `SKILL.md` with the condition for reading or exporting it. Do not add empty folders, placeholder files, duplicated summaries, or a resource for material already maintained by Agent Knowledge.

When a helper is intended for `cutagent-sdk`, make it an ES module whose default async function accepts the supplied runner context. Reuse the supplied values rather than reconnecting or re-reading the initial timeline snapshot:

```js
export default async function findInterviewClips({ sdk, project, timeline, snapshot, progress }) {
  const selection = sdk.selectTimelineClips(
    snapshot,
    (clip, track) => track.type === "video" && clip.name.startsWith("Interview"),
    { limit: 100 },
  );

  progress(`Found ${selection.items.length} interview clips`);
  console.log({
    project: project.name,
    timeline: timeline.name,
    clips: selection.items.map(({ clip, track }) => ({
      name: clip.name,
      track: track.index,
      range: clip.recordRange,
    })),
  });
}
```

This helper only selects and reports snapshot-bound clips. A skill that changes them must use the current semantic domain methods, await their terminal results, and refresh state before a dependent mutation. Do not present a read-only helper as an edit.

## Save a personal skill

In the CutAgent app, use `cutagent_skill_create_draft` only after an explicit request to create or save a skill. Supply `name`, `description`, `instructions_markdown`, `resources`, and `enabled`. Use an empty `resources` array when the skill is self-contained.

The current creation service accepts names of 3–64 lowercase letters, digits, or hyphens, with a letter or digit at both ends. Descriptions are required and limited to 240 characters. Each created resource must be non-empty UTF-8 text under `references/`, `scripts/`, or `assets/`; creation accepts at most 20 resources of 64 KiB each. Keep `SKILL.md` below the 128 KiB loader limit.

Pass `enabled: false` for a draft and `enabled: true` when the user asks to make it active immediately. Report any untested branch instead of implying that activation validates it. The tool refuses a duplicate skill name and currently creates new personal skills; it does not update an existing skill in place. Built-in Creative Skills are server-owned and cannot be edited through this local creation route.

## Validate what the skill actually claims

Check three things separately:

1. **Package validity:** the service accepts the frontmatter and resources, and reports the expected `draft` or `ready` status.
2. **Agent behavior:** fresh prompts activate the skill for its intended requests, avoid unrelated requests, choose the correct branch, and preserve the user's current scope.
3. **DaVinci Resolve result:** when the skill claims an editing outcome, run a representative authorized case and inspect the evidence required by that outcome. Structural readback can prove structure; temporal playback is needed for motion and pacing; audition is needed for sound quality.

Record untested branches as unverified. Enabling a skill, exporting a helper, receiving a zero exit status, or seeing one still frame does not establish native or creative success. After testing, remove instructions that did not change behavior and move conditional detail behind precise resource pointers.

For a complex or substantially revised skill, forward-test realistic prompts in fresh agent contexts. Check both intended activation and nearby requests that should not activate it, then prune no-op instructions and repeat the test without leaking the expected route or previous conclusions into the prompt.
