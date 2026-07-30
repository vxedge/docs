# docs/diagrams

Editable architecture diagrams for the vxedge platform. Source format is native draw.io
(`.drawio` = mxGraphModel XML) — diffable in git, editable in draw.io Desktop or
[app.diagrams.net](https://app.diagrams.net).

| File | Contents |
|---|---|
| `sdv-ee-architecture.drawio` | Next-generation SDV zonal E/E architecture, two pages: **1 — Hardware (physical E/E)** and **2 — Software (logical stack)** |

Both pages derive from `../ARCHITECTURE.md`. **That file stays the master spec** — if a diagram
and `ARCHITECTURE.md` disagree, the diagram is wrong. Change the spec first, then the diagram.

## The two perspectives

**Page 1 — Hardware.** Blocks are physical/virtualised hardware entities, connectors are physical
link types. A single `VEHICLE` container holds all six zones (`front-left`, `front-right`,
`rear-left`, `rear-right`, `central-hpc`, `gateway`), each with its zone controller (ZCU),
zone-local bus segment, ECUs, sensors and actuators. Zones attach to a shared Ethernet backbone
(802.1Q trunk, one VLAN per slice); body zones additionally ride a CAN-FD/LIN backbone. Off-board
elements (5G core, RAN, OTA repo, Prometheus, SONiC-VS twin) sit outside the vehicle boundary.

Front zones are laid out mirrored (ZCU at the bottom, nearest the backbone) so every ZCU→backbone
connector is a short vertical drop — front and rear zones read symmetrically about the spine.

**Page 2 — Software.** The same six zones read as a layered stack: applications → middleware
(signal/comms plane) → guest OS → vxedge zone/compute backend, over a shared vxgateway data-plane
band and host-platform band. Columns align 1:1 with the hardware zones, so a block on page 1 has a
stack on page 2 at the same horizontal position. The right-hand column is the API-first control
plane (CLI/frontends → vxAPI → `vxedged` → `vxedge-core`, fed by manifests and, upstream of those,
the SysML v2 model).

## Conventions

**Connector semantics map to `links[].type`** (`ARCHITECTURE.md` §6.1). Ethernet backbone,
zone access link, CAN-FD, LIN, GMSL2 serdes, actuator drive, 5G Uu and internal fabric each have a
fixed stroke colour/weight/dash — the legend panel on page 1 is the authority, and it is built from
the same style strings the diagram uses.

**Zone containers carry manifest metadata.** Each zone is an `<object>` with data attributes —
`vxid`, `role`, `kind`, `backend`, `slice`, `spec` — visible in draw.io via *right-click → Edit
Data*. This keeps the picture traceable to the manifests rather than drifting into decoration.
Populate them on any zone you add.

**Fill colour encodes domain**, not vendor: blue = ADAS/safety, green = body/comfort/energy,
amber = connectivity, purple = central compute.

**The diagram is descriptive; the manifest is the contract.** Nothing exists in the testbed
because it is drawn here. A block added to the diagram must land in a vehicle or experiment
manifest (`ARCHITECTURE.md` §6) before it is real.

## Extending

Page 1's legend panel doubles as an extension palette:

1. Copy the dashed **ZONE SLOT** group into the `VEHICLE` container.
2. *Right-click → Edit Data* and set `vxid` / `role` / `backend` / `slice`.
3. Fill in ZCU, sensors, ECUs, actuators from the block palette above it.
4. Connect the ZCU to the backbone with the *Ethernet backbone* connector style.
5. Add the matching column on page 2 (headers at the top; each band takes one box per column).

Everything is a plain container/child hierarchy with absolute geometry — no layout engine to fight.
Zone containers are `container=1`, so dragging a zone moves its contents with it.

## Page geometry and printing

Both pages are **2420 × 1711 units — exactly √2 : 1, A-series landscape**, with the content inset
by a uniform 100-unit margin (content box 2220 × 1511 at 100,100 → 2320,1611). One page is one
sheet: *File ▸ Print ▸ Fit to page*, landscape, fills the paper with no tiling and nothing clipped.

Legibility is the real constraint, not fit. Scaled onto each sheet size, the 12-unit body text
lands at:

| Sheet | Body text | Verdict |
|---|---|---|
| A4 landscape | ~4 pt | fits perfectly, but reference-only — expect to lean in |
| **A3 landscape** | ~6 pt | **recommended for handouts and design reviews** |
| A2 landscape | ~8 pt | comfortable; the right size for a wall or poster session |

Screen and PDF are unaffected — zoom is free there. If you need a genuinely readable A4, print a
region rather than shrinking the whole page: select a zone (or the legend) and use *File ▸ Print ▸
Selection Only*.

If you change the layout, keep the page ratio at √2 — set *File ▸ Page Setup* to a custom size
whose width ÷ height is 1.4142, or the fit-to-page print stops being a clean single sheet.

## Editing and export

```bash
drawio docs/diagrams/sdv-ee-architecture.drawio          # open in the desktop app

# export a page to PNG/SVG/PDF with the diagram XML embedded (stays editable)
drawio -x -f png -e -b 10 -p 1 -o hardware.drawio.png docs/diagrams/sdv-ee-architecture.drawio
drawio -x -f svg -e -b 10 -p 2 -o software.drawio.svg docs/diagrams/sdv-ee-architecture.drawio

# print-ready PDF, both pages, page geometry preserved
drawio -x -f pdf -e -a -o sdv-ee-architecture.pdf docs/diagrams/sdv-ee-architecture.drawio
```

SVG is the best choice for papers and slides — it scales without the type-size penalty above.

Exported images are deliberately **not** committed — they go stale silently, and the `.drawio`
renders on GitHub. Generate them on demand.

### One gotcha worth knowing

draw.io typesets **backtick-delimited text as AsciiMath**. A label reading `` `links[]` `` renders
as *l ∈ ks[]* (`in` → ∈). Do not use backticks for code spans in labels — write `links[]` plain.
Setting `math="0"` on the model does not suppress it in CLI export.
