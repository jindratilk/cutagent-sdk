# `timeline clip-markers batch`

Syntax: `cutagent timeline clip-markers batch --batch VALUE --timeline-id VALUE`

## Search terms

- batch clip markers
- exact V1 clip identities
- chapter markers on clips
- clip-local marker offsets

## What it does

Insert clip markers in one batch using exact IDs and clip-local offsets. Entries require timeline_item_id, record_start, record_end, offset, duration, color, name and note. Different existing markers at requested positions fail preflight; identical existing markers are reused. Retimed, reversed, mixed-rate, or unproven source mappings are rejected before writes. Source and timeline frame rates must be known and match.

## Preflight and readback

Prepare all entries and run connected dry-run. If a mutation fails, reconcile the retained partial receipt before retrying.

## Public arguments and options

- `--batch` (required) — JSON file containing exact V1 clip marker entries
- `--timeline-id` (required)

## Boundaries and gotchas

- Required flags are --batch and --timeline-id.
- The file must be JSON, at most 16 MiB, with an array or an object containing entries.
- Duration is a positive integer and cannot extend beyond the clip end.
- Each target must match exactly one clip on V1.
- The command does not switch timelines or move the playhead.
- Duplicate positions in the input are rejected.
- The batch does not silently shift conflicting markers.
- Source-range and marker readback must be available.

## Examples

- `cutagent timeline clip-markers batch --help`
  Expected: Shows the public syntax, arguments, options, and documented defaults.
