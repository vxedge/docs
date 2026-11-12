# Versioning and changelogs

Each repo under `github.com/vxedge/` is an **independent git repo with its own version
history** (see the workspace contributor guide): there is no single "vxedge version." This document
is the convention every repo follows so an OEM engineer can clone one, read one file, and
know exactly what they're getting.

## Rules

1. **SemVer per repo.** Tags are `vMAJOR.MINOR.PATCH` (e.g. `v0.1.0`), following
   [Semantic Versioning 2.0.0](https://semver.org/). Pre-1.0 (all repos today): breaking
   changes bump MINOR, everything else bumps PATCH: normal SemVer-0.x practice.
2. **`CHANGELOG.md` per repo**, [Keep a Changelog](https://keepachangelog.com/) format:
   an `## [Unreleased]` section accumulates entries as work lands; cutting a tag moves
   that section under a dated version heading and opens a fresh `## [Unreleased]`.
   Categories: `Added`, `Changed`, `Fixed`, `Deprecated`, `Removed`, `Security`. Every
   `CHANGELOG.md` gets a repo-local `AGENTS.md` pointer alongside the other
   docs it already lists.
3. **No tag before the entry exists.** A version is cut by moving `[Unreleased]` content
   under a new heading in the same commit as the tag; never tag first and backfill later.
4. **`v0.1.0` cut 2026-07-13**: the phase-1 gate closed that day (H1+H3+H4 numbers in
   hand). Tagged: `docs`, `vxedge`, `vxagents`, `vxtelemetry`, `vxota`, `vxperiments` and the zone-image
   repo (since archived): the seven repos that actually delivered phase-1 content. Three other
   repos (since archived) were empty, and a tag on nothing is meaningless.
   **Tagging and visibility are decoupled**: a tag is cut the moment a milestone is real,
   independent of whether the repository is public yet.
5. **Compatibility across repos.** The only thing that couples repos is **vxAPI**
   (`vxedge/proto/vxedge/v1/*.proto`). Its wire changes are additive and stay in `vxedge.v1`
   (`ARCHITECTURE.md` §5.2). A behaviour change, such as a new refusal, is called out in the
   `vxedge` changelog and in every dependent repo's next `CHANGELOG.md` entry (`vxagents`,
   `vxtelemetry`, `vxota` all speak vxAPI-adjacent conventions even before they use the client
   SDK directly). Manifest schema changes (`ARCHITECTURE.md` §6) are the
   second coupling point, same rule.
6. **Reproducibility tags stay separate from release tags.** Experiment results already
   pin an exact state via `metadata.json`: the workspace identity, the package digest, and
   `tools`, every tool binary the daemon runs with its version, sha256 and build profile
   (`ARCHITECTURE.md` §13). That's a *finer-grained* provenance mechanism than a repo release
   tag and is not replaced by this policy: a campaign can run between tags, or on a tool built
   from a branch, and the binary's digest still says which.

## What OEM-adoption needs beyond this doc

Cutting tags and writing changelogs by hand doesn't scale past the first release. Part of the
automation exists: a tag-triggered release workflow in `vxedge`, `vxagents`, `vxota`,
`vxtelemetry`, `vxmodels` and `vxmcp` publishes each version's changelog section as its release
notes, and `vxedge`'s also builds the CLI and daemon for x86-64 and ARM64 Linux, writes
`SHA256SUMS` and attaches build provenance. There is still no `git-cliff`/Conventional-Commits
enforcement and no cross-repo compatibility-matrix generation. That work is tracked as its own devops board section (see `docs/ROADMAP.md`
"Release engineering") rather than implemented ad hoc here.

## Release checklist

For each release of any repository:

1. **Changelog:** a curated section for the version, dated the tag day, with a short summary first.
2. **Version:** the version in `Cargo.toml` or its equivalent, and in `CITATION.cff` with its
   `date-released`.
3. **Tag:** an annotated `vX.Y.Z` on the release commit, and the release workflow passing.
4. **Facts:** the repository's row in the Releases table in `FACTS.md`, in the same week. A docs
   release also updates `project.version` and `project.released`, which `scripts/check-release.py`
   checks against `CITATION.cff`.
5. **Roadmap and site:** `ROADMAP.md` if open work changed, then a website update review.

