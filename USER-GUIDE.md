# vxedge User Guide

For SDV / automotive engineers using vxedge as a testbed. Onboarding lives in
[GETTING-STARTED.md](GETTING-STARTED.md); the full spec in [ARCHITECTURE.md](ARCHITECTURE.md);
host requirements in [TESTBED-SETUP.md](TESTBED-SETUP.md); live progress in [RESULTS.md](RESULTS.md).

**Honest state banner:** vxedge is a research-grade *executable virtual prototype* of a zonal
SDV E/E architecture — not a certified tool and not a "digital twin" of any physical vehicle
(that word is reserved for hardware-in-the-loop parity, phase 4). What is verified today is
listed per-verb below; everything else fails loudly rather than pretending.

## 1. Concepts

- **A workspace is the unit of work — a folder, not a single file.** An experiment is a
  directory holding a `.vxp` package descriptor (id, version, entry, `requires`) plus
  top-level YAML documents, each declaring its own `kind` — `experiment` (the test),
  `vehicle` (the system under test), `road` (the environment, optional), `baseline` (which
  software), `component` — and `id`. Every cross-reference is by id, never by path, so files
  can be renamed or reorganized without breaking anything; a whole workspace can also be one
  file of `---`-separated documents. The CLI/daemon keep no other configuration; every result
  archive records the workspace's SHA-256.
- **A workspace is a sandbox.** It owns its own `scripts/run.sh` (the campaign: repetitions,
  warmup, measurement window), `parts/` (its loadables), `assets/` (scenario files), `tools/`
  (its own analysis), and `results/` (one archive per run) — a folder that can be zipped,
  sent, unzipped and run standalone. `vxedge experiment new <id> [--template minimal|slicing]`
  scaffolds one; `vxedge experiment validate` runs every cross-file check and every model
  invariant before anything is provisioned. Full schema: ARCHITECTURE.md §6.0.
- **Structure and software are separate files.** One `vehicle.yaml` carries many `baseline`
  files, so an A/B arm is two baselines over one unchanged vehicle, not two vehicle files that
  drift apart. The vehicle *names* a slice (`links[].slice: adas`); the experiment *defines*
  it (`network.slices[].mode: vlan|s-nssai`) — the only reference that crosses the
  structure/test boundary, and `experiment validate` checks it.
- **Slices** are the network partitions under test: `mode: vlan` (per-slice VLAN + HTB
  queue-tree reservation on the virtual gateway — the H1 mechanism, verified) or
  `mode: s-nssai` (real 5G slices via Open5GS/UERANSIM — the H2 mechanism, verified).
- **vxgateway** is the software edge gateway the daemon provisions from the vehicle/experiment:
  a VLAN-filtering bridge (`network.data_plane: kernel-bridge`, default) or an OVS bridge
  (`ovs`) — same plan, pluggable rendering backend — a shaped trunk uplink (the shared
  bottleneck where slice contention is measured), and one access port per zone-node interface.
  A link's `impairments` block (rate/delay/jitter/loss, via netem) and declarative `harness`
  block (medium/length/weight, reporting-only) model the physical wiring between two nodes.
- **Zones, nodes, and roles.** Zones are the six regions (`front-left`, `front-right`,
  `rear-left`, `rear-right`, `central-hpc`, `gateway`); a node is a device with a `role`
  (`zone-controller`, `hpc`, `gateway`, `ecu`, `sensor`, `actuator`, `switch`) sitting in one.
  Each node runs under a packaging **backend** — `container` (network namespace),
  `qemu-microvm` (raw QEMU, direct kernel boot) or `libvirt` (full VM) — with identical
  network attachment; the packaging choice is itself an experimental variable (H3).
  `ComputeService` is `role: hpc` filtered over that same backend split, not a separate
  provisioning path.
- **Jobs**: every mutating command returns a job with live streamed progress; a job that
  couldn't finish reports FAILED with the real error, never a hollow success.
- **Results archives** (`results/<exp>/<run>.zip`) are the reproducibility unit: raw metric
  scrapes, structured samples, agent summaries, environment metadata, the workspace itself.
  `v0.1.0` (2026-07-13) tags the checkpoint where this became true end to end — H1/H3/H4 all
  reproducible from a tagged manifest, not just runnable once.

## 2. CLI reference

