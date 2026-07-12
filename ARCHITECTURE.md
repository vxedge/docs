# vxedge Research Plan and ARCHITECTURE

Project: vxedge
Purpose: Research-grade orchestration and experiment platform to evaluate 5G network-slice mapping
to zonal & central SDV E/E architectures — **entirely in software**. A software-defined virtual
gateway (`vxgateway`, built on the Linux networking stack) replaces physical edge gear; KVM/QEMU
VMs managed through libvirt provide zonal ECUs (QNX, Zephyr, FreeRTOS, Android Automotive);
containerized central compute runs Autoware/ROS2 and NVIDIA AD workloads (Alpamayo, DeepStream,
TensorRT); and a Rust control plane (`vxedged`) orchestrates manifest-driven vehicles,
experiments, services, and telemetry — exposing a versioned gRPC/Protobuf API (**vxAPI**)
consumed by thin frontends: the `vxedge` CLI today; Qt/QML, web/TypeScript, and Electron
frontends next; locally over a Unix socket or cloud-hosted behind mTLS.

---

## Table of contents

1. Executive summary
2. Research goals & hypotheses
3. High-level architecture (topology & components)
4. Repositories & single-source rules
5. vxedge control plane & API (vxedged, vxAPI, frontends, CLI)
6. Manifests (experiment & vehicle schemas)
7. Network model — vxgateway (SDN slicing)
8. Service model (OTA, telemetry, extensibility)
9. Virtualization & zone provisioning (libvirt, QEMU/KVM, QNX, RTOS, containers)
10. Compute model (Autoware/ROS2, Alpamayo, inference, OTA hosting)
11. Edge agents & telemetry collection (vxagents / vxtelemetry)
12. Experiment methodology, metrics, and analysis plan
13. Reproducibility, CI/CD, artifact publication
14. Safety, security, licensing, and industrialization notes
15. Implementation policy & phased roadmap
16. Appendix: example manifests, gateway snippets, run sequence

---

## 1 — Executive summary

vxedge is a reproducible, modular framework to define and run SDV experiments that combine zone
virtual ECUs, central compute, a **software-defined virtual edge gateway** with 5G-style slicing,
and services (OTA, telemetry). Manifests declare the whole system — up to and including a complete
**software-bootstrapped vehicle** (`vxedge vehicle up`). The Rust CLI orchestrates the lifecycle
using a simple `up|down` model across all subsystems.

The platform is designed to:

- generate publishable results (latency/jitter percentiles, OTA reliability, isolation metrics);
- stay production-representative: the same middleware (Eclipse SDV: Kuksa/VSS, Zenoh, uProtocol),
  network stack (OVS/tc/FRR/WireGuard, SONiC as production NOS twin), and AD workloads
  (Autoware, NVIDIA Alpamayo) used or converged on by OEMs;
- run on a single NVIDIA GPU host (scaling to several), with an explicit later path onto NVIDIA
  hardware (Jetson AGX, DRIVE AGX / DRIVE OS, BlueField/DOCA offload);
- be **API-first**: all orchestration lives behind vxAPI (gRPC/Protobuf) served by the `vxedged`
  daemon. The CLI, GUIs (Qt/QML, Electron), and web dashboards are interchangeable thin clients,
  and the same API hosts locally or in the cloud (controller mode federating multiple hosts).

No physical router is required: the edge-gateway role is fully absorbed by `vxgateway`.

---

## 2 — Research goals & hypotheses

**Primary goal:** Quantify whether a **software-defined virtual gateway** — built from the
production Linux SDN stack (OVS/Linux bridge, tc queue trees, VXLAN, WireGuard, FRR) and running
co-located with virtualized zonal ECUs and central compute — can provide slice isolation and
deterministic performance for SDV workloads mapped to logical 5G slices.

**Hypotheses to test:**

- **H1 (isolation):** Per-slice VLAN/VXLAN mapping with hierarchical tc queue-tree reservations in
  vxgateway can keep p95/p99 latency for ADAS (URLLC-like) traffic near baseline under heavy
  infotainment load.
- **H2 (real slicing vs. static mapping):** True 5G slicing (S-NSSAI PDU sessions via
  Open5GS + UERANSIM) provides measurably different — and under contention, stronger — isolation
  than static VLAN-to-slice mapping.
- **H3 (virtualization choice):** Virtual ECU packaging (full VM via libvirt vs. container vs.
  microVM via raw QEMU/QMP or cloud-hypervisor) measurably affects latency/jitter observable at
  zone-to-compute flows.
- **H4 (service co-location):** OTA service co-located in central compute (deployed on demand)
  does not compromise ADAS slice SLAs when slices and queue reservations are correctly configured.

**Deliverables:** Reproducible experiment artifacts, datasets, scripts, and publishable analysis —
plus a reference "vehicle-in-software" composition demonstrating the full stack end to end.

**Framing note:** unlike physical edge gear, the virtual gateway shares the host with the
workloads it isolates. Determinism controls (PREEMPT_RT kernel, `isolcpus`, CPU pinning,
hugepages) are part of the method, and their effect is itself reported.

---

## 3 — High-level architecture (topology & components)

```
                       Cloud / Operator Edge (optional)
        +--------------------------------------------------------------+
        |  Open5GS 5G core (slices/S-NSSAI) · NOC · OTA repo · Grafana |
        |  SONiC-VS "production NOS twin" · (NVIDIA Air sandbox)       |
        +-------------------------------+------------------------------+
                                        |
                            Internet / emulated 5G backhaul
                            (UERANSIM gNB/UE · optional Sionna
                             channel realism via NVIDIA 6G program)
                                        |
        +----------------- NVIDIA GPU host(s) — PREEMPT_RT ------------+
        |                                                              |
        |  +--------------------------------------------------------+  |
        |  | vxgateway (virtual edge gateway — VM or netns set)     |  |
        |  |  OVS/bridge VLAN trunk · tc queue trees per slice ·    |  |
        |  |  VXLAN inter-host · WireGuard · FRR (BGP)              |  |
        |  +----+---------------------+---------------------+------+  |
        |       | 802.1q trunk        |                     |          |
        |  Zones (QEMU/KVM via libvirt):                Compute        |
        |   - zone-front-left   QNX SDP 8 / RTOS (ADAS)  (containers): |
        |   - zone-front-right  QNX SDP 8 / RTOS (ADAS)   - Autoware/  |
        |   - zone-rear-left    comfort, BMS, clients       ROS2       |
        |   - zone-rear-right   comfort, BMS, clients     - Alpamayo/  |
        |   - zone-central-hpc  (maps to compute below)     AlpaSim    |
        |   - zone-gateway      uplink into vxgateway     - DeepStream |
        |                                                 - TensorRT   |
        |  Signal plane: Eclipse Kuksa databroker (COVESA VSS)         |
        |  Comms: DDS / rmw_zenoh · uProtocol (phase 3)                |
        |  World: CARLA server (GPU) → carla-ros-bridge → Autoware     |
        +--------------------------------------------------------------+
```

