# PROVISIONING.md — node-provisioning engine + vehicle-fleet layer

Single, self-contained working document for this initiative: design, use-case manifests,
functional requirements, and task-board status, all in one place (consolidated 2026-08-10 from a
separate `NODE-PROVISIONING.md` + `docs/ROADMAP.md` Track V split — this work is substantial enough
to pick up in isolation without juggling files). Governs `crates/vxedge-core/src/zones/`, the new
`crates/vxedge-core/src/containers/` module, their relationship to `crates/vxedge-core/src/
fiveg/`, and (Track F) a multi-vehicle-instance layer above `VehicleService`. Read `ARCHITECTURE.md`
§9 (virtualization) and §15 (containerization policy) first — this doc extends both, contradicts
neither.

**How to read this document, in order:** §1–2 grounds scope and reviews an external proposal that
prompted this work. §3 is the **use-case-driven methodology** this initiative follows — real YAML
manifests first, validated, before any Rust abstraction is designed. §4 is the current draft use
case (a six-zone reference vehicle) awaiting that validation. §§5–9 are the design derived from
existing patterns (written before §3's methodology was adopted as house process for this
initiative — kept because it's still correct, but §3's use case is what governs new decisions from
here on, not the other way around). §10 is the task board — Track V (single-vehicle node
provisioning) and Track F (multi-vehicle fleet layer), with live status.

## 1. What this layer is for, and what it is not for

vxedge is a **research platform** evaluating 5G network slicing over zonal/central SDV
architectures, running on **commodity dev-host / GPU-host hardware** — not a production
automotive ECU, and not a functional-safety-certified target. `ARCHITECTURE.md`'s own framing:
"entirely in software," QEMU/KVM VMs "managed via libvirt by default with a raw-QEMU microVM
backend option." The metrics this platform is built to produce (§12: p50/p95/p99 slice latency,
jitter, packet loss, OTA delivery latency, telemetry completeness) are all measured **above** the
virtualization layer, not inside it. Nothing in the platform's phase gates (H1–H4, `docs/ROADMAP.md`)
depends on hypervisor boot latency, vCPU-exit handling cost, or virtio ring-buffer throughput —
those would matter enormously if vxedge *were* building production ECU firmware; they are not
what phase 1–3 gates measure.

This matters because it sets the actual bar for this layer: **reliable, idempotent, low-drama
provisioning of heterogeneous nodes**, using components mature and audited enough that engineering
time goes into the 5G-slicing research question, not into re-deriving virtualization primitives
the industry has already spent a decade hardening. A design that optimizes for ECU-grade
determinism and in-process vCPU thread loops is solving a problem this project does not have, at
the cost of one it does: shipping the actual provisioning layer soon, on a foundation that doesn't
need a security audit before the next experiment campaign can trust it.

If vxedge's mission changes — if a later phase genuinely targets a real embedded ECU deployment
target rather than a dev-host research testbed — revisit §2's verdict. Nothing here forecloses
that; it just isn't today's problem.

## 2. Review of the external proposal ("Gemini brief")

