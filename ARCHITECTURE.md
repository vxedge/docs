# vxedge Research Plan and ARCHITECTURE 

Project: vxedge  
Purpose: Research-grade orchestration and experiment platform to evaluate 5G network-slice mapping to zonal & central SDV E/E architectures. Uses MikroTik CCR2004 as the edge gateway, KVM/QEMU VMs for zonal ECUs (Android Automotive, FreeRTOS, Zephyr), containerized central compute (Autoware/ROS2), and a Rust CLI (vxedge) to orchestrate manifest-driven experiments, services, and telemetry.

---

## Table of contents

1. Executive summary
2. Research goals & hypotheses
3. High-level architecture (topology & components)
4. Repositories & single-source rules
5. vxedge CLI (commands, semantics, UX)

---

## 1 — Executive summary

vxedge is a reproducible, modular framework to define and run SDV experiments that combine zone virtual ECUs, central compute, edge gateway slicing (CCR2004) and services (OTA, telemetry). Manifests declare the whole experiment (zones, compute, network, services). The Rust CLI (vxedge) orchestrates the lifecycle using a simple `up|down` model across all subsystems. The platform is designed to generate publishable results (latency/jitter percentiles, OTA reliability, isolation metrics) and evolve toward production pipelines.

---

## 2 — Research goals & hypotheses

**Primary goal:** Quantify how well commodity edge gear (MikroTik CCR2004) combined with host virtualization and central compute can provide isolation and deterministic performance for SDV workloads when mapped to logical 5G slices.

**Hypotheses to test:**

- Proper VLAN/VXLAN + per-slice queueing on CCR2004 can keep p95/p99 latency for ADAS (URLLC-like) near baseline under heavy infotainment load.
- OTA service co-located in central compute (deployed on demand) will not compromise ADAS slice SLAs if slices and queue-tree reservations are correctly configured.
- Virtual ECU choice (VM vs container vs microVM) affects latency/jitter observable at zone-to-compute flows.

**Deliverables:** Reproducible experiment artifacts, datasets, scripts, and publishable analysis.

---

## 3 — High-level architecture (topology & components)

```
                               Cloud / Operator Edge (optional)
               +-------------------------------------------------------+
               |  Cloud CHR / Open5GS / NOC / OTA repository / Grafana |
               +-------------------------+-----------------------------+
                                         |
                                   Internet / 5G Backhaul
                                         |
                    +-----------------------+------------------------+
                    |  MikroTik CCR2004 Edge Gateway (RouterOS v7+)  |
                    |  - VLANs, mangle, queue-tree, WireGuard, BGP   |
                    +----+--------------+-------------+-------------+
                         | Trunk (802.1q) |             |
                         |                |             |
        +----------------+-------+   +----+--------+  +--+---------------+
        | Host (AMD Ryzen)      |   | Host (optional) |  | Additional Hosts |
        | - vSwitch (bridge)     |   | - k8s / Docker  |  | (cloud or NUC)   |
        | - QEMU/KVM VM Manager  |   | - Containers    |  |                  |
        | - vxzones (VMs)        |   | - vxcompute     |  |                  |
        +----+-------------------+   +----+-----------+  +------------------+
             |                          |
    Zones:   |                          |
    - zone-front-left   (VMs, RTOS, ADAS sensors/nodes)
    - zone-front-right  (VMs, RTOS, ADAS sensors/nodes)
    - zone-rear-left    (comfort, BMS, infotainment clients)
    - zone-rear-right   (comfort, BMS, infotainment clients)
    - zone-central-hpc  (Autoware, OTA server, inference)
    - zone-gateway      (uplink to CCR2004, VLAN slicing)
```

**Key components:**

- **vxedge CLI (Rust)** — orchestrator + provisioning (core).
- **vxzones** — authoritative zone manifests, VM images, RTOS builds.
- **vxcompute** — central compute manifests, Autoware/ROS2 images, inference.
- **vxota** — OTA server & signing tooling (artifact store).
- **vxagents** — performant Rust agents for measurements and metrics.
- **vxtelemetry** — telemetry ingestion & Prometheus export.
- **vxperiments** — manifest-driven experiments and results.

---

## 4 — Repositories & single-source rules

Canonical repos (under vxedge org):

