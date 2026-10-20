# Configuration

`hotel-60rooms-sim-v1.toml` holds every setting of the synthetic load
generator. Nothing is hardcoded in Python. The hotel is simulated; no value
here describes a real property.

## Provenance rule

Each parameter is a TOML table with a `value` and exactly one of these keys:

| Key | Meaning | Extra rules |
|---|---|---|
| `source` | The value comes from a cited source (title, publisher, URL). | Needs `retrieved = YYYY-MM-DD`. |
| `assumption` | The project's own estimate. | Optional `min` and `max` give the plausible range; the value must lie inside it. |
| `definition` | A project choice that defines the simulated hotel or the run, such as the random seed. | Not a measurement. |

`unit` is optional free text. Any other key is rejected.

The loader (`src/ke_ems/loadgen/config.py`) refuses a file that breaks these
rules, so an unsourced number cannot enter a run. A source that has not been
read in full is not cited as a source: use `assumption` until it has been.

## Changing a value

A changed value is a different dataset. Output metadata records the SHA-256 of
the configuration file, so a change is visible in the results.
