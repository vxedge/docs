# Facts registry

This file is the single registry of published facts: measured numbers, verdicts, phase states,
the parity ledger and what has been delivered. The website ([vxedge.dev](https://vxedge.dev))
builds every number and state it shows from this file and nothing else. The GitHub READMEs and
[`RESULTS.md`](RESULTS.md) quote it.

Each measured value is copied from a frozen summary in
[`vxperiments/results/`](https://github.com/vxedge/vxperiments/tree/main/results). Those summaries
record the input manifest's sha256. This file does not replace them; it is the one place they are
quoted from. [`RESULTS.md`](RESULTS.md) explains the numbers: what each hypothesis tests and the
caveat that matters most.

**To change a fact:** edit it here first, in the same change as the summary or state that moved.
Then run `python3 scripts/facts.py check` from this repo. The website picks the change up on its
next build. Its CI fails if the vendored copy is stale, or if a page shows a number that is not
registered here.

**Format.** Every table whose first column is `Key` is machine-read by
[`scripts/facts.py`](https://github.com/vxedge/docs/blob/main/scripts/facts.py). A table with a `Value` column holds one fact per row. Any
other keyed table is a row table: each cell becomes `<key>.<column>`, where the column name is the
first word of its header, lowercased (`p99 µs (IQR)` → `p99`). Keys are lowercase and never change
meaning once published. A fact that is retired is deleted, not renamed.

State words are fixed. For deliveries: **measured** (frozen, reproduced results), **live** (works
today, no frozen number), **building** (partly landed), **planned** (specified, not built). For the
parity ledger: **real** (the production software or kernel path itself), **emulated** (real software
on modelled hardware), **planned**, **caveat** (works, with a stated limit on what it can tell you).

## 1 · Project

| Key | Value | Source |
|---|---|---|
| `project.name` | vxedge | — |
| `project.version` | 0.2.1 | [`CITATION.cff`](CITATION.cff) |
| `project.released` | 2026-10-19 | [`CITATION.cff`](CITATION.cff) |
| `project.stage` | pre-release | pre-1.0: the manifest schema and vxAPI may change between minor versions; published results are frozen ([`VERSIONING.md`](VERSIONING.md)) |
| `project.status` | Phases 1–2 complete, phase 3 in progress | [`ROADMAP.md`](ROADMAP.md) |
| `project.phase` | 3 | [`ROADMAP.md`](ROADMAP.md) |
| `project.licence_code` | Apache-2.0 | [`LICENSE`](LICENSE) |
| `project.licence_docs` | CC BY 4.0 | [`LICENSE-DOCS`](LICENSE-DOCS) |
| `project.hypotheses` | 4 | [`ARCHITECTURE.md`](ARCHITECTURE.md) §2 |
| `project.hypotheses_hold` | 4 | §2 below |
| `project.reproduced` | 4 | §2 below: each verdict re-reached by an independent second campaign |
| `project.repos` | 9 | `README.md`: `docs` and eight code repositories |
| `project.mcp_spec` | 2026-07-28 | `vxmcp` targets this MCP specification revision |

### Phases

| Key | Phase | Gate | State |
|---|---|---|---|
| `phase.1` | Slicing core, API-first | Reproducible H1/H3/H4 numbers | done |
| `phase.2` | Real slices and workloads | H2: S-NSSAI vs static VLAN | done |
| `phase.3` | Production SDV alignment | `vxedge vehicle up` boots a full vehicle end to end | in progress |
| `phase.4` | Hardware in the loop | Jetson / DRIVE / BlueField / V2X radio | specified |
| `phase.5` | Remote and multi-user | none yet | backlog |

### Tracks

| Key | Track | Status |
|---|---|---|
| `track.m` | M: SysML v2 model governance | M0–M3 closed; M4 waits on a GPU host |
| `track.c` | C: containerization | complete through C3.2 |
| `track.p` | P: `vxparts` unification | complete |

## 2 · Results

The tables under each hypothesis heading (H1–H4) and under *Other completed experiments* are
measurements. The website paints those values, and only those, in its measured-value colour. The
method, parameters and verdicts are not measurements and are not painted.

### Method and parameters

The same method for every campaign, and the parameters each hypothesis was tested with. These are
configuration, not measurements.

| Key | Value | Source |
|---|---|---|
| `method.reps` | 5 reps | per arm or load point |
| `method.rate` | 1000 pps | probe rate |
| `method.duration` | 60 s | per point |
| `method.probes` | 60 000 probes | per point |
| `method.warmup` | 10 s | discarded before probing |
| `method.campaign_time` | ~35 min | full `exp-001` campaign on an idle host, [`GETTING-STARTED.md`](GETTING-STARTED.md) |
| `h1.max_load` | 600 mbit | H1: highest offered infotainment load |
| `h1.uplink` | 500 mbit | H1: root rate of the shared uplink, `exp-001-ws/main.yaml` |
| `h1.overload` | 1.2× | H1: max load ÷ uplink |
| `h1.loads` | 5 loads | H1, H2: load levels swept |
| `h1.threshold` | 2.0× | H1: pass threshold for p99 at max load ÷ p99 idle |
| `h2.tolerance` | 1.1× | H2: S-NSSAI p99 growth may exceed VLAN growth by at most this factor |
| `h3.arms` | 6 arms | H3: packaging arms compared |
| `h3.probes` | 1.8M probes | H3: probes across all archives |
| `h4.artifact` | 5 MB | H4: artifact size, delivered back to back |
| `h4.arms` | 2 arms | H4: baseline and OTA burst |

### Verdicts

| Key | Hypothesis | Experiment | Verdict | Manifest sha256 | Archives |
|---|---|---|---|---|---|
| `h.1` | Isolation: VLAN + tc reservations keep ADAS p99 near baseline under infotainment load | `exp-001` | holds | `2666fbf561ae…` | 25 archives |
| `h.2` | Real S-NSSAI slicing vs static VLAN mapping | `exp-010` | holds | `4fa24418b7a1…` | 25 archives |
| `h.3` | Virtual-ECU packaging affects zone-to-compute latency | `exp-002b` | holds | `625840eeeb0c…` | 30 archives |
| `h.4` | Co-located OTA does not compromise the ADAS slice | `exp-003` | holds | `1efebdef615f…` | 10 archives |

### H1: isolation (`exp-001`)

| Key | Value | Source |
|---|---|---|
| `h1.p99_max` | 81.9 µs | ADAS p99 at the highest load |
| `h1.p99_idle` | 89.6 µs | ADAS p99 at zero load |
| `h1.ratio` | 0.91× | p99 at max load ÷ p99 idle |
| `h1.loss` | 0.0 % | packet loss at every load level |

Supplementary repeats on a newer host kernel. The frozen campaign above is unchanged; these two
repeats confirm the verdict on kernel 7.0.0-38-generic (the frozen run used 7.0.0-28-generic).
Source: [`vxperiments/results/exp-001-repro-2026-10-13-run2/exp-001-repro-check.md`](https://github.com/vxedge/vxperiments/blob/main/results/exp-001-repro-2026-10-13-run2/exp-001-repro-check.md).

| Key | Value | Source |
|---|---|---|
| `h1r.kernel` | 7.0.0-38-generic | host kernel of both repeats |
| `h1r.sha` | `ac2496e3f58e…` | input manifest sha256 of both repeats (differs from the frozen `2666fbf561ae…` by a tolerance fix in the pinning helper and comment edits) |
| `h1r.ratio_run1` | 0.94× | repeat 1: p99 at max load ÷ p99 idle |
| `h1r.ratio_run2` | 1.00× | repeat 2: p99 at max load ÷ p99 idle |
| `h1r.within` | 12 of 15 | metric × load pairs of repeat 2 whose median lies inside repeat 1's IQR |
| `h1r.archives` | 25 archives | per repeat |

Per load level. Latency in µs with the IQR across repetitions in brackets.
Source: [`vxperiments/results/exp-001/exp-001-summary.md`](https://github.com/vxedge/vxperiments/blob/main/results/exp-001/exp-001-summary.md).

| Key | load (mbit) | p50 µs (IQR) | p95 µs (IQR) | p99 µs (IQR) | loss % |
|---|---:|---:|---:|---:|---:|
| `h1.load.0` | 0 | 49.9 (0.8) | 71.4 (6.7) | 89.6 (6.4) | 0.0 |
| `h1.load.100` | 100 | 51.1 (3.0) | 72.0 (6.1) | 87.5 (7.0) | 0.0 |
| `h1.load.250` | 250 | 49.8 (1.9) | 70.1 (3.3) | 84.5 (4.7) | 0.0 |
| `h1.load.400` | 400 | 50.6 (1.3) | 72.3 (3.1) | 85.2 (4.2) | 0.0 |
| `h1.load.600` | 600 | 51.4 (1.8) | 69.2 (2.8) | 81.9 (5.0) | 0.0 |

### H2: real slicing vs static mapping (`exp-010`)

| Key | Value | Source |
|---|---|---|
| `h2.ratio_snssai` | 0.95× | S-NSSAI p99 growth, idle → max load |
| `h2.ratio_vlan` | 0.91× | VLAN p99 growth over the same sweep (`exp-001`) |
| `h2.floor` | 317–337 µs | S-NSSAI p99 across all loads: software UPF and GTP-U |

Per load level, S-NSSAI path.
Source: [`vxperiments/results/exp-010/exp-010-summary.md`](https://github.com/vxedge/vxperiments/blob/main/results/exp-010/exp-010-summary.md).

| Key | load (mbit) | p50 µs (IQR) | p95 µs (IQR) | p99 µs (IQR) | loss % |
|---|---:|---:|---:|---:|---:|
| `h2.load.0` | 0 | 269.3 (7.3) | 305.2 (11.5) | 335.1 (14.1) | 0.0 |
| `h2.load.100` | 100 | 254.1 (3.6) | 299.5 (2.6) | 324.1 (6.9) | 0.0 |
| `h2.load.250` | 250 | 261.6 (4.0) | 313.1 (4.7) | 336.6 (12.7) | 0.0 |
| `h2.load.400` | 400 | 260.9 (1.9) | 294.7 (7.4) | 318.7 (23.0) | 0.0 |
| `h2.load.600` | 600 | 260.7 (4.7) | 293.4 (5.9) | 317.2 (10.8) | 0.0 |

### H3: virtualization choice (`exp-002b`)

| Key | Value | Source |
|---|---|---|
| `h3.transport` | −26.0 µs | Δp50, virtio MMIO → PCI (`microvm-pci` vs `microvm-mmio`) |
| `h3.transport_iqr` | 2.2 µs | IQR of that comparison |
| `h3.management` | −17.3 µs | Δp50, libvirt vs raw QEMU (`libvirt-q35` vs `q35-pci`) |
| `h3.management_iqr` | 2.0 µs | IQR of that comparison |
| `h3.vhost` | −9.5 µs | Δp50, vhost-net on vs off (`q35-vhost` vs `q35-pci`) |
| `h3.vhost_iqr` | 2.5 µs | IQR of that comparison |
| `h3.machine` | −0.3 µs | Δp50, q35 vs microvm (`q35-pci` vs `microvm-pci`): no measurable effect |

Per packaging arm. CPU and RSS are means across repetitions.
Source: [`vxperiments/results/exp-002b/exp-002b-summary.md`](https://github.com/vxedge/vxperiments/blob/main/results/exp-002b/exp-002b-summary.md).

| Key | arm | p50 µs (IQR) | p99 µs (IQR) | CPU % | RSS MB |
|---|---|---:|---:|---:|---:|
| `h3.arm.container` | container | 54.6 (1.3) | 94.4 (2.8) | 4.3 | 7.3 |
| `h3.arm.libvirt-q35` | libvirt-q35 | 70.3 (1.6) | 117.6 (2.4) | 8.2 | 166.2 |
| `h3.arm.q35-vhost` | q35-vhost | 78.1 (2.5) | 122.9 (4.4) | 9.1 | 150.6 |
| `h3.arm.q35-pci` | q35-pci | 87.6 (2.0) | 138.6 (2.6) | 11.3 | 150.9 |
| `h3.arm.microvm-pci` | microvm-pci | 87.9 (2.2) | 138.2 (3.2) | 11.4 | 150.2 |
| `h3.arm.microvm-mmio` | microvm-mmio | 113.9 (2.0) | 165.0 (6.3) | 15.0 | 146.4 |

### H4: OTA co-location (`exp-003`)

| Key | Value | Source |
|---|---|---|
| `h4.p50_baseline` | 52.2 µs | ADAS p50 without OTA |
| `h4.p50_ota` | 51.9 µs | ADAS p50 during the OTA burst |
| `h4.delta` | −0.3 µs | difference of the two |
| `h4.iqr` | 6.0 µs | baseline IQR, the one-sided threshold |
| `h4.deliveries` | 361 deliveries | signed deliveries per repetition (median) |
| `h4.failed` | 0 | failed deliveries |
| `h4.loss` | 0.0 % | packet loss in both arms |
| `h4.repro_inside` | 0 of 6 | metric/arm pairs of the same-day second campaign inside the first campaign's IQR; the verdict held |

Per arm.
Source: [`vxperiments/results/exp-003/exp-003-summary.md`](https://github.com/vxedge/vxperiments/blob/main/results/exp-003/exp-003-summary.md).

| Key | arm | p50 µs (IQR) | p95 µs (IQR) | p99 µs (IQR) | OTA deliveries ok/fail |
|---|---|---:|---:|---:|---:|
| `h4.arm.baseline` | baseline | 52.2 (6.0) | 80.7 (4.9) | 97.7 (5.6) | n/a |
| `h4.arm.ota-burst` | ota-burst | 51.9 (1.7) | 79.9 (6.3) | 93.1 (5.5) | 361 / 0 |

### Other completed experiments

| Key | Value | Source |
|---|---|---|
| `exp005.confirmed` | 20 of 20 | `exp-005`: cold-start first-packet effect, repetitions confirming it |
| `exp014.verdict` | holds | `exp-014`: star vs daisy-chained zones, hop-count effect |

## 3 · Deliveries

### Parity ledger

How close each part of the virtual vehicle is to production today, and what closes the gap
(`p3`, `p4`: the phase that does).

| Key | Part | Today | State | Closes the gap |
|---|---|---|---|---|
| `parity.network` | Network path | Linux kernel: OVS or bridge, tc HTB per slice, VXLAN, WireGuard | real | BlueField offload · p4 |
| `parity.core` | 5G core | Open5GS with real S-NSSAI PDU sessions | real | — |
| `parity.radio` | 5G radio | UERANSIM gNB and UE in software | emulated | Aerial RAN · p4 |
| `parity.zones` | Zone ECUs | Real guest OS under container, microVM or KVM | emulated | QNX SDP 8 · p3 |
| `parity.harness` | Harness | Per-link rate, delay, jitter, loss; 100BASE-T1 length and weight | emulated | TSN 802.1Qbv · p3 |
| `parity.mcu` | MCU firmware | Unmodified firmware on register-level models | planned | Renode · p3 |
| `parity.sensors` | Sensors | World streams carried as slice traffic | planned | CARLA · p3 |
| `parity.compute` | Central compute | Autoware and ROS 2 in containers | planned | DRIVE AGX · p4 |
| `parity.timing` | Timing | Userspace timestamps on a shared host | caveat | Kernel timestamps · open |

### Zones

State of each zone of the reference vehicle (`vx-vehicle-01` family, [`ARCHITECTURE.md`](ARCHITECTURE.md) §3
topology figure). `parity.zones` above is the ledger row for the zone ECUs as a class; this table is per zone.
The front zones run the ADAS slice and are planned until their QNX / RTOS guests land.

| Key | Zone | Role | State |
|---|---|---|---|
| `zone.front_left` | front-left | QNX SDP 8 / RTOS, ADAS | planned |
| `zone.front_right` | front-right | QNX SDP 8 / RTOS, ADAS | planned |
| `zone.rear_left` | rear-left | comfort, BMS, clients | emulated |
| `zone.rear_right` | rear-right | comfort, BMS, clients | emulated |
| `zone.central` | central | maps to central compute | emulated |
| `zone.gateway` | gateway | uplink into `vxgateway` | emulated |

### Frontends

The clients of the vxAPI ([`ARCHITECTURE.md`](ARCHITECTURE.md) §5.1 layers figure). Every one is a thin client:
no orchestration logic lives in a frontend.

| Key | Frontend | Role | State |
|---|---|---|---|
| `frontend.cli` | vxedge CLI | primary frontend, Rust | real |
| `frontend.mcp` | vxmcp | MCP server for AI agent tooling | building |
| `frontend.sdk` | Generated SDKs | Rust built; TypeScript and C++ planned | building |
| `frontend.web` | Web dashboard | TypeScript | planned |
| `frontend.studio` | vxedge Studio | Electron, future | planned |

### Use cases

| Key | Use case | State | Evidence |
|---|---|---|---|
| `case.isolation` | Slice isolation | measured | H1, H2 |
| `case.topology` | Zonal topology studies | measured | `exp-014`, `exp-005` |
| `case.packaging` | ECU packaging and fidelity | measured | H3 |
| `case.ota` | OTA beside safety workloads | measured | H4 |
| `case.agents` | Agent-operated experiments | building | `vxmcp`, `vxmodels` |
| `case.autonomy` | Autonomy closed loop | planned | `exp-011` |
| `case.signals` | Signals and diagnostics | building | phase 3 |
| `case.reproduce` | Reproduce anything | live | every archive |

### Agent path

How a generated experiment reaches the bench.

| Key | Step | State |
|---|---|---|
| `gate.propose` | Propose a SysML v2 model | live |
| `gate.typecheck` | Gate 1: model type check | live |
| `gate.validate` | Gate 2: `vxedge manifest validate --json` | live |
| `gate.confirm` | Multi-round-trip confirmation before a state change | building |
| `gate.run` | Idempotent `up`, streamed as a job, audited | live |
| `gate.archive` | Evidence archived with digests | live |

### vxmcp tools

| Key | Tool | Service | State |
|---|---|---|---|
| `mcp.status` | `experiment_status` | ExperimentService | live |
| `mcp.list` | zone / compute list | ZoneService · ComputeService | live |
| `mcp.watch` | job watch · events | JobService · EventService | live |
| `mcp.results` | results summary | results archive | planned |
| `mcp.mutate` | up · down · traffic up | behind confirmation | building |

### Other deliveries

| Key | Value | Source |
|---|---|---|
| `retarget.validate` | live | an experiment retargets to another vehicle by id and validates |
| `vehicle.up` | live | the `vehicle` verbs (up, down, status) on a bare vehicle: gateway and zones (verified 2026-10-13, one-zone vehicle, idempotent second `up`, clean `down`). The example vehicle boots a zone bundle you build locally, per host, so no registry login is needed; the guest answering on its probe port is not yet verified. The phase-3 gate, a full vehicle end to end, is not claimed |
| `retarget.fleet` | planned | two vehicles at once (fleet layer) |
| `paper.1` | in preparation | phase-1 dataset (H1/H3/H4) for arXiv, [`ROADMAP.md`](ROADMAP.md) |
