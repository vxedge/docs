# Changelog

All notable changes to this repo are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/), see `VERSIONING.md`.

## [Unreleased]

### Added

- `ARCHITECTURE.md` §6.0.3 and §7 specify the TSN variant of the gateway, which is not implemented yet:
  - `network.shaping` (`kind: taprio`) puts an IEEE 802.1Qbv gate schedule on the uplink in place of
    the HTB tree, with one class per slice, classified by VLAN;
  - `network.time_sync` (`kind: gptp`) makes the gateway the 802.1AS grandmaster for the listed
    container devices, whose offset and peer delay vxedged's exporter serves as samples.
  The §7 TSN bullet points to them and states that under `taprio` the uplink has no line rate.

### Changed

- `FACTS.md` Releases: vxedge 0.26.0, vxtelemetry 0.8.0 and vxmcp 0.5.0 (one archive format and one
  descriptor, X-30). `USER-GUIDE.md` says a legacy `<id>.vxp` descriptor is refused, and
  `GETTING-STARTED.md` §4 says to run the `repro` campaign from outside the home directory.
- Reproduce instructions follow vxperiments' package-only layout (X9.5): `GETTING-STARTED.md` §4
  and `USER-GUIDE.md` §b run exp-001 from its package with `vxedge campaign plan|start --profile
  quick|repro`, in place of the removed `scripts/run.sh` and `notebooks/analyze_exp001.py`, and the
  runner's staleness-gate troubleshooting entry is gone. `RESULTS.md` says how to reproduce a
  result (the packages and `vxedge campaign`) and re-judge the published archives
  (`scripts/verdict-parity.sh --fetch`, with exp-010's H2 checked by `notebooks/analyze_exp010.py`),
  and links the retired analysis notebooks at the vxperiments `v0.2.1` tag. No FACTS key or value
  changes.
- `ARCHITECTURE.md` §6.0, §6.0.3, §6.0.7, §6.0.8, §11 and §13: one archive format and one
  descriptor (decision X-30). `vxarchive/2` is the only archive vxtelemetry writes and the only one
  vxedge and vxtelemetry read; a `vxarchive/1` archive is refused with the current format named. A
  legacy `<name>.vxp` descriptor is refused with the steps to migrate, and the archive's workspace
  copy is `package/`.
- `FACTS.md` `archives.doi`: the latest archive version is 2026-11-v2 (10.5281/zenodo.24192950), the
  frozen campaigns in `vxarchive/2` plus the exp-003 release rerun of 2026-11-13.
- `ARCHITECTURE.md` §6.0.3: a check tool step's `samples` read its output lines as series on
  `checks/<step>`, which metrics and criteria aggregate like a probe's, and what `Plan` refuses
  in them (X9.15).
- `FACTS.md` zone backends: `backend.qemu_mcu`, live, validated on the FreeRTOS and Zephyr `probe-mps2` firmware
  (vxparts `zone/{freertos,zephyr}/firmware/probe-mps2` 0.1.0, public; `vx-vehicle-04` gate 10/10 on vxedge 0.17.0).
- `ARCHITECTURE.md` §9: `backend: qemu-mcu`, microcontroller firmware on QEMU's `mps2-an385`: the firmware
  bundle, the semihosting command line, the NIC's MAC, and TCG-only results. §6.0 lists the new backend value.
- `ARCHITECTURE.md` §6.0.3: a parameter can bind a storyboard parameter
  (`scenario.parameters.<name>`), and `pkg vendor` carries a scenario's road and storyboard.
- `ARCHITECTURE.md` §6.0.3: the descriptor's `requires.simulator`, how a host has a simulator
  (`HostService.Capabilities`), and `ERROR_REASON_SIMULATOR_UNAVAILABLE`.
- `ARCHITECTURE.md` §6.0 and §6.0.3: `kind: road` and `kind: scenario` point at OpenDRIVE and
  OpenSCENARIO files, and an experiment names its scenario with `scenario:` (`world:` still reads
  as it). Covers what `Plan` checks, `ERROR_REASON_SCENARIO_INVALID`, and the typed scenario in
  `PackageService.Inspect`.
- `ARCHITECTURE.md` §6.0.8: an offline layout also carries the infra image every container node
  runs, with its Linux platforms only.
- `ARCHITECTURE.md` §6.0.3: the example writes exp-001's loss bound as a member of `all`, as its
  notebook judges it, and the `guards` text names where guards are used instead.
- `ARCHITECTURE.md` §6.0.3: a `vxarchive/1` archive's failed scrapes are noted on a value, not
  counted as a gap. `USER-GUIDE.md`: `vxedge results verdict` and `compare`, offline.
- `ARCHITECTURE.md` §5 and §6.0.3, `USER-GUIDE.md`: `ResultService.Compare`. It sets a campaign
  against a reference, per metric at each point against the reference's median and IQR, and per
  criterion. Adds `vxedge campaign compare`.
- `ARCHITECTURE.md` §5 and §6.0.3, `USER-GUIDE.md`: `ResultService.Verdict`. It judges an
  experiment's criteria over a campaign's archives, typed per criterion. The verdict recorded at
  a campaign's end goes into `campaign.json`, `CampaignStatus.verdict` and `verdict.json`. Adds
  `vxedge campaign verdict`.
- `ARCHITECTURE.md` §6.0.3: how a criterion reads results. A metric names its `series` and
  `labels`, or the `ratio` of two metrics, and gives each trial one value: the series' last sample
  inside the trial's measure phase (decision X-24). Aggregates run across the selected trials and
  add `median`, `iqr`, `sum` and `stddev`. Operands combine as `ratio`, `diff`, `max` and `min`
  and take an `offset`. A tolerance can be an operand, `outside` joins the ops, and `guards`
  make a criterion inconclusive unless they pass (decision X-25).
- `ARCHITECTURE.md` §5 and §6.0.3: `ResultService` (`List`, `Get`, `Fetch`): results by digest,
  described from their own metadata, and `ERROR_REASON_RESULT_UNKNOWN`.
- `ARCHITECTURE.md` §9: what `realtime.pinned_cpus` does on each backend, and the devices `Plan` and `up`
  refuse to pin (vxedge#127, #129).
- `ARCHITECTURE.md` §5 and §6.0.3: `CampaignService.Start`, `Get`, `List` and `Watch`. These cover
  a trial's five phases, archives that carry the trial's identity, `campaign.json`, resuming by
  `request_id`, cancelling between trials, one campaign at a time, and
  `ERROR_REASON_CAMPAIGN_UNKNOWN`.
- `ARCHITECTURE.md` §5 and §6.0.3: `CampaignService.Plan` and how a campaign becomes trials. Every
  sweep point and every arm is a trial, an arm equal to a sweep point names it (decision X-22),
  each trial is provisioned on its own (X-23), and each point's bound document is checked.
- `ARCHITECTURE.md` §5 and §6.0.8: `PackageService` (`Inspect`, `List`, `Pull`, `Import`), the
  package cache through vxAPI, `ManifestRef.package` by digest and `ERROR_REASON_PACKAGE_UNKNOWN`.
- `ARCHITECTURE.md` §12: a measurement's samples include `vxprobe_rtt_distribution_seconds`, a
  cumulative histogram whose differences between samples give latency over time.
- `USER-GUIDE.md`: `vxedge traffic up` runs a profile inside its source node once the node's zone is
  up, instead of refusing it.
- `ARCHITECTURE.md` §5, §6.0.3 and §12: an experiment's `measurements` block (`rtt-probe`, by node
  id), run by `MeasurementService` (`Start`, `Stop`, `Status`; `vxedge measure`) inside each end's
  network namespace, with the far side of the uplink for `to: internet`. Samples reach the ingest
  through the daemon's exporter as `measurements/<id>`. `Plan` checks each measurement under
  `ERROR_REASON_MEASUREMENT_INVALID`, and a VM or attached end is refused.
- Guest-OS examples are generic and name only guest images that have shipped: `ARCHITECTURE.md` §1, §3, §6.0.2,
  §9, §14 and §15, `FACTS.md` (parity ledger and zones), `ACRONYMS.md`, `USER-GUIDE.md`, `TESTBED-SETUP.md`,
  `NOTICE` and both diagrams. Planned guest images and hypervisor targets are no longer listed.
- `ARCHITECTURE.md` §5 and §11: `LogService.Follow` streams the log lines the ingest reads from
  each entity's files (serial consoles, hypervisor logs, service and traffic output) as `log`
  records, resumable by `seq` and filtered by entity and stream; archive v2 keeps them as
  `logs/<entity>.jsonl.zst`; `Plan` and `entities.json` name each entity's log files.
- `ARCHITECTURE.md` §5 and §11: `TelemetryService.StreamRecords` streams the ingest's sample,
  gap and phase records live, in archive order, resumable by `seq`; `StreamMetrics` is built and
  carries its samples by entity.
- `ARCHITECTURE.md` §12: host-side measurements. The daemon's exporter serves per-node CPU and
  memory and per-slice queue counters, each series labelled with its entity, and is scraped as a
  `host` target.
- `ARCHITECTURE.md` §12: entity paths, the one name every telemetry record uses for what it is
  about, derived from model ids; scrape targets bound to entities by address; `Plan` lists them and
  `collect` archives them as `entities.json`.
- `ARCHITECTURE.md` §11: telemetry records (`sample`, `gap`, `phase`), named by entity, the same
  live and archived; and archive v2 (`vxarchive/2`), a zip with an index of every member's sha256
  and zstd-compressed records, readable by Python's standard library from 3.14.
- `ARCHITECTURE.md` §6.0.7 and `USER-GUIDE.md`: `pkg vendor` also copies the local part folders the
  documents reference whose files the source's git checkout tracks, such as an attach adapter;
  untracked files are build outputs and stay behind.
- `ARCHITECTURE.md` §9, `backend: attach`: the commands run through `sh -c`, and each names its interpreter
  (`sh start.sh`), since a package keeps no file modes.
- `ARCHITECTURE.md` §9: a `qemu-microvm` bundle sizes its guest (`cpus`, `memory_mb`), and an aarch64 bundle can ask
  for the CPU's virtualization extensions (`"virtualization": true`: EL2, GICv3).
- `FACTS.md`: vxedge 0.11.0, vxmcp 0.2.5.
- `ARCHITECTURE.md` §6.0.3: typed experiment intent. `hypothesis`; `parameters` with type, unit, default, bounds and `binds` by id path (no
  templating); `metrics`; structured `criteria` (operands, `lt`/`le`/`gt`/`ge`/`within`,
  `all`/`any`, `min_samples`) that evaluate to `pass`, `fail` or `inconclusive`, never rounding
  `inconclusive` to a pass; and `campaign` (arms, sweep, repetitions, warmup, duration, profiles),
  which replaces `method` where declared. `Plan` reports bad parameters and criteria as
  `ERROR_REASON_PARAMETER_INVALID` and `ERROR_REASON_CRITERION_INVALID` before any trial.
- `ARCHITECTURE.md` §6.0.8, distribution and trust: `pkg push`
  as one OCI artifact whose single layer is the packed file (`application/vnd.vxedge.vxp.v1.tar`,
  so the layer digest is the package digest); `pkg pull` by digest only; a signature covers the
  package digest, and verification is recorded beside the package, keyed by digest, since a
  folder cannot hold its own signature; GitHub attestations for published packages and Sigstore
  key-pair bundles for air-gapped labs; a host trust policy that refuses unverified packages with
  `ERROR_REASON_SIGNATURE_INVALID`; and `pack --offline` with parts in an OCI layout beside the
  package.
- Direction stays internal: `ROADMAP.md` is now phase status and what has shipped, with no open-work
  or publication list. `ARCHITECTURE.md` drops the market positioning in §14, the scope of later
  phases in §15, the planned remote and cloud-hosted modes in §5.3, the phase-4 hardware rungs,
  and unreleased frontends. `GETTING-STARTED.md`, `USER-GUIDE.md`, `README.md` and `AGENTS.md`
  no longer point to per-repo `TASKS.md` files, which moved to the maintainers' internal board.
- `USER-GUIDE.md`: the `pkg` row adds `pkg vendor` and `vendor --check` (vxedge 0.8.0), and the
  `experiment up` and `vehicle up` rows say that a `vxp/1` package whose lock does not match is
  refused with `ERROR_REASON_LOCK_MISMATCH` and that `--unlocked` runs it anyway (0.7.0).
  `ARCHITECTURE.md` §6.0.7 and §13 name the releases that shipped lock enforcement, the package
  digest, the kernel record and vendoring, and the lock's `parts` include a published config part
  such as an OTA artifact store (vxedge#100, not yet released).
- `ARCHITECTURE.md` §6.0.7: `pkg vendor` (decision X-5), ahead of the release that ships it: it copies
  another folder's documents into a package, never its scripts or build outputs; the lock records
  each copy's `source` (`<owner>/<repo>/<path>`) and digest; `--replace`, re-vendoring, the lock
  written even when the package no longer builds, the local references it lists, and `--check` for
  local edits and source drift. A private source is never vendored into a public package.
- `TESTBED-SETUP.md` Tier M: the SysML v2 standard library pin is SysML-v2-Release 2026-09.1, matching `vxmodels` CI.
- CI uses `actions/checkout@v7` instead of v4.
- Rust 1.99.1 is the documented toolchain, matching vxedge 0.6.1: `TESTBED-SETUP.md` Tier 0, `GETTING-STARTED.md` prerequisites and `AGENTS.md`. `vxedge doctor` now compares versions against the pin and enforces the protoc 3.21 and buf 1.71 floors listed in Tier 0.
- `ARCHITECTURE.md` §6.0, §6.0.7 and §13: what vxedge 0.6.0 shipped is the `vxp/1` descriptor; the
  lock, the packed form and the `pkg` verbs are on `main` and unreleased, and no release records
  the package digest yet. The lock records parts and images as the documents pin them, offline,
  with no media type (decision X-10). The packed form's ustar header is spelled out field by
  field, including the name/prefix split and empty device numbers, so a second implementation
  writes the same bytes. `USER-GUIDE.md`: `experiment new` scaffolds a locked `vxp/1` package,
  and the `pkg` verbs are listed.
- `ARCHITECTURE.md` §6.0.7 and §13 name what a run records, ahead of the release that records it:
  `unlocked` on the three `Up` requests and on `WorkspacePlanRequest`; `Run.package_locked` beside `Run.package`, `false` only
  for `up --unlocked`; `up` refuses a `vxp/1` package that cannot be packed; and every run records
  its kernel release and whether it is PREEMPT_RT (`kernel_release`, `kernel_preempt_rt`,
  `Run.kernel`, `kernel` in `metadata.json`), so `kernel.preempt_rt: preferred` results say which
  kernel they came from.
- `ARCHITECTURE.md` §6.0, §6.0.7 and `USER-GUIDE.md`: the lock, the packed form and the `pkg` verbs
  shipped in vxedge 0.6.1; `up` checking the lock and recording the digest are on `main`.

### Added

- `ARCHITECTURE.md` §6.0.3 and §6.0.7: the package format `vxp/1`, which ships in vxedge 0.6.0. The
  descriptor becomes `vxp.yaml`, with `schema`, a `namespace/name` id, SemVer `version`, `requires`
  including a vxedge range, and `x-` keys. `vxp.lock` records each input's digest and every
  published reference, and `up` refuses a package that disagrees with it. The packed form is
  `<name>-<version>.vxp`, an uncompressed, deterministic tar of exactly the identity's inputs,
  and its SHA-256 is the package digest. Legacy `<name>.vxp` descriptors load through vxedge 0.7.x.
- `ARCHITECTURE.md` §13: a run records the package digest beside the workspace identity.
- `ARCHITECTURE.md` §6.0.3 (planned): a `schema` discriminator for the `.vxp` descriptor, with
  `x-` extension keys.
- `ARCHITECTURE.md` §13: the workspace identity rule `vxws/2`, with its default excludes and
  `.vxpignore`, and every recorded identity naming its algorithm. `vxws/1` stays verifiable.

### Changed

- `ARCHITECTURE.md` §13: the archive records the package digest and lock state under the `package`
  object `metadata.json` already writes (`id`, `version`), not as new top-level keys.
- `ARCHITECTURE.md` §6.0.3: the `.vxp` `id` and `entry` checks are in place, no longer planned.
- `ARCHITECTURE.md` §13: the results archive carries the full workspace and verifies itself
  (`vxtelemetry verify`).
- `vxmcp` 0.2.2 in the `FACTS.md` releases table.
- `vxedge` 0.5.3 and `vxtelemetry` 0.3.0 in the `FACTS.md` releases table.
- `vxedge` 0.5.2, `vxmcp` 0.2.1 and `vxtelemetry` 0.2.1 in the `FACTS.md` releases table.
- `USER-GUIDE.md`: `telemetry` verbs live, `--stage compute`, the traffic endpoint refusal, and a row
  for the agent-surface RPCs reached through `vxmcp`. `ROADMAP.md`: the agent surface and signal
  plane released; CLI verbs for the agent surface are the open vxAPI work. `ARCHITECTURE.md` §5.1:
  every service `vxmcp` wraps.
- `vxedge` 0.5.1 in the `FACTS.md` releases table.
- `vxedge` 0.5.0 and `vxmcp` 0.2.0: `FACTS.md` releases, `api.agents` (the agent sequence through
  `vxmcp`, verified live), `frontend.mcp`, `mcp.mutate` and `gate.confirm` live, and the signal plane
  released. `ARCHITECTURE.md` §5.2: the agent surface is built, and its services are in the table.
- `scripts/check-links.py` and `scripts/check-release.py` in CI: relative links must resolve, and `CITATION.cff` must match `project.version`. `VERSIONING.md`: a release checklist.
- `ACRONYMS.md`: VMM, Cloud Hypervisor, Wasm and WASI. `GETTING-STARTED.md`: every zone backend. `USER-GUIDE.md`: `vxedge ota status`. `ROADMAP.md`: the vxAPI agent surface for 0.5.0.
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

- `ARCHITECTURE.md` §5.4 and §16: `vxedge telemetry` verbs are wired (`up`/`down` through
  `SvcService`, `collect` through `TelemetryService.Collect`). §16's example is now a workspace
  `main.yaml`, replacing the §6.1 shape and its `:latest` image tags.
- `ARCHITECTURE.md` §13: results go to `results.artifact_dir`, not `results_prefix`. Archive
  metadata records the `vxtelemetry` version, not a CLI version. The archive carries the
  workspace's documents only, so it is not yet re-runnable on its own; the full workspace is
  planned.
- `ARCHITECTURE.md` §6.0.2 and §6.0.3: `vxedge manifest bom` is planned, not built. The daemon's
  preflight, not `experiment validate`, checks `.vxp` `requires`.
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
- Jailhouse hypervisor evaluated and rejected (stale upstream, no OEM adoption).
- OTA design (§8) adopts Uptane's trust-model vocabulary (signed root/targets metadata,
  image-repo vs. director-repo split) without taking aktualizr as a dependency; **Rugix
  Ctrl** recommended over RAUC for phase-3 atomic slot updates, evaluated against
  https://rugix.org's OTA engine comparison.
- "Digital twin" avoided as project terminology in publications, reserved for phase-4
  hardware-in-the-loop; this is an "executable virtual prototype."
