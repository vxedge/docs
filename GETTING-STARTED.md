# Getting started

vxedge is an all-software research platform for mapping 5G network slices onto zonal &
central SDV (software-defined vehicle) E/E architectures: a virtual edge gateway
(`vxgateway`), QEMU/KVM virtual ECUs, containerized AD compute, and a Rust control plane
(`vxedged`) driven entirely by YAML manifests. Read
[`ARCHITECTURE.md`](ARCHITECTURE.md) for the full picture; this page gets you from
zero to a measured experiment; day-to-day usage lives in [USER-GUIDE.md](USER-GUIDE.md), and
every acronym is defined in [`ACRONYMS.md`](ACRONYMS.md).

**Pre-release (0.x).** The manifest schema and vxAPI may change between minor versions
([`VERSIONING.md`](VERSIONING.md)); published results are frozen and do not change.

**Repository status.** All nine repositories (`docs`, `vxedge`, `vxagents`, `vxtelemetry`, `vxota`, `vxperiments`,
`vxparts`, `vxmodels` and `vxmcp`) are public. The zone bundle step in section 4 builds from the `vxparts` clone, so it
runs as written.

## 1. Prerequisites

Verified versions as of 2026-10:

| Tool | Version | Install |
|---|---|---|
| Rust | 1.96+ (pinned by `rust-toolchain.toml`; with rustup installed, the first `cargo` command in the repo fetches the right toolchain automatically) | `curl https://sh.rustup.rs -sSf \| sh` |
| protoc | any recent (36.x current upstream, as of 2026-10) | distro package, or the [release zip](https://github.com/protocolbuffers/protobuf/releases) → `~/.local/bin` |
| buf | 1.71+ (optional: proto lint/SDK gen) | [release binary](https://github.com/bufbuild/buf/releases) → `~/.local/bin` |
| git + gh | any recent | distro package |

Later phases additionally need QEMU/KVM + libvirt, Open vSwitch, and an NVIDIA GPU
(CARLA/Autoware/Alpamayo workloads); none of that is required to build and run the
control plane today.

## 2. Workspace layout

vxedge is a **meta-workspace of independent git repos**, cloned side by side (the parent
folder is *not* a git repo):

```bash
mkdir vxedge && cd vxedge
for r in docs vxedge vxagents vxtelemetry vxota vxperiments vxparts vxmodels vxmcp; do
  gh repo clone vxedge/$r
done
```

| Repo | What |
|---|---|
| `docs` | Architecture specification (`ARCHITECTURE.md`), user documentation, results, roadmap and the facts registry (`FACTS.md`) |
| `vxedge` | **Start here**: control plane (`vxedged`), vxAPI (gRPC/Protobuf), CLI |
| `vxparts` | Unified loadable registry of zone (virtual-ECU) and central-compute images, published via OCI/ORAS |
| `vxota` / `vxtelemetry` | OTA and telemetry service code |
| `vxagents` | Rust measurement agents (latency probes, traffic gen, pcap) |
| `vxperiments` | Experiment + vehicle manifests, notebooks, results |
| `vxmodels` | SysML v2 system models + `vxmodel` manifest renderer, track M (`ARCHITECTURE.md` §6.3) |
| `vxmcp` | MCP (Model Context Protocol) server over vxAPI, for agent tooling |

Every repo has an `AGENTS.md` (scope + rules) and `TASKS.md` (phased work items);
`docs/ROADMAP.md` is the program-level board with the cross-repo critical path.

## 3. Get the binaries

**Prebuilt (CLI and daemon, Linux x86-64 and ARM64):** download the latest `vxedge` release, check it, and run it.
Each release carries `SHA256SUMS` and build provenance.

```bash
gh release download -R vxedge/vxedge --pattern '*x86_64*' --pattern SHA256SUMS      # aarch64 on ARM
sha256sum --ignore-missing -c SHA256SUMS                                             # must say OK
gh attestation verify vxedge-*-x86_64-unknown-linux-gnu.tar.gz -R vxedge/vxedge     # needs gh 2.49 or newer
tar xzf vxedge-*-x86_64-unknown-linux-gnu.tar.gz                                     # vxedge, vxedged, LICENSE, NOTICE
```

The binaries are built on Ubuntu 24.04 (glibc 2.39), so they run on 24.04 and newer. The experiment runner
below uses the binaries built from source in the next step, because it also needs `vxagents` and `vxtelemetry`.

### Or build everything from source

```bash
for r in vxedge vxagents vxtelemetry; do (cd $r && cargo build --workspace); done
```

Quick unprivileged smoke (daemon + CLI over a Unix socket):

```bash
cd vxedge
./target/debug/vxedged --listen unix:///tmp/vxedge.sock --runtime-dir /tmp/vxrt &
./target/debug/vxedge --endpoint unix:///tmp/vxedge.sock status
# gateway vxgateway: state=1 detail=no gateway provisioned
./target/debug/vxedge --help          # full command tree
```

Real provisioning (`up`, `zone up`) needs CAP_NET_ADMIN: run `vxedged` under sudo, or
`sudo setcap cap_net_admin+ep target/debug/vxedged`. Without it, `up` validates the
manifest and then fails with an actionable message (by design).

## 4. Run your first experiment (exp-001)

The flagship walkthrough: a full slice-isolation measurement, one command per step.

```bash
cd vxperiments/experiments/exp-001-ws
sudo -E env "PATH=$PATH" ./scripts/run.sh --quick                              # ~1 min pipeline validation
python3 ../../notebooks/analyze_exp001.py ../../results/exp-001-quick          # table + H1 verdict
```

`sudo -E` is ignored by sudo-rs, the default on Ubuntu 26 (it prints a notice). That is harmless: the explicit
`env "PATH=$PATH"` is what carries your toolchain into the root process, so the command works the same either way.

After pulling new commits, rebuild all three binaries before a run (`cargo build --workspace` in `vxedge`,
`vxagents` and `vxtelemetry`, as your own user, not root). The runner refuses to measure with a binary older
than its source and tells you the exact command, including a `touch` of the rebuilt binaries.

Zone bundles for a bare vehicle are built on your own host, not pulled from a registry, so no registry
login is needed. For `vx-vehicle-01`, from the workspace root:
`vxparts/parts/zone/linux/stack/probe-bundle/build.sh "$PWD/vxperiments/vehicles/vx-vehicle-01/bundle"`
(`bundle/` is git-ignored). The bundle embeds your host kernel, so its digest differs per host, and
`vehicle up` stops before provisioning anything if it is missing. Two host details to know:
the root daemon creates its socket owned by root with mode 755, so a non-root `vxedge` client needs
`sudo chown $USER` on the socket (or run it with `sudo`); and on Ubuntu `/boot/vmlinuz-*` is mode 600,
so `build.sh` fails until the kernel image is readable (copy it somewhere readable and pass `KERNEL=`).
The `exp-001` runner needs neither the bundle nor a login.

Results land in `vxperiments/results/`. Quick runs write to `results/exp-001-quick/` (disposable);
the frozen campaign owns `results/exp-001/`, and reruns use `--repro` (date-suffixed dir); a dir holding a
frozen campaign's archives is never overwritten in place. The raw archives of the published campaigns
are on Zenodo: [10.5281/zenodo.23804197](https://doi.org/10.5281/zenodo.23804197).

The `--quick` numbers are pipeline validation only (marked NOT reportable). The full
campaign is `./scripts/run.sh --repro` (it never overwrites the frozen `results/exp-001/`): ~35 minutes, 5 repetitions x 5 load
levels, 60k samples per point; keep the machine otherwise idle and prefer the
`performance` CPU governor. Reference result and methodology: RESULTS.md and the
`experiment-methodology` skill.

## 5. Zones and VM guest bundles

Container-backed zones work out of the box (`vxedge zone up --vxid …` after `up`). The VM
backends (`qemu-microvm`, `libvirt`) boot a guest *bundle* built once per host:

```bash
sudo chmod 644 /boot/vmlinuz-$(uname -r)        # Ubuntu ships the kernel root-only
cd vxparts && ./parts/zone/linux/stack/probe-bundle/build.sh   # -> ./bundle + digests
```

See USER-GUIDE.md §3c for wiring a bundle into a manifest.

## 6. Poke the API directly

The contract lives in `vxedge/proto/vxedge/v1/` (package `vxedge.v1`). Any gRPC tool works;
with [grpcurl](https://github.com/fullstorydev/grpcurl), from the workspace root:

```bash
grpcurl -unix -plaintext -import-path vxedge/proto \
  -proto vxedge/v1/lifecycle.proto \
  /tmp/vxedge.sock vxedge.v1.GatewayService/Status
```

Proto hygiene: `buf lint` in the `vxedge` repo (CI enforces it).

## 7. Manifests: the only input

Everything the platform does is declared in YAML manifests (schema:
`ARCHITECTURE.md` §6; worked example: §16). The parser is strict (unknown fields are
errors) and semantic validation covers slice references, vxid uniqueness, and slice-mode
consistency. Experiment manifests live in `vxperiments/experiments/`, vehicle manifests in
`vxperiments/vehicles/`.

## 8. Troubleshooting

- **`protoc` not found during `cargo build`**: install protoc (table above); the proto
  codegen runs inside the build via `crates/vxedge-api/build.rs`.
- **`cannot reach vxedged at unix:///run/vxedge.sock`**: the default socket path needs
  root-writable `/run`; for development pass a user-writable path to *both* sides
  (`--listen`/`--endpoint unix:///tmp/vxedge.sock`) or set `VXEDGE_ENDPOINT`.
- **A verb prints "not wired to the daemon yet (scaffold)"**: intentionally unimplemented;
  USER-GUIDE.md §2 lists each verb's state. Check it before assuming a bug.
- **An experiment runner refuses with "older than source file …"** (the staleness gate):
  rebuild as your user (`cargo build --workspace && touch <binary>`; cargo doesn't relink
  unchanged binaries, so mtime alone can look stale).
- **`insufficient privileges … CAP_NET_ADMIN`**: run the daemon under sudo or setcap it
  (see §3); provisioning refuses to half-apply without privileges.
- **Bundle build: "vmlinuz not readable"**: Ubuntu ships kernels 0600;
  `sudo chmod 644 /boot/vmlinuz-$(uname -r)`.

## 9. Where to contribute next

Check `docs/ROADMAP.md` (program board) and `RESULTS.md` (what's done vs open). Phases 1 and 2 are
complete and phase 3 is in progress ([`FACTS.md`](FACTS.md)); `v0.1.0` was tagged across the delivering
repos when the phase-1 gate passed (2026-07-13). Current open fronts, from the roadmap's open work:

1. `vxedge`: `vxedge vehicle up` end to end (the phase-3 gate)
2. `vxparts` (`parts/hpc/`): Autoware/ROS 2 + CARLA + carla-ros-bridge, closed loop (needs a Tier 2 GPU host)
3. `vxparts` (`parts/zone/`): QNX SDP 8 / AAOS images + real-RTOS guest bundles
   (Zephyr/FreeRTOS) beyond the linux-probe bundle
4. Track M: M4 (scenario models, fidelity ledger), which waits on a GPU host
5. Release pipeline: GHCR images with digests, and a tag-triggered release for the repositories
   other than `vxedge`

Conventions to know before your first PR: manifests are the sole source of truth; no
orchestration logic in any frontend; every image is digest-tagged. Details per repo in its `AGENTS.md`.
