# AGENTS.md: vxedge/docs

Documentation repo for the vxedge platform. **`ARCHITECTURE.md` is the single architecture
specification**, every other repo's AGENTS.md derives from it and must not contradict it.

## Contents

- `GETTING-STARTED.md`: onboarding: prerequisites (Rust 1.99+/protoc/buf), workspace
  cloning, build + smoke test, contribution entry points. Keep its versions current when
  toolchains move.
- `USER-GUIDE.md`: public-facing usage doc (concepts, per-verb CLI state, workflows,
  results, production-vocabulary mapping). Update its CLI-state table whenever a verb goes
  live or changes shape, OEM engineers read this first.
- `RESULTS.md`: measured results for H1–H4: what each hypothesis tests, the verdict, and the caveat
  that matters most. The numbers themselves are registered in `FACTS.md` and quoted here; update
  this page when a campaign is re-frozen or a caveat changes.
- `TESTBED-SETUP.md`: single-machine host requirements, tiered by phase (OS, resources,
  software versions). Anything the testbed needs that it doesn't list is a bug in it.
- `ARCHITECTURE.md`: the architecture specification (16 sections). Key anchors: §2 hypotheses H1–H4,
  §5 vxAPI/control plane, §6 manifest schemas (experiment + vehicle), §7 vxgateway network
  model, §9 virtualization (libvirt/QEMU/KVM), §15 language policy + phases,
  §16 worked examples.
- `ROADMAP.md`: the public phase status: phase gates passed and what has shipped. Open work,
  plans and future phases are tracked on the maintainers' internal board, never here.
- `VERSIONING.md`: SemVer + `CHANGELOG.md` (Keep a Changelog) conventions every repo
  follows; when tags get cut (not before the phase-1 gate) and what stays out of scope for
  hand-maintained docs.
- `ACRONYMS.md`: glossary of every acronym used across these docs, grouped by field
  (5G/RAN, SDN, SDV, virtualization, compute/AI, vxAPI, standards, OTA, methodology).
  Hand-maintained; update it alongside `ARCHITECTURE.md` when a new acronym lands.
- `diagrams/`: editable draw.io architecture diagrams (`sdv-ee-architecture.drawio`: hardware
  and software perspectives of the zonal E/E architecture). Derived from `ARCHITECTURE.md`, which
  stays authoritative, update the spec first, then the diagram. See `diagrams/README.md` for
  conventions and the extension palette.
- Papers, slides, reproducibility guide land here as they are written.

## Rules

- Any change to manifest schemas, vxAPI surface or CLI command shape MUST be made in
  `ARCHITECTURE.md` first, then propagated to affected repos' AGENTS.md.
- When a phase gate is reached, update `FACTS.md`, `ROADMAP.md` and `RESULTS.md` here in one change set.
- **Direction stays internal.** Public docs say what exists and what has shipped. Roadmaps, open work
  lists, future phases, unreleased product names, publication plans and market or partner
  positioning live in the private board, not in any public repo.
- **Numbers live in `FACTS.md`.** A result, phase state or delivery state changes there first, in
  the same change as the summary or state that moved; then `python3 scripts/facts.py check` (CI
  runs it). Never type a measured number into another page, quote the registered value.
- The org profile README (`vxedge/.github`, `profile/README.md`) quotes `h1.ratio` in its results table and is not
  covered by `scripts/facts.py check`: when that fact changes, update the README in the same change set.
- Prose style: state fidelity caveats plainly (shared-host gateway, RTOS-as-guest inversion);
  reproducibility claims must name the mechanism (digests, versioned manifests, idempotent CLI).

## Quality bars

Two contributor guides: **testbed-quality** and **experiment-methodology**,
the quality bars every repo change and every reported number are judged against.