**Key components:**

- **vxedged (Rust)** — control-plane daemon: orchestration + provisioning core behind **vxAPI**
  (gRPC/Protobuf). See §5.
- **vxedge CLI (Rust)** — thin vxAPI client; the primary frontend.
- **vxgateway** — the software-defined edge gateway: Linux-native data plane (OVS or Linux
  bridge, tc, VXLAN, WireGuard, FRR), provisioned declaratively by the CLI. See §7.
- **vxzones** — authoritative zone manifests, VM images (QNX SDP 8, Zephyr, FreeRTOS, AAOS),
  RTOS builds.
- **vxcompute** — central compute manifests, Autoware/ROS2 images, Alpamayo/AlpaSim, inference.
- **vxota** — OTA server & signing tooling (artifact store).
- **vxagents** — performant Rust agents for measurements and metrics.
- **vxtelemetry** — telemetry ingestion & Prometheus export (VSS-aligned; see §11).
- **vxperiments** — manifest-driven experiments, vehicle manifests, and results.

---

## 4 — Repositories & single-source rules

Canonical repos (under vxedge org):

- `vxedge/vxedge` — Rust workspace: `vxedge-core` (domain lib), `vxedged` (daemon, vxAPI),
  `vxedge-cli` (thin client), `proto/` (vxAPI Protobuf IDL — the source for all generated SDKs:
  Rust/tonic, C++/Qt GRPC, TypeScript/connect-es), plus **gateway provisioning templates**
  (netlink/OVS/nftables/tc, libvirt domain XML templates).
- `vxedge/vxzones` — zone definitions, VM images, RTOS/QNX artifacts, publish scripts.
- `vxedge/vxcompute` — central compute, Autoware, Alpamayo, inference images, compute manifests.
- `vxedge/vxota` — OTA server, signing, manifests.
- `vxedge/vxagents` — Rust agents, metrics exporters.
- `vxedge/vxtelemetry` — telemetry ingestion and exporters.
- `vxedge/vxperiments` — experiment manifests, **vehicle manifests**, notebooks, results.
- `vxedge/docs` — papers, slides, reproducibility guide.

**Single-source rules:**

- A zone/compute's manifest is authoritative for its images and node IDs.
- Services declared under `services` in an experiment manifest are the authoritative runtime
  descriptors for that experiment (image + config). The code lives in vxota or vxtelemetry as
  appropriate.
- A **vehicle manifest** is the authoritative composition of zones + compute + network + services
  for a software-bootstrapped vehicle; experiments reference a vehicle rather than restating it.
- CLI uses manifests as sole input; state stored in ephemeral runtime directories and vxedge logs.
- Exactly two cross-language interfaces exist: **manifests** (YAML content) and **vxAPI**
  (Protobuf IDL under `vxedge/vxedge/proto/`, authoritative; client SDKs are generated, never
  hand-written). No bespoke ad-hoc RPC.

---

## 5 — vxedge control plane & API (vxedged, vxAPI, frontends, CLI)

**Principle (API-first):** the split every production SDV toolchain converges on — Tesla-style
fleet tooling, NVIDIA DriveWorks tools, AUTOSAR Adaptive development tooling — is a headless core
behind a strongly-typed IDL, with every UI a disposable thin client. vxedge adopts it outright:
**no orchestration logic lives in any frontend.**

### 5.1 Layers & frontends

```
 frontends:  vxedge CLI │ Qt/QML HMI │ web dashboard (TS) │ Electron "vxedge Studio" (future)
                 │            │              │                      │
                 └──────┬─────┴──────┬───────┴─────────┬────────────┘
                        ▼ generated SDKs (Rust · C++/Qt GRPC · TypeScript/connect-es)
                ┌───────────────────────────────────────────────┐
                │ vxAPI — gRPC/Protobuf, package vxedge.v1      │
                │ (UDS local · mTLS TCP remote · gRPC-Web)      │
                ├───────────────────────────────────────────────┤
                │ vxedged — daemon: async job engine, event bus,│
                │ reconciler (desired vs observed), audit log   │
                ├───────────────────────────────────────────────┤
                │ vxedge-core — manifests, validation, backends:│
                │ libvirt · rtnetlink/OVSDB · containers ·      │
                │ Open5GS · traffic                             │
                └───────────────────────────────────────────────┘
```

- **vxedge-core** (Rust lib): pure domain logic; no user-facing I/O.
- **vxedged** (Rust daemon, tonic + tonic-web): hosts vxAPI. Every mutating verb is an **async
  job** with server-streamed progress; the reconciler compares desired (manifest) vs observed
  state — that is what makes `up|down` idempotent.
- **Frontends** (all thin clients of the same API):
  - **`vxedge` CLI** (Rust) — unchanged UX; local Unix socket by default, `--endpoint` for
    remote; auto-spawns an ephemeral local daemon for single-host lab use.
  - **Qt/QML operator HMI** (C++; Qt ≥ 6.8 speaks gRPC natively into QML via Qt GRPC) — live
    slice dashboard styled as an instrument cluster; doubles as the in-vehicle HMI demo.
  - **Web dashboard / Electron** (TypeScript; connect-es-generated SDK over gRPC-Web) — cloud
    console first, "vxedge Studio" desktop app later.
  - **vxedge-tray** (Rust, StatusNotifierItem/SNI system tray) — at-a-glance gateway/experiment
    state + quick up/down from the desktop; pairs with a **systemd unit for vxedged**
    (socket-activated where possible). Same thin-client rule: 1:1 vxAPI calls, no logic.