An external proposal (pasted into this repo's task history 2026-08-07, not otherwise recorded)
argued for a from-scratch, in-process VMM: `vxedge-core` opens `/dev/kvm` directly, issues
`KVM_CREATE_VM`/`KVM_RUN` ioctls itself, runs vCPU loops on native threads, implements VirtIO ring
buffers by hand, and adds a WASM-capsule execution mode for RTOS/MCU-class nodes — explicitly to
avoid shelling out to `qemu-system-*`/`firecracker`/`libvirtd`/incus. It asked for this "as fast as
possible."

**Verdict: reject the from-scratch in-process VMM; adopt two of the proposal's real components on
their own merits, at a much narrower scope than proposed.**

### 2.1 Fact-check of the named components

The proposal cites specific crates/projects as the stack. Checked against real sources (not taken
on faith, since a proposal this specific deserves the same verification this repo applies to any
other technical claim):

| Named component | Verdict |
|---|---|
| `kvm-ioctls`, `vm-memory`, `virtio-queue` (rust-vmm) | **Real, mature, corporate-backed** (AWS/Google/Intel via the rust-vmm org). Firecracker and Cloud Hypervisor are both built on exactly these crates — this is accurate. |
| `bollard` + `nix` (containers) | **Real, mature.** Already the direction this repo independently converged on for container provisioning (§4). |
| `libkrun` | **Real**, Red Hat-backed (`containers/libkrun`), incorporates code from Firecracker/rust-vmm/Cloud-Hypervisor. Its actual purpose is process-isolation-via-lightweight-VM, notably for platforms (macOS) that can't run real containers natively — **not an obvious fit here**, since this platform already runs real containers natively via Podman. Citing it as a justification for building a *custom* VMM undersells that libkrun itself is a finished, adoptable VMM — if anything it's a counter-argument to hand-rolling one. |
| `fdt-rs` | **Real**, mature-ish, `no_std` flattened-device-tree parser. Legitimate, narrow-purpose — relevant only if/when this platform boots ARM guests needing synthetic device-tree injection, which it does not today. |
| `treVM` | **Real, but not what the proposal implies.** It's a 2026 academic paper and prototype (IEEE DCOSS-IoT 2026, arXiv 2604.27570) — "Tiny Rust Embedded Virtual Machines with WASM," built *specifically on top of Ariel OS* (a general-purpose Rust RTOS for 32-bit microcontrollers), using Wasmtime as its WASM runtime. It is months old, tied to one specific RTOS, and not a general-purpose crate this codebase could add to `Cargo.toml` and use standalone. Treating it as a stable stack component on par with `kvm-ioctls` significantly overstates its maturity. |
| `virtio-loopback` | **Not found.** No crate, project, or paper under this name turned up in a direct search. Every other component in the proposal traces to something real; this one doesn't. Flagged plainly rather than built around: don't design anything that depends on a component that may not exist. |

### 2.2 The scope problem, independent of the fact-check

Even where every cited component were real and mature, building a from-scratch VMM is the wrong
call for this project **right now**, for reasons that would hold even if the fact-check above had
come back clean:

- **"As fast as possible" and "raw KVM ioctls + hand-rolled VirtIO rings + custom seccomp filters"
  are contradictory asks.** Firecracker and Cloud Hypervisor are exactly this design, built by
  dedicated teams over years, security-audited, and battle-tested at hyperscale. Re-deriving that
  from primitives is one of the slowest, highest-risk paths available — not a shortcut to
  avoiding "external binary execution," a multi-year systems-engineering undertaking wearing the
  clothes of one.
- **The stated justification (storage bloat, brittle CLI text-parsing, functional-safety
  determinism) describes a resource-constrained production ECU, not this project's actual
  deployment target** (§1). Cloud Hypervisor and Firecracker already solve "no CLI text-parsing" —
  both are API-first over a Unix socket, no stdout-scraping involved — without requiring this repo
  to own vCPU-exit handling.
- **Safety-relevant framing ("Freedom from Interference," ISO-26262-flavored mixed-criticality
  isolation) implies a certification bar this repo has no process for and does not need for its
  actual research questions.** Claiming FFI-grade isolation from a from-scratch, unaudited VMM
  would be a false claim of rigor this project doesn't have the process to back up — worse than
  not claiming it at all.

### 2.3 What's worth keeping

Two ideas in the proposal are genuinely good, decoupled from the in-process-VMM framing:

- **A lightweight, sandboxed execution mode for RTOS/MCU-class control-loop nodes** is a real gap
  today — `ARCHITECTURE.md` §9's guest palette already names Zephyr/FreeRTOS as microVM images for
  "sensor/ECU nodes," which means today's only option for that zone class is a full microVM boot
  (qemu-microvm or, per §6/§7, eventually Cloud Hypervisor) even for a node that might genuinely
  be simulable as a sandboxed control loop with no real kernel underneath.
  **Wasmtime directly** (mature, audited, in production use well beyond research contexts) is worth
  prototyping for exactly this — decoupled from `treVM`/Ariel-OS specifically, which this repo has
  no reason to depend on. See §7.3.
- **`fdt-rs`** stays a legitimate, cheap-to-adopt-later component if/when this platform boots ARM
  guests that need synthetic device-tree injection (AAOS on ARM is on the roadmap). Not needed
  today; no action now; noted for when it is.

## 3. Use-case-driven methodology (governs how this initiative proceeds from here)

Directive from the project architect, 2026-08-08/2026-08-10: design this bottom-up from real use
cases, not top-down from abstract principle. Concretely, the order is:

1. **Real YAML use cases first** — actual `kind: vehicle` + `kind: baseline` manifests
   representing a genuine software baseline: the virtual appliances/devices it's built from, the
   resources they need, and the requirements they carry. Not a toy two-device example the way
   most of today's experiment vehicles are (deliberately minimal, scoped to one hypothesis each)
   — a topology closer to what a real prototype vehicle's E/E architecture actually looks like:
   many nodes, many roles, many `vxparts` references, across all six zone positions.
2. **Validate the use case** — reviewed by the architect before anything downstream is built on
   it. §4 below is that draft, awaiting exactly this review. Nothing in §§5–9 is re-derived from
   §4 yet; §§5–9 predate this methodology (written 2026-08-07, kept because still correct) and
   §4 is checked against them for consistency, not the other way around, going forward.
3. **Only then, functional requirements / abstractions** — what does provisioning *this* topology
   actually demand of the Rust API layer, derived from what's really in the manifest (how many
   node kinds, which backends they actually need, what a realistic `parts:` list references) —
   not from a hypothetical worst case.
