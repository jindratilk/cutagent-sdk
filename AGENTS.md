# CutAgent standalone repository guide

This public repository contains the AGPL-3.0-only standalone CutAgent SDK, local CutAgent CLI/runtime, and reviewed Agent Skills. Work from the owning source and current release status. Run the source, skills, runtime, and package checks for a change before claiming it works.

`skills/` contains public instructions for local DaVinci Resolve work. `skills/cutagent/SKILL.md` is the entry router; each other directory is a focused Agent Skill. Keep every skill independent of CutAgent accounts, subscriptions, Cloud services, private asset catalogs, and the commercial desktop runner. A skill may use user supplied files, a separately installed local tool, the public SDK, the public CutAgent CLI, or live DaVinci Resolve capabilities. It must not present an unavailable standalone feature as built in.

Edit skill source directly, then run `node scripts/verify-skills.mjs --write` to update the exact public manifest and `npm run verify:skills` to check it. Review every new file before publication. Do not mirror the private CutAgent monorepo or its Agent Knowledge and Creative Skills wholesale. The public skill text and assets are an expressly reviewed AGPL projection.

`native/cutagent_cli/public_reference/` is the generated version-matched CutAgent CLI reference. SDK declarations and installed runtime capabilities own exact executable facts; skills should point to them instead of copying command inventories. Do not hand-edit extracted or generated SDK/CLI sources or source inventories. `RELEASE_STATUS.md` owns current qualification and limitations; tests or documentation edits do not establish a new live DaVinci Resolve acceptance.
