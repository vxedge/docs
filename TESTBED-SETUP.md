# TESTBED-SETUP.md — running the whole testbed on one local machine

Target: the full vxedge testbed — control plane, vxgateway, virtual ECUs, AD workloads —
running flawlessly on a single machine. Requirements are tiered by phase so you only
install what the work in front of you needs. `vxedge doctor --tier N` (delivered
2026-07-13) verifies tiers 0–3 automatically with actionable fix hints; `--json` for CI.

## Tier 0 — control-plane development (works today)

| Requirement | Version / value | Check |
|---|---|---|
| OS | Ubuntu 24.04 LTS or newer (any modern systemd Linux works) | `lsb_release -a` |
| Kernel | ≥ 6.8 (dev host: 7.0.0-28-generic, upgraded from 6.17.0-35 — see `STATUS.md` Environment) | `uname -r` |
| CPU / RAM / disk | 4 cores, 8 GB, 20 GB free | — |
| Rust | 1.96.1 (pinned by `rust-toolchain.toml`; rustup auto-installs) | `rustc --version` |
| protoc | ≥ 3.21 (35.x current) | `protoc --version` |
| buf (optional) | ≥ 1.71 | `buf --version` |
| iproute2 | ≥ 6.1 (`ip`, `bridge`, `tc`) | `ip -V` |

## Tier 1 — H1 experiments: gateway + probes (phase 1)

Everything in Tier 0, plus:

| Requirement | Notes |
|---|---|
| CAP_NET_ADMIN | **Two mechanisms now, not one** — corrected 2026-08-05 after a live `exp-010` `--repro` run failed against the 2026-07-17 guidance below. The 2026-08-04 rtnetlink port (`docs/TASKS.md` #16) moved bridge/veth/VLAN/address/route creation, WireGuard device creation, and the fiveg host-attachment path off the `ip`/`bridge` shell-out and into `vxedged`'s own in-process syscalls — for exactly that portion, `sudo setcap cap_net_admin+ep <path-to-vxedged>` now **does** work (no child process involved, so the fork+exec propagation problem below doesn't apply), and needs re-running after every rebuild since a fresh binary carries no capability. `tc`, `nft`, `wg` (key/peer config), and `ovs-vsctl` are **still** shell-outs, unchanged, and still need the NOPASSWD-sudo config below (e.g. `<user> ALL=(root) NOPASSWD: /usr/sbin/ip, /usr/sbin/bridge, /usr/sbin/tc, /usr/sbin/nft, /usr/bin/wg, /usr/bin/ovs-vsctl`) — a cached interactive sudo credential (`sudo -v`, kept alive) works just as well as NOPASSWD for these, and is what every current campaign runner actually uses. Do not run `vxedged` itself as root either way — phase 2's fiveg driver needs `podman` to keep running as the deploying user's own identity (see Tier 2). *Original 2026-07-17 finding, still true for the shell-out half*: capabilities don't propagate across `fork`+`exec` to separate child processes, which is why `setcap` alone was insufficient before the rtnetlink port and still doesn't cover `tc`/`nft`/`wg`/`ovs-vsctl` today |
| iproute2 + nftables | already present on the dev host |
| CPU isolation (recommended) | pin gateway + probe cores: `isolcpus`/`cpuset` — record in results metadata |
| Kernel flavour caveat | generic (non-PREEMPT_RT) is fine for first numbers; **must** be recorded as a determinism caveat (§12). PREEMPT_RT (Ubuntu Pro real-time kernel) is the upgrade path |

No OVS and no WireGuard needed for H1 — the gateway uses the kernel bridge.

## Tier 2 — real workloads: zones, 5G, CARLA (phase 2)

Everything above, plus:

| Requirement | Version / value | Notes |
|---|---|---|
| CPU / RAM / disk | 12+ cores, 64 GB, 250 GB free (NVMe) | CARLA + Autoware + zones concurrently |
| KVM + QEMU | qemu-system-x86 ≥ 8.x | `kvm-ok`; user in `kvm`/`libvirt` groups. `qemu-microvm` zone/vehicle nodes need **no sudo entry** — confirmed live 2026-08-06: `vxedged` launches `qemu-system-x86_64` unescalated (kvm-group access to `/dev/kvm` plus `TUNSETOWNER` on the tap it attaches to, set at tap-creation time, is everything it needs). Do not add a NOPASSWD sudoers entry for `qemu-system-x86_64` — it buys nothing this backend needs and grants root code execution the daemon doesn't require |
| libvirt | ≥ 10.x | `virsh version`; daemon enabled |
| Open vSwitch (optional variant) | `apt install openvswitch-switch` | alternative gateway data plane; **do not** hand-create bridges — vxedge owns its bridge lifecycle |
| WireGuard tools | `apt install wireguard-tools` | telemetry/OTA transport links |
| NVIDIA GPU | RTX-class, ≥ 12 GB VRAM; driver ≥ 550; CUDA per DeepStream/TensorRT matrix | CARLA server + inference share it |
| Container runtime | **Podman** (preferred; Docker-compatible OCI) + NVIDIA Container Toolkit | digest-pinned images only; hybrid policy: ARCHITECTURE §15 |
| Open5GS + UERANSIM | **containerized: `vx5g-core` / `vx5g-ran` images** (`vxedge/containers/fiveg/`) | S-NSSAI slicing (H2). Host needs only `modprobe sctp`. Host PPA install is legacy — disable its services (`systemctl disable --now 'open5gs-*'`), purge once the pod path is proven. Extend the Tier 1 sudoers entry to also cover `nsenter` (fiveg's CN/RAN transit link + bridge attachment join a pod's netns by PID) — same NOPASSWD-for-the-deploying-user model, no wider than that |

## Tier 3 — full vehicle + HMI (phase 3)

Adds: Kuksa databroker container, CARLA assets (~20 GB), AAOS emulator images, Qt ≥ 6.8
(QML HMI), Node 20+ (web dashboard build). RAM comfortably 96 GB for the six-zone
vehicle manifest with AAOS + QNX guests concurrently.

## Tier M — modeling workstation (optional, any phase; track M)

Authoring-time only — none of this runs during a measured experiment, so it has **zero
effect on results** and no host-resource requirements beyond an editor.

| Requirement | Version / value | Notes |
|---|---|---|
| SysIDE (parse/type gate) | **0.9.1** (`syside-languageserver.zip`, sha256 `1c3da428…`) | headless via `vxmodels/scripts/validate-sysml.mjs` (LSP driver; SysIDE has no one-shot CLI); VS Code extension of the same version for authoring |
| SysML v2 standard library | **SysML-v2-Release 2026-04** `sysml.library` (tarball sha256 `44996ee2…`) | required for stdlib imports (`ScalarValues::*` …) to resolve |
| Node | ≥ 20 (dev host: 22) | runs the language server + driver |
| OMG pilot implementation (optional) | 2026-05 (Jupyter kernel) | semantic reference / visualization; not in the CI gate |
| `vxmodel` renderer | Rust (Tier 0 toolchain) | builds with the same toolchain once the crate lands (M2) |
| Validation loop | — | model gate above, then `vxmodel render` output must pass `vxedge manifest validate --json` (Tier 0 binaries) |

## Rules

- Versions above are the **verified** set; bumps go through this file in the same PR.
- One machine is the design target through phase 3; multi-host (`vxedged --controller`,
  VXLAN inter-host) is optional scale-out, not a requirement.
- Anything the testbed needs that this file doesn't list is a bug in this file.