4. **Only then, implementation** — the provisioning-backend work (Track V's task board, §10).

Why this order, not the reverse: §§5–9's design (spec-translation split, the generic `containers`
module, the CLI-vs-library test) was derived from what already exists in code plus reasoning about
what backends are available — sound, but not yet checked against a real, full-scale vehicle
topology. A "true prototype car" manifest is the cheapest possible way to find out whether that
design actually holds at realistic scale (does the `containers` module's group-per-pod shape
still fit when central-hpc hosts three containerized functions instead of one podman-pod's worth?
does `VmSpec` still cover every zone-class device once there are a dozen of them, not two?) before
committing Rust API surface to it.

## 4. Draft use case: a six-zone reference vehicle (awaiting validation)

This populates a real, already-scoped `vxparts` backlog item, not an invented example:
`vxparts/parts/veh/car/config/reference-sedan-6zone` (`ghcr.io/vxedge/parts/veh/car/config/
reference-sedan-6zone`) has existed since Track D as a named, `todo`-status placeholder — its own
README states the two ways to populate it: "author a genuinely new six-zone reference topology…
or defer to Track M/`vxmodels` to render it from SysML." This draft takes the first path, as a
concrete, reviewable YAML artifact rather than waiting on SysML tooling that doesn't exist yet.

### 4.1 Topology

All six canonical zone roles (`ARCHITECTURE.md` §3) except `gateway` — consistent with every
existing vehicle manifest in `vxperiments`, none of which declares a `gateway` zone entry; the
gateway is provisioned separately by `GatewayService` from the experiment's own network/slices,
never as a vehicle device. `central-hpc` hosts the AD compute stack; the four corner zones each
carry a small, realistic device mix (an ECU plus a sensor or actuator) rather than one device
each, per the "so many vxparts, true prototype car" framing this draft is checking §§5–9 against.

**Honesty constraint, stated once here rather than per line below**: today's only *real, live,
registry-verified* zone-class guest bundle is `zone/linux/stack/probe-bundle:0.1.0`
(`sha256:33c9c8d8625bd5c6d1f4d3d0c561fdaa930e057fcd1fb24fb3badb402f25429d`, re-verified via `oras
resolve` while drafting this). QNX/AAOS/Zephyr have **zero published parts** — confirmed by
listing `vxparts/parts/zone/{qnx,aaos,zephyr}/os/`, all empty. `hpc/ad/stack/ad-baseline` (the
real composite this draft wants for `central-hpc`) has real source files in the `vxparts` repo but
**failed live `oras resolve`** (`ghcr.io/vxedge/parts/hpc/ad/stack/ad-baseline:0.1.0: not found`)
— its own composite-publish script requires every constituent (including `hpc/ad/config/
autoware-params`) published first, and at least one hasn't been. So every device below uses
`probe-bundle` as its actual bundle today, with a comment naming the RTOS/guest image a real
deployment would eventually use once that part exists — exactly `vx-vehicle-01`'s own precedent
("one device is enough… without waiting on a production-representative guest image"), extended to
six zones instead of one.

| Zone | Device | Role | Real backend today | Aspirational guest (not yet published) |
|---|---|---|---|---|
| front-left | `fl-safety-ecu` | ecu | qemu-microvm + `probe-bundle` | QNX SDP 8 (safety ECU) |
| front-left | `fl-camera-sensor` | sensor | qemu-microvm + `probe-bundle` | Zephyr/FreeRTOS |
| front-right | `fr-body-ecu` | ecu | qemu-microvm + `probe-bundle` | QNX SDP 8 |
| front-right | `fr-steer-actuator` | actuator | qemu-microvm + `probe-bundle` | Zephyr/FreeRTOS |
| rear-left | `rl-radar-sensor` | sensor | qemu-microvm + `probe-bundle` | Zephyr/FreeRTOS |
| rear-right | `rr-brake-actuator` | actuator | qemu-microvm + `probe-bundle` | Zephyr/FreeRTOS |
| central-hpc | `hpc-ad-01` | hpc | container + `ad-baseline` **(unverified — see above)** | n/a, already Linux-container-native |

