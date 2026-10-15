# ADR 0004: Development environment is an Ubuntu Server VM

- Status: Accepted for v0.1
- Date: 2026-10-15

## Context

The project context names a laptop running Docker as the development machine. The maintainer's laptop is an Intel-based Mac running macOS 13 (Ventura). Evidence gathered on 2026-10-13 and 2026-10-14:

- Docker's install page for Docker Desktop on Mac states that it supports the current macOS release and the two before it (retrieved 2026-10-13). macOS 13 is older than that window.
- Docker Desktop release notes (seen through a search excerpt, retrieved 2026-10-13) state that macOS 13 support ended with version 4.48.0 (2025-10-09), and Docker's docs state that versions older than six months behind the latest release are not available for download (truncated excerpt, not fully read). An old release would also lack a year of security fixes.
- Third-party compatibility lists (seen 2026-10-13) show this Mac model cannot run macOS Sonoma 14 or later, so upgrading macOS is not an option.
- UTM's installation docs describe it as free and open source. A third-party guide states stable UTM 4.7.5 needs macOS 11.3 or newer and the 5.0 beta needs macOS 13 or newer (not confirmed on UTM's own release page).

## Decision

1. Develop inside an Ubuntu Server 26.04.1 LTS (amd64) virtual machine run by UTM on the Mac. Docker lists Ubuntu 26.04 as a supported release for Docker Engine (page updated 2026-08-10).
2. VM settings: 2 virtual CPUs, 6 GB RAM (about 5.3 GB visible to Linux), a 40 GB virtual disk with the root volume extended to about 37 GB.
3. Install Docker Engine from Docker's apt repository. Installed on 2026-10-14: Docker Engine 29.9.0, containerd.io 2.4.1, docker-buildx-plugin 0.38.0, docker-compose-plugin 5.6.0. These host tools are recorded, not pinned.
4. Workflow: edit and commit on the Mac only. The VM clones the public repository and only pulls and runs. The commit identity therefore lives in one place.
5. All published ports bind to `127.0.0.1` inside the VM. Docker-published ports bypass `ufw` and `firewalld`, so the binding is the access control. Browsers on the Mac reach the VM through an SSH tunnel.

## Consequences

- Only linux/amd64 images are exercised. The registry also offers arm64 builds (ADR 0003), which stay untested until the optional hardware milestone.
- The VM adds a layer between the Mac and the stack. SSH tunnels are needed to open the OpenEMS UI from a Mac browser.
- A contributor on Linux, or on a Mac that Docker Desktop supports, needs none of this. `deploy/compose.yaml` does not depend on the VM.
- Disk, CPU and RAM are limited by the VM size above. Revisit if the database or the Python layer outgrow it.
- The Jetson is not used as the development host. It is reserved for the optional hardware-validation milestone, where an independent arm64 test is the point.

## Alternatives considered

- **Docker Desktop on macOS 13.** Unsupported by current releases (above). Not chosen.
- **VirtualBox.** Sources conflict on whether current releases support Intel Mac hosts. Not chosen, and not resolved.
- **Cloud development environment.** Needs reliable internet and departs from the laptop assumption. Not evaluated in depth.
- **Jetson Nano as the development host.** Its software stack is frozen on JetPack 4 (Ubuntu 18.04, Linux 4.9), compatibility with current OpenEMS images is unverified, and it has 4 GB of RAM. Not chosen.
- **Installing Linux over macOS.** Invasive and unnecessary. Not chosen.

## Open points

- Whether a firewall is needed inside the VM. None is configured. If one is added, it must use `iptables` rules that Docker supports (see Docker's firewall notes).
- Pending OS package updates in the VM. Apply before M2 is closed.
