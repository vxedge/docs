# ACRONYMS.md — glossary

Every acronym used across `ARCHITECTURE.md` and the other program docs, explained in
plain language and grouped by field. Not auto-generated — update it by hand alongside
`ARCHITECTURE.md` when a new acronym enters the vocabulary (same discipline as
`AGENTS.md`'s other cross-referenced docs).

Two acronyms are genuinely ambiguous in this project's own docs, depending on context —
flagged inline where they occur: **UDS** (Unix Domain Socket vs. Unified Diagnostic
Services) and **OSI** (ASAM's simulator interface vs. the classic 7-layer networking
model — vxedge only ever means the former).

---

## 5G / RAN / mobile core

The `vxedge` core-network/RAN stack (Open5GS + UERANSIM), relevant to H2 and the
`open5gs-ueransim-patterns` skill.

- **5G** — Fifth-generation cellular network standard; the slicing technology H2 tests.
- **RAN** — Radio Access Network. The base-station side of the network (here: UERANSIM's
  simulated `gNB`).
- **CN** — Core Network. The non-radio side (AMF, SMF, UPF, etc.) — here: Open5GS.
- **gNB** — "next-generation NodeB," the 5G base station.
- **UE** — User Equipment. The device connecting to the network — here, a simulated
  modem (UERANSIM) inside a zone/pod, not a phone.
- **UERANSIM** — Open-source UE + RAN simulator; vxedge's RAN implementation.
- **PDU (session)** — Packet Data Unit session: the data connection a UE establishes to
  reach a network (roughly, "the tunnel that carries its traffic").
- **S-NSSAI** — Single Network Slice Selection Assistance Information: the identifier
  for one network slice, made of an **SST** + optional **SD**.
- **SST** — Slice/Service Type: the broad category of a slice (e.g. "URLLC-like").
- **SD** — Slice Differentiator: a finer-grained tag distinguishing slices that share an
  SST.
- **URSP** — UE Route Selection Policy: rules that tell a UE which slice to send a given
  traffic class over.
- **URLLC** — Ultra-Reliable Low-Latency Communication: the 5G traffic class the ADAS
  slice is modeled on.
- **DNN** — Data Network Name: the network a PDU session connects to (successor to the
  older term **APN**, Access Point Name).
- **AMF** — Access and Mobility Management Function: handles UE registration/mobility.
- **SMF** — Session Management Function: manages PDU sessions.
- **UPF** — User Plane Function: actually forwards user traffic (the data-plane NF).
- **NRF** — Network Repository Function: lets core NFs discover each other.
- **AUSF** — Authentication Server Function.
- **UDM** / **UDR** — Unified Data Management / Unified Data Repository: subscriber data
  functions.
- **PCF** — Policy Control Function.
- **BSF** — Binding Support Function.
- **NSSF** — Network Slice Selection Function: picks the right slice for a UE.
- **NF** — Network Function: generic term for any of the boxes above.
- **SBI** — Service-Based Interface: the HTTP-based protocol core NFs use to talk to
  each other.
- **PFCP** — Packet Forwarding Control Protocol: the SMF↔UPF control channel.
- **NGAP** — NG Application Protocol: the signaling protocol between gNB and AMF.
- **NAS** — Non-Access Stratum: UE↔core signaling that rides over, but is logically
  independent of, the radio link.
- **N2 / N3** — 3GPP reference points: N2 is gNB↔AMF (control), N3 is gNB↔UPF (data) —
  vxedge's CN-pod↔RAN-pod transit subnet stands in for both.
- **GTP** / **GTP-U** — GPRS Tunneling Protocol (User plane): how UPF tunnels a UE's
  actual traffic.
- **SCTP** — Stream Control Transmission Protocol: the transport NGAP rides on.
- **SA** — Standalone (5G SA = a 5G core end-to-end, not anchored on 4G) — the
  architecture the DT/BMW/Valeo/Ericsson/Qualcomm slicing trial vxedge cites reproduced.
- **V2X** — Vehicle-to-Everything: umbrella term for vehicle wireless comms.
- **V2V** / **V2I** — Vehicle-to-Vehicle / Vehicle-to-Infrastructure.
- **RSU** — Roadside Unit: a V2I endpoint (phase-3 node type).
- **PC5** — The 3GPP sidelink interface used for direct V2X (no core network hop).

## SDN & Linux networking (vxgateway)

The `vxgateway` data plane, relevant to `network-provisioning-patterns`.

- **SDN** — Software-Defined Networking: separating the control logic from the packet
  forwarding — vxgateway's whole premise.
- **OVS** — Open vSwitch: a software switch; one of vxgateway's two bridge backends.
- **OVSDB** — Open vSwitch Database protocol: how OVS is configured/queried.
- **VLAN** — Virtual LAN: tags that separate traffic on one physical/virtual wire — how
  vxgateway maps slices today (`mode: vlan`).
- **VXLAN** — Virtual Extensible LAN: tunnels VLAN-style segments across hosts.
- **HTB** — Hierarchical Token Bucket: the Linux `tc` queueing discipline vxgateway uses
  for per-slice bandwidth guarantees.
- **rtnetlink** — The Linux kernel's netlink socket family for network configuration;
  the planned successor to today's iproute2-shell-out backend.
- **FRR** — FRRouting: open-source routing daemon suite (provides vxgateway's **BGP**).
- **BGP** — Border Gateway Protocol: the routing protocol FRR speaks for cloud
  interconnect.
- **TSN** — Time-Sensitive Networking: deterministic-latency Ethernet extensions
  (phase-3 gateway variant).
- **gPTP** / **PTP** — (generalized) Precision Time Protocol: clock sync TSN depends on.
- **NOS** — Network Operating System: SONiC (SONiC-VS) is vxedge's "production NOS
  twin."
- **BASE-T1** (100BASE-T1 / 1000BASE-T1) — Automotive Ethernet PHY standards vxgateway's
  link `impairments` emulate.
- **DPDK** — Data Plane Development Kit; **VPP** — Vector Packet Processing (FD.io): a
  kernel-bypass data-plane option for URLLC-focused runs.
- **DOCA** — NVIDIA's SDK for offloading OVS/tc-style intent onto a BlueField DPU
  (phase-4 hardware exit ramp).
- **CAN** — Controller Area Network; **LIN** — Local Interconnect Network: legacy
  automotive buses, modeled via `type: can` links (phase 3).
- **SocketCAN** / **vcan** — Linux's native CAN subsystem / its virtual-CAN device.
- **DBC** — A CAN database file format defining frame layouts (used by restbus
  simulation to map CAN ↔ VSS).

## SDV & automotive E/E architecture

- **SDV** — Software-Defined Vehicle: a vehicle whose behavior is primarily defined by
  software, not fixed wiring — vxedge's whole subject.
- **E/E** — Electrical/Electronic (architecture): how a vehicle's electronics are wired
  and organized (zonal vs. domain-based, etc.).
- **ECU** — Electronic Control Unit: an embedded computer controlling one vehicle
  function — what vxedge's "zones" stand in for.
- **ADAS** — Advanced Driver-Assistance Systems: the URLLC-like traffic class H1/H2
  test.
- **AD** — Autonomous Driving.
- **HMI** — Human-Machine Interface: the phase-3 Qt/QML operator dashboard.
- **AUTOSAR** — AUTomotive Open System ARchitecture: the standard automotive software
  architecture vxedge's QNX/C++ conventions are described as "adjacent" to.
- **OEM** — Original Equipment Manufacturer: the vehicle maker — vxedge's target
  audience/adopter.
- **VSS** — Vehicle Signal Specification: **COVESA**'s standard catalog of vehicle
  signal names (speed, door state, etc.), used via the Kuksa databroker.
- **COVESA** — Connected Vehicle Systems Alliance: the standards body behind VSS/Kuksa.
- **BMS** — Battery Management System: one of the comfort/EV zone workloads modeled.
- **HVAC** — Heating, Ventilation, and Air Conditioning: another comfort-zone workload.
- **GMSL** / **FPD-Link** — Gigabit Multimedia Serial Link / Flat Panel Display Link:
  the physical transport real camera/sensor data rides in a vehicle (vxedge substitutes
  slice traffic through vxgateway instead).
- **UDS** *(automotive sense)* — Unified Diagnostic Services: the ISO 14229 diagnostic
  protocol behind the phase-3 UDS/DoIP probe. Not to be confused with the networking
  sense below.
- **DoIP** — Diagnostics over IP: carries UDS diagnostics over Ethernet/IP.
- **SAE** — Society of Automotive Engineers: standards body (e.g. the WCX venue).

## Virtualization & zones

- **VM** — Virtual Machine.
- **KVM** — Kernel-based Virtual Machine: the Linux hypervisor vxedge builds on.
- **QEMU** — Quick EMUlator: the machine emulator KVM uses; also runs standalone as the
  `qemu-microvm` zone backend.
- **QMP** — QEMU Machine Protocol: how the microVM backend controls QEMU directly.
- **microVM** — A minimal-device-model QEMU machine type, for lower overhead than a
  full VM.
- **QNX / SDP** — QNX Software Development Platform 8: the real-time OS used for
  ADAS/safety zone guests.
- **RTOS** — Real-Time Operating System (Zephyr, FreeRTOS, QNX).
- **AAOS** — Android Automotive OS: the infotainment zone guest.
- **MCU** — Microcontroller Unit: the class of chip Renode-backed zones emulate at
  register level.
- **GPIO / I2C / SPI / PWM / ADC** — Low-level hardware I/O buses/peripherals
  (General-Purpose I/O, Inter-Integrated Circuit, Serial Peripheral Interface, Pulse
  Width Modulation, Analog-to-Digital Converter) — the register-level I/O layer QEMU
  device models / Renode expose to guests.
- **NAND / UBI** — Flash storage technology; came up as a reason Rugix (not RAUC) fits
  vxedge's QEMU/libvirt block-storage bundles (no real NAND to manage).

## Compute, AI & GPU (vxcompute)

- **GPU** — Graphics Processing Unit.
- **CUDA** — NVIDIA's parallel-compute platform/API.
- **TensorRT** — NVIDIA's inference-optimization SDK (DeepStream pipelines target it).
- **DCGM** — Data Center GPU Manager; **NVML** — NVIDIA Management Library: how GPU
  utilization/VRAM/thermal metrics get collected.
- **VRAM** — Video RAM (GPU memory) — one of the tracked GPU metrics.
- **MIG** — Multi-Instance GPU: NVIDIA's hardware GPU-partitioning feature
  (`resources.gpu: mig-slice`).
- **ROS2** — Robot Operating System 2: the middleware Autoware runs on.
- **DDS** — Data Distribution Service: the pub/sub protocol standard under ROS2.
- **rmw** — ROS MiddleWare: ROS2's pluggable transport layer (`rmw_zenoh` vs.
  `rmw_fastrtps`).
- **CARLA** — Open-source autonomous-driving simulator (proper name, not an acronym);
  the source of realistic sensor/perception traffic.
- **LLM** — Large Language Model: relevant to track M's GenAI-authored-experiment goal.

## API & software architecture (vxAPI)

- **API** — Application Programming Interface.
- **gRPC** — Google's RPC framework (originally "gRPC Remote Procedure Calls"); the
  transport vxAPI is built on.
- **RPC** — Remote Procedure Call: a function call made across a network boundary.
- **IDL** — Interface Definition Language: the Protobuf `.proto` files describing
  vxAPI's contract.
- **Protobuf** — Protocol Buffers: Google's binary serialization format, the wire
  format gRPC uses.
- **SDK** — Software Development Kit: the generated per-language vxAPI client
  libraries (Rust/tonic, C++/Qt GRPC, TypeScript/connect-es).
- **CLI** — Command-Line Interface: the `vxedge` binary, a thin vxAPI client.
- **UDS** *(networking sense)* — Unix Domain Socket: vxedge's default local transport
  between the CLI and `vxedged`. Not to be confused with the automotive sense above.
- **mTLS** — mutual Transport Layer Security: both client and server present
  certificates — vxedge's remote-transport auth.
- **TLS** — Transport Layer Security: the encryption protocol mTLS builds on.
- **OIDC** — OpenID Connect: the bearer-token auth scheme for remote vxAPI access.
- **REST** — Representational State Transfer: the alternative API style vxAPI
  deliberately isn't (it's gRPC), though an optional REST façade is possible later.
