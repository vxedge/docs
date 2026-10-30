# vxedge documentation

Specification, results and user documentation for vxedge.

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey.svg)](LICENSE-DOCS)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23802762.svg)](https://doi.org/10.5281/zenodo.23802762)
[![Release](https://img.shields.io/github/v/tag/vxedge/docs?label=release)](https://github.com/vxedge/docs/tags)

vxedge is an open, all-software testbed for mapping 5G network slices onto zonal and central software-defined-vehicle (SDV) E/E architectures on a single machine. Every published number ships with the manifest and image digests that produced it.

**Pre-release (0.x):** the manifest schema and vxAPI may change between minor versions; published results are frozen.

| Document | What |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | The architecture specification: research goals and hypotheses, topology, vxAPI, manifest schemas, network/service/virtualization models, methodology, phased roadmap |
| [RESULTS.md](RESULTS.md) | Measured results for H1–H4, with numbers, verdicts and caveats |
| [FACTS.md](FACTS.md) | **The registry of every published number and state.** The website and every README quote it |
| [ROADMAP.md](ROADMAP.md) | Phase status and open work |
| [GETTING-STARTED.md](GETTING-STARTED.md) | From zero to a measured experiment |
| [USER-GUIDE.md](USER-GUIDE.md) | Concepts, CLI reference, workflows, SDV vocabulary map |
| [TESTBED-SETUP.md](TESTBED-SETUP.md) | Host requirements, tiered by experiment class |
| [VERSIONING.md](VERSIONING.md) | SemVer and changelog conventions across repos |
| [ACRONYMS.md](ACRONYMS.md) | Glossary |
| [diagrams/](diagrams/) | E/E architecture diagrams (draw.io) |

## Repositories

All repositories below are public.

| Repo | What |
|---|---|
| [vxedge](https://github.com/vxedge/vxedge) | The control plane (`vxedged`), vxAPI, CLI, and vxgateway |
| [vxagents](https://github.com/vxedge/vxagents) | Measurement agents: probes and traffic generation |
| [vxtelemetry](https://github.com/vxedge/vxtelemetry) | Telemetry ingestion and results archiving |
| [vxota](https://github.com/vxedge/vxota) | OTA server and signing (the H4 workload) |
| [vxperiments](https://github.com/vxedge/vxperiments) | Experiments, analysis, frozen results |
| [vxparts](https://github.com/vxedge/vxparts) | OCI/ORAS registry of every loadable the platform boots |
| [vxmodels](https://github.com/vxedge/vxmodels) | SysML v2 models and the manifest renderer |
| [vxmcp](https://github.com/vxedge/vxmcp) | MCP server over vxAPI |

## Links

- Site: <https://vxedge.dev>
- Contributing: [CONTRIBUTING](https://github.com/vxedge/.github/blob/main/CONTRIBUTING.md) · Security: [SECURITY](https://github.com/vxedge/.github/blob/main/SECURITY.md)
- License: Apache-2.0 ([`LICENSE`](LICENSE)) for code; CC BY 4.0 ([`LICENSE-DOCS`](LICENSE-DOCS)) for docs, results, figures and models
