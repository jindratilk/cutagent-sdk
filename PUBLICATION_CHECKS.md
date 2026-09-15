# Source publication checks — 2026-09-15

- Upstream source: CutAgent 3.0 checkpoint `afab93c4f`; 1,544 extracted source hashes verified, including the new marker batch and reviewed terminal projection repair.
- Standalone-owned Free integration is preserved. Agent Knowledge references match current upstream after package-name substitution.
- 98 Python tests pass. Build and strict consumer types pass. Runtime suite: 47 initial passes; two stale action counts corrected and the affected three tests passed.
- Installed tarball consumer passes public imports, strict types, setup, status and uninstall; this check does not connect to DaVinci Resolve.
- Gitleaks scanned all 1,815 candidate source files. Two findings were inspected: a named audio EQ preset and a fixed test idempotency identifier; neither is a credential. No confirmed secrets or developer-local path markers found.
- Commercial application, cloud/billing code, private Creator Skills, vendor applications, local QA profiles and private release reports are excluded.
- AGPL-3.0-only license preserved. Previous Git refs were saved in a verified maintainer-local bundle before replacing public history.
- See RELEASE_STATUS.md for exact native test provenance and platform limitations. npm publication is separate from source availability.
