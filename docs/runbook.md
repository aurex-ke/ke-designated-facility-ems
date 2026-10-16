# Runbook: simulated OpenEMS Edge stack (milestone 2)

Development stack, simulation only. Nothing is deployed anywhere. OpenEMS is run
unmodified from its upstream images. This project is not affiliated with OpenEMS.

Tested on 16 Oct 2026 only on this setup: Ubuntu Server 26.04.1 LTS (amd64) in a
UTM virtual machine on an Intel Mac, Docker Engine 29.9.0, Compose plugin 5.6.0.

## 1. First start

```bash
cd deploy
cp .env.example .env     # first time only; this file holds no secrets
sudo docker compose config > /dev/null && echo CONFIG_OK
sudo docker compose up -d
sudo bash smoke-test.sh
```

- `up -d` creates the volumes on first use. A one-shot seed service then installs
  the image's default Edge config and adds the simulated chain
  (`deploy/edge-seed/`). Edge needs about 30 seconds. The smoke test waits up to
  90 seconds for the Debug Log.
- After an update, if `.env.example` gained variables, add them to your `.env`.
  Compose stops with a clear error when one is missing.

## 2. Everyday commands

```bash
sudo docker compose ps -a
sudo docker compose logs --since 5m openems-edge | grep -E 'Activate| ERROR | WARN '
sudo docker compose stop      # stops containers, keeps everything
sudo docker compose down      # removes containers and network, keeps the volumes
sudo docker compose down -v   # ALSO DELETES the Edge config and data volumes
```

Do not combine `--tail` with `grep` on the Edge log: the Debug Log writes a line
every second and pushes everything else out of a short tail.

## 3. Open the UI and the console (development only)

The ports are bound to 127.0.0.1 inside the VM. From your computer, use an SSH tunnel
(replace the placeholders; never put real addresses in this repository):

```bash
ssh -N -L 127.0.0.1:8081:127.0.0.1:8081 -L 127.0.0.1:8080:127.0.0.1:8080 USER@VM_ADDRESS
```

Ctrl-C closes the tunnel. Close it when you are done.

- UI: `http://127.0.0.1:8081`. Leave the prefilled password to log in as guest.
- Felix console: `http://127.0.0.1:8080/system/console/configMgr`.
- Typing `admin` in the UI password field gives extended permissions, and the
  console login is `admin` / `admin`. Both are the defaults documented in the
  OpenEMS "Getting Started" guide (retrieved 16 Oct 2026).

Using those documented defaults is a **development-only exception**, accepted on
16 Oct 2026 for a loopback-only stack reached through an SSH tunnel. Never expose
these ports and never ship this setup with default logins.

## 4. Start again from the seed, or test a second copy

Reset the real stack (destructive: deletes Edge configuration and history):

```bash
sudo docker compose down -v
sudo docker compose up -d
```

Test a fresh volume without touching the real stack, using a second Compose project
and different host ports:

```bash
sudo env EDGE_FELIX_PORT=18080 UI_HTTP_PORT=18081 COMPOSE_PROJECT_NAME=ke-ems-seedtest docker compose up -d
sudo env EDGE_FELIX_PORT=18080 UI_HTTP_PORT=18081 COMPOSE_PROJECT_NAME=ke-ems-seedtest bash smoke-test.sh
sudo env COMPOSE_PROJECT_NAME=ke-ems-seedtest docker compose down -v   # deletes only the test project
```

Before `down -v`, check `COMPOSE_PROJECT_NAME` really says `ke-ems-seedtest`.

## 5. What to expect

- **The simulated chain is a household example**, not a hotel: it uses a household
  standard load profile. The hotel scenario arrives in milestone 3.
- **The battery drains.** It starts at 50 % and the chain has no PV, so it can only
  discharge. It reached about 0 % within roughly 4 to 5 hours in two observations
  on 16 Oct 2026. After that the grid carries all consumption. A restart sets it
  back to 50 %. The smoke test therefore never asserts values.
- Edge history survives a restart because the data volume is kept.
- Observed on 16 Oct 2026: Edge used about 260 to 420 MiB (cap 2 GiB), and the data
  volume was about 96 MB.

## 6. Known log messages

| Message | What we know |
|---|---|
| `ERROR Worker error. NoSuchElementException: No value present` | Seen twice at each healthy start. If it repeats every ~10 s, Edge is missing its default config (the failure of 16 Oct before the seed fix). |
| `WARN There are no Schedulers configured!` | One or two at start; the OpenEMS guide calls it normal at first start. Repeating every second means the scheduler config is missing. |
| `WARN Environment variable "NOTIFY_SOCKET" not set` | No systemd in the container. Harmless. |
| `WARN Unable to find ObjectClassDefinition ...` | Upstream wording for several core components at start. No effect observed. |
| `ERROR Authentication failed` for `authenticateWithToken` | Seen twice at the first browser load, before the guest login. Probably the UI trying a stored token (inference). |
| `ERROR Unable to read historic data: None of the requested Channels is available` | Seen once, before any simulated component existed. Not seen since. |
| `_appManager[...] State:INFO: Defekte App erkannt` with `App.Core.Meta[Missing configuration for instance ...]` | Seen on 300 consecutive Debug Log lines (about 5 minutes at one line per second, my arithmetic) on a fresh volume on 16 Oct 2026. Not seen on the long-running stack. The Core config files were identical in both. Cause unknown. The simulated chain kept running and the sum state showed Info meanwhile. The smoke test prints the sum state and the count of these lines for information. Open question: does it always clear, and when? |

## 7. Updating the OpenEMS images

1. Follow the pinning procedure in `docs/adr/0003-pin-openems-images-by-digest.md`.
2. The seed service depends on two details of the Edge image: its start-up script
   `/etc/s6-overlay/s6-rc.d/init-openems-config/run` installs the default config only
   into an empty directory, and the defaults live in `/var/lib/openems-default-config`.
   Read both again in the new image:

   ```bash
   sudo docker run --rm --entrypoint /bin/sh IMAGE -c 'cat /etc/s6-overlay/s6-rc.d/init-openems-config/run; ls -R /var/lib/openems-default-config'
   ```
3. Run the fresh-volume test from section 4 and the smoke test before committing.

## 8. Development VM notes

- The VM uses UTM CPU type "max" and the kernel option `tsc=reliable`. On some boots
  the kernel cannot calibrate the TSC clock and falls back to `acpi_pm`. The freezes
  first seen on 15 Oct 2026 did not recur on 16 Oct. Evidence and settings go in
  ADR 0004.
- Optional heartbeat logger, to detect a frozen VM afterwards:

  ```bash
  nohup sh -c 'while true; do echo "$(date -u +%s) $(cat /sys/devices/system/clocksource/clocksource0/current_clocksource)" >> "$HOME/heartbeat.log"; sleep 5; done' >/dev/null 2>&1 &
  awk 'NR>1 && $1-p>10 {print "gap of", $1-p, "s before line", NR} {p=$1}' "$HOME/heartbeat.log"
  ```

  The second command prints every pause longer than 10 seconds.
