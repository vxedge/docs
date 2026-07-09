# Getting Started with vxedge

vxedge is an all-software research platform for mapping 5G network slices onto zonal &
central SDV (software-defined vehicle) E/E architectures: a virtual edge gateway
(`vxgateway`), QEMU/KVM virtual ECUs, containerized AD compute, and a Rust control plane
(`vxedged`) driven entirely by YAML manifests. Read
[`ARCHITECTURE.md`](ARCHITECTURE.md) for the full picture; this page gets you to a running
daemon in minutes.

## 1. Prerequisites

Verified versions as of 2026-07:

| Tool | Version | Install |
|---|---|---|
| Rust | 1.96+ (pinned by `rust-toolchain.toml` — with rustup installed, the first `cargo` command in the repo fetches the right toolchain automatically) | `curl https://sh.rustup.rs -sSf \| sh` |
| protoc | any recent (35.x current) | distro package, or the [release zip](https://github.com/protocolbuffers/protobuf/releases) → `~/.local/bin` |
| buf | 1.71+ (optional: proto lint/SDK gen) | [release binary](https://github.com/bufbuild/buf/releases) → `~/.local/bin` |
| git + gh | any recent | distro package |

Later phases additionally need QEMU/KVM + libvirt, Open vSwitch, and an NVIDIA GPU
(CARLA/Autoware/Alpamayo workloads) — none of that is required to build and run the
control plane today.

## 2. Workspace layout

vxedge is a **meta-workspace of independent git repos**, cloned side by side (the parent
folder is *not* a git repo):

```bash
mkdir vxedge && cd vxedge
for r in docs vxedge vxzones vxcompute vxota vxagents vxtelemetry vxperiments; do
  gh repo clone vxedge/$r
done
```

| Repo | What |
|---|---|
| `docs` | Master spec (`ARCHITECTURE.md`), program task board, publication plan |
| `vxedge` | **Start here** — control plane (`vxedged`), vxAPI (gRPC/Protobuf), CLI |
| `vxzones` / `vxcompute` | Zone (virtual-ECU) and central-compute manifests + images |
| `vxota` / `vxtelemetry` | OTA and telemetry service code |
| `vxagents` | Rust measurement agents (latency probes, traffic gen, pcap) |
| `vxperiments` | Experiment + vehicle manifests, notebooks, results |

Every repo has an `AGENTS.md` (scope + rules) and `TASKS.md` (phased work items);
`docs/TASKS.md` is the program-level board with the cross-repo critical path.

## 3. Build and run the control plane

```bash
cd vxedge          # the core repo
cargo build --workspace
cargo test --workspace   # expect: vxedge-core's manifest tests pass (5 at time of writing)
```

Terminal 1 — the daemon (serves vxAPI on a Unix socket):

```bash
./target/debug/vxedged --listen unix:///tmp/vxedge.sock
```

Terminal 2 — the CLI (a thin vxAPI client):

```bash
./target/debug/vxedge --endpoint unix:///tmp/vxedge.sock status
# gateway vxgateway: state=1 detail=scaffold: no backend provisioned

./target/debug/vxedge --endpoint unix:///tmp/vxedge.sock --json status   # machine-readable
./target/debug/vxedge --help                                             # full command tree
```

`state=1` is `RESOURCE_STATE_DOWN` — honest output: the gateway backend (OVS/tc
provisioning) is the next work item on the phase-1 critical path.

## 4. Poke the API directly

The contract lives in `vxedge/proto/vxedge/v1/` (package `vxedge.v1`). Any gRPC tool works;
with [grpcurl](https://github.com/fullstorydev/grpcurl), from the workspace root:

```bash
grpcurl -unix -plaintext -import-path vxedge/proto \
  -proto vxedge/v1/lifecycle.proto \
  /tmp/vxedge.sock vxedge.v1.GatewayService/Status
```

Proto hygiene: `buf lint` in the `vxedge` repo (CI enforces it).

## 5. Manifests — the only input

Everything the platform does is declared in YAML manifests (schema:
`ARCHITECTURE.md` §6; worked example: §16). The parser is strict — unknown fields are
errors — and semantic validation covers slice references, vxid uniqueness, and slice-mode
consistency. Experiment manifests live in `vxperiments/experiments/`, vehicle manifests in
`vxperiments/vehicles/`.

## 6. Troubleshooting

- **`protoc` not found during `cargo build`** — install protoc (table above); the proto
  codegen runs inside the build via `crates/vxedge-api/build.rs`.
- **`cannot reach vxedged at unix:///run/vxedge.sock`** — the default socket path needs
  root-writable `/run`; for development pass a user-writable path to *both* sides
  (`--listen`/`--endpoint unix:///tmp/vxedge.sock`) or set `VXEDGE_ENDPOINT`.
- **A verb prints "not wired to the daemon yet (scaffold)"** — expected: only `status` is
  wired today. `docs/TASKS.md` shows exactly what works at any point in time; check it
  before assuming a bug.

## 7. Where to contribute next

Check `docs/TASKS.md` (program board — includes the current phase-1 status assessment).
The current critical path, in order:

1. `vxedge` — vxgateway backend: OVS/bridge + tc HTB queue trees behind `vxedge up` (TASKS §2)
2. `vxagents` — latency/jitter probes + traffic generator
3. `vxtelemetry` — ingestion + `telemetry collect`
4. `vxperiments` — `exp-001` (ADAS slice isolation, hypothesis H1)

Conventions to know before your first PR: manifests are the sole source of truth; no
orchestration logic in any frontend; every image is digest-tagged; commits without a
Co-Authored-By trailer. Details per repo in its `AGENTS.md`.
