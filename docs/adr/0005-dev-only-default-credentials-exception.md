# ADR 0005: Documented default logins are allowed in the development stack only

- Status: Accepted for v0.1 development
- Date: 2026-10-16

## Context

The project rule is no default credentials. OpenEMS Edge and its UI ship with documented defaults, and the stack needs a login at least once to create components by hand.

Evidence gathered on 2026-10-16:

- The OpenEMS "Getting Started" guide (retrieved 2026-10-16) says to log in to the Apache Felix web console with username `admin` and password `admin`. For the UI it says to log in as guest by leaving the standard password, or to type `admin` in the password field for extended permissions.
- The UI login page shows a single password field with a default value that logs in as guest. Edge's log records `Authentication successful with password only for user [Guest]`.
- The Apache Felix web console README (retrieved 2026-10-16) lists a `password` property with default `admin` and encourages changing it. It also lists a ticket titled "Unable to change default password in webconsole" (FELIX-6804), which we did not read.
- The OpenEMS source on its develop branch (retrieved 2026-10-16; not necessarily the 2026.9.0 tag) has a user service that keeps users from configuration with a password hash and salt. How to change a password in 2026.9.0 was not verified.
- Without credentials, the console answers HTTP 401. `deploy/smoke-test.sh` asserts this.
- The configuration files in `deploy/edge-seed/` contain no credentials. Their property names were reviewed before they were committed.

## Decision

1. The documented default logins (the guest default, `admin` typed in the UI, and `admin` / `admin` for the Felix console) may be used in the development stack only. That stack is simulation only, published on `127.0.0.1` inside the VM and reached through an SSH tunnel (ADR 0004).
2. No credentials are stored in this repository. `deploy/.env.example` holds none, and the seed files hold none.
3. Day-to-day runs need no login: the seed service creates the simulated chain. A login is needed only to inspect the stack (guest) or to change its configuration by hand.
4. `BIND_ADDRESS` stays `127.0.0.1`. Changing it requires reading this ADR first.
5. This exception does not cover any deployment, pilot or non-simulated use. Authentication is out of scope for v0.1. A later milestone must replace the defaults before any such use.

## Consequences

- Anyone who can reach the VM's loopback ports can use the defaults. The VM accepts SSH password logins (observed). SSH hardening is out of scope for v0.1.
- The project rule is not met for the development stack. This ADR is the recorded exception.
- The smoke test would catch a console that answers without asking for a login.

## Alternatives considered

- **Set a password through a Felix configuration file.** Not chosen: the secret would live in the config volume, and the open Felix ticket above leaves it unclear whether the change takes effect in the bundled version.
- **Change the UI password after the first login.** Not chosen yet: how to do this in 2026.9.0 was not verified.
- **Disable the Felix console.** Not chosen: whether the image allows it is unverified.
- **Create the chain without ever logging in.** Done for normal runs through the seed. Creating the seed files needed the console once.

## Open points

- Find out whether the UI and console passwords can be changed in 2026.9.0, and where a new value would be stored.
- Decide authentication for any later milestone that goes beyond simulation.