Deliberately **not** included: an AAOS/IVI device (no real or realistically-composable part
exists yet for it — adding one here would mean inventing a fictional part ref, which this draft
won't do) and `svc`-class parts (`kuksa-databroker`, `vxota`) — those are experiment-level
`services:` block entries per §6.0's "vehicle names a slice; the experiment defines it" rule
extended to services, not vehicle-manifest `functions:`, so they belong in a companion experiment
manifest, not here.

### 4.2 `vehicle.yaml` (draft)

```yaml
kind: vehicle
id: vx-reference-sedan-01
class: road
subtype: car

# Six-zone reference topology (vxparts veh/car/config/reference-sedan-6zone). Every zone-class
# device uses the one real, registry-verified guest bundle (zone/linux/stack/probe-bundle)
# today; the `role` below is the honest structural label this manifest is making a claim about
# -- the differentiated RTOS image that role implies (QNX for ecu, Zephyr/FreeRTOS for
# sensor/actuator) does not exist as a published vxparts part yet. Grow this file part-by-part
# as those land, per vx-vehicle-01's own precedent.
zones:
  front-left: {}
  front-right: {}
  rear-left: {}
  rear-right: {}
  central-hpc: {}

devices:
  fl-safety-ecu:      { role: ecu,      zone: front-left,  backend: qemu-microvm }
  fl-camera-sensor:   { role: sensor,   zone: front-left,  backend: qemu-microvm }
  fr-body-ecu:        { role: ecu,      zone: front-right, backend: qemu-microvm }
  fr-steer-actuator:  { role: actuator, zone: front-right, backend: qemu-microvm }
  rl-radar-sensor:    { role: sensor,   zone: rear-left,   backend: qemu-microvm }
  rr-brake-actuator:  { role: actuator, zone: rear-right,  backend: qemu-microvm }
  hpc-ad-01:          { role: hpc,      zone: central-hpc, backend: container }

functions:
  fl-safety-fn:     { deployed_on: fl-safety-ecu }
  fl-camera-fn:     { deployed_on: fl-camera-sensor }
  fr-body-fn:       { deployed_on: fr-body-ecu }
  fr-steer-fn:      { deployed_on: fr-steer-actuator }
  rl-radar-fn:      { deployed_on: rl-radar-sensor }
  rr-brake-fn:      { deployed_on: rr-brake-actuator }
  hpc-ad-fn:        { deployed_on: hpc-ad-01 }

links:
  - id: link-fl-safety
    endpoints: [{ node: fl-safety-ecu, port: eth0, ip: 10.120.1.11/24 }]
    slice: adas
  - id: link-fl-camera
    endpoints: [{ node: fl-camera-sensor, port: eth0, ip: 10.120.1.12/24 }]
    slice: adas
  - id: link-fr-body
    endpoints: [{ node: fr-body-ecu, port: eth0, ip: 10.120.2.11/24 }]
    slice: adas
  - id: link-fr-steer
    endpoints: [{ node: fr-steer-actuator, port: eth0, ip: 10.120.2.12/24 }]
    slice: adas
  - id: link-rl-radar
    endpoints: [{ node: rl-radar-sensor, port: eth0, ip: 10.120.3.11/24 }]
    slice: adas
  - id: link-rr-brake
    endpoints: [{ node: rr-brake-actuator, port: eth0, ip: 10.120.4.11/24 }]
    slice: adas
  - id: link-hpc-ad
    endpoints: [{ node: hpc-ad-01, port: eth0, ip: 10.120.5.11/24 }]
    slice: adas
```

### 4.3 `parts.yaml` (draft baseline)

```yaml
kind: baseline
id: bl-vx-reference-sedan-01

parts:
  # Real, live, registry-verified (re-checked via `oras resolve` while drafting this section).
  - ref: ghcr.io/vxedge/parts/zone/linux/stack/probe-bundle:0.1.0
    digest: sha256:33c9c8d8625bd5c6d1f4d3d0c561fdaa930e057fcd1fb24fb3badb402f25429d
    target_ids: [fl-safety-fn, fl-camera-fn, fr-body-fn, fr-steer-fn, rl-radar-fn, rr-brake-fn]

  # NOT verified live -- `oras resolve` on this tag failed (2026-08-10, "not found"). Source
  # files exist in vxparts but the composite has not actually been published; at least one
  # constituent (hpc/ad/config/autoware-params) is itself unpublished. Do not treat this
  # manifest as executable until this entry is either resolved live or replaced.
  - ref: ghcr.io/vxedge/parts/hpc/ad/stack/ad-baseline:0.1.0
    digest: "TBD -- unverified, see note above"
    target_ids: [hpc-ad-fn]
```

### 4.4 What validating this means

Not "does it parse" — `vxedge experiment validate`-shaped correctness is necessary but not the
point. Validation here means the architect confirming: (a) this is a realistic-enough shape for a
prototype car (device mix per zone, role choices, whether seven devices is the right scale or
too few/many for what "so many vxparts" was asking for); (b) the honesty framing (real vs.
aspirational parts) is the right way to handle the QNX/AAOS/Zephyr/ad-baseline gaps, versus some
other resolution (e.g., blocking on publishing `ad-baseline` for real first); (c) whether a second
draft use case is needed (e.g., one that includes an experiment-level `services:` block alongside
this vehicle, showing kuksa-databroker/vxota in their correct place) before moving to §3 step 3.

## 5. What already exists (do not re-derive)

- `crates/vxedge-core/src/zones/backend.rs` — `ZoneBackend` trait, three implementations
  (`ContainerBackend` netns-only, `QemuMicrovmBackend` raw QEMU CLI, `LibvirtBackend` `virsh`
  CLI), one dispatch site `backend_for(kind)`. `kernel_cmdline`/`bundle_paths` are already pure,
  shared spec-translation functions — the split principle below extends what's already there.
- `crates/vxedge-core/src/fiveg/lifecycle.rs` — a separate, pod-shaped podman CLI integration for
  the 5G core, unrelated to `ZoneBackend`.
- `NodePlan` (`zones/plan.rs`) — pure desired-state data, already carries `bundle`/`remote_bundle`
  (mutually exclusive, "planning records intent only, never fetches") as the precedent for any new
  optional per-backend field.
- `Shell` (`gateway/netops.rs`) — the CLI-shelling primitive, `escalate` injected not computed.
- Sequential, single-node-at-a-time provisioning (`stage_zones` in `crates/vxedged/src/
  experiment.rs`) is deliberate: exp-002b showed concurrent guest startup causes CPU contention
  that invalidates measurement campaigns. Nothing in this doc changes that.

## 6. The provisioning stack this repo is actually building

```
                    vxedge-core (in-process, pure-Rust orchestration)
   ┌──────────────────────────────────────────────────────────────────────┐
   │  ZoneBackend seam (zones/backend.rs)     containers/ module (new)    │
   └──────────────────────────────────────────────────────────────────────┘
        │                    │                    │              │
        ▼                    ▼                    ▼              ▼
 ┌─────────────┐     ┌──────────────┐     ┌──────────────┐  ┌───────────┐
 │  libvirt     │     │ qemu-microvm │     │Cloud Hyperv- │  │  bollard  │
 │  (virt crate)│     │ (unchanged,  │     │ isor client  │  │ (Podman   │
 │              │     │  no further  │     │ (Phase B,    │  │  Docker-  │
 │              │     │  investment) │     │  spiked)     │  │  compat)  │
 └──────┬───────┘     └──────┬───────┘     └──────┬───────┘  └─────┬─────┘
        │                    │                    │                │
        ▼                    ▼                    ▼                ▼
   libvirtd,           /dev/kvm via         /dev/kvm via       Podman daemon,
   in-process FFI,      QEMU's own           CH's own          rootless user
   no sudo needed        process              process             socket
```

Every box here is an **existing, audited, already-maintained** VMM or container engine, reached
via its own stable API (FFI or a Unix-socket REST client) instead of a CLI's stdout. None of it
requires `vxedge-core` to own `/dev/kvm` directly, a vCPU thread loop, or a VirtIO ring-buffer
implementation — that engineering already exists, upstream, security-audited, and this repo
consumes it rather than re-derives it.

## 7. Design principles

### 7.1 Split spec translation from launch, at the grain that's real

One pure `VmSpec` (kernel/initrd/cmdline/pinned_cpus/endpoint) shared by every VM-shaped engine
(qemu-microvm today, libvirt, Cloud Hypervisor once spiked); one pure `ContainerSpec`
(image/entrypoint/env) for container-shaped engines. Neither is part of `ZoneBackend`'s
object-safe trait signature (an associated type would break `&dyn ZoneBackend`) — each is an
internal discipline a backend module follows, consolidating what `kernel_cmdline`/`bundle_paths`
already do today into one named, reusable spec per execution model.

### 7.2 A generic container-provisioning module — not owned by `fiveg`, not owned by `zones`

New module: `crates/vxedge-core/src/containers/mod.rs`. Owns a `bollard`-backed `ContainerClient`
and a `ContainerGroup` primitive (an infra container providing a shared netns, joined via
`NetworkMode: container:<infra_id>` — bollard has no native "pod" concept, so this makes the
group explicit). Consumed by **two** real call sites: `fiveg::lifecycle` (today's podman CLI
calls become `ContainerClient` calls) and the zone `container` backend's future OCI payload
(currently netns-only). Two real call sites from day one is what earns this as a seam under this
repo's own `service-boundaries` rule ("two implementations, or two call sites") — not a
speculative abstraction.

### 7.3 A lightweight capsule mode for control-loop nodes — prototyped, not assumed

Decoupled from `treVM`/Ariel-OS: a `WasmCapsuleBackend` (fourth `ZoneBackend` impl, gated behind
its own manifest `backend: wasm-capsule` value) that runs a `.wasm` module via `wasmtime` directly,
in-process, for zone nodes that are genuinely simulable as a sandboxed control loop rather than a
full guest kernel — a real, currently-unserved gap for the Zephyr/FreeRTOS "sensor/ECU node" class
(§9's own guest palette). This is a **prototype-and-evaluate** item, not committed infrastructure:
build one, run it against one real sensor-node manifest, and decide based on results whether it
earns permanent status. `wasmtime` itself is the only new dependency this needs — mature, widely
audited, no in-process-VMM ioctl work required.

### 7.4 Considered and rejected

- **Runtime backend registry.** `backend_for`'s static `match` already satisfies "dispatch once,
  at one site." A registry only earns its complexity if selection needs to be dynamic; `Backend`
  is a closed, manifest-declared enum — it doesn't.
- **Typestate lifecycle enum** (`Defined→Starting→Running→Stopped` as distinct types). Competes
  with `NodeState`/`Observable` as a second source of truth for the same fact; the reconciler
  model (`up`/`down` converge desired vs. observed) doesn't want a client-side FSM.
- **In-process raw-KVM hypervisor.** §2.

### 7.5 CLI vs. library — the decision test

Does adopting a backend's library avoid requiring anything beyond what the testbed already
installs for other reasons, or is there no meaningful CLI to shell out to in the first place (the
backend is API-first)? If yes to either, the library wins.

| Backend | CLI today | Library | Verdict |
|---|---|---|---|
| libvirt | `virsh` | `virt` crate | **Library.** `libvirtd` already required (Tier 2); `libvirt-dev` headers are one new doc line, not a new daemon family. Removes the last CLI-shell privilege-escalation exposure on the VM side — `virt`'s FFI runs in-process against `libvirtd`, authorized by group membership, no `sudo` at all. |
| Podman | `podman` CLI | `bollard` | **Library, close to free.** The REST-compatible socket exists on any Podman install but isn't enabled by default; must be the rootless **user** socket specifically (a different identity resolves a different, possibly-unbuilt image store — a real incident already lived through, 2026-07-17). |
| Cloud Hypervisor | `ch-remote` (itself a thin wrapper) | `cloud-hypervisor-client` | **Library, not close.** API-first by design; shelling to a wrapper-of-a-wrapper is strictly worse. |
| Raw `qemu-system-x86_64` | Direct process launch | None that fits (QMP is a hand-rollable protocol, not a maintained crate for this use case) | **No library to reach for — the actual finding.** Stop investing in `QemuMicrovmBackend` beyond its current (2026-08-06) fixed state; new VM-side effort goes to the Cloud Hypervisor spike instead. |

## 8. Testing approach (TDD, three tiers — this repo's existing convention, applied here)

1. **Unit — pure spec-translation logic first, before any backend touches it.** `VmSpec`/
   `ContainerSpec` construction from a `NodePlan`, and the `containers` module's `ContainerGroup`
   naming/idempotency logic, are pure functions — write their tests before the `bollard`/`virt`
   call that consumes them, exactly the discipline `core_run_specs` already demonstrates in
   `fiveg::lifecycle` (pure, unit-tested without touching podman).
2. **Unprivileged e2e in plain `cargo test`.** Anything that can run without root/KVM/a real
   daemon (error-path construction, idempotency-check logic against a fake `NodeState`) stays in
   the default `cargo test` run.
3. **Privileged/environmental behind `#[ignore]`**, with a reason string, mirroring
   `gateway-verification`'s existing convention: a live libvirt domain define/start/destroy, a
   live Podman group stand-up, a live Cloud Hypervisor VM boot. Plain `cargo test` must always
   pass unprivileged.

Every new backend lands with all three tiers present before being wired into `backend_for`'s
match — not after, per this repo's existing `rust-patterns` house rule.

## 9. Roadmap

See §10 for the phased, numbered task list (Track V + Track F) this document's design maps to.
Summary: Track V phase 1 (containers module + fiveg migration, libvirt→virt crate) is scoped and
ready to start once §4's use case is validated; Track V phase 2 (Cloud Hypervisor spike) follows
once phase 1 lands; the WASM-capsule prototype (§7.3) is an independent, parallel-track
evaluation; the in-process-VMM direction (§2) is recorded as reviewed and rejected, not silently
dropped, so a future session doesn't re-propose it without this document's reasoning in view;
Track F (multi-vehicle fleet layer) does not start until Track V is at a high success rate.

## 10. Task board

Moved here from `docs/ROADMAP.md` 2026-08-10, consolidating design and task status into one file.
**Status as of 2026-08-10: design phase. §4's use case is drafted and awaiting validation; no
Track V or Track F item has started implementation.** This section is the live status —
update it in place as items move, rather than appending a separate changelog.

### Track V — node-provisioning engine (single vehicle)

Extends Track C (`docs/ROADMAP.md`), gates nothing in phases 1–3. Blocked on §4's use case being
validated (§3) before V0/V1 implementation starts — the use case is what confirms the design in
§§5–9 actually holds at realistic scale before Rust API surface commits to it.

- [ ] V0 — `LibvirtBackend`: `virsh` CLI → `virt` crate (`vxedge-core::zones::backend`). Removes
      the last CLI-shell privilege-escalation exposure on the VM side entirely (in-process FFI
      against `libvirtd`, group-membership/polkit authorized, no `sudo` at all — stronger than
      the qemu-microvm tap-ownership fix, `docs/ROADMAP.md` 2026-08-06 entry). New build-time
      dependency on libvirt headers (`libvirt-dev`) — add to `docs/TESTBED-SETUP.md` Tier 2 in
      the same change, not as a follow-up. `libvirt_domain_xml`'s XML generation is untouched
      (pure, transport-independent); only `virsh()`'s CLI transport is replaced.
- [ ] V1 — generic `containers` module (`crates/vxedge-core/src/containers/mod.rs`, new): a
      `bollard`-backed `ContainerClient` + `ContainerGroup` primitive (infra container owns the
      shared netns; joiners attach via `NetworkMode: container:<infra_id>`, since bollard has no
      native pod concept). Two real call sites from day one, satisfying `service-boundaries`'
      own "two call sites" rule for a real seam, not a speculative one: `fiveg::lifecycle`
      (V2, below) and the zone `container` backend's future OCI payload (V3). Must connect to the
      rootless **user** Podman socket specifically, never the system socket — a different
      identity resolves a different, possibly-unbuilt image store (real incident, 2026-07-17,
      documented in `fiveg::lifecycle`'s history). `docs/TESTBED-SETUP.md` gains the socket
      enablement line (`systemctl --user enable --now podman.socket`) in the same change.
- [ ] V2 — migrate `fiveg::lifecycle`'s podman CLI calls (`podman()`, `pod_pid`, `pod_exists`,
      `run_detached`, `pod_containers`) onto V1's `ContainerClient`. `core_run_specs` and the
      veth/bridge/nsenter networking (`host_ip`/`nsenter_run`/`setup_transit_link`/
      `setup_upf_tun`) stay in `fiveg` unchanged — N2/N3-equivalent networking built on top of two
      container groups, not container management itself, does not move to `containers/`. Async
      ripple: `fiveg_up`/`bridge_up`/`ue_up`/`fiveg_down` become `async fn`; the four
      `blocking(...)` wrappers around them in `vxedged::services::ZoneSvc::lifecycle` come off in
      favor of direct `.await`.
- [ ] V3 — zone `container` backend gets a real OCI payload via V1's `ContainerClient` (currently
      netns-only, `zones::backend::container_up`). Open design question to resolve before
      starting, not mid-implementation: bollard has no "join a namespace by name" primitive
      (only "join another container's namespace by ID/PID") — likely direction is inverting
      control so the group's infra container provides the netns and the zone backend's veth peer
      moves in by the infra container's PID instead of by name.
- [ ] V4 — spike `CloudHypervisorBackend` (fourth `ZoneBackend` impl) using the
      `cloud-hypervisor-client` crate (OpenAPI-generated against CH's own REST-over-UDS API).
      Recommended over Firecracker for this project specifically: CH's richer device model
      (PCI, CPU/memory/device hotplug) is a better fit for the guest palette actually on the
      roadmap (QNX SDP 8, AAOS, Zephyr/FreeRTOS — `ARCHITECTURE.md` §9) than Firecracker's
      deliberately spartan five-device model, and no mature/canonical Firecracker Rust client was
      confirmed during evaluation (2026-08-07) where `cloud-hypervisor-client` was. Scoping
      caution: CH is headless — AAOS's own §9 line requires "virtio-gpu or GPU passthrough," so
      that guest stays on libvirt/QEMU regardless of this item. Validate first against the
      already-live-tested linux-probe bundle before attempting a richer guest; don't assert
      QNX-on-CH works without that empirical step. Companion decision, not a separate item: once
      V4 lands, stop further investment in `QemuMicrovmBackend` beyond its current (2026-08-06)
      fixed state — raw `qemu-system-x86_64` has no comparable typed Rust binding to reach for
      (QMP is a hand-rollable protocol, not a maintained crate), and CH is the gap that closes.
- [ ] V5 — prototype `WasmCapsuleBackend` (fifth `ZoneBackend` impl, `backend: wasm-capsule`):
      run a `.wasm` module via `wasmtime` directly, in-process, for zone nodes simulable as a
      sandboxed control loop rather than a full guest kernel — a real, currently-unserved gap for
      the Zephyr/FreeRTOS "sensor/ECU node" class (today's only option is a full microVM boot).
      Deliberately decoupled from the external proposal's `treVM`/Ariel-OS coupling — `wasmtime`
      alone is the only new dependency, mature and audited independent of that pairing.
      **Evaluate-and-decide, not committed infrastructure**: build one, run it against one real
      sensor-node manifest, decide based on results whether it earns permanent status.
- [ ] V6 (parked, not scheduled) — `fdt-rs` for synthetic device-tree injection, if/when an ARM
      guest (AAOS on ARM) needs it. No action until that's a real, scheduled guest target.

**Explicitly rejected, recorded so it isn't re-proposed without this reasoning in view**: a
from-scratch, in-process KVM hypervisor (raw `kvm-ioctls` VM/vCPU management, hand-rolled VirtIO
ring buffers, custom seccomp filters) as this project's provisioning backend. Full reasoning in §2.

### Track F — vehicle-fleet layer (multiple concurrent vehicle instances over vxAPI)

**Hard gate, stated by the architect 2026-08-08: Track F cannot start until Track V is done with
a high success rate.** Not a parallel track — provisioning one vehicle reliably is the
prerequisite for provisioning many. Nothing below is scheduled until that gate opens.

Real current blocker, confirmed in code 2026-08-08 (not speculative): `EdgeState.active:
Option<ActiveExperiment>` (`crates/vxedged/src/services.rs:66`) is a single slot, and
`GatewayPlan::from_model` hardcodes `"vxbr0"`/`"vxup0"`/`"vxup0p"` as literal bridge/tap names
(`crates/vxedge-core/src/gateway/plan.rs:461-463`). Two concurrent `vehicle up` calls today
collide on the same bridge, full stop — this has to be fixed before any fleet layer can exist
above it, not as an implementation detail underneath one.

- [ ] F0 (blocked on Track V) — per-instance resource namespacing: derive bridge/tap/cache/
      runtime-dir names from the vehicle id (reuse `sha2`, already a workspace dependency, for a
      short stable hash — no new hashing crate) instead of the current hardcoded `vxbr0`-family
      literals.
- [ ] F1 (blocked on Track V) — `EdgeState.active` becomes a collection (`HashMap<VehicleId,
      ActiveInstance>` or similar) instead of `Option<ActiveExperiment>`'s single slot.
- [ ] F2 (blocked on F0/F1) — a vehicle-instance registry: `dashmap` (mature, sharded concurrent
      map — matches this codebase's own "don't reinvent a concurrent map" instinct) keyed by
      vehicle id, populated/removed by `VehicleService`'s existing `up`/`down`, queried by a new
      fleet-scoped RPC surface (list/status-all). Explicitly **not** an actor/supervision
      framework (`ractor` was considered and set aside 2026-08-08): for a handful of concurrent
      research-testbed vehicle instances, plain `tokio::task::JoinSet` + `dashmap` is
      proportionate and consistent with every other concurrency choice already in this codebase
      (`rust-patterns`' own mutex/channel rules) — revisit only if real fleet scale (dozens+,
      genuine fault-isolation needs between instances) materializes.
- [ ] F3 (blocked on F2) — fleet-scoped vxAPI surface (list active vehicles, status-all,
      bulk down) — proto design not started; needs its own pass once F0–F2 land and the shape of
      "an instance" (what state it carries beyond today's per-vehicle `VehicleStatus`) is clear
      from real use.
