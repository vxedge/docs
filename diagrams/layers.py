#!/usr/bin/env python3
"""Render diagrams/vxapi-layers.svg, the §5.1 layers-and-frontends diagram of ARCHITECTURE.md.

    python3 diagrams/layers.py

Update ARCHITECTURE.md §5.1 first, then this file. Style and states: see blueprint.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import blueprint as bp  # noqa: E402
from blueprint import box, group, line, text, MID  # noqa: E402

W, H = 1200, 640
bp.start(W, H, "vxAPI layers: frontends, generated SDKs, vxAPI, vxedged and vxedge-core",
         "Thin frontends call the vxAPI through generated SDKs. On the host, vxAPI fronts the vxedged daemon (job engine, event bus, reconciler, audit log), which sits on vxedge-core (manifests, validation and the libvirt, network, container, 5G and traffic backends). Solid boxes are built today; dashed boxes are specified and not built yet.")

group(40, 30, 1120, 120, "FRONTENDS  (THIN CLIENTS: NO ORCHESTRATION LOGIC)")
fronts = [("vxedge CLI", "primary frontend · Rust", "REAL", False), ("vxmcp", "MCP server for AI agent tooling", "BUILDING", False),
          ("Web dashboard", "TypeScript", "PLANNED", True), ("vxedge Studio", "Electron, future", "PLANNED", True)]
for i, (t, s, st, d) in enumerate(fronts):
    box(70 + i * 270, 62, 250, 70, t, s, st, d)
    line(195 + i * 270, 150, 195 + i * 270, 190, dashed=d)

box(70, 190, 1060, 66, "Generated SDKs", "Rust (built) · TypeScript / connect-es and C++ (planned): generated from the IDL, never hand-written", "BUILDING")
line(600, 256, 600, 285)

group(40, 285, 1120, 290, "ONE HOST")
box(70, 318, 1060, 66, "vxAPI", "gRPC / Protobuf, package vxedge.v1 · Unix socket locally · mTLS TCP remote and gRPC-Web are planned (phase 5)", "REAL")
box(70, 398, 1060, 66, "vxedged", "async job engine · event bus · reconciler (desired vs observed) · audit log", "REAL")
box(70, 478, 1060, 80, "vxedge-core", "manifests · validation · backends", "REAL")
text(86, 545, "libvirt · rtnetlink / OVSDB · containers · Open5GS · traffic", 12, 400, MID)
line(600, 384, 600, 398)
line(600, 464, 600, 478)

bp.legend(610, "every verb is a vxAPI call; every mutating call returns a job")
Path(__file__).with_name("vxapi-layers.svg").write_text(bp.finish())
print("wrote diagrams/vxapi-layers.svg")
