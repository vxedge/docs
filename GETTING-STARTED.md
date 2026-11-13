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
| Rust | 1.99+ (pinned by `rust-toolchain.toml`; with rustup installed, the first `cargo` command in the repo fetches the right toolchain automatically) | `curl https://sh.rustup.rs -sSf \| sh` |
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
| `vxperiments` | Experiment packages, vehicle manifests, frozen results |
| `vxmodels` | SysML v2 system models + `vxmodel` manifest renderer, track M (`ARCHITECTURE.md` §6.3) |
| `vxmcp` | MCP (Model Context Protocol) server over vxAPI, for agent tooling |

Every repo has an `AGENTS.md` (scope + rules) and a `CHANGELOG.md`; `docs/ROADMAP.md` is the
public phase status.

## 3. Get the binaries

**Prebuilt (CLI and daemon, Linux x86-64 and ARM64):** download the latest `vxedge` release, check it, and run it.
Each release carries `SHA256SUMS` and build provenance.

```bash
gh release download -R vxedge/vxedge --pattern '*x86_64*' --pattern SHA256SUMS      # aarch64 on ARM
sha256sum --ignore-missing -c SHA256SUMS                                             # must say OK
gh attestation verify vxedge-*-x86_64-unknown-linux-gnu.tar.gz -R vxedge/vxedge     # needs gh 2.49 or newer
tar xzf vxedge-*-x86_64-unknown-linux-gnu.tar.gz                                     # vxedge, vxedged, LICENSE, NOTICE
```

The binaries are built on Ubuntu 24.04 (glibc 2.39), so they run on 24.04 and newer. The campaign in §4 also
runs `vxprobe` and `vxtraffic` (`vxagents`) and `vxtelemetry`: download those releases the same way, or build
them from source below. `vxedged` finds them on its `PATH`.

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

Real provisioning (`up`, `zone up`) needs CAP_NET_ADMIN, plus CAP_SYS_ADMIN to enter a
node's network namespace: run `vxedged` under sudo, or
`sudo setcap cap_net_admin,cap_sys_admin+ep target/debug/vxedged`. Without it, `up` validates the
manifest and then fails with an actionable message (by design).

## 4. Run your first experiment (exp-001)

The flagship walkthrough: the H1 slice-isolation campaign, run from its package. Every experiment in
`vxperiments` is a `vxp/1` package, and every campaign runs the same way.

A campaign runs through `vxedged`, which needs CAP_NET_ADMIN (§3) and finds `vxprobe`, `vxtraffic` and
`vxtelemetry` on its `PATH`. From the workspace root, with `vxedge`, `vxedged` and those three on your `PATH`:

```bash
sudo -v                                                 # so the daemon below starts without a prompt
sudo env "PATH=$PATH" vxedged --listen unix:///tmp/vx.sock --runtime-dir /tmp/vxrt &
sudo chown $USER /tmp/vx.sock                           # once the daemon is listening
export VXEDGE_ENDPOINT=unix:///tmp/vx.sock
cd vxperiments/experiments/exp-001-ws
vxedge experiment validate                              # every check, no daemon
vxedge campaign plan --profile quick                    # the trials, checked; touches nothing
vxedge campaign start --profile quick                   # pipeline check: one archive per trial, then the H1 verdict
```

The explicit `env "PATH=$PATH"` is what carries your toolchain into the root process. The root daemon creates
its socket owned by root with mode 755, hence the `chown` for a non-root `vxedge` client.

The `quick` numbers are pipeline validation only and are never reported. The full campaign is
`vxedge campaign start --profile repro`: 5 repetitions x 5 load levels, 60k samples per point. Keep the machine
otherwise idle and prefer the `performance` CPU governor. Run it from a clone outside your home directory, for
example under `/var/tmp`: the campaign writes its archives into the package folder, and file indexers or sync
clients watching your home directory can load the host while trials run (`campaign start` warns about it). A campaign writes its archives, `campaign.json` and
`verdict.json` under `results/<campaign id>/` in the package folder; `vxedge campaign verdict <campaign id>`
judges it again, and `vxedge campaign compare <campaign id> exp-001 --reference-workspace ../..` compares it
with the frozen campaign (the package's README says how). The raw archives of the published campaigns are on Zenodo:
[10.5281/zenodo.23804197](https://doi.org/10.5281/zenodo.23804197), and `scripts/verdict-parity.sh --fetch` in
`vxperiments` re-judges them with each package's criteria. Reference result and methodology: RESULTS.md and
the `experiment-methodology` skill.

Zone bundles for a bare vehicle are built on your own host, not pulled from a registry, so no registry
login is needed. For `vx-vehicle-01`, from the workspace root:
`vxparts/parts/zone/linux/stack/probe-bundle/build.sh "$PWD/vxperiments/vehicles/vx-vehicle-01/bundle"`
(`bundle/` is git-ignored). The bundle embeds your host kernel, so its digest differs per host, and
`vehicle up` stops before provisioning anything if it is missing. On Ubuntu `/boot/vmlinuz-*` is mode 600,
so `build.sh` fails until the kernel image is readable (copy it somewhere readable and pass `KERNEL=`).
The exp-001 package needs neither the bundle nor a login: its zones are host processes.

## 5. Zones and VM guest bundles

Container-backed zones work out of the box (`vxedge zone up --vxid …` after `up`). The VM
backends (`qemu-microvm`, `libvirt`, `cloud-hypervisor`) boot a guest *bundle* built once per
host, and `wasm-capsule` runs a WebAssembly module through the `vxcapsule` runner that ships beside
`vxedged` ([`TESTBED-SETUP.md`](TESTBED-SETUP.md) lists what each needs):

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
- **`insufficient privileges … CAP_NET_ADMIN`**: run the daemon under sudo or setcap it
  (see §3); provisioning refuses to half-apply without privileges.
- **Bundle build: "vmlinuz not readable"**: Ubuntu ships kernels 0600;
  `sudo chmod 644 /boot/vmlinuz-$(uname -r)`.

## 9. Where to contribute

Check `docs/ROADMAP.md` (phase status) and `RESULTS.md` (what is measured). The gates of
phases 1 to 3 have passed and phase 3 content is in progress ([`FACTS.md`](FACTS.md)); `v0.1.0` was tagged across the delivering
repos when the phase-1 gate passed (2026-07-13). To propose work, open an issue on the repository it
belongs to, or on `vxedge/docs` for anything that spans repositories.

Conventions to know before your first PR: manifests are the sole source of truth; no
orchestration logic in any frontend; every image is digest-tagged. Details per repo in its `AGENTS.md`.