### 5.2 API surface (vxAPI, `proto/vxedge/v1/`)

| Service | RPCs (declarative, manifest-in) |
|---|---|
| `GatewayService` | `Apply`, `Up`, `Down`, `Status` |
| `ZoneService` / `ComputeService` | `Apply`, `Up`, `Down`, `List`, `Remove`, `PushImage` (client-streaming) |
| `SvcService` (ota, telemetry) | `Up`, `Down`, `Status` |
| `VehicleService` | `Up`, `Down`, `Status` |
| `ExperimentService` | `Up`, `Down`, `Status` |
| `TrafficService` | `Up`, `Down` |
| `JobService` | `Get`, `Watch` (server-streamed progress; every mutating RPC returns a `Job`) |
| `EventService` | `Subscribe` (state transitions, audit events) |
| `TelemetryService` | `StreamMetrics` (live), `Collect` (archive job) |

Rules: mutating RPCs carry manifest documents (or references to them) — the API introduces **no
second source of truth** beside manifests; daemon state stays in ephemeral runtime dirs + logs.
The proto package is versioned (`vxedge.v1`): additive changes stay in v1, breaking changes mean
`vxedge.v2`.

**Why gRPC/Protobuf** (not SOME/IP, not bare REST): SOME/IP–`ara::com` is the *in-vehicle service
plane* — the wrong tool for an orchestration/tooling plane; bare REST lacks first-class streaming
and codegen rigor. One Protobuf IDL generates every SDK, gRPC-Web covers browsers and Electron,
and Protobuf is what Eclipse uProtocol already speaks — schema reuse when the signal plane lands
in phase 3. An optional REST/OpenAPI façade can be added later by transcoding, without touching
the core.

### 5.3 Transport, security, deployment modes

- **Local (default):** Unix domain socket, peer-credential auth.
- **Remote:** TCP + mTLS, OIDC bearer tokens; roles viewer/operator/admin; every mutating call is
  audit-logged.
- **Cloud-hosted:** `vxedged --controller` runs anywhere and federates one or more site daemons
  (one per GPU host, reached over WireGuard + mTLS) behind the **same vxAPI**. Frontends never
  know whether they talk to a single host or a fleet controller, and never touch hypervisors
  directly.

### 5.4 CLI — commands & semantics

**Location:** `vxedge/vxedge` (Rust workspace: `vxedge-core`, `vxedged`, `vxedge-cli`, `proto/`).
**Binaries:** `vxedge` (thin client), `vxedged` (daemon).
**Global behavior:** all lifecycle commands follow `up|down` semantics. Where staging is required,
`up` performs staging + start; `down` stops + cleanup. All operations are idempotent.

**Commands (canonical)**

```bash
# Daemon / control plane
vxedged serve [--listen unix:///run/vxedge.sock | https://0.0.0.0:8443] [--controller]

# Client endpoint (applies to every command below; defaults to the local Unix socket)
vxedge [--endpoint <url>] ...

# Gateway (vxgateway — virtual edge gateway)
vxedge up|down|status

# Zones
vxedge zone up --vxid <vxid>
vxedge zone down --vxid <vxid>
vxedge zone list
vxedge zone add --manifest vxzones/...yaml
vxedge zone rm --vxid <vxid>
vxedge zone image push --vxid <vxid> --from <path> --registry <url?>

# Compute
vxedge compute up --vxid <vxid>
vxedge compute down --vxid <vxid>
vxedge compute add --manifest vxcompute/...yaml
vxedge compute rm --vxid <vxid>
vxedge compute image push --vxid <vxid> --from <path> --registry <url?>

# Services (OTA, telemetry)
vxedge ota up --experiment <exp-manifest.yaml>
vxedge ota down --experiment <exp-manifest.yaml>
vxedge telemetry up --experiment <exp-manifest.yaml>
vxedge telemetry down --experiment <exp-manifest.yaml>
vxedge telemetry collect --manifest vxperiments/exp-001.yaml --out results/exp-001.zip

# Vehicle (software-bootstrapped SDV: gateway + zones + compute + signal plane + services)
vxedge vehicle up --manifest vxperiments/vehicles/<vehicle>.yaml
vxedge vehicle down --manifest vxperiments/vehicles/<vehicle>.yaml
vxedge vehicle status --manifest vxperiments/vehicles/<vehicle>.yaml

# Experiments (manifest-driven; may reference a vehicle manifest)
vxedge experiment up --manifest vxperiments/exp-001.yaml
vxedge experiment down --manifest vxperiments/exp-001.yaml

# Traffic generation
vxedge traffic up --manifest ...
```

`vxedge vehicle up` is sugar for the ordered composition: gateway up → zones up → compute up →
signal plane up (Kuksa, phase 3) → services up. `vehicle down` tears down in reverse.

Every CLI verb is a 1:1 wrapper over a vxAPI RPC — anything the CLI can do, every other frontend
(QML, web, Electron, scripts against the TS/C++ SDKs) can do identically.

---

## 6 — Manifests — final schemas (YAML)

### 6.1 Experiment manifest

