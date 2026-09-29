---
name: cutagent
description: Route an agent working on a DaVinci Resolve project through the standalone CutAgent SDK, CutAgent CLI, and focused local editing skills. Use for editing, inspecting, captioning, grading, audio, Fusion, or delivery tasks.
license: AGPL-3.0-only
---

# CutAgent standalone

Help the user produce an editable result in DaVinci Resolve using the locally installed `cutagent` package. This skill is a router; read only the focused skill that fits the next task. All workflows use the public package, local tools, and supplied or locally licensed media.

## Choose a route

- Read `cutagent-setup` for installation, DaVinci Resolve Free or Studio connection, and live status.
- Read `cutagent-sdk` for composed TypeScript edits with shared state and durable operations.
- Read `cutagent-cli` for a focused command, diagnostics, or a capability without a suitable SDK method.
- Read the focused domain skill for projects, editing, Fusion, audio, captions, color, multicam, or rendering. Load an optional `cutagent-*` creative skill only when it matches the user's intended result.
- Read `cutagent-verification` before claiming a visual, audible, temporal, or delivered outcome.

The installed SDK declarations and `native/cutagent_cli/public_reference/` are the exact version-matched API and command sources. Check live `cutagent --json capabilities` and `cutagent --json status` before depending on a feature or connection. DaVinci Resolve edition, transport, current project, and media matter more than a remembered command name.

## Work on the user's target

Bind changes to the intended project, timeline, clip occurrence, source, and time domain. Preserve unrelated work, linked audio, media, and editability. Inspect the relevant state, make the smallest coherent change, then verify the actual result. An operation can partially apply even when a wait or process fails; inspect live state before retrying. Do not treat an exit code or one still frame as proof of an entire edit.

Use supplied local media and assets with suitable rights. When a needed input is unavailable, ask for that input or use a separately installed local tool chosen for the task. Do not request credentials for CutAgent services.
