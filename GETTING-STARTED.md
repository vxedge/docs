# Getting Started with vxedge

vxedge is an all-software research platform for mapping 5G network slices onto zonal &
central SDV (software-defined vehicle) E/E architectures: a virtual edge gateway
(`vxgateway`), QEMU/KVM virtual ECUs, containerized AD compute, and a Rust control plane
(`vxedged`) driven entirely by YAML manifests. Read
[`ARCHITECTURE.md`](ARCHITECTURE.md) for the full picture; this page gets you from
zero to a measured experiment; day-to-day usage lives in [USER-GUIDE.md](USER-GUIDE.md).

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

## 3. Build everything

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

Real provisioning (`up`, `zone up`) needs CAP_NET_ADMIN — run `vxedged` under sudo, or
`sudo setcap cap_net_admin+ep target/debug/vxedged`. Without it, `up` validates the
manifest and then fails with an actionable message (by design).

## 4. Run your first experiment (exp-001)

The flagship walkthrough: a full slice-isolation measurement, one command per step.

```bash
cd vxperiments
sudo -E env "PATH=$PATH" ./scripts/run-exp-001.sh --quick   # ~1 min pipeline validation
python3 notebooks/analyze_exp001.py results/exp-001          # table + H1 verdict
```

The `--quick` numbers are pipeline validation only (marked NOT reportable). The full
campaign is `./scripts/run-exp-001.sh` without flags: ~35 minutes, 5 repetitions x 5 load
levels, 60k samples per point — keep the machine otherwise idle and prefer the
`performance` CPU governor. Reference result and methodology: STATUS.md and the
`experiment-methodology` skill.

## 5. Zones and VM guest bundles

Container-backed zones work out of the box (`vxedge zone up --vxid …` after `up`). The VM
backends (`qemu-microvm`, `libvirt`) boot a guest *bundle* built once per host:

```bash
sudo chmod 644 /boot/vmlinuz-$(uname -r)        # Ubuntu ships the kernel root-only
cd vxzones && ./scripts/build-guest-bundle.sh   # -> images/linux-probe/bundle + digests
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

## 7. Manifests — the only input

Everything the platform does is declared in YAML manifests (schema:
`ARCHITECTURE.md` §6; worked example: §16). The parser is strict — unknown fields are
errors — and semantic validation covers slice references, vxid uniqueness, and slice-mode
consistency. Experiment manifests live in `vxperiments/experiments/`, vehicle manifests in
`vxperiments/vehicles/`.

## 8. Troubleshooting

- **`protoc` not found during `cargo build`** — install protoc (table above); the proto
  codegen runs inside the build via `crates/vxedge-api/build.rs`.
- **`cannot reach vxedged at unix:///run/vxedge.sock`** — the default socket path needs
  root-writable `/run`; for development pass a user-writable path to *both* sides
  (`--listen`/`--endpoint unix:///tmp/vxedge.sock`) or set `VXEDGE_ENDPOINT`.
- **A verb prints "not wired to the daemon yet (scaffold)"** — truthfully unimplemented;
  USER-GUIDE.md §2 lists each verb's state. Check it before assuming a bug.
- **An experiment runner refuses with "older than source file …"** — the staleness gate:
  rebuild as your user (`cargo build --workspace && touch <binary>`; cargo doesn't relink
  unchanged binaries, so mtime alone can look stale).
- **`insufficient privileges … CAP_NET_ADMIN`** — run the daemon under sudo or setcap it
  (see §3); provisioning refuses to half-apply without privileges.
- **Bundle build: "vmlinuz not readable"** — Ubuntu ships kernels 0600;
  `sudo chmod 644 /boot/vmlinuz-$(uname -r)`.

## 9. Where to contribute next

Check `docs/TASKS.md` (program board) and `STATUS.md` (what's done vs open). The H1 spine —
gateway, agents, telemetry, exp-001 — is complete with published-quality numbers; current
open fronts, in order:

1. `vxperiments` — exp-002 (H3: VM vs microVM vs container packaging over identical slices)
2. `vxota` — OTA server v1 (unblocks exp-003 / H4 and closes the phase-1 gate)
3. `vxzones` — real-RTOS guest bundles (Zephyr/FreeRTOS) beyond the linux-probe bundle
4. Phase 2: Open5GS/UERANSIM S-NSSAI slicing, CARLA→ROS2 closed loop, harness impairments

Conventions to know before your first PR: manifests are the sole source of truth; no
orchestration logic in any frontend; every image is digest-tagged; commits without a
Co-Authored-By trailer. Details per repo in its `AGENTS.md`.
