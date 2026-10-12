# ADR 0002: OpenEMS Edge plus a separate Python layer

- Status: Accepted for v0.1 (revisit after M2)
- Date: 2026-10-13

## Context

The simulated hotel needs PV and storage control and a path to ingestion, sub-metering, a tariff model and compliance reporting.

OpenEMS describes Edge as the component that runs on site, communicates with devices and services, collects data and executes control algorithms. Its README says OpenEMS is generally used with external hardware, with the exception of a simulated development environment described in its Getting Started guide. (Source: OpenEMS README as seen via third-party mirrors, retrieved 2026-10-13. The official repository was not read directly.)

## Decision

1. Use OpenEMS Edge for PV and storage control, run with its simulators.
2. Build a separate Python layer for ingestion, sub-metering (HVAC, kitchen, laundry, hot water, lighting), the tariff model and compliance reporting.
3. Use OpenEMS's built-in UI for now. No custom dashboard.
4. Run everything with Docker Compose, with an MQTT broker and a database. All settings live in config files.

## Consequences

- **Licences.** The OpenEMS README states that Edge and Backend are under the Eclipse Public License 2.0 and the UI is under the GNU Affero General Public License 3.0 (retrieved 2026-10-13 via mirrors). Because v0.1 uses the built-in UI, the AGPL applies to that component. Plan: run OpenEMS unmodified from upstream, do not copy its code into this repository, and re-check obligations before distributing any container image or modified source. This is not legal advice.
- **Separation.** Control stays in OpenEMS. Analysis and compliance stay in Python. This keeps our MIT code separate from OpenEMS code.
- **No affiliation.** OpenEMS is credited in NOTICE.md. No endorsement is implied.

## Open points (not decided here)

- Which OpenEMS simulator components, drivers and controllers are available for PV and storage. No component names are asserted. M2 will read the official documentation first.
- How the Python layer exchanges data with OpenEMS (the stack includes an MQTT broker). To be settled in a later ADR after M2.
- Pinned versions of OpenEMS and all images. Chosen in M2.
- Java and container requirements for running Edge. Verify at M2.

## Alternatives not evaluated

Other EMS platforms and a Python-only simulation were not evaluated for this ADR. If evaluated later, record the result in a new ADR.
