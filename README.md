# vxedge Docs

This repository hosts documentation, reproducibility guides, and research artifacts
for the **vxedge** project.

## Contents

- [ARCHITECTURE.md](ARCHITECTURE.md) — complete system architecture, research design, and manifest schema.
- Reproducibility Guide (coming soon) — how to re-run published experiments step by step.
- Experiment Reports — structured results and analysis from `vxedge/vxperiments`.

## About vxedge

vxedge is a research-grade orchestration and experiment platform to evaluate **5G network-slice mapping to zonal & central SDV E/E architectures**.  
It provides:
- MikroTik CCR2004 edge gateway slicing.
- QEMU/KVM for zonal ECUs.
- Containerized central compute (Autoware, inference).
- Rust CLI (`vxedge`) to orchestrate experiments, services, and telemetry.

## Getting Started

- Core CLI & orchestrator: [vxedge/vxedge](https://github.com/vxedge/vxedge)
- Zone definitions & artifacts: [vxedge/vxzones](https://github.com/vxedge/vxzones)
- Experiment manifests: [vxedge/vxperiments](https://github.com/vxedge/vxperiments)

## License

Documentation is licensed under **CC-BY 4.0** unless otherwise noted.
Code artifacts referenced follow their respective repo licenses (MIT/Apache-2.0).