```yaml
experiment:
  id: <string>
  name: <string>
  description: <string>
  duration_s: <int>
  results_prefix: <path>
  vehicle: <path to vehicle manifest>   # optional; composes zones/compute/network from it

network:
  topology: mesh|star|custom
  defaults:
    bandwidth: <bps>
    latency: <ms>
  slices:                               # slice definitions consumed by vxgateway (and 5G core)
    - id: <slice-id>                    # e.g. adas, infotainment, ota, telemetry
      mode: vlan | s-nssai              # static VLAN mapping (H1) or real 5G slice (H2)
      vlan: <vlan id>                   # when mode: vlan
      s_nssai: { sst: <int>, sd: <hex> }  # when mode: s-nssai (Open5GS/UERANSIM)
      qos:
        min_rate_mbps: <int>            # guaranteed reservation (tc queue tree)
        max_rate_mbps: <int>
        priority: <int>

services:
  ota:
    id: ota-01
    type: ota
    image:
      url: <registry or local path>
      kind: container | vm
    config: <service-specific config object>
  telemetry:
    id: telemetry-01
    type: telemetry
    image:
      url: <registry or local path>
      kind: container | vm
    config: <service-specific config object>

compute:
  - id: vxcompute-<role>-<seq>
    name: <human-readable>
    image:
      url: <image url>
      kind: container | vm
    resources:
      cpu: <cores>
      memory: <GB>
      gpu: <none | passthrough | mig-slice>   # GPU pass-through / TensorRT-optimized containers
    services:
      - <service-id>

zones:
  - id: vxzone-<zone>-<seq>
    name: <human-readable>
    role: front-left | front-right | rear-left | rear-right | central-hpc | gateway
    nodes:
      - id: node-<type>-<seq>
        type: ecu | sensor | gateway | infotainment | telemetry-client | rsu   # rsu = V2X roadside unit (phase 3)
        function: <text>
        image:
          url: <image url>
          kind: vm | container | rtimage
        backend: libvirt | qemu-microvm | container | renode   # default: libvirt for vm/rtimage;
                                                               # renode = MCU-class, register-level I/O (phase 3)
        realtime:                                     # optional determinism controls
          pinned_cpus: [<host cpu ids>]
          hugepages: <bool>
        network:
          - iface: <name>
            vlan: <vlan id>
            slice: <slice-id>            # binds the iface to a slice from network.slices
            ip: <cidr>                   # optional node address (e.g. 10.101.0.2/24); zone
                                         # backends configure it at `zone up`
        slice_policy:                    # optional, URSP-style UE-side slice selection (phase 2):
          - match: <traffic class | dscp | app id>   #   per-traffic-class routing onto concurrent
            slice: <slice-id>                        #   PDU sessions when slices use mode: s-nssai
        io:                              # optional, emulator-level device models (phase 3)
          devices: [virtio-gpio, i2c, spi, can]      # QEMU devices; register-level via backend: renode
        sensors:                         # optional, restbus simulation (phase 3)
          - id: <sensor id>
            dbc: <path to .dbc>          # CAN frame definitions
            vss: <VSS signal path>       # Kuksa mapping
        actuators:
          - id: <actuator id>
            dbc: <path to .dbc>
            vss: <VSS signal path>
            plant: first-order | fmu:<path>          # response model, run by the vxplant agent
                                                     # (FMI/FMU co-simulation: phase 4)
    services:
      - <service-id>

links:
  - from: <vxid or vxid:nodeid>
    to: <vxid or vxid:nodeid>
    type: vlan_trunk | vxlan | wireguard | direct | can
    properties:
      - { vlan: <id> }                       # vlan_trunk
      - { bus: <vcan name>, bitrate: <bps> } # can — SocketCAN/vcan; CAN-over-Ethernet via cannelloni
      - { impairments: { rate_mbps: <int>, latency_ms: <float>,   # per-link PHY realism via netem
                         jitter_ms: <float>, loss_pct: <float> } } # e.g. 100/1000BASE-T1 (phase 2)

traffic_profiles:
  <profile-id>:
    source: <vxid:nodeid or 'internet' or 'carla'>   # 'carla' = real sensor/perception traffic
    target: <vxid:nodeid or 'internet'>
    pps: <int>                                       # synthetic profiles only
    bandwidth_mbps: <int>
    payload_bytes: <int>
    carla:                                           # when source: carla
      scenario: <scenario name>
      sensors: [camera, lidar, ...]
      bridge: ros2                                   # carla-ros-bridge into Autoware/Alpamayo

telemetry:
  prometheus:
    scrape_targets:
      - <host:port>
  gpu:                                   # GPU metrics (DCGM/NVML): utilization, VRAM, throttling
    enabled: <bool>
  pcap:
    interfaces:
      - name: <iface>
        duration_s: <int>

results:
  artifact_dir: path/to/results/exp-001
  upload: false
  upload_target: <registry or s3>
```

### 6.2 Vehicle manifest

A vehicle manifest composes an entire SDV in software. It reuses the `zones`, `compute`,
`network` (incl. `slices`) and `services` blocks above, plus:

```yaml
vehicle:
  id: <string>
  name: <string>                    # e.g. vx-vehicle-01 "OEM-representative zonal E/E"
  description: <text>
  signal_plane:                     # phase 3
    kuksa:
      image: { url: <url>, kind: container }
      vss_catalog: <path>           # COVESA VSS signal catalog
  comms:
    ros2_rmw: rmw_zenoh | rmw_fastrtps   # ROS2 transport between zones and compute
  world:                            # optional co-simulation source
    simulator: carla | alpasim | none
    image: { url: <url>, kind: container }
```

When adding or modifying a manifest, match these schemas exactly; the CLI has no other validation
source to fall back on.

---

## 7 — Network model — vxgateway (SDN slicing)

The edge gateway is a **virtual network function** built entirely from the production open-source
Linux SDN stack, provisioned declaratively by `vxedge` (Rust `rtnetlink`/OVSDB, no shell
templating):

- **Data plane:** Open vSwitch (or Linux bridge) carrying an 802.1q trunk; one VLAN per slice.
  Deployed either as a set of network namespaces on the host (default; lowest overhead, fully
  inspectable) or as a dedicated VM (stronger isolation of the gateway itself).
- **Queueing / slice QoS:** hierarchical tc (HTB) queue trees per slice with guaranteed min-rate
  for URLLC-like slices — the object of hypothesis H1.
- **Real 5G slicing (H2):** Open5GS core + UERANSIM gNB/UE terminate PDU sessions per S-NSSAI;
  slice definitions in the manifest (`mode: s-nssai`) provision both the 5G core and the gateway.
  Zone nodes may additionally carry a URSP-style `slice_policy` (per-traffic-class selection
  across concurrent PDU sessions), mirroring UE-side slicing as deployed on production
  automotive modems (Qualcomm Snapdragon Auto 5G; cf. the DT/BMW/Valeo/Ericsson/Qualcomm 5G SA
  slicing trial, which vxedge reproduces openly in software). Optional radio-channel realism
  via **NVIDIA Sionna** (6G Developer Program); full **Aerial CUDA-Accelerated RAN** is a
  stretch goal requiring specific NVIDIA platforms.
