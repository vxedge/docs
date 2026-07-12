# VERSIONING.md — release versioning & changelogs across the vxedge workspace

Each repo under `github.com/vxedge/` is an **independent git repo with its own version
history** (see workspace `CLAUDE.md`) — there is no single "vxedge version." This document
is the convention every repo follows so an OEM engineer can clone one, read one file, and
know exactly what they're getting.

## Rules

1. **SemVer per repo.** Tags are `vMAJOR.MINOR.PATCH` (e.g. `v0.1.0`), following
   [Semantic Versioning 2.0.0](https://semver.org/). Pre-1.0 (all repos today): breaking
   changes bump MINOR, everything else bumps PATCH — normal SemVer-0.x practice.
2. **`CHANGELOG.md` per repo**, [Keep a Changelog](https://keepachangelog.com/) format:
   an `## [Unreleased]` section accumulates entries as work lands; cutting a tag moves
   that section under a dated version heading and opens a fresh `## [Unreleased]`.
   Categories: `Added`, `Changed`, `Fixed`, `Deprecated`, `Removed`, `Security`. Every
   `CHANGELOG.md` gets a repo-local `AGENTS.md`/`CLAUDE.md` pointer alongside the other
   docs it already lists.
3. **No tag before the entry exists.** A version is cut by moving `[Unreleased]` content
   under a new heading in the same commit as the tag — never tag first and backfill later.
4. **What's *not* versioned yet:** these repos are pre-phase-1-gate and **private**
   (`vxzones` is the current exception — see `PUBLICATION.md`). No `v0.1.0` tags are cut
   until the phase-1 gate closes (H1+H3+H4 numbers in hand, repos going public per the
   publication gate) — cutting a "stable-looking" tag before then would mislead anyone who
   finds the repo early. Until then, `CHANGELOG.md`'s `[Unreleased]` section *is* the
   changelog; commit history + `docs/STATUS.md` are the source of truth for "what works
   today."
5. **Compatibility across repos.** The only thing that couples repos is **vxAPI**
   (`vxedge/proto/vxedge/v1/*.proto`) — a breaking proto change is a MINOR bump (pre-1.0)
   in `vxedge` and must be called out in every dependent repo's next `CHANGELOG.md` entry
   (`vxagents`, `vxtelemetry`, `vxota` all speak vxAPI-adjacent conventions even before they
   use the client SDK directly). Manifest schema changes (`ARCHITECTURE.md` §6) are the
   second coupling point — same rule.
6. **Reproducibility tags stay separate from release tags.** Experiment results already
   pin an exact state via `metadata.json` (manifest SHA-256, and now `tool_versions` — see
   `vxperiments/scripts/run-exp-002b.sh`'s `env_metadata()` for the current shape) — that's
   a *finer-grained* provenance mechanism than a repo release tag and is not replaced by
   this policy; a future result should record `tool_versions` per repo (already 3 of 3 in
   place for the `exp-002b` runner: `vxedge`, `vxagents`, `vxtelemetry`) rather than a
   coarser release tag, since a campaign can run between tags.

## What OEM-adoption needs beyond this doc

Cutting tags and writing changelogs by hand doesn't scale past the first release, and none
of the CI automation for it exists yet (no `git-cliff`/Conventional-Commits enforcement, no
tag-triggered GitHub Release workflow, no cross-repo compatibility-matrix generation). That
work is tracked as its own devops board section — see `docs/TASKS.md` "Release engineering
& versioning (devops)" — rather than implemented ad hoc here.
