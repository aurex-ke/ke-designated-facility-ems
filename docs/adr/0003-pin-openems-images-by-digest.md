# ADR 0003: Pin OpenEMS images by tag and digest

- Status: Accepted for v0.1. M2 validation passed on amd64 (see Open points). Revisit when updating a pin.
- Date: 2026-10-15
- Updated: 2026-10-17

## Context

Reproducibility rules require pinned image versions. A tag such as `2026.9.0` can in principle be re-pushed to point at different content, and `latest` moves at any time. OpenEMS publishes Docker images for Edge and for its built-in UI.

Evidence gathered on 2026-10-15 (output of `docker buildx imagetools inspect`, run by the maintainer on Docker Engine 29.9.0):

- `openems/edge:2026.9.0` exists, index digest `sha256:afd148c64b9d619bd9d2fd34591f9691a0300c1906fb38f808f151fc51cea836`, with `linux/amd64` and `linux/arm64` manifests.
- `openems/ui-edge:2026.9.0` exists, index digest `sha256:77dc3cc85597715ed8470106d2c752792c37f515a19195dc4ddd4d363e67713e`, with `linux/amd64` and `linux/arm64` manifests.

Conflicting sources, recorded and not resolved by guessing:

- A Docker Hub tag listing seen through a search engine on 2026-10-13 showed `2026.4.0` as the newest numbered tag. The registry query above shows `2026.9.0` exists, so that listing was stale.
- OpenEMS release pages on GitHub list a `2026.9.0` release (seen through search results on 2026-10-13; the release notes were not read in full).

## Decision

1. Use OpenEMS Edge and UI version `2026.9.0` for v0.1.
2. Reference each image as `name:tag@sha256:<index digest>` in `deploy/.env.example`. The digest is of the multi-architecture index, so the same pin resolves to the right build on x86-64 and arm64.
3. Never use `latest` or a bare tag.

## Updating a pin

1. Run `docker buildx imagetools inspect <image>:<new tag>` for both images and confirm the tag exists for the platforms we use.
2. Read the upstream release notes for the new version.
3. Read the Edge image's start-up script again, because the seed service in `deploy/compose.yaml` depends on it: `/etc/s6-overlay/s6-rc.d/init-openems-config/run` installs the image's default config only into an empty config directory, and reads it from `/var/lib/openems-default-config` (read in 2026.9.0 on 2026-10-16; the command is in `docs/runbook.md`, section 7).
4. Update both values in `deploy/.env.example`, test on a fresh volume, run `deploy/smoke-test.sh` (see `docs/runbook.md`), and record the change in `CHANGELOG.md` and in a new ADR if behaviour changes.

## Consequences

- Pulls are reproducible and a re-pushed tag cannot silently change what we run.
- Pins do not receive upstream security fixes until we update them on purpose.
- The image licences have not been checked. ADR 0002 records the OpenEMS README statement (via mirrors) that Edge is under EPL-2.0 and the UI under AGPL-3.0. Re-check against the official repository before distributing any image or modified source. This is not legal advice.
- Only the amd64 builds have been run (ADR 0004). The arm64 builds exist in the registry but are untested here until the optional hardware milestone.
- The seed service relies on two internals of the Edge image: its start-up script and the default-config path. A new image can change them, so every pin update repeats the check above.

## Open points

- Resolved for amd64 on 2026-10-16 and 2026-10-17: both images run with the compose settings in `deploy/compose.yaml`. `deploy/smoke-test.sh` passed on the long-running stack, after a container recreate, after a clean reboot and on fresh volumes (see `docs/runbook.md`). arm64 is untested.
- Pins for the Python layer, MQTT broker and database. Chosen in the milestones that add them.
