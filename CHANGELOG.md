# Changelog

All notable changes to this repo are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/), see `VERSIONING.md`.

## [Unreleased]

### Added

- `scripts/check-links.py` and `scripts/check-release.py` in CI: relative links must resolve, and `CITATION.cff` must match `project.version`. `VERSIONING.md`: a release checklist.
- `FACTS.md`: `signal.plane`, the Kuksa databroker as a stage of `vehicle up`, and `vehicle.up` now names the backends each run covered and that `libvirt` has not run in a full vehicle. `ROADMAP.md` lists the signal plane's open work.
- `ARCHITECTURE.md` §5.4 and the CLI table in `USER-GUIDE.md`: `experiment up --stage signal-plane`.
- `ARCHITECTURE.md` §5.4 and `USER-GUIDE.md`: `--stage` on `vehicle` verbs, `--stage compute`, and hpc devices answering to `vxedge compute`, not `vxedge zone`.
- `ARCHITECTURE.md` §6.0.1, §5.4, §8: `signal_plane.kuksa` on a vehicle, placed on a container device, with its own stage between compute and services. It runs with `--insecure`, so slice isolation is its only protection.
- `FACTS.md` (`vehicle.up`): every-backend run on `vx-vehicle-03`.
- Phase-3 gate passed on `vx-vehicle-02`: `FACTS.md` (`phase.3`, `project.status`, `vehicle.up`), `ROADMAP.md`, `RESULTS.md` and the CLI table in `USER-GUIDE.md`.
- Zenodo DOI `10.5281/zenodo.23802762` (all versions; `0.2.3` is `10.5281/zenodo.23802763`) in `CITATION.cff`, `FACTS.md` (`project.doi`) and the README badge.
- Dataset DOI `10.5281/zenodo.23804197` (all versions; `2026-11` is `10.5281/zenodo.23810053`) for the raw result archives: `FACTS.md` (`archives.doi`), `RESULTS.md` and `GETTING-STARTED.md`.
- Second campaigns for H2 and H4 run on 2026-10-30 and published in the dataset: `FACTS.md` (`h2.repro_ratio`, `h2.repro_floor`, `h2.repro_inside`, `h4.repro_inside`) and `RESULTS.md`.
- `FACTS.md`: `repro.kernel`, the host kernel of the 2026-10-30 second campaigns.
- `ARCHITECTURE.md` §6.0.1, §6.0.2, §6.0.3, §8: a vehicle may host services, each placed on a container device with `on:`; `localhost/…` refs name images in the host's Podman store; the one-attachment-per-device limit is stated.
- `ARCHITECTURE.md` §5.4: `vehicle status` observes the host instead of reporting daemon memory, and a stage that does not exist yet is not reported as done.

- `backend: cloud-hypervisor` in `ARCHITECTURE.md`, `USER-GUIDE.md` and `TESTBED-SETUP.md`, validated on `linux-probe` only.
- `backend: wasm-capsule` and `kind: wasm` in `ARCHITECTURE.md`, `USER-GUIDE.md` and `TESTBED-SETUP.md`, validated on `reflector-capsule` only.
- `ARCHITECTURE.md` §5.2: `NosCheckService`, what is not built, the versioning policy, and the agent surface planned for `vxedge` 0.5.0. §5.4: the `nos-check` commands.
- `FACTS.md`: a Releases table with each code repository's version, and a Zone backends table.

### Fixed

- `ROADMAP.md`: tag-triggered releases exist in six repositories, not only `vxedge`.
- `GETTING-STARTED.md`, `TESTBED-SETUP.md`, `USER-GUIDE.md`: `vxedged` needs `CAP_SYS_ADMIN` as well as `CAP_NET_ADMIN` under `setcap`, because entering a named network namespace is `setns(2)`.

## [0.2.3] - 2026-10-30

### Fixed

- `CITATION.cff`: a single `license` (`CC-BY-4.0`, for the docs, results and figures; the code licence stays `Apache-2.0` in `LICENSE`). Zenodo rejected the two-licence list ("Citation metadata load failed"), so `v0.2.2` was never archived; `v0.2.3` is the first archived release.

## [0.2.2] - 2026-10-29

### Changed

