# CutAgent CLI

Use CutAgent CLI through `cutagent` for focused inspection, one supported operation, or a CLI-only feature. Use CutAgent SDK for composed authoring that shares state across several operations; see [SDK usage](sdk.md). For installation and transport startup, see [setup](setup.md).

## Find the exact command

Do not reconstruct command names or flags from memory. Search the version-matched command catalog at the path supplied by the CutAgent runtime, then read the relevant command card or plain-text help. In a standalone CutAgent package checkout, the same catalog is at `native/cutagent_cli/public_reference/catalog-context.md`. From a Node project with CutAgent installed, `import.meta.resolve("cutagent/package.json")` locates that package root; if neither path is available, use command help.

```sh
cutagent timeline summarize --help
```

Plain help is human-readable. Add `-j` or `--agent` when a script needs the structured help payload instead. Treat the catalog as syntax documentation, not proof that the active DaVinci Resolve edition and project support a feature. Use `cutagent capabilities FEATURE_ID` when the command card identifies a feature whose live support matters.

Do not assume Studio transport. `status` reports the active `studio_external` or `embedded_free` connection. Blackmagic's external scripting preference applies to Studio; Free connects through CutAgent's embedded script.

## Read only the state you need

- Use `status` for connection, edition, project, and timeline readiness. Add `--include-ui` only when a modal or macOS UI-readiness problem matters because it can request Automation permission.
- Use `context` for the current page, playhead, marks, and item at the playhead.
- Use `timeline summarize` for an editor-readable map around the playhead. It defaults to a 30-second radius; request `--window all` or `--include-items` only when the full map or item rows are needed.
- Use narrower track, clip, media, or property reads when an exact identity or value drives the next operation. Observe each command card's distinction between source, record, and Fusion time.

```sh
cutagent --agent status
cutagent --agent context
cutagent --agent timeline summarize --radius 20s --track-type video
cutagent -j --select name,id timeline list
```

Prefer `--agent` for compact readable output. Use `-j` / `--json` when code needs exact fields. `--select` projects JSON reads to named fields and avoids loading irrelevant output.

If compact output is truncated, read the spill file named in the marker or rerun with the suggested narrowing flags. Repeating the same broad command does not reveal more information.

## Mutate an exact target

Use `--dry-run` when the chosen mutation supports a useful preview. A dry run validates and reads but does not prove the eventual mutation will succeed. When the same supported change applies to several clips, use a `bulk` subcommand instead of invoking a single-clip command repeatedly. Preview the selector once, then reuse it for one mutation:

```sh
cutagent --agent bulk select --track 2 --name-starts-with c- --duration 4s
cutagent --agent --dry-run bulk clip-color-set Orange --track 2 --name-starts-with c- --duration 4s
```

Check that the matched occurrences, track type, track index, and record range are the intended targets. Bulk results can be partial; inspect the returned `matched`, `applied`, and `failed` rows and retry only failed targets with a narrower selector. `--fail-fast` stops later work but does not roll back earlier successful rows.

Do not turn preflight into a ritual. A read-only request needs no mutation preview, and a uniquely identified single clip does not need a bulk scan.

## Interpret completion and errors

JSON responses always use `ok`, `data`, `error`, and `meta`. Branch on `ok` and the stable `error.code`, not message text. Exit codes classify success (`0`), validation or policy (`2`), environment or tooling (`3`), DaVinci Resolve/API runtime (`4`), and unexpected internal failure (`1`).

For a mutation, inspect returned per-target results and relevant metadata such as `verification_status`, `recoverability`, and `rollback_hint`. Process exit alone does not prove a visual, audible, or motion result. Use the smallest relevant state readback and add rendered or visual evidence only when the claim requires it; see [checking results](checking-results.md).

On failure, preserve any successful rows or recovery information before retrying. Follow structured details and suggested fixes, and run retries sequentially after `DB_LOCKED`. See [errors and recovery](errors-and-recovery.md) for recovery decisions.
