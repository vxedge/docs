# Roadmap

Where vxedge stands, phase by phase. The full phase definitions are in
[`ARCHITECTURE.md`](ARCHITECTURE.md) §15, and the measured results are in [`RESULTS.md`](RESULTS.md).
Per-repo work items live in each repository's own `TASKS.md`. Acronyms are defined in
[`ACRONYMS.md`](ACRONYMS.md).

References elsewhere in this repository to numbered program-board items (`#14`, `#28`, …) and
dated state snapshots point to the maintainers' internal working board. This page is the public summary of
that board.

## Phase status

The phase, track and delivery states below are registered in [`FACTS.md`](FACTS.md); change them
there first.

| Phase | Gate | Status |
|---|---|---|
| **1**: slicing core, API-first | Reproducible H1/H3/H4 numbers | **Gate passed.** All three hold and were independently reproduced. See [`RESULTS.md`](RESULTS.md) |
| **2**: real slices & workloads | H2: S-NSSAI vs static VLAN | **Gate passed.** H2 holds and was reproduced. OVS data plane, per-link harness impairments, SONiC-VS NOS twin, and the full Open5GS/UERANSIM lifecycle are delivered |
| **3**: production SDV alignment | `vxedge vehicle up` boots a full vehicle end to end | **Gate passed** on [`vx-vehicle-02`](https://github.com/vxedge/vxperiments/tree/main/results/phase-3-gate-2026-11-01): three zones on two backends, central compute and a service placed on a slice, with probe guests. The phase's content is still landing: see the list below |
| **4**: hardware in the loop (optional) | Jetson / DRIVE / BlueField / V2X radio | Specified, not started |
| **5**: remote / multi-user deployment | none yet | Backlog: mTLS + OIDC for vxAPI's TCP transport, role model, actor-aware audit |

Cross-cutting tracks:

- **M (SysML v2 model governance, `vxmodels`):** M0–M3 are closed. M4 (scenario models, fidelity ledger) is
  waiting on a GPU host for CARLA.
- **C (containerization):** complete through C3.2. The 5G stack and platform services run in containers,
  and the measured path stays on the host.
- **P (`vxparts` unification):** complete. The earlier zone and compute repositories are merged into
  the unified OCI/ORAS loadable registry.

## Open work

**Phase 2 carry-overs**

- `exp-004`, `exp-012` and `exp-020` are each blocked on a real prerequisite: a compute-timing agent, the TSN
  gateway variant, and CARLA respectively.
- `vxagents`: DSCP marking, clock-sync probing, and PCAP helpers.
- SO_TIMESTAMPING (kernel timestamps) in place of userspace-monotonic probing.

**Phase 3**

- Signal plane: the Kuksa databroker stage is released in `vxedge` 0.5.0. Its feeders, CAN mapping and plant model are open.
- `exp-011`: real ADAS traffic, CARLA → ROS 2 → Autoware closed loop. It needs a Tier 2 GPU host
  ([`TESTBED-SETUP.md`](TESTBED-SETUP.md)).
- QNX SDP 8 and Android Automotive zones, and an embedded Qt/QML IVI loadable.
- vxAPI: CLI verbs for the agent surface (runs, planning, capabilities, job list and cancel, traffic
  status). The surface itself is released in `vxedge` 0.5.0 and reached through `vxmcp` 0.2.0.
- On-demand reproduction pipeline for published experiments.

**Release engineering**

- A tag-triggered GitHub Release per repository: done for `vxedge`, `vxagents`, `vxota`, `vxtelemetry`, `vxmodels` and `vxmcp`. `vxparts` publishes by manual dispatch. `vxperiments` and `docs` are tagged but have no release workflow.
- Release binaries for `vxedge` and `vxedged` on x86-64 and ARM64 Linux: done as of `v0.2.0`.
- GHCR images with recorded digests.
- A cross-repository compatibility matrix.

**Publication**

- Paper #1 (the phase-1 dataset: H1/H3/H4) is in preparation for arXiv.
- A citable, archived reproducibility bundle (Zenodo DOI) will accompany it.

## Contributing to the roadmap

Open an issue on the repository the work belongs to. For anything that spans repositories, open it in
[`vxedge/docs`](https://github.com/vxedge/docs/issues).
