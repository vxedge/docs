# Changelog

All notable changes to this repo are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/), see `VERSIONING.md`.

## [Unreleased]

### Changed

- `GETTING-STARTED.md`: prebuilt `vxedge` binaries (checksums and provenance) as the first way to get the CLI and daemon; `VERSIONING.md` and `ROADMAP.md` record the `vxedge` release workflow and `v0.2.0`.
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
