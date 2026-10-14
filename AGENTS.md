# AGENTS.md — vxedge/docs

Documentation repo for the vxedge platform. **`ARCHITECTURE.md` is the single architecture
specification** — every other repo's AGENTS.md and TASKS.md derive from it and must not contradict it.

## Contents

- `GETTING-STARTED.md` — onboarding: prerequisites (Rust 1.96+/protoc/buf), workspace
  cloning, build + smoke test, contribution entry points. Keep its versions current when
  toolchains move.
- `USER-GUIDE.md` — public-facing usage doc (concepts, per-verb CLI state, workflows,
  results, production-vocabulary mapping). Update its CLI-state table whenever a verb goes
  live or changes shape — OEM engineers read this first.
- `RESULTS.md` — measured results for H1–H4: what each hypothesis tests, the verdict, and the caveat
  that matters most. The numbers themselves are registered in `FACTS.md` and quoted here; update
  this page when a campaign is re-frozen or a caveat changes.
- `TESTBED-SETUP.md` — single-machine host requirements, tiered by phase (OS, resources,
  software versions). Anything the testbed needs that it doesn't list is a bug in it.
- `PROVISIONING.md` — self-contained design + use-case manifests + task board (Track V/Track F)
  for the node-provisioning engine (`vxedge-core`'s `ZoneBackend` seam + the `containers` module)
  and the multi-vehicle-fleet layer above it. Use-case-driven: real vehicle/baseline YAML first,
  validated, before functional requirements or implementation. Includes a reviewed-and-rejected
  verdict on building a from-scratch in-process KVM hypervisor. Extends `ARCHITECTURE.md` §9/§15,
  doesn't replace them. `docs/ROADMAP.md` carries only a one-line pointer here, not the task board.
- `FACTS.md` — **the registry of every published number and state**: measured values (copied from
  `vxperiments` frozen summaries), verdicts, phase/track states, the parity ledger, delivery states.
  The website builds every number it shows from this file; `RESULTS.md` and the GitHub READMEs
  quote it. Machine-read by `scripts/facts.py` (`json` for the website, `check` for docs).
- `ARCHITECTURE.md` — the architecture specification (16 sections). Key anchors: §2 hypotheses H1–H4,
  §5 vxAPI/control plane, §6 manifest schemas (experiment + vehicle), §7 vxgateway network
  model, §9 virtualization (libvirt/QEMU/QNX), §15 language policy + 4-phase roadmap,
  §16 worked examples.
- `ROADMAP.md` — the public phase status and open work: phase gates and the cross-repo critical
  path. Per-repo `TASKS.md` files hold the detailed work items.
- `VERSIONING.md` — SemVer + `CHANGELOG.md` (Keep a Changelog) conventions every repo
  follows; when tags get cut (not before the phase-1 gate) and what stays out of scope for
  hand-maintained docs vs. the devops board (`ROADMAP.md`).
- `ACRONYMS.md` — glossary of every acronym used across these docs, grouped by field
  (5G/RAN, SDN, SDV, virtualization, compute/AI, vxAPI, standards, OTA, methodology).
  Hand-maintained; update it alongside `ARCHITECTURE.md` when a new acronym lands.
- `diagrams/` — editable draw.io architecture diagrams (`sdv-ee-architecture.drawio`: hardware
  and software perspectives of the zonal E/E architecture). Derived from `ARCHITECTURE.md`, which
  stays authoritative — update the spec first, then the diagram. See `diagrams/README.md` for
  conventions and the extension palette.
- Papers, slides, reproducibility guide land here as they are written.

## Rules

- Any change to manifest schemas, vxAPI surface, CLI command shape, or the phase roadmap MUST
  be made in `ARCHITECTURE.md` first, then propagated to affected repos' AGENTS.md/TASKS.md.
- When a phase gate is reached, update `FACTS.md`, `ROADMAP.md` and `RESULTS.md` here in the same change set
  as the per-repo TASKS.md updates.
- **Numbers live in `FACTS.md`.** A result, phase state or delivery state changes there first, in
  the same change as the summary or state that moved; then `python3 scripts/facts.py check` (CI
  runs it). Never type a measured number into another page — quote the registered value.
- The org profile README (`vxedge/.github`, `profile/README.md`) quotes `h1.ratio` in its results table and is not
  covered by `scripts/facts.py check`: when that fact changes, update the README in the same change set.
- Prose style: state fidelity caveats honestly (shared-host gateway, QNX-as-guest inversion);
  reproducibility claims must name the mechanism (digests, versioned manifests, idempotent CLI).

## Quality bars

Two contributor guides: **testbed-quality** and **experiment-methodology**
— the quality bars every repo change and every reported number are judged against.
