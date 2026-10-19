# Changelog

All notable changes are recorded here. The format follows Keep a Changelog, and the project follows Semantic Versioning. The `v0.1.0` tag is created only when the v0.1 scope is complete.

## [Unreleased]

### Added

- README with scope, status and out-of-scope list.
- Problem statement with regulation facts checked on 2026-10-13.
- ADR 0001 (record architecture decisions) and ADR 0002 (OpenEMS Edge plus a separate Python layer).
- LICENSE (MIT), NOTICE.md, CITATION.cff and .gitignore.
- ADR 0003 (pin OpenEMS images by tag and digest) and ADR 0004 (development environment: Ubuntu VM).
- `deploy/compose.yaml` and `deploy/.env.example`: OpenEMS Edge and UI 2026.9.0 pinned by digest, ports bound to localhost.
- `deploy/edge-seed/`: Felix configuration files for a simulated chain on a household load profile, captured 2026-10-16.
- A one-shot `openems-edge-seed` Compose service that prepares a fresh Edge config volume: it installs the image's default config, then the seed.
- `deploy/smoke-test.sh`: checks the containers, console protection, the UI, startup activations, the live Debug Log and steady-state errors.
- `docs/runbook.md`: start, stop, reset, tunnel, known log messages, image update checklist and VM notes.
- ADR 0005 (documented default logins are allowed in the development stack only).
- `CONTRIBUTING.md`, `SECURITY.md` and `CODE_OF_CONDUCT.md` (adopts Contributor Covenant 3.0 by link), plus issue forms for bug reports and data corrections.

### Changed

- Compose: the Edge websocket port 8085 is no longer published. Added an Edge memory cap and container log rotation, both set in `deploy/.env.example`.
- ADR 0003 and ADR 0004 updated with the M2 evidence: clock behaviour, UTM version, OS updates and the image start-up dependency.
- README status and milestone table: M1 and M2 complete.

### Fixed

- Seeding an empty Edge config volume made Edge skip its own default config, leaving it without scheduler and websocket controller. The seed service now installs the image defaults first. Found by a fresh-volume test on 2026-10-16.