- **TSN variant (phase 3):** time-aware scheduling via `taprio`/`cbs` qdiscs + gPTP time sync
  (`linuxptp`, 802.1AS) as an alternative gateway shaping mode — enables HTB-vs-TSN isolation
  comparisons matching production automotive Ethernet backbones.
- **Legacy bus edges (`type: can`, phase 3):** SocketCAN/vcan buses per zone, exposed to guests
  via QEMU CAN controllers and tunneled across the backbone with cannelloni; CAN frames map to
  VSS signals via Kuksa feeders — the zonal-controller CAN-aggregation role that makes the
  prototype vehicle-shaped rather than datacenter-shaped.
- **Harness modeling:** the manifest `links` section *is* the wiring harness. Per-link
  `impairments` (tc netem: rate cap, latency/jitter, loss) emulate PHY characteristics such as
  100/1000BASE-T1; CAN/LIN drops ride `type: can` links (LIN modeled as a constrained bus).
  Because harness topology is manifest data, it becomes an experimental variable — star vs
  daisy-chained zones, sensor-to-ECU path placement — iterable in minutes, which no physical
  testbed offers. Power distribution is modeled only as VSS signals (vxplant power tree,
  optional); electrical/thermal fidelity is explicitly out of scope. gPTP/TSN (above) is the
  harness's timing layer.
- **Tunnels:** VXLAN for inter-host communication; WireGuard (in-kernel) for secure telemetry and
  OTA transport.
- **Routing:** static for lab experiments; FRR provides BGP for cloud interconnect.
- **Firewalling:** nftables per VLAN/slice.
- **Production NOS twin:** the same slice/VLAN/VXLAN/BGP intent is also rendered onto a
  **SONiC-VS** virtual switch (community qcow2). SONiC is the production open-source NOS
  (Linux Foundation; NVIDIA ships production SONiC on Spectrum), which demonstrates that vxedge
  slice configs express identically on a production NOS. The SONiC-VS data plane is functional
  but **not timing-representative**, so all latency/jitter measurements run against the
  Linux-native vxgateway path. (NVIDIA Cumulus VX is deprecated as a standalone image and is not
  used; NVIDIA Air remains only an optional cloud sandbox.)
- **Determinism controls:** gateway forwarding cores pinned and isolated (`isolcpus`), PREEMPT_RT
  host kernel, hugepages. An optional **FD.io VPP (DPDK)** data-plane variant exists for
  URLLC-focused runs needing minimal per-packet latency variance.
- **Hardware offload path (phase 4):** the same OVS/tc intent offloads onto NVIDIA
  **BlueField DPU / ConnectX** via DOCA — the production exit ramp from the virtual gateway.
- **Monitoring:** gateway counters, tc/OVS statistics, and syslog exported to the central
  Prometheus node.

---

## 8 — Service model (OTA, telemetry, extensibility)

- All services defined under top-level `services` in the manifest.
- `ota` and `telemetry` are the core supported types.
- Services can be referenced in `zones` or `compute` nodes.
- CLI deploys services on-demand via `vxedge service <name> up|down --experiment <manifest>`.
- Extensible: future `vxsvc-*` repos can be added and referenced in manifests. The phase-3
  **Kuksa databroker** (vehicle signal plane, COVESA VSS) is deployed via the vehicle manifest's
  `signal_plane` block rather than as an experiment service.
- Each service definition includes `id`, `type`, `image`, `config`.

**OTA design (H4, `vxota`):** the service exists to be a *realistic, measurable* OTA
workload for H4, not a fleet-management platform — two industry concerns are kept
deliberately separate:

- **Trust model (adopted as design vocabulary, not as a dependency):** artifact metadata
  follows the shape of **Uptane** (the automotive-specific, TUF-derived OTA security
  framework — the closest thing to an ISO/SAE 21434 / UNECE R156-aligned standard) —
  signed root/targets-style manifests, image-repo vs. director-repo separation. The
  reference implementation **aktualizr** (C++) is *not* adopted as a dependency: it would
  contradict the Rust-first service policy (§15) for no benefit vxota needs today.
- **Delivery/orchestration (out of scope for vxota v1):** production fleet tools —
  **Eclipse hawkBit** (Java rollout server + DDI API) and **Mender** (Go, server+client)
  — are named here only as the production analogs an OEM engineer would recognize
  (mapped in `docs/USER-GUIDE.md` §6); neither is wired in, since vxota's zones/compute
  nodes are ephemeral per-experiment instances, not persistent fleet devices needing
  campaign/rollout management.