- **gRPC-Web** — A gRPC variant browsers can call directly; how the web
  dashboard/Electron frontends reach vxAPI.
- **JSON** — JavaScript Object Notation: used for `--json` CLI output and iproute2's
  machine-readable reads.
- **YAML** — the manifest file format (experiment/vehicle manifests).
- **FFI** — Foreign Function Interface: cross-language function calling (relevant to
  any native bindings).
- **OCI** — Open Container Initiative: the standard container image format Podman
  images conform to.
- **GHCR** — GitHub Container Registry: where container images get published with
  digests.

## Standards, modeling & simulation (track M)

- **SysML** — Systems Modeling Language: the modeling language `vxmodels` authors in
  (v2 specifically — textual, git-diffable).
- **OMG** — Object Management Group: the standards body that owns SysML.
- **MBSE** — Model-Based Systems Engineering: the discipline SysML/track M applies.
- **INCOSE** — International Council on Systems Engineering: an MBSE-adjacent standards
  community.
- **ASAM** — Association for Standardization of Automation and Measurement Systems:
  the body behind OSI/OpenSCENARIO.
- **OSI** *(ASAM sense)* — Open Simulation Interface: the boundary standard between a
  world simulator (CARLA) and the AD stack (phase 4). vxedge never means the classic
  networking "7-layer OSI model."
