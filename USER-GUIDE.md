# vxedge User Guide

For SDV / automotive engineers using vxedge as a testbed. Onboarding lives in
[GETTING-STARTED.md](GETTING-STARTED.md); the full spec in [ARCHITECTURE.md](ARCHITECTURE.md);
host requirements in [TESTBED-SETUP.md](TESTBED-SETUP.md); live progress in [STATUS.md](STATUS.md).

**Honest state banner:** vxedge is a research-grade *executable virtual prototype* of a zonal
SDV E/E architecture — not a certified tool and not a "digital twin" of any physical vehicle
(that word is reserved for hardware-in-the-loop parity, phase 4). What is verified today is
listed per-verb below; everything else fails loudly rather than pretending.

## 1. Concepts

- **Manifests are the only input.** An *experiment manifest* (YAML) declares slices, zones,
  compute, traffic, telemetry and results; a *vehicle manifest* (phase 3) composes a full
  software vehicle. The CLI/daemon keep no other configuration; every result archive records
  the manifest's SHA-256.
- **Slices** are the network partitions under test: `mode: vlan` (per-slice VLAN + HTB
  queue-tree reservation on the virtual gateway — the H1 mechanism, verified) or
  `mode: s-nssai` (real 5G slices via Open5GS/UERANSIM, phase 2).
- **vxgateway** is the software edge gateway the daemon provisions from the manifest:
  a VLAN-filtering Linux bridge, a shaped trunk uplink (the shared bottleneck where slice
  contention is measured), and one access port per zone-node interface.
- **Zones & nodes** are virtual ECUs. Each node runs under a packaging **backend** —
  `container` (network namespace), `qemu-microvm` (raw QEMU, direct kernel boot) or
  `libvirt` (full VM) — with identical network attachment; the packaging choice is itself
  an experimental variable (H3).
- **Jobs**: every mutating command returns a job with live streamed progress; a job that
  couldn't finish reports FAILED with the real error, never a hollow success.
- **Results archives** (`results/<exp>/<run>.zip`) are the reproducibility unit: raw metric
  scrapes, structured samples, agent summaries, environment metadata, the manifest itself.

## 2. CLI reference (state as of phase 1)

All lifecycle verbs follow `up|down[|status]`; operations are idempotent.

| Command | State | Notes |
|---|---|---|
| `vxedged serve --listen unix://… --runtime-dir …` | live | needs CAP_NET_ADMIN for real `up` (sudo or setcap) |
| `vxedge up\|down --manifest <exp.yaml>` | live | provisions/removes the gateway; sets the daemon's active experiment |
| `vxedge status` | live | observed gateway + per-slice state |
| `vxedge zone up\|down --vxid <zone-id>` | live | runs the zone's nodes under their backends; needs an active experiment |
| `vxedge zone list` | live | per-node observed state |
| `vxedge zone add/rm/image push` | planned | image store / registry work |
| `vxedge manifest validate [--json]` | live | local-only schema+semantic check (same check `up` runs); powers manifest CI |
| `vxedge doctor [--tier N] [--json]` | live | host preflight against TESTBED-SETUP tiers 0–3, actionable fix hints |
| `vxedge ota up\|down --experiment …` | live | spawns/manages `vxota serve` from the manifest's `services.ota` block (used by exp-003) |
| `vxedge telemetry up\|down\|collect` | planned | vxtelemetry runs standalone today (see §4); daemon wiring open |
| `vxedge compute …` | planned | phase 2 (Autoware/CARLA workloads) |
| `vxedge vehicle up\|down\|status` | planned | phase 3 |
| `vxedge experiment new <id> [--template minimal\|slicing]` | live | scaffolds a workspace folder; no daemon, no network, no GPU |
| `vxedge experiment validate [path]` | live | local-only; loads a workspace and runs every cross-file check, reporting all problems at once |
| `vxedge experiment lower [path] [-o <file>]` | live | local-only; turns a §6.0 workspace into the §6.1 manifest `experiment up` runs. `channels` is not carried — §6.1 has no interaction layer |
| `vxedge experiment\|traffic up` | planned | today the experiment runner script orchestrates. `experiment up` does not consume the §6.0 workspace shape yet — that lands with the loader wiring |

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
cd vxperiments
sudo -E env "PATH=$PATH" ./scripts/run-exp-001.sh --quick   # ~1 min pipeline validation -> results/exp-001-quick/
sudo -E env "PATH=$PATH" ./scripts/run-exp-001.sh           # full campaign (~35 min, idle host) -> results/exp-001/
sudo -E env "PATH=$PATH" ./scripts/run-exp-001.sh --repro   # later rerun -> results/exp-001-repro-<date>/
python3 notebooks/analyze_exp001.py results/exp-001          # archives -> table + verdict
```

A dir already holding a campaign's archives is never overwritten in place — full runs
refuse it, repro checks and quick runs get their own dirs (`scripts/lib/results_dir.sh`).

Numbers from `--quick` runs are pipeline validation only and are marked NOT reportable.
Reference result (2026-07-10, full campaign): ADAS slice p99 held at 0.93x baseline under
1.2x offered overload from the infotainment slice, zero loss (see STATUS.md).

### c) VM-backed zones (guest bundles)

VM backends boot a *bundle* (kernel + initramfs with an autostarting payload), built once:

```bash
sudo chmod 644 /boot/vmlinuz-$(uname -r)      # Ubuntu ships the kernel root-only
cd vxzones && ./scripts/build-guest-bundle.sh # -> images/linux-probe/bundle (digests in meta.json)
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
| harness `impairments` (phase 2) | 100/1000BASE-T1 PHY characteristics; TSN variant = 802.1Qbv/Qav + gPTP |
| results archives | test-bench evidence packages (ASAM OSI/FMI/XIL alignment, phase 4) |

## 7. Getting help / contributing

Each repo carries `AGENTS.md` (scope + rules) and `TASKS.md` (work items);
`docs/TASKS.md` is the program board. Quality bars are codified as repo skills
(`.claude/skills/`): `rust-patterns`, `testbed-quality`, `experiment-methodology`,
`gateway-verification` (vxedge), `sysml-authoring` (vxmodels).
A verb that prints "not wired to the daemon yet (scaffold)" is truthfully unimplemented —
check STATUS.md before assuming a bug.
