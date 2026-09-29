---
name: cutagent-sdk
description: Author a local TypeScript or JavaScript editing workflow with the standalone CutAgent SDK. Use for multiple related DaVinci Resolve operations that need typed state, preview, recovery, and readback.
license: AGPL-3.0-only
---

# CutAgent SDK

Use the installed `cutagent` package and its declarations for exact methods and types. Connect with `CutAgent.connect()`, select the actual project and timeline, obtain a fresh snapshot, and close the client in `finally`. Use semantic domain methods before typed actions; use CutAgent CLI for a bounded operation when it is clearer.

For mutations, identify durable objects and distinguish source, timeline record, and Fusion frames. Where a method offers a preview, inspect its affected and protected state before applying it. Supply the required idempotency key, retain the operation reference, wait for a terminal result, and refresh state before dependent work. A timed-out local wait does not cancel an operation. On uncertainty, reattach or inspect state before retrying with the original key. `partially_applied`, `verification_failed`, and recovery failures need their returned evidence reviewed.

Read `cutagent/actions`, the package's TSDoc and examples for exact action carriers, arguments, and return types. An exported method does not prove that the connected DaVinci Resolve edition currently supports it. Compare the live result and capability report. Never invent an SDK symbol or bypass types for a mutation.
