# ke-designated-facility-ems

**Simulation only. Nothing is deployed. There are no pilots, partners or users.**

An open-source, simulation-first reference implementation of an energy management system (EMS) for Kenyan designated facilities. A designated facility is a commercial, industrial or institutional site above the energy-use threshold set in Kenyan regulation (see [docs/problem-statement.md](docs/problem-statement.md)).

**Current status: v0.1 in development. Milestones M1 (documentation) and M2 (OpenEMS Edge and its UI in Docker Compose, with a simulated household example) are complete. M3 (hotel load generator) is in progress: a configuration loader and a generator of flat test data exist, but there is no hotel load profile yet.**

## v0.1 scenario

A simulated 60-room hotel, ID `hotel-60rooms-sim-v1`. The hotel size, load profile and tariff values are **assumptions**, to be calibrated against real bills. Whether this hotel would exceed the designated-facility threshold is also an assumption.

## Approach

- [OpenEMS](https://github.com/openems/openems) Edge for PV and storage control, run with its simulated development environment.
- A separate Python layer for ingestion, sub-metering (HVAC, kitchen, laundry, hot water, lighting), a tariff model and compliance reporting.
- OpenEMS's built-in UI for now.
- Docker Compose, an MQTT broker, a database and Python. All settings live in config files.

See [docs/adr/0002-openems-edge-plus-python-layer.md](docs/adr/0002-openems-edge-plus-python-layer.md).

## Try the simulated stack

`deploy/` runs OpenEMS Edge and its built-in UI in Docker Compose with a small simulated example: a household load profile, a battery and a balancing controller. It is not the hotel. It was tested on one setup only, Ubuntu Server 26.04 (amd64) in a UTM virtual machine. See [docs/runbook.md](docs/runbook.md) for the commands, the smoke test and the known log messages.

## Try the load generator (M3, in progress)

`src/ke_ems/loadgen/` is the start of the Python layer. So far it holds a configuration loader, a timestamp grid, a deterministic CSV writer and one command that writes a **flat test fixture**. The fixture is constant test data. It is not hotel data and not a measurement. No hotel load profile exists yet.

```bash
# run the tests (standard library only, no install step)
PYTHONPATH=src python3 -m unittest discover -s tests -t . -v

# write the fixture (15-minute rows for 365 days) into data/loadgen/, which git ignores
PYTHONPATH=src python3 -m ke_ems.loadgen fixture config/hotel-60rooms-sim-v1.toml
```

Every parameter in `config/hotel-60rooms-sim-v1.toml` must state its source (with a retrieval date), an assumption or a definition; the loader refuses anything else. Running the command twice gives byte-identical files, and the metadata file records the SHA-256 of the config and of the output. Python 3.11 or later is required (standard-library TOML parser); only Python 3.14 has been tested. What a row's kW value means (an average over the interval or an instantaneous reading) is not decided yet. It will be settled when the feed into OpenEMS is tested.

## Out of scope for v0.1

Utility API integration, authentication, multi-site support, real hardware, billing, M-Pesa, and a custom dashboard.

## Milestones

| ID | Milestone | Status |
|---|---|---|
| M1 | Repo, README, problem statement, architecture decision records | Complete |
| M2 | OpenEMS Edge with simulators in Docker Compose | Complete |
| M3 | Hotel load generator and sub-meter data | In progress |
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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for what helps right now and the evidence rules. Participation is covered by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Contact

Open a GitHub Issue on this repository. For security vulnerabilities, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.
