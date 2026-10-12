# ke-designated-facility-ems

**Simulation only. Nothing is deployed. There are no pilots, partners or users.**

An open-source, simulation-first reference implementation of an energy management system (EMS) for Kenyan designated facilities. A designated facility is a commercial, industrial or institutional site above the energy-use threshold set in Kenyan regulation (see [docs/problem-statement.md](docs/problem-statement.md)).

**Current status: v0.1 in development. Milestone M1 (documentation) only. No code exists yet.**

## v0.1 scenario

A simulated 60-room hotel, ID `hotel-60rooms-sim-v1`. The hotel size, load profile and tariff values are **assumptions**, to be calibrated against real bills. Whether this hotel would exceed the designated-facility threshold is also an assumption.

## Approach

- [OpenEMS](https://github.com/openems/openems) Edge for PV and storage control, run with its simulated development environment.
- A separate Python layer for ingestion, sub-metering (HVAC, kitchen, laundry, hot water, lighting), a tariff model and compliance reporting.
- OpenEMS's built-in UI for now.
- Docker Compose, an MQTT broker, a database and Python. All settings live in config files.

See [docs/adr/0002-openems-edge-plus-python-layer.md](docs/adr/0002-openems-edge-plus-python-layer.md).

## Out of scope for v0.1

Utility API integration, authentication, multi-site support, real hardware, billing, M-Pesa, and a custom dashboard.

## Milestones

| ID | Milestone | Status |
|---|---|---|
| M1 | Repo, README, problem statement, architecture decision records | In progress |
| M2 | OpenEMS Edge with simulators in Docker Compose | Planned |
| M3 | Hotel load generator and sub-meter data | Planned |
| M4 | Ingestion and storage | Planned |
| M5 | Tariff model and one peak-shifting scenario | Planned |
| M6 | Compliance report | Planned |
| M7 | Write-up of results | Planned |
| M8 | Optional Jetson Nano hardware validation (never required) | Planned |

## Reproducibility rules

Semantic versioning, pinned dependency and image versions, seeded random generators, and every number citing its source and retrieval date.

## Not legal advice

This project summarises public regulations for engineering purposes. It is not legal advice. Check the current regulation text before relying on anything here.

## Licence and credits

MIT for this repository's own code and text (see [LICENSE](LICENSE)). OpenEMS is credited under its own licences in [NOTICE.md](NOTICE.md). This project is not affiliated with or endorsed by OpenEMS.

## Contact

Open a GitHub Issue on this repository.