All lifecycle verbs follow `up|down[|status]`; operations are idempotent.

| Command | State | Notes |
|---|---|---|
| `vxedged serve --listen unix://… --runtime-dir …` | live | needs CAP_NET_ADMIN for real `up` (sudo or setcap) |
| `vxedge up\|down --manifest <workspace-dir>` | live | provisions/removes the gateway; sets the daemon's active experiment. `--manifest` names a §6.0 workspace directory (or one file of `---`-separated documents) |
| `vxedge status` | live | observed gateway + per-slice state |
| `vxedge zone up\|down --vxid <zone-id\|device-id>` | live | runs the nodes of a zone (a region), or a single device by its own id; needs an active experiment |
| `vxedge zone list` | live | per-node observed state, with each device's host interfaces (`port=`, `peer=`) |
| `vxedge zone add/rm/image push` | planned | image store / registry work |
| `vxedge manifest validate --manifest <path> [--json]` | live | local-only. Takes a §6.0 workspace — a directory, or one file of `---`-separated documents — and runs every cross-file check *and* every model invariant, the same checks `up` runs. It is the only schema there is (§6.1/§6.2 were retired 2026-07-31) |
| `vxedge events [--kind K]... [--json]` | live | streams what the daemon is doing: `gateway.up`, `gateway.slice-applied`, `zone.up`/`down`, `service.up`/`down`, `traffic.started`/`stopped`, plus `job.state`. Domain facts about resources, not job progress — and lossy by design, so it is a live view rather than a record. For "what happened, in order, without loss", read the audit log |
| `vxedge doctor [--tier N] [--json]` | live | host preflight against TESTBED-SETUP tiers 0–3, actionable fix hints |
| `vxedge ota up\|down [--experiment <path>]` | live | spawns/manages `vxota serve` from the workspace's `services.ota` block; cwd-resolved by default like `experiment` verbs, `--experiment` overrides. A campaign normally reaches this through `experiment up --stage services` (what exp-003 actually does) rather than calling it standalone |
| `vxedge telemetry up\|down\|collect` | planned | vxtelemetry runs standalone today (see §4); daemon wiring open |
| `vxedge compute up\|down --vxid <id>` / `list` | live | a second RPC surface over the same node backends as `zone`, filtered to `role: hpc` devices — not a separate provisioning path. `add`/`rm`/`image push` planned |
| `vxedge vehicle up\|down\|status` | planned | phase 3 |
| `vxedge experiment new <id> [--template minimal\|slicing]` | live | scaffolds a workspace folder; no daemon, no network, no GPU |
| `vxedge experiment validate` | live | local-only; loads the workspace here and runs every cross-file check, reporting all problems at once |
| `vxedge experiment up\|down\|status` | live | acts on the workspace in the **current directory** (the single `.vxp`); no name, no `--manifest`. `--chdir <dir>` to run from elsewhere. `up` provisions gateway → zones → services and **does not start traffic** — use `vxedge traffic up`. `--stage gateway\|zones\|services` (repeatable) restricts it: a campaign measuring on the host-side veth peers stages only the gateway, and one whose isolation contract is a single arm at a time stages the gateway then brings each arm up with `zone up --vxid` |
| `vxedge traffic up\|down --manifest …` | live | drives the declared profiles; kept separate from `experiment up` because load is time-bounded and a campaign sweeps it over a fixed topology |

Global flags: `--endpoint` (default local Unix socket), `--json`.

## 3. Typical workflows

### a) Slicing sandbox (no measurement)

```bash
sudo -E env "PATH=$PATH" ./target/debug/vxedged --listen unix:///tmp/vx.sock --runtime-dir /tmp/vxrt &
vxedge --endpoint unix:///tmp/vx.sock up --manifest exp.yaml     # bridge + VLANs + HTB
vxedge --endpoint unix:///tmp/vx.sock status                     # per-slice observed state
vxedge --endpoint unix:///tmp/vx.sock zone up --vxid vxzone-front-left-01
vxedge --endpoint unix:///tmp/vx.sock zone list
vxedge --endpoint unix:///tmp/vx.sock down --manifest exp.yaml
```

### b) A measurement campaign (the exp-001 pattern)

Campaigns are orchestrated by a runner script that encodes the methodology (warmup outside
the probe window, ≥5 repetitions, environment metadata, archive per run):

