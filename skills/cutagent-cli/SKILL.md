---
name: cutagent-cli
description: Use the standalone CutAgent CLI for focused DaVinci Resolve inspection, editing, diagnostics, and CLI-only capabilities. Use when exact command syntax or structured results are needed.
license: AGPL-3.0-only
---

# CutAgent CLI

Use the `cutagent` executable. Read exact syntax from installed `native/cutagent_cli/public_reference/index.json`, its matching command card, or `cutagent <command> --help`; do not reconstruct flags from memory. Check `cutagent --json status` and live `cutagent --json capabilities` when connection or feature availability matters.

Use `--json` for machine results and branch on `ok`, `data`, `error`, and `meta`. Inspect the smallest relevant project, timeline, clip, or media state. Use supported dry runs and selectors for mutations, verify the matched occurrences, then inspect per-target results and read back the changed state. A bulk operation can partially apply. Follow `error.code` and `suggested_fix`; do not replay an uncertain mutation solely because a process exited nonzero.

The reference documents syntax. It does not prove a feature works in the active DaVinci Resolve edition, project storage, or transport. Keep native operations on the public CutAgent CLI path rather than editing its local database implementation directly.