- **OpenSCENARIO** — ASAM's standard format for traffic/scenario definitions (phase-4
  mapping target for CARLA scenarios).
- **FMI** / **FMU** — Functional Mock-up Interface / Functional Mock-up Unit: the
  standard for importing plant models (e.g. Simulink-exported) into `vxplant`.
- **XIL** — X-in-the-Loop: umbrella term for **SIL** (Software-in-the-Loop) and **HIL**
  (Hardware-in-the-Loop) testing — vxedge aims to speak the same bench-API semantics as
  OEM HIL rigs.

## OTA & security (vxota)

- **OTA** — Over-The-Air (update): vxota's whole subject, and H4's workload.
- **Uptane** — An automotive-specific, TUF-derived OTA security framework; vxota
  follows its metadata *shape* without depending on its reference implementation.
- **TUF** — The Update Framework: the general (non-automotive) update-security spec
  Uptane derives from.
- **RAUC** — Robust Auto-Update Controller: an established atomic-update tool,
  considered as vxota's phase-3 slot-update fallback.
- **Rugix (Ctrl)** — A Rust-native atomic-update tool; vxota's preferred phase-3
  candidate over RAUC (Rust-policy fit).

## Methodology, reproducibility & DevOps

- **CI** / **CD** — Continuous Integration / Continuous Delivery: automated
  build/test/publish pipelines (GitHub Actions here).
- **PR** — Pull Request.
- **RTT** — Round-Trip Time: the core latency metric vxprobe measures.
- **IQR** — Interquartile Range: the spread measure used to judge whether a rerun's
  numbers are "reproducible" (within the original's IQR).
- **p50 / p95 / p99** — Percentile latency notation (the value below which 50%/95%/99%
  of samples fall) — not an acronym, but ubiquitous enough to define: p99 is the
  "worst-case-ish" tail latency figure.
- **RSS** — Resident Set Size: a process's actual in-memory footprint, one of H3's
  resource-cost metrics.
- **SHA256** — The cryptographic hash algorithm used to digest-tag every manifest,
  image, and archive for reproducibility.
- **CSV** — Comma-Separated Values: the tabular result-export format.
- **SemVer** — Semantic Versioning: the `MAJOR.MINOR.PATCH` convention every repo
  follows.
- **LTS** — Long-Term Support (e.g. an OS/toolchain release channel).
- **PPA** — Personal Package Archive: an Ubuntu third-party package source (the
  now-removed host Open5GS install came from one).
- **NOPASSWD** — A sudoers option letting a specific command run without a password
  prompt — how `vxedged` gets `CAP_NET_ADMIN`-requiring privileges without running as
  root.
