# vxedge Docs

This repository hosts documentation, reproducibility guides, and research artifacts
for the **vxedge** project.

## Contents

- [STATUS.md](STATUS.md) — living progress report: phases, critical path, per-repo state.
- [GETTING-STARTED.md](GETTING-STARTED.md) — prerequisites, workspace setup, first experiment.
- [USER-GUIDE.md](USER-GUIDE.md) — concepts, CLI reference, workflows, results, SDV vocabulary map.
- [TESTBED-SETUP.md](TESTBED-SETUP.md) — single-machine host requirements, tiered by phase.
- [ARCHITECTURE.md](ARCHITECTURE.md) — complete system architecture, research design, and manifest schemas.
- [TASKS.md](TASKS.md) — program-level task board: phase gates and the cross-repo critical path.
- [PUBLICATION.md](PUBLICATION.md) — arXiv/venue plan, paper skeletons, partner-selection procedure.
- Reproducibility Guide (coming soon) — how to re-run published experiments step by step.
- Experiment Reports — structured results and analysis from `vxedge/vxperiments`.

## About vxedge

vxedge is a research-grade orchestration and experiment platform to evaluate **5G
network-slice mapping to zonal & central SDV E/E architectures — entirely in software**.
It provides:

- **vxgateway** — a software-defined virtual edge gateway (OVS/Linux bridge VLANs, tc queue
  trees, VXLAN, WireGuard, FRR), with real 5G slicing via Open5GS + UERANSIM.
- QEMU/KVM zonal ECUs managed via libvirt (QNX SDP 8, Zephyr/FreeRTOS, Android Automotive).
- Containerized central compute (Autoware/ROS2, NVIDIA Alpamayo/AlpaSim, DeepStream/TensorRT).
- An API-first Rust control plane: the `vxedged` daemon exposes **vxAPI** (gRPC/Protobuf);
  the `vxedge` CLI, and future Qt/QML, web, and Electron frontends, are thin clients.
- Manifest-driven everything — up to a full software-bootstrapped vehicle
  (`vxedge vehicle up`).

## Getting Started

See [GETTING-STARTED.md](GETTING-STARTED.md). Key repos:

- Control plane, vxAPI & CLI: [vxedge/vxedge](https://github.com/vxedge/vxedge)
- Loadable registry (zone/compute images): [vxedge/vxparts](https://github.com/vxedge/vxparts)
- Experiment manifests: [vxedge/vxperiments](https://github.com/vxedge/vxperiments)

## License

Documentation is licensed under **CC-BY 4.0** unless otherwise noted.
Code artifacts referenced follow their respective repo licenses (MIT/Apache-2.0).