```bash
cd vxperiments/experiments/exp-001-ws
sudo -E env "PATH=$PATH" ./scripts/run.sh --quick   # ~1 min pipeline validation -> ../../results/exp-001-quick/
sudo -E env "PATH=$PATH" ./scripts/run.sh --repro   # full rerun (~35 min, idle host) -> ../../results/exp-001-repro-<date>/
python3 ../../notebooks/analyze_exp001.py ../../results/exp-001   # archives -> table + verdict
```

A dir already holding a campaign's archives is never overwritten in place — full runs
refuse it, repro checks and quick runs get their own dirs (`scripts/lib/results_dir.sh`).

Numbers from `--quick` runs are pipeline validation only and are marked NOT reportable.
Reference result (2026-08-03 corrected campaign, superseding the original 2026-07-10 run
— see RESULTS.md's Phase 1 row for why): ADAS slice p99 held at 0.91x baseline under 1.2x
offered overload from the infotainment slice, zero loss (see RESULTS.md).

### c) VM-backed zones (guest bundles)

VM backends boot a *bundle* (kernel + initramfs with an autostarting payload), built once:

```bash
sudo chmod 644 /boot/vmlinuz-$(uname -r)      # Ubuntu ships the kernel root-only
cd vxparts && ./parts/zone/linux/stack/probe-bundle/build.sh # -> ./bundle (digests in meta.json)
```

Point a node's `image.url` at the bundle dir with `kind: rtimage` and
`backend: qemu-microvm` or `backend: libvirt`. Guest network comes from the manifest's
`ip:` via the kernel cmdline; the payload (a vxprobe reflector) starts automatically.

## 4. Measurement agents & telemetry (standalone today)

- `vxprobe reflect|send` — RTT p50/p95/p99, jitter, loss; live Prometheus `/metrics`;
  JSON summary on stdout (stdout is machine-readable; logs go to stderr).
- `vxtraffic` — rate-accurate UDP load (`--pps` or `--bandwidth-mbps`).
- `vxtelemetry ingest|collect` — scrapes manifest targets, archives
  `results/<exp>.zip` with metadata (experiment id, manifest SHA-256, tool versions,
  ingest completeness).

## 5. Reading results

Every archive contains `metadata.json` (reproducibility fields), `manifest.yaml`,
`ingest/raw/**.prom` (timestamped scrapes), `ingest/samples.jsonl` (structured samples),
agent summaries, and `run-env.json` (kernel, RT flag, governor, pinning, timestamping
method, load level, repetition). Analysis reads archives only; figures must regenerate
headlessly. Report medians with IQR across repetitions; state sample counts next to tail
percentiles; keep the recorded caveats attached (shared-host gateway, non-PREEMPT_RT
kernel, userspace timestamps).

## 6. Mapping to production SDV vocabulary

| vxedge | Production counterpart |
|---|---|
| vxgateway (bridge/VLAN/HTB) | zonal gateway / central switch QoS (automotive Ethernet) |
| slices `mode: vlan` → `s-nssai` | static VLAN partitioning → 5G network slicing (S-NSSAI/URSP) |
| zones + backends | zonal ECUs under a Type-1 hypervisor (fidelity ladder: KVM → Xen dom0less → QNX Hypervisor) |
| `type: can` links (phase 3) | CAN/LIN drops behind zonal controllers (restbus, DBC, Kuksa/VSS) |
| harness `impairments` (delivered) + `harness` block | 100/1000BASE-T1 PHY characteristics (rate/delay/jitter/loss) + declarative length/weight for harness-reduction reporting; TSN variant = 802.1Qbv/Qav + gPTP (phase 2, open) |
| results archives | test-bench evidence packages (ASAM OSI/FMI/XIL alignment, phase 4) |

## 7. Getting help / contributing

Each repo carries `AGENTS.md` (scope + rules) and `TASKS.md` (work items);
`docs/ROADMAP.md` is the program board. Quality bars are codified as repo skills
(`.claude/skills/`): `rust-patterns`, `testbed-quality`, `experiment-methodology`,
`gateway-verification` (vxedge), `sysml-authoring` (vxmodels).
A verb that prints "not wired to the daemon yet (scaffold)" is truthfully unimplemented —
check RESULTS.md before assuming a bug.
