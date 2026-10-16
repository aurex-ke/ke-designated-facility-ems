# Edge seed configuration (simulated chain)

Felix Configuration Admin files for a minimal **simulated** OpenEMS Edge chain.
They were captured verbatim on 16 Oct 2026 from a development stack in which the
five components below were created in the Felix web console, following the
OpenEMS "Getting Started" guide (https://openems.github.io/openems.io/openems/latest/gettingstarted.html,
retrieved 16 Oct 2026). Default values were accepted except the datasource
`source` and the ID references between components.

| ID | Factory PID | Role |
|---|---|---|
| `ctrlDebugLog0` | `Controller.Debug.Log` | Writes a one-line summary to the log each cycle |
| `datasource0` | `Simulator.Datasource.CSV.Predefined` | Load profile `H0_HOUSEHOLD_SUMMER_WEEKDAY_STANDARD_LOAD_PROFILE` |
| `meter0` | `Simulator.GridMeter.Acting` | Simulated grid meter fed by `datasource0` |
| `ess0` | `Simulator.EssSymmetric.Reacting` | Simulated battery (capacity 10000, initial state of charge 50, as stored in the file) |
| `ctrlBalancing0` | `Controller.Symmetric.Balancing` | Controls `ess0` to balance the grid power at `meter0` |

## Status

**Stack validation only.** The load profile is a household standard load profile,
not a hotel profile. Nothing here says anything about hotel energy use. The
hotel scenario (`hotel-60rooms-sim-v1`) arrives in milestone 3.

## How it is used

The `openems-edge-seed` service in `deploy/compose.yaml` prepares a fresh Edge
config volume in two steps:

1. If the volume is empty, it installs the image's own default configuration
   (shipped in the image at `/var/lib/openems-default-config`). Edge's start-up
   script only installs those defaults into an empty directory, so they would be
   skipped once our files are in place. Without them Edge has no scheduler and no
   websocket controller, and the simulated chain never runs.
2. It copies the files in `config/` into the volume.

If `Simulator/` already exists in the volume, it does nothing and never overwrites
anything. To start again from the seed, remove the stack's volumes:
`docker compose down -v` deletes the Edge configuration and data, so use it with
care.

This relies on internals of `openems/edge:2026.9.0`, read from its init script on
16 Oct 2026. Re-check them whenever the image is updated.

Validation of this mechanism is part of milestone 2 and is not complete until the
smoke test passes on a fresh volume.

## Do not edit by hand

- Files use **CRLF** line endings. `.gitattributes` stops git converting them.
- Some values are stored in an encoded form (for example `factor`).
- Each file name is a UUID that must match the `service.pid` inside it.

To change a setting: change it in a development stack, capture the file,
review it for secrets, then commit it.

## Credits

OpenEMS is a project of the OpenEMS Association e.V. This repository is not
affiliated with it. See `NOTICE.md` in the repository root.