- `vxedge/vxedge` — core + CLI + RouterOS templates (master doc, CLI).
- `vxedge/vxzones` — zone definitions, VM images, RTOS artifacts, publish scripts.
- `vxedge/vxcompute` — central compute, Autoware, inference images, compute manifests.
- `vxedge/vxota` — OTA server, signing, manifests.
- `vxedge/vxagents` — Rust agents, metrics exporters.
- `vxedge/vxtelemetry` — telemetry ingestion and exporters.
- `vxedge/vxperiments` — experiments manifests, notebooks, results.
- `vxedge/docs` — papers, slides, reproducibility guide.

**Single-source rules:**

- A zone/compute’s manifest is authoritative for its images and node IDs.
- Services declared under services in an experiment manifest are the authoritative runtime descriptors for that experiment (image + config). The code lives in vxota or vxtelemetry as appropriate.
- CLI uses manifests as sole input; state stored in ephemeral runtime directories and vxedge logs.

---

## 5 — vxedge CLI — commands & semantics (final)

**Location:** `vxedge/vxedge/cli` (Rust).  
**Binary:** `vxedge` (single binary).  
**Global behavior:** all lifecycle commands follow `up|down` semantics. Where staging is required, `up` performs staging + start; `down` stops + cleanup.

**Commands (canonical)**

```bash
# Edge (CCR2004)
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

# Experiments (manifest-driven)
vxedge experiment up --manifest vxperiments/exp-001.yaml
vxedge experiment down --manifest vxperiments/exp-001.yaml

# Traffic generation 
vxedge traffic up --manifest ...

```

---

## 6 — Experiment manifest — final schema (YAML)

```yaml
experiment:
  id: <string>
  name: <string>
  description: <string>
  duration_s: <int>
  results_prefix: <path>

network:
  topology: mesh|star|custom
  defaults:
    bandwidth: <bps>
    latency: <ms>

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
    services:
      - <service-id>

zones:
  - id: vxzone-<zone>-<seq>
    name: <human-readable>
    role: front-left | front-right | rear-left | rear-right | central-hpc | gateway
    nodes:
      - id: node-<type>-<seq>
        type: ecu | sensor | gateway | infotainment | telemetry-client
        function: <text>
        image:
          url: <image url>
          kind: vm | container | rtimage
        network:
          - iface: <name>
            vlan: <vlan id>
    services:
      - <service-id>

links:
  - from: <vxid or vxid:nodeid>
    to: <vxid or vxid:nodeid>
    type: vlan_trunk | vxlan | wireguard | direct
    properties:
      - { vlan: <id> }

traffic_profiles:
  <profile-id>:
    source: <vxid:nodeid or 'internet'>
    target: <vxid:nodeid or 'internet'>
    pps: <int>
    bandwidth_mbps: <int>
    payload_bytes: <int>

telemetry:
  prometheus:
    scrape_targets:
      - <host:port>
  pcap:
    interfaces:
      - name: <iface>
        duration_s: <int>

results:
  artifact_dir: path/to/results/exp-001
  upload: false
  upload_target: <registry or s3>
```

---

## 7 — Network model & RouterOS patterns (CCR2004)

- Use VLANs per slice with per-slice queue-tree reservations.
- VXLAN tunnels for inter-host communications.
- WireGuard for secure telemetry and OTA transport.
- Routing: static for lab experiments, optional BGP for cloud interconnect.
- Queueing: hierarchical with guaranteed min-rate for URLLC slices.
- Monitoring: RouterOS SNMP + syslog to central Prometheus node.

---

## 8 — Service model (OTA, telemetry, extensibility)

- All services defined under top-level `services` in the manifest.
- Only `ota` and `telemetry` types supported for simplicity.
- Services can be referenced in `zones` or `compute` nodes.
- CLI deploys services on-demand via `vxedge service <name> up|down --experiment <manifest>`.
- Extensible: future `vxsvc-*` repos can be added and referenced in manifests.
- Each service definition includes `id`, `type`, `image`, `config`.

---

## 9 — Virtualization & zone provisioning (QEMU, RTOS, containers)

- Zones run on host virtualization (QEMU/KVM) or containers.
- RTOS zones: FreeRTOS, Zephyr microVM images.
- Android Automotive zones: QEMU with GPU passthrough where possible.
- CLI stages images, creates VM instances, and configures network interfaces.
- Persistent storage optional per zone; logs and telemetry collected centrally.

---

## 10 — Compute model (vxcompute — Autoware/ROS2, inference, OTA hosting)

