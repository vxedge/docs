# AGENTS.md — vxedge/docs

Master documentation repo for the vxedge platform. **`ARCHITECTURE.md` is the single master
spec** — every other repo's AGENTS.md and TASKS.md derive from it and must not contradict it.

## Contents

- `GETTING-STARTED.md` — onboarding: prerequisites (Rust 1.96+/protoc/buf), workspace
  cloning, build + smoke test, contribution entry points. Keep its versions current when
  toolchains move.
- `USER-GUIDE.md` — public-facing usage doc (concepts, per-verb CLI state, workflows,
  results, production-vocabulary mapping). Update its CLI-state table whenever a verb goes
  live or changes shape — OEM engineers read this first.
- `STATUS.md` — living progress report (phases %, H1 critical path, per-repo state,
  environment gaps). **Update it in the same change set as any push that moves progress.**
- `TESTBED-SETUP.md` — single-machine host requirements, tiered by phase (OS, resources,
  software versions). Anything the testbed needs that it doesn't list is a bug in it.
- `ARCHITECTURE.md` — the master spec (16 sections). Key anchors: §2 hypotheses H1–H4,
  §5 vxAPI/control plane, §6 manifest schemas (experiment + vehicle), §7 vxgateway network
  model, §9 virtualization (libvirt/QEMU/QNX), §15 language policy + 4-phase roadmap,
  §16 worked examples.
- `TASKS.md` — the program-level task board: phase gates and cross-repo critical path.
  Per-repo TASKS.md files hold the detailed work items.
- `PUBLICATION.md` — arXiv/venue plan, paper skeletons, partner-selection procedure, and the
  publication gate (never preprint before repos are public and results rerun reproducibly).
- Papers, slides, reproducibility guide land here as they are written.

## Rules

- Any change to manifest schemas, vxAPI surface, CLI command shape, or the phase roadmap MUST
  be made in `ARCHITECTURE.md` first, then propagated to affected repos' AGENTS.md/TASKS.md and
  the workspace-root CLAUDE.md.
- When a phase gate is reached, update `TASKS.md` here in the same change set as the per-repo
  TASKS.md updates.
- Prose style: state fidelity caveats honestly (shared-host gateway, QNX-as-guest inversion);
  reproducibility claims must name the mechanism (digests, versioned manifests, idempotent CLI).

## Project skills

AI/contributor skills in `.claude/skills/`: **testbed-quality** and **experiment-methodology**
— the quality bars every repo change and every reported number are judged against.
