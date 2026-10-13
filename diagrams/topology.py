#!/usr/bin/env python3
"""Render diagrams/zonal-topology.svg, the §3 topology diagram of ARCHITECTURE.md.

    python3 diagrams/topology.py

Standard library only. The SVG carries its own light panel, so it reads the same on GitHub, in the
rendered docs and in a slide, in either colour theme. Style: solid outline = built today (real or
emulated); dashed steel = specified, not built yet (the states in FACTS.md's parity ledger).
Update ARCHITECTURE.md §3 first, then this file.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from blueprint import *  # noqa: E402,F401,F403
import blueprint as bp  # noqa: E402

W, H = 1200, 820
bp.start(W, H, "vxedge topology: operator edge, one host with vxgateway, zones and central compute",
         "A software gateway on one host trunks VLAN slices to zone controllers (QEMU/KVM, microVM or container) and to central compute containers; the operator edge, a 5G core and an emulated backhaul sit above. Solid boxes are built today; dashed boxes are specified and not built yet.")
# operator edge
group(40, 34, 1120, 126, "OPERATOR EDGE (OPTIONAL)")
box(70, 66, 340, 76, "Open5GS 5G core", "slices · S-NSSAI", "REAL")
box(430, 66, 340, 76, "SONiC-VS", "production-NOS check", "EMULATED")
box(790, 66, 340, 76, "NOC · OTA repository · Grafana", "optional operator services")

# backhaul
line(600, 160, 600, 196)
add(f'<rect x="420" y="196" width="360" height="46" rx="5" fill="#FFFFFF" stroke="{INK}" stroke-width="1.5"/>')
text(600, 216, "emulated 5G backhaul", 13.5, 700, anchor="middle")
text(600, 233, "UERANSIM gNB / UE", 12, 400, MID, "middle")
text(776, 232, "EMULATED", 10, 600, TEAL, "end", True, "1")
line(600, 242, 600, 270)

# host
group(40, 270, 1120, 500, "HOST  (PREEMPT_RT RECOMMENDED)")
box(70, 304, 1060, 80, "vxgateway", "OVS or Linux bridge · VLAN trunk · tc queue tree per slice · VXLAN · WireGuard · FRR", "REAL")
for x in (210, 600, 990):
    line(x, 384, x, 424)
text(600, 410, "802.1Q trunk", 11.5, 600, MID, "middle", True, ".6")
add(f'<rect x="530" y="396" width="140" height="18" fill="{TINT}"/>')
text(600, 410, "802.1Q trunk", 11.5, 600, MID, "middle", True, ".6")

# zones
group(70, 424, 690, 214, "ZONES  (QEMU/KVM VIA LIBVIRT · MICROVM · CONTAINER)")
zones = [
    ("zone-front-left", "QNX SDP 8 / RTOS (ADAS)", "PLANNED", True),
    ("zone-front-right", "QNX SDP 8 / RTOS (ADAS)", "PLANNED", True),
    ("zone-rear-left", "comfort · BMS · clients", "EMULATED", False),
    ("zone-rear-right", "comfort · BMS · clients", "EMULATED", False),
    ("zone-central-hpc", "maps to central compute", "EMULATED", False),
    ("zone-gateway", "uplink into vxgateway", "EMULATED", False),
]
for i, (t, s, st, dsh) in enumerate(zones):
    box(90 + (i % 2) * 330, 456 + (i // 2) * 58, 310, 50, t, "", st, dsh)
    text(90 + (i % 2) * 330 + 16, 456 + (i // 2) * 58 + 40, s, 11.5, 400, MID)

# compute
group(790, 424, 340, 214, "CENTRAL COMPUTE  (CONTAINERS)")
comp = ["Autoware / ROS 2", "Alpamayo / AlpaSim", "DeepStream", "TensorRT"]
for i, t in enumerate(comp):
    box(810, 456 + i * 42, 300, 34, t, "", "PLANNED", True)

# planes
group(70, 654, 1060, 92, "PLANES")
box(90, 682, 330, 50, "Signal plane", "", "BUILDING")
text(106, 723, "Eclipse Kuksa databroker (COVESA VSS)", 11.5, 400, MID)
box(440, 682, 330, 50, "Comms", "", "PLANNED", True)
text(456, 723, "DDS / rmw_zenoh · uProtocol (phase 3)", 11.5, 400, MID)
box(790, 682, 320, 50, "World", "", "PLANNED", True)
text(806, 723, "CARLA (GPU) → carla-ros-bridge → Autoware", 11.5, 400, MID)


bp.legend(800)
Path(__file__).with_name("zonal-topology.svg").write_text(bp.finish())
print("wrote diagrams/zonal-topology.svg")
