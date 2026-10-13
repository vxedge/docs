#!/usr/bin/env python3
"""Render diagrams/zonal-topology.svg, the §3 topology diagram of ARCHITECTURE.md.

    python3 diagrams/topology.py

Standard library only. The SVG carries its own light panel, so it reads the same on GitHub, in the
rendered docs and in a slide, in either colour theme. Style: solid outline = built today (real or
emulated); dashed steel = specified, not built yet (the states in FACTS.md's parity ledger).
Update ARCHITECTURE.md §3 first, then this file.
"""

from html import escape
from pathlib import Path

W, H = 1200, 820
INK, MID, TEAL, STEEL, RULE, TINT, PANEL = "#1E2023", "#5A5E66", "#0E7C6B", "#5A5E66", "#C9C9C4", "#F3F3F0", "#FAFAF8"
out: list[str] = []


def add(s: str) -> None:
    out.append(s)


def text(x, y, s, size=13, weight=400, fill=INK, anchor="start", mono=False, spacing=None):
    fam = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" if mono else "ui-sans-serif,system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{ls}>{escape(s)}</text>')


def box(x, y, w, h, title, sub="", state="", dashed=False, fill="#FFFFFF", rx=5):
    stroke = STEEL if dashed else INK
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>')
    ty = y + (24 if sub else (22 if h >= 50 else h / 2 + 5))
    text(x + 16, ty, title, 14.5, 700)
    if sub:
        text(x + 16, y + 45, sub, 12, 400, MID)
    if state:
        col = TEAL if state in ("REAL", "EMULATED") else MID
        text(x + w - 14, y + 20, state, 10, 600, col, "end", True, "1")


def group(x, y, w, h, label):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{TINT}" stroke="{RULE}" stroke-width="1.2"/>')
    text(x + 18, y + 24, label, 11.5, 600, MID, mono=True, spacing=".6")


def line(x1, y1, x2, y2, dashed=False):
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    add(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{INK if not dashed else STEEL}" stroke-width="1.5" fill="none"{dash}/>')


add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">')
add('<title id="t">vxedge topology: operator edge, one host with vxgateway, zones and central compute</title>')
add('<desc id="d">A software gateway on one host trunks VLAN slices to zone controllers (QEMU/KVM, microVM or container) and to central compute containers; the operator edge, a 5G core and an emulated backhaul sit above. Solid boxes are built today; dashed boxes are specified and not built yet.</desc>')
add(f'<rect width="{W}" height="{H}" rx="10" fill="{PANEL}" stroke="{RULE}"/>')

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

# legend
add(f'<rect x="40" y="790" width="22" height="12" rx="2" fill="#FFFFFF" stroke="{INK}" stroke-width="1.5"/>')
text(70, 800, "built today (real, emulated or building)", 11.5, 400, MID)
add(f'<rect x="360" y="790" width="22" height="12" rx="2" fill="#FFFFFF" stroke="{STEEL}" stroke-width="1.5" stroke-dasharray="4 3"/>')
text(390, 800, "specified, not built yet", 11.5, 400, MID)
text(1160, 800, "states follow the parity ledger in FACTS.md", 11.5, 400, MID, "end")
add("</svg>")
Path(__file__).with_name("zonal-topology.svg").write_text("\n".join(out) + "\n")
print("wrote diagrams/zonal-topology.svg")
