---
name: cutagent-setup
description: Install and connect the standalone CutAgent SDK and CutAgent CLI to DaVinci Resolve Free or Studio on a supported local machine. Use for setup, transport, discovery, and connection errors.
license: AGPL-3.0-only
---

# Standalone setup

Check the installed package's `README.md`, `docs/GETTING_STARTED.md`, and `RELEASE_STATUS.md` for the current qualified platforms and prerequisites. The source package is built and packed locally; a GitHub skill installation does not install the CutAgent runtime.

Run `npx cutagent setup` for Studio or `npx cutagent setup --free` for Free after installing the package. Start `cutagent runtime start --transport studio_external` for Studio or `--transport embedded_free` for Free. Studio needs external scripting set to Local; Free needs its installed CutAgentSDK script activated from DaVinci Resolve's Scripts menu after the runtime starts.

Check `cutagent --json status`: require `data.status === "connected"` and `data.resolve === true`. A ready runtime process or `cutagent status --json` installation metadata is not a live DaVinci Resolve connection. Use the discovery file printed by the runtime when the SDK script runs in another shell. Follow structured connection errors; do not use development authorization bypasses or change another CutAgent installation's launcher.