- `GETTING-STARTED.md`: prebuilt `vxedge` binaries (checksums and provenance) as the first way to get the CLI and daemon; `VERSIONING.md` and `ROADMAP.md` record the `vxedge` release workflow and `v0.2.0`.
- `vxmcp` is public (all nine repositories are now): linked from `README.md` and `GETTING-STARTED.md` (clone loop and repository status).
- `FACTS.md`: vxmcp list and watch tools are live; mutating tools and the confirmation gate (`gate.confirm`, `mcp.mutate`) are building, with `svc_down` and `experiment_down` behind confirmation.
- `vxagents`, `vxtelemetry`, `vxota` and `vxperiments` are public: linked from `README.md`, `GETTING-STARTED.md` (clone loop and repository status), the org profile, `RESULTS.md` and `FACTS.md` (evidence paths now link to the frozen summaries; the `exp-001` repeat source pointed at a path that does not exist and now points at the run-2 check file).

## [0.2.1] - 2026-10-19

### Added

- `FACTS.md`: per-zone (`zone.*`) and per-frontend (`frontend.*`) states, so the website quotes them instead of typing them.
- Supplementary `exp-001` repeats on kernel 7.0.0-38 registered in `FACTS.md` (`h1r.*`) and summarised in `RESULTS.md`, with a note on why a current checkout's workspace hash matches neither run; the frozen numbers are unchanged.

### Changed

- Getting started and the user guide: the example vehicle boots a locally built, per-host zone bundle, so no registry login is needed; added the daemon-socket and `/boot/vmlinuz` host notes and a note that `sudo -E` is ignored under sudo-rs.
- Repositories that are not public yet are no longer linked (README, `RESULTS.md`, `FACTS.md`), and `GETTING-STARTED.md` clones only `docs`.
- protoc "current" is 36.x in `GETTING-STARTED.md` and `TESTBED-SETUP.md`.
- `AGENTS.md`: the org profile quotes `h1.ratio`, so it changes with it.

## [0.2.0] - 2026-10-13

### Added

- `FACTS.md`: the registry of every published number and state, read by `scripts/facts.py` (CI runs `check`); the website and READMEs quote it.
- Generated architecture diagrams (`diagrams/topology.py`, `layers.py`) replacing the ASCII figures in `ARCHITECTURE.md`, with a CI sync check.
- Open-source release preparation: `LICENSE` (Apache-2.0), `NOTICE`, rewritten `README.md`. Program board, status journal and publication plan moved out; public summaries now live in `RESULTS.md` and `ROADMAP.md`.

### Changed

- Reproduction commands in `GETTING-STARTED.md` and `USER-GUIDE.md` corrected to `experiments/exp-001-ws/scripts/run.sh`; `vehicle up` documented as live on a bare vehicle.
- Page titles cleaned up for the rendered docs.

## [0.1.0] - 2026-07-13

**Phase-1 gate passed**: `ARCHITECTURE.md` §2's H1, H3, and H4 hypotheses all have
reproducible numbers (`vxperiments`' exp-001/exp-002/exp-002b/exp-003). First tagged
release across the phase-1-participating repos.

### Added
- `ARCHITECTURE.md` (16 sections): the architecture specification: hypotheses H1-H4 (§2), vxAPI
  control-plane design (§5), manifest schemas for experiments and vehicles (§6), vxgateway
  network model (§7), service model incl. OTA/Uptane design (§8), virtualization/hypervisor
  fidelity ladder (§9), compute model (§10), metrics/methodology (§12), reproducibility
  rules (§13), language policy + phase roadmap (§15), worked examples (§16).
- `ROADMAP.md`: program-level task board: critical path, phase gates 1-4, the devops/
  release-engineering board.
- `RESULTS.md`: living progress report, updated every push that moves progress.
- `ROADMAP.md`: arXiv/venue plan, paper skeletons, partner-selection procedure, the
  publication gate.
- `GETTING-STARTED.md`, `TESTBED-SETUP.md` (host requirements tiered by phase),
  `USER-GUIDE.md` (public-facing usage doc, CLI verb state table).
- `VERSIONING.md`: the SemVer + Keep-a-Changelog convention this release itself follows.

### Notable decisions folded in along the way
- Cumulus VX deprecated in favor of a from-scratch software-defined vxgateway
  (bridge/VLAN/tc HTB, OVS variant planned), no physical/vendor router anywhere.
- Jailhouse hypervisor evaluated and rejected (stale upstream, no OEM adoption); the
  hypervisor fidelity ladder targets Xen dom0less and QNX Hypervisor instead (phase 4).
- OTA design (§8) adopts Uptane's trust-model vocabulary (signed root/targets metadata,
  image-repo vs. director-repo split) without taking aktualizr as a dependency; **Rugix
  Ctrl** recommended over RAUC for phase-3 atomic slot updates, evaluated against
  https://rugix.org's OTA engine comparison.
- "Digital twin" avoided as project terminology in publications, reserved for phase-4
  hardware-in-the-loop; this is an "executable virtual prototype."
