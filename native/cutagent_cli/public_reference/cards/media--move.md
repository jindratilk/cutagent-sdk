# `media move`

Syntax: `cutagent media move [NAME] [TARGET] [--moves VALUE]`

## Search terms

- move clip to Media Pool bin
- organize asset into folder
- relocate source item between bins
- move footage out of Master
- file media into nested bin
- move audio clip to target folder
- change Media Pool item folder
- return clip to Master bin

## What it does

Move one clip and a saved setup array of clips to media pool folders.

## Do not use when

Use `media folders move` when moving an entire bin/subtree rather than one item. Use `media rename` when the item stays in its bin but needs a new display name. Do not use a name-only move until duplicate matches have been disambiguated by current folder and full Media Pool search.

## Preflight and readback

Use exact search to capture source folders, source paths, and uniqueness, then use `media folders tree` to prove each destination exists. Dry-run performs the complete shared source/destination preflight without moving.

## Public arguments and options

- `NAME` (optional) — Clip name
- `TARGET` (optional) — Target folder path
- `--moves` (optional) — JSON array of {name, target}, {path, target}, or {media_id, target} move items

## Boundaries and gotchas

- It accepts the same `/`/`>` navigation syntax and must already exist; no bin is created automatically.
- Dry-run connects to DaVinci Resolve and resolves both objects, unlike simpler dry-runs that only echo arguments.
- A missing source or destination therefore fails during dry-run.

## Examples

- `cutagent media move --help`
  Expected: Shows the public syntax, arguments, options, and documented defaults.
