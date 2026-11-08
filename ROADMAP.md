# Roadmap

Where vxedge stands, phase by phase. This page lists what is done and shipped. The measured results
are in [`RESULTS.md`](RESULTS.md), and acronyms are defined in [`ACRONYMS.md`](ACRONYMS.md).

References elsewhere in this repository to numbered work items (`#14`, `#28`, …) and dated state
snapshots point to the maintainers' internal working board.

## Phase status

The phase, track and delivery states below are registered in [`FACTS.md`](FACTS.md); change them
there first.

| Phase | Gate | Status |
|---|---|---|
| **1**: slicing core, API-first | Reproducible H1/H3/H4 numbers | **Gate passed.** All three hold and were independently reproduced. See [`RESULTS.md`](RESULTS.md) |
| **2**: real slices & workloads | H2: S-NSSAI vs static VLAN | **Gate passed.** H2 holds and was reproduced. The OVS data plane, per-link harness impairments, the SONiC-VS NOS twin and the full Open5GS/UERANSIM lifecycle are delivered |
| **3**: production SDV alignment | `vxedge vehicle up` boots a full vehicle end to end | **Gate passed** on [`vx-vehicle-02`](https://github.com/vxedge/vxperiments/tree/main/results/phase-3-gate-2026-11-01): three zones on two backends, central compute and a service placed on a slice, with probe guests. Phase-3 content is still in progress |

Cross-cutting tracks:

- **M (SysML v2 model governance, `vxmodels`):** M0–M3 are closed.
- **C (containerization):** complete through C3.2. The 5G stack and platform services run in containers,
  and the measured path stays on the host.
- **P (`vxparts` unification):** complete. The earlier zone and compute repositories are merged into
  the unified OCI/ORAS loadable registry.

## What has shipped

The latest release of each repository is in [`FACTS.md`](FACTS.md) under Releases, and the deliveries
since phase 3 opened are under Other deliveries. Each repository's `CHANGELOG.md` lists what changed in
every release.

## Contributing

Open an issue on the repository the work belongs to. For anything that spans repositories, open it in
[`vxedge/docs`](https://github.com/vxedge/docs/issues).
