# Changelog

All notable changes to this repo are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/) — see `VERSIONING.md`.

## [Unreleased]

## [0.1.0] - 2026-07-13

**Phase-1 gate passed**: `ARCHITECTURE.md` §2's H1, H3, and H4 hypotheses all have
reproducible numbers (`vxperiments`' exp-001/exp-002/exp-002b/exp-003). First tagged
release across the phase-1-participating repos.

### Added
- `ARCHITECTURE.md` (16 sections) — the master spec: hypotheses H1-H4 (§2), vxAPI
  control-plane design (§5), manifest schemas for experiments and vehicles (§6), vxgateway
  network model (§7), service model incl. OTA/Uptane design (§8), virtualization/hypervisor
  fidelity ladder (§9), compute model (§10), metrics/methodology (§12), reproducibility
  rules (§13), language policy + phase roadmap (§15), worked examples (§16).
- `TASKS.md` — program-level task board: critical path, phase gates 1-4, the devops/
  release-engineering board.
- `STATUS.md` — living progress report, updated every push that moves progress.
- `PUBLICATION.md` — arXiv/venue plan, paper skeletons, partner-selection procedure, the
  publication gate.
- `GETTING-STARTED.md`, `TESTBED-SETUP.md` (host requirements tiered by phase),
  `USER-GUIDE.md` (public-facing usage doc, CLI verb state table).
- `VERSIONING.md` — the SemVer + Keep-a-Changelog convention this release itself follows.

### Notable decisions folded in along the way
- Cumulus VX deprecated in favor of a from-scratch software-defined vxgateway
  (bridge/VLAN/tc HTB, OVS variant planned) — no physical/vendor router anywhere.
- Jailhouse hypervisor evaluated and rejected (stale upstream, no OEM adoption); the
  hypervisor fidelity ladder targets Xen dom0less and QNX Hypervisor instead (phase 4).
- OTA design (§8) adopts Uptane's trust-model vocabulary (signed root/targets metadata,
  image-repo vs. director-repo split) without taking aktualizr as a dependency; **Rugix
  Ctrl** recommended over RAUC for phase-3 atomic slot updates, evaluated against
  https://rugix.org's OTA engine comparison.
- "Digital twin" avoided as project terminology in publications — reserved for phase-4
  hardware-in-the-loop; this is an "executable virtual prototype."