- Compute nodes run containerized workloads (Autoware, ROS2).
- OTA server may be deployed in a compute node if referenced in the experiment manifest.
- Compute nodes can host inference workloads; resources declared in manifest (`cpu`, `memory`).
- Services deployed dynamically as per manifest references.

---

## 11 — Edge agents & telemetry collection (vxagents / vxtelemetry)

- Rust agents deployed per experiment to collect metrics, latency, and traffic.
- Prometheus exporters for centralized metric collection.
- Optional PCAP capture for detailed traffic analysis.
- Agents and telemetry services configured via manifest and CLI commands.
- Designed to be lightweight to avoid perturbing experiment results.

---

## 12 — Experiment methodology, metrics, and analysis plan

**Methodology:**

1. **Preparation:**
   - Validate manifest syntax and semantics.
   - Stage images on host(s) using CLI.
   - Ensure CCR2004 VLANs and queue trees are configured per slice.

2. **Execution:**
   - `vxedge experiment up` to provision edge, zones, compute, and services.
   - Generate traffic as per `traffic_profiles`.
   - Collect telemetry (Prometheus + PCAP) and service logs.

3. **Postprocessing:**
   - Extract metrics from Prometheus exporters.
   - Parse PCAPs for latency, jitter, packet loss.
   - Aggregate results per slice and per node.

**Metrics:**

- **Network:** p50/p95/p99 latency, jitter, packet loss per slice.
- **Compute:** CPU/memory utilization, service response times.
- **OTA:** deployment success rate, artifact delivery latency.
- **Telemetry agents:** data ingestion rates, metric completeness.

**Analysis plan:**

- Compare latency/jitter under different virtualization choices.
- Evaluate slice isolation under heavy multi-zone traffic.
- Quantify OTA and telemetry impact on URLLC slices.
- Generate reproducible tables, charts, and CSV datasets for publication.

---

## 13 — Reproducibility, CI/CD, artifact publication (registries)

- **Reproducibility:**
  - All manifests under `vxperiments` are versioned and authoritative.
  - Images and RTOS builds tagged with SHA256 digest.
  - CLI ensures idempotent `up|down` operations.

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

- **Security:**
  - WireGuard for encrypted telemetry and OTA transport.
  - Images validated with SHA256 digests.
  - No root exposure in containerized services.
  - CCR2004 firewall configured per VLAN.

- **Licensing:**
  - Open-source Rust CLI and agents (MIT/Apache-2.0).
  - RTOS images may carry separate licenses (FreeRTOS, Zephyr).
  - Autoware/ROS2 under Apache-2.0.

- **Industrialization notes:**
  - All manifests modular, reusable across multiple experiments.
  - Edge gateway patterns applicable to physical SDV prototypes.
  - CI/CD pipelines support automated image and manifest validation.
  - Publishable results designed to integrate into research papers or internal dashboards.

---

## 15 — Appendix: example manifests, RouterOS snippets, run sequence

### Example experiment manifest snippet

```yaml
experiment:
  id: exp-001
  name: ADAS slice isolation test
  duration_s: 1800
  results_prefix: results/exp-001

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

### RouterOS CCR2004 snippet

```text
/interface vlan
add name=vlan-front-left vlan-id=101 interface=ether1
add name=vlan-front-right vlan-id=102 interface=ether1
add name=vlan-rear-left vlan-id=103 interface=ether1
add name=vlan-rear-right vlan-id=104 interface=ether1
add name=vlan-central-hpc vlan-id=105 interface=ether1
add name=vlan-gateway vlan-id=106 interface=ether1



/queue tree
add name=adas parent=ether1 max-limit=100M
add name=infotain parent=ether1 max-limit=500M
```

### Run sequence (CLI)

1. `vxedge up`
2. `vxedge zone up --vxid vxzone-front-left`
3. `vxedge zone up --vxid vxzone-front-right`
4. `vxedge compute up --vxid vxcompute-central`
5. `vxedge service ota up --experiment vxperiments/exp-001.yaml`
6. `vxedge service telemetry up --experiment vxperiments/exp-001.yaml`
7. `vxedge experiment up --manifest vxperiments/exp-001.yaml`
8. Collect results: `vxedge telemetry collect --manifest vxperiments/exp-001.yaml --out results/exp-001.zip`
9. Tear down: `vxedge experiment down --manifest vxperiments/exp-001.yaml` then services, compute, zones, edge

---