- **Slot/image-swap updates (phase 3, optional):** if a later experiment wants a *real*
  atomic image swap on a running zone (vs. vxota v1's signed-blob delivery), the
  candidate is **Rugix Ctrl** (Rust, memory-safe, secure-by-default signature
  verification, native content-defined-chunking delta updates — chosen over the more
  established **RAUC** specifically for the Rust-policy fit; RAUC remains the fallback
  if Rugix's narrower deployment history or its gaps — no NAND/UBI, no encrypted
  updates, both irrelevant to our QEMU/libvirt block-storage bundles — become a
  blocker). Maps naturally onto vxzones guest bundles, which are already
  kernel+initramfs "slots" in Rugix/RAUC's sense.

---

## 9 — Virtualization & zone provisioning (libvirt, QEMU/KVM, QNX, RTOS, containers)

**Stack, bottom to top:** host Linux (PREEMPT_RT, isolcpus, hugepages) → KVM → QEMU — managed by
**libvirt**, driven by `vxedge` through the Rust `virt` crate.

- **libvirt is the default zone backend** for `kind: vm | rtimage`. The CLI compiles zone
  manifests into libvirt domain XML: lifecycle (`define/start/destroy/undefine`) gives idempotent
  `up|down` and queryable `status`; vNICs attach to the vxgateway OVS/bridge trunk with per-vNIC
  VLAN tags; `<cputune>` (vcpupin/emulatorpin), hugepages, and virtio multiqueue express the
  manifest's `realtime:` block; storage pools hold the SHA256-digest-tagged images.
- **microVM escape hatch:** `backend: qemu-microvm` drives raw QEMU (QMP, `microvm` machine type)
  — or cloud-hypervisor/Firecracker — bypassing libvirt's device model for the minimal-latency
  arm of hypothesis H3. Both backends hide behind the same `vxedge zone up` interface.
- **Guest palette:**
  - **QNX SDP 8** (free non-commercial license) — QEMU x86-64/ARM guest; the
    production-representative ADAS/safety guest for `front-left`/`front-right` zones. QNX is what
    production ADAS and cockpit controllers run, which anchors OEM relevance.
  - **Zephyr / FreeRTOS** — microVM images for sensor/ECU nodes.
  - **Android Automotive (AAOS)** — infotainment zone; QEMU with virtio-gpu or GPU passthrough.
  - **Containers** — for nodes where packaging as a container is the experimental variable.
- **Fidelity caveat (stated honestly in publications):** production zonal controllers invert this
  stacking — silicon runs a Type-1 hypervisor (QNX Hypervisor and peers) hosting guests, whereas
  here KVM plays the hypervisor and QNX is a guest. Functionally equivalent for slice-isolation
  research; the gap closes via the **hypervisor fidelity ladder** below and, ultimately, DRIVE OS
  on DRIVE AGX hardware (phase 4).
- **Hypervisor fidelity ladder** (production-grade rungs only — no research-toy hypervisors):
  - *Rung 0 (software-only, phase 1–3):* KVM with strict static partitioning — isolcpus/cpuset
    pinned cells, hugepages — the Linux approximation of partitioning and the baseline arm of
    the freedom-from-interference experiment (exp-004).
  - *Rung 1 (phase 4):* **Xen dom0less** as a dedicated boot-entry host profile — production
    open-source with an active functional-safety track (Xen 4.21 dom0less refactoring; AMD/Honda
    automotive demos, Xen Summit 2025); Zephyr domUs boot sub-second.
  - *Rung 2 (phase 4):* **QNX Hypervisor** — the production zonal-controller stack itself
    (license permitting; pairs with DRIVE OS QNX).
  Each rung converts part of the stated caveat into a measured claim (exp-004 reruns per rung).
- CLI stages images, creates instances, and configures network interfaces; persistent storage
  optional per zone; logs and telemetry collected centrally.

### Sensor, actuator & I/O virtualization (four layers)

1. **Perception sensors** (camera, lidar, radar, GNSS/IMU) — synthesized by the world
   simulator (CARLA; AlpaSim / Sensor RTX as the higher-fidelity path). In a real vehicle
   these ride GMSL/FPD-Link serdes into the ADAS ECU; here the transport **is** slice traffic
   through vxgateway (`traffic_profiles.source: carla`) — sensor streams are the measured
   ADAS load, not synthetic filler.
2. **Body sensors/actuators** (doors, HVAC, wipers, BMS…) — **restbus simulation**: simulated
   nodes emit/consume CAN frames per DBC definitions (`sensors:`/`actuators:` in the node
   schema); Kuksa's CAN provider maps DBC signals ↔ VSS. Closed-loop behavior comes from the
   **vxplant agent** (in `vxagents`): subscribes to actuator commands, integrates a plant
   model (first-order default; FMI/FMU import in phase 4 so OEMs can drop in Simulink-exported
   models), publishes sensor feedback.
3. **Register-level I/O** (GPIO/ADC/PWM/I2C/SPI) — application-class ECUs (QNX, AAOS) use QEMU
   device models (`io.devices`); MCU-class ECUs needing register fidelity use **Renode**
   (`backend: renode`): full peripheral models running unmodified Zephyr/FreeRTOS firmware.
4. **Actuation loop closure** — control commands (steering/throttle/brake) return to CARLA via
   carla-ros-bridge vehicle control, closing the loop world → sensors → slices → AD stack →
   actuation → world. End-to-end **control-loop latency under slice contention** is a
   first-class metric (§12).

**Boundary standards (phase 4):** ASAM **OSI** at the simulator↔stack boundary, **FMI/FMU**
for plant models, **XIL**-style semantics for the bench API — so the virtual testbed and
OEM HIL rigs speak the same protocols (the SIL→HIL migration story).

---

## 10 — Compute model (vxcompute — Autoware/ROS2, Alpamayo, inference, OTA hosting)

- Compute nodes run containerized workloads. Two AD stacks are supported as ADAS-slice workloads,
  which usefully stress the network differently:
  - **Autoware / ROS2** (Apache-2.0) — classical modular AV stack; consumes CARLA sensor streams
    via carla-ros-bridge.
  - **NVIDIA Alpamayo / AlpaSim** (open-sourced at CES 2026) — reasoning-VLA driving model and
    open simulation framework; runs on the host GPU without DRIVE hardware. Fine-tuning and
    DRIVE Hyperion integration are out of scope (phase 4).
- Perception/inference workloads use **DeepStream / TensorRT**; container definitions are
  optimized for GPU pass-through and TensorRT runtime (see `resources.gpu` in the schema).
- OTA server may be deployed in a compute node if referenced in the experiment manifest.
- Resources declared in manifest (`cpu`, `memory`, `gpu`); services deployed dynamically per
  manifest references.
- Optional in-vehicle-style workload orchestration via **Eclipse Ankaios/BlueChi** (phase 3) to
  mirror production SDV runtimes.

---

## 11 — Edge agents & telemetry collection (vxagents / vxtelemetry)

- Rust agents deployed per experiment to collect metrics, latency, and traffic.
- Prometheus exporters for centralized metric collection; **GPU metrics tracked alongside**
  (DCGM/NVML: utilization, VRAM boundaries, thermal/power throttling) since AD workloads share
  the host with the gateway.
- **VSS alignment:** vehicle-signal telemetry follows the COVESA VSS catalog via the Kuksa
  databroker (phase 3). The open-source C++ **AWS IoT FleetWise edge agent** serves as a design
  reference for signal collection/campaign semantics — as a reference only: the AWS-hosted
  FleetWise service closes to new customers in April 2026 and is not a dependency.
- Optional PCAP capture for detailed traffic analysis.
- Agents and telemetry services configured via manifest and CLI commands.
- Designed to be lightweight to avoid perturbing experiment results.

---

## 12 — Experiment methodology, metrics, and analysis plan

**Methodology:**

1. **Preparation:**
   - Validate manifest syntax and semantics (experiment + referenced vehicle manifest).
   - Stage images on host(s) using CLI (libvirt storage pools / container registry).
   - `vxedge up` provisions vxgateway slices (VLANs, tc queue trees; S-NSSAI slices in the
     5G core for `mode: s-nssai`).

2. **Execution:**
   - `vxedge vehicle up` (or `vxedge experiment up` referencing a vehicle) to provision gateway,
     zones, compute, signal plane, and services.
   - Generate traffic per `traffic_profiles` — synthetic (pps/bandwidth) and/or real perception
     traffic (`source: carla`).
   - Collect telemetry (Prometheus + GPU metrics + PCAP) and service logs.

3. **Postprocessing:**
   - Extract metrics from Prometheus exporters.
   - Parse PCAPs for latency, jitter, packet loss.
   - Aggregate results per slice and per node.

**Metrics:**

- **Network:** p50/p95/p99 latency, jitter, packet loss per slice.
- **Closed loop (phase 2+):** end-to-end control-loop latency — world → sensors → slices →
  AD stack → actuation → world — under slice contention.
- **Compute:** CPU/memory/GPU utilization, service response times.
- **OTA:** deployment success rate, artifact delivery latency.
- **Telemetry agents:** data ingestion rates, metric completeness.

**Analysis plan:**

- Compare latency/jitter under different virtualization choices (H3: libvirt VM vs container vs
  microVM).
- Evaluate slice isolation under heavy multi-zone traffic (H1), and static VLAN mapping vs real
  S-NSSAI slicing (H2).
- Quantify OTA and telemetry impact on URLLC slices (H4).
- Quantify the effect of determinism controls (pinning, PREEMPT_RT, VPP data plane) on tail
  latency.
- Generate reproducible tables, charts, and CSV datasets for publication.

---

## 13 — Reproducibility, CI/CD, artifact publication (registries)

- **Reproducibility:**
  - All manifests under `vxperiments` are versioned and authoritative.
  - Images and RTOS builds tagged with SHA256 digest.
  - CLI ensures idempotent `up|down` operations (libvirt domain lifecycle; declarative gateway
    provisioning).
  - Because the gateway is software, its full provisioning is unit/integration-testable in CI
    against network namespaces — no physical router in the loop.

- **CI/CD:**
  - GitHub Actions pipelines for building images, testing CLI, and publishing manifests.
  - Artifacts automatically uploaded to private registry or S3 bucket.
  - Experimental runs can be triggered and reproduced on demand.

- **Artifact publication:**
  - Results archived per `results_prefix` in experiment manifest.
  - Metadata includes experiment ID, manifest checksum, CLI version.
  - Registry uploads optional; ensures compliance with reproducible research principles.

---

## 14 — Safety, security, licensing, and industrialization notes

- **Safety:**
  - Non-safety-critical lab environment; no real vehicle control signals.
  - Experiments simulate zonal ECU traffic in virtual/isolated networks.
  - The platform is production-*representative*, not safety-certified; the QNX-as-guest
    inversion (§9) and shared-host gateway are documented fidelity caveats.

- **Security:**
  - WireGuard for encrypted telemetry and OTA transport.
  - Images validated with SHA256 digests.
  - No root exposure in containerized services.
  - nftables firewall per VLAN/slice on vxgateway.

- **Licensing:**
  - Open-source Rust CLI and agents (MIT/Apache-2.0).
  - QNX SDP 8 under QNX free non-commercial license (research use); Zephyr/FreeRTOS under their
    respective licenses.
  - Autoware/ROS2 under Apache-2.0; Alpamayo models/AlpaSim under NVIDIA's open-model licenses;
    SONiC, OVS, FRR, Open5GS, UERANSIM, Eclipse SDV components under their upstream OSS licenses.

- **Industrialization notes:**
  - Middleware and patterns match the production SDV convergence: Eclipse SDV (Kuksa/VSS, Zenoh,
    uProtocol, Ankaios), SOAFEE-style cloud/vehicle virtual-ECU parity, NVIDIA DRIVE-adjacent
    compute, and UE-side slicing semantics matching production automotive modems (Qualcomm
    Snapdragon Auto, URSP). This makes results directly legible to NVIDIA-DRIVE-partner OEMs
    (JLR-class zonal E/E programs) and Qualcomm-Digital-Chassis programs alike.
  - ARM64 zone/compute variants (phase 3) target NVIDIA Jetson and the cloud virtual-ECU
    parity paths both silicon vendors ship: Snapdragon vSoC / Virtual Platforms on Graviton
    and Google Cloud.
  - All manifests modular, reusable across multiple experiments.
  - Gateway patterns have an explicit hardware exit ramp: SONiC on Spectrum, or OVS/DOCA offload
    on BlueField/ConnectX.
  - CI/CD pipelines support automated image and manifest validation.
  - Publishable results designed to integrate into research papers or internal dashboards.

---

## 15 — Implementation policy & phased roadmap

### Languages

- **Rust** — `vxedge-core`, `vxedged` daemon (vxAPI/tonic), `vxedge` CLI, `vxagents`, gateway
  provisioning (rtnetlink/OVSDB, `virt` crate for libvirt).
- **C++** — everything touching ROS 2/DDS/Autoware, DeepStream/TensorRT plugins, QNX-side
  components (automotive-native, AUTOSAR-adjacent), and the Qt/QML operator HMI (Qt GRPC client).
- **Python** — Sionna, notebooks, analysis pipelines.
- **TypeScript** — web dashboard, Electron "vxedge Studio", generated vxAPI SDK (connect-es).
- **Shell** — glue only.
- Manifests (YAML) and the generated vxAPI (Protobuf) are the only cross-language interfaces.

### Phases

1. **Phase 1 — slicing core, API-first from day one:** `vxedge-core` + `vxedged` + vxAPI v1
   (Gateway/Zone/Compute/Job/Event services) with the CLI as thin client; vxgateway
   (OVS/tc/FRR/WireGuard) + synthetic traffic + vxagents/vxtelemetry → the H1/H3/H4 isolation
   numbers. This alone is the paper.
2. **Phase 2 — real slices & workloads:** Open5GS/UERANSIM S-NSSAI slicing (H2) incl.
   URSP-style `slice_policy` (UE-side selection over concurrent PDU sessions);
   CARLA → ROS2 → Autoware as real ADAS traffic, **closed-loop** (actuation back into CARLA;
   control-loop latency metric); per-link harness `impairments` (netem, BASE-T1 emulation);
   QNX SDP 8 and AAOS zones; SONiC-VS production-NOS twin; TypeScript vxAPI SDK + minimal web
   dashboard (live slice metrics over gRPC-Web).
3. **Phase 3 — production SDV alignment:** vehicle manifest end-to-end (`vxedge vehicle up`);
   Kuksa/VSS signal plane; rmw_zenoh/uProtocol comms; Ankaios workload orchestration; Sionna
   channel realism (NVIDIA 6G Developer Program); Alpamayo/AlpaSim workload; optional
   Rugix-Ctrl-based atomic slot updates on vxzones guest bundles (§8 OTA design); Qt/QML
   operator HMI (Qt GRPC); cloud-hosted `vxedged --controller` federating multiple GPU hosts;
   Electron
   "vxedge Studio" groundwork; vxedge-tray (Rust SNI tray, thin vxAPI client) + vxedged
   systemd unit; ARM64 zone/compute/agent variants (Jetson + Snapdragon
   vSoC / Graviton parity); CAN/LIN edge modeling (`type: can`, SocketCAN/vcan + Kuksa CAN
   feeders); TSN gateway variant (taprio/cbs + gPTP); UDS/DoIP diagnostic probe for OTA runs;
   V2X groundwork — multi-vehicle composition (second vehicle-manifest instance, V2V) + `rsu`
   nodes (V2I); sensor/actuator virtualization — restbus simulation (DBC + Kuksa CAN
   provider), **vxplant** plant-model agent, QEMU `io.devices`, **Renode backend** for
   MCU-class virtual ECUs.
4. **Phase 4 — hardware (optional):** Jetson AGX in the loop (affordable DRIVE-lineage stand-in);
   DRIVE AGX + DRIVE OS (Linux/QNX); BlueField/DOCA gateway offload; Aerial CUDA-Accelerated RAN;
   V2X radio realism — C-V2X PC5 sidelink (Sionna channel models; PAWR/AERPAW outdoor
   validation); ASAM boundary standards — OSI (simulator↔stack), FMI/FMU plant-model import,
   XIL-style bench semantics; optional VSS power-tree modeling; hypervisor fidelity ladder
   rungs 1–2 — Xen dom0less host profile and QNX Hypervisor (freedom-from-interference
   measured per rung via exp-004).

---

## 16 — Appendix: example manifests, gateway snippets, run sequence

### Example experiment manifest snippet

```yaml
experiment:
  id: exp-001
  name: ADAS slice isolation test
  duration_s: 1800
  results_prefix: results/exp-001
  vehicle: vxperiments/vehicles/vx-vehicle-01.yaml

network:
  slices:
    - id: adas
      mode: vlan
      vlan: 101
      qos: { min_rate_mbps: 100, max_rate_mbps: 200, priority: 1 }
    - id: infotainment
      mode: vlan
      vlan: 103
      qos: { min_rate_mbps: 0, max_rate_mbps: 500, priority: 5 }

services:
  ota:
    id: ota-01
    type: ota
    image:
      url: registry/vxota:latest
      kind: container
    config:
      artifacts: /opt/ota/artifacts
  telemetry:
    id: telemetry-01
    type: telemetry
    image:
      url: registry/vxtelemetry:latest
      kind: container
    config:
      scrape_interval_s: 5
```

### vxgateway provisioning (rendered by the CLI; shown as equivalent shell for illustration)

```bash
# OVS trunk + per-slice VLANs (one access port per zone vNIC, tagged)
ovs-vsctl add-br vxbr0
ovs-vsctl add-port vxbr0 vz-front-left  tag=101   # adas slice
ovs-vsctl add-port vxbr0 vz-front-right tag=102
ovs-vsctl add-port vxbr0 vz-rear-left   tag=103   # infotainment slice
ovs-vsctl add-port vxbr0 vz-central-hpc tag=105

# Per-slice queue tree (HTB): guaranteed min-rate for ADAS, capped infotainment
tc qdisc add dev vxup0 root handle 1: htb default 50
tc class add dev vxup0 parent 1:  classid 1:1  htb rate 1gbit
tc class add dev vxup0 parent 1:1 classid 1:10 htb rate 100mbit ceil 200mbit prio 1  # adas
tc class add dev vxup0 parent 1:1 classid 1:50 htb rate 1mbit   ceil 500mbit prio 5  # infotain
```

### Run sequence (CLI)

0. `vxedged serve`                                        # or let the CLI auto-spawn a local daemon
1. `vxedge up`                                            # vxgateway: bridges, VLANs, queue trees
2. `vxedge zone up --vxid vxzone-front-left`
3. `vxedge zone up --vxid vxzone-front-right`
4. `vxedge compute up --vxid vxcompute-central`
5. `vxedge service ota up --experiment vxperiments/exp-001.yaml`
6. `vxedge service telemetry up --experiment vxperiments/exp-001.yaml`
7. `vxedge experiment up --manifest vxperiments/exp-001.yaml`
8. Collect results: `vxedge telemetry collect --manifest vxperiments/exp-001.yaml --out results/exp-001.zip`
9. Tear down: `vxedge experiment down --manifest vxperiments/exp-001.yaml` then services, compute, zones, gateway

Or, end to end with a vehicle manifest:
`vxedge vehicle up --manifest vxperiments/vehicles/vx-vehicle-01.yaml` →
`vxedge experiment up --manifest vxperiments/exp-001.yaml` → collect → `experiment down` →
`vehicle down`.

---
