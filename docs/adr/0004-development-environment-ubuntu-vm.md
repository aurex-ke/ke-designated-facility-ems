# ADR 0004: Development environment is an Ubuntu Server VM

- Status: Accepted for v0.1
- Date: 2026-10-15
- Updated: 2026-10-17

## Context

The project context names a laptop running Docker as the development machine. The maintainer's laptop is an Intel-based Mac running macOS 13 (Ventura). Evidence gathered on 2026-10-13 and 2026-10-14:

- Docker's install page for Docker Desktop on Mac states that it supports the current macOS release and the two before it (retrieved 2026-10-13). macOS 13 is older than that window.
- Docker Desktop release notes (seen through a search excerpt, retrieved 2026-10-13) state that macOS 13 support ended with version 4.48.0 (2025-10-09), and Docker's docs state that versions older than six months behind the latest release are not available for download (truncated excerpt, not fully read). An old release would also lack a year of security fixes.
- Third-party compatibility lists (seen 2026-10-13) show this Mac model cannot run macOS Sonoma 14 or later, so upgrading macOS is not an option.
- UTM's installation docs describe it as free and open source. A third-party guide states stable UTM 4.7.5 needs macOS 11.3 or newer and the 5.0 beta needs macOS 13 or newer (not confirmed on UTM's own release page). The maintainer runs UTM 4.7.5 (build 118), read from UTM's About window on 2026-10-17, on macOS 13.7.8.

## Decision

1. Develop inside an Ubuntu Server 26.04.1 LTS (amd64) virtual machine run by UTM on the Mac. Docker lists Ubuntu 26.04 as a supported release for Docker Engine (page updated 2026-08-10).
2. VM settings: 2 virtual CPUs, 6 GB RAM (about 5.3 GB visible to Linux), a 40 GB virtual disk with the root volume extended to about 37 GB. The UTM CPU type is "max" and the kernel command line carries `tsc=reliable` (see Clock and freeze evidence).
3. Install Docker Engine from Docker's apt repository. Installed on 2026-10-14: Docker Engine 29.9.0, containerd.io 2.4.1, docker-buildx-plugin 0.38.0, docker-compose-plugin 5.6.0. These host tools are recorded, not pinned. On 2026-10-17 Docker Engine was updated to 29.9.1 and containerd.io to 2.4.2 (the compose plugin still reports v5.6.0; docker-buildx-plugin was not re-checked).
4. Workflow: edit and commit on the Mac only. The VM clones the public repository and only pulls and runs. The commit identity therefore lives in one place.
5. All published ports bind to `127.0.0.1` inside the VM. Docker-published ports bypass `ufw` and `firewalld`, so the binding is the access control. Browsers on the Mac reach the VM through an SSH tunnel.
6. Stop the VM with `sudo poweroff` and wait until UTM shows it stopped. After an abrupt stop on 2026-10-16, reads of a container's log returned nothing until the containers were recreated (`docs/runbook.md`, section 9; the cause is unproven).
7. Take a UTM clone, with the VM stopped, before applying OS package updates. One was taken on 2026-10-17.

## Consequences

- Only linux/amd64 images are exercised. The registry also offers arm64 builds (ADR 0003), which stay untested until the optional hardware milestone.
- The VM adds a layer between the Mac and the stack. SSH tunnels are needed to open the OpenEMS UI from a Mac browser.
- A contributor on Linux, or on a Mac that Docker Desktop supports, needs none of this. `deploy/compose.yaml` does not depend on the VM.
- Disk, CPU and RAM are limited by the VM size above. Revisit if the database or the Python layer outgrow it.
- The Jetson is not used as the development host. It is reserved for the optional hardware-validation milestone, where an independent arm64 test is the point.
- OS packages: 28 were updated on 2026-10-17 (Docker Engine, containerd.io, `rust-coreutils` 0.8.0 to 0.10.0 and others) with no kernel change and no reboot requirement. A clean reboot afterwards kept the kernel options, and the stack came back by itself. `open-vm-tools` and `snapd` were deferred by Ubuntu's phased updates and are still pending.

## Clock and freeze evidence

The VM froze twice on 2026-10-15, with the UTM default CPU type and no kernel options: once about one second after the first `docker compose up`, and once during a 30-minute idle test. The cause was never proven. A third-party essay (dwheeler.com, 2025-10-15, retrieved 2026-10-15; the author says it was found with AI help) blames the CPU type's TSC clock calibration and recommends CPU type "max" plus `tsc=reliable`. Both were applied on 2026-10-15.

Kernel log of every recorded boot (UTC, `journalctl -k`):

| Boot | TSC calibration | Clock source in use |
|---|---|---|
| 2026-10-15 18:04 (before the changes) | failed | `acpi_pm` |
| 2026-10-15 19:44 (before the changes) | succeeded, 3503 MHz | `tsc`, then `acpi_pm` after 36 minutes (watchdog skew) |
| 2026-10-15 21:04 | failed | `acpi_pm` |
| 2026-10-15 21:41 | failed | `acpi_pm` |
| 2026-10-15 22:02 | succeeded, 3503.767 MHz | `tsc` (the boot lasted about 18 minutes) |
| 2026-10-15 22:26 | failed | `acpi_pm` (about 19 hours) |
| 2026-10-17 08:32 | failed | `acpi_pm` (about 6 hours) |
| 2026-10-17 14:31 | failed | `acpi_pm` (about 5 hours) |
| 2026-10-17 19:34 | succeeded, 3503.241 MHz | `tsc`, still in use after 49 minutes |

- Calibration failed on 6 of the 9 boots. The two changes did not make it reliable.
- On the two boots that calibrated after the changes, `tsc` stayed in use: about 18 minutes, and at least 49 minutes, which is past the 36 minutes at which the watchdog demoted it on 2026-10-15. Two observations only.
- No freeze has been observed since the changes. About 30 hours of heartbeat logs (a timestamp and the clock source every 5 seconds) across four boots show no pause longer than 10 seconds. The 21:04 and 21:41 boots on 2026-10-15 had no logger and were watched by hand.
- Whether the changes fixed the freezes cannot be separated from luck on this evidence: the original freeze was not reproduced before the changes, and its cause was never proven.

## Alternatives considered

- **Docker Desktop on macOS 13.** Unsupported by current releases (above). Not chosen.
- **VirtualBox.** Sources conflict on whether current releases support Intel Mac hosts. Not chosen, and not resolved.
- **Cloud development environment.** Needs reliable internet and departs from the laptop assumption. Not evaluated in depth.
- **Jetson Nano as the development host.** Its software stack is frozen on JetPack 4 (Ubuntu 18.04, Linux 4.9), compatibility with current OpenEMS images is unverified, and it has 4 GB of RAM. Not chosen.
- **Installing Linux over macOS.** Invasive and unnecessary. Not chosen.

## Open points

- Whether a firewall is needed inside the VM. None is configured. If one is added, it must use `iptables` rules that Docker supports (see Docker's firewall notes).
- `open-vm-tools` and `snapd` updates were deferred by phased rollout on 2026-10-17. Apply them when offered and re-run `deploy/smoke-test.sh` afterwards.
- The cause of the 2026-10-15 freezes is unproven. Keep the heartbeat logger running in long sessions (`docs/runbook.md`, section 8).
