# NODE-PROVISIONING.md — the in-process node-provisioning engine

Master spec for how `vxedge-core` brings up, tears down, and observes the heterogeneous nodes an
experiment or vehicle manifest can declare: zone-class VMs/microVMs, zone-class containers,
compute/HPC containers, and (proposed, not yet built) lightweight control-loop capsules. This
document governs `crates/vxedge-core/src/zones/`, the new `crates/vxedge-core/src/containers/`
module, and their relationship to `crates/vxedge-core/src/fiveg/`. Read `ARCHITECTURE.md` §9
(virtualization) and §15 (containerization policy) first — this doc extends both, contradicts
neither.

Written 2026-08-07 in response to a proposal for building the same capability as a from-scratch,
in-process KVM hypervisor. §2 reviews that proposal on its merits. §§3–7 are the design this repo
is actually adopting, which reuses it where it holds up and departs from it where it doesn't.

## 1. What this layer is for, and what it is not for

vxedge is a **research platform** evaluating 5G network slicing over zonal/central SDV
architectures, running on **commodity dev-host / GPU-host hardware** — not a production
automotive ECU, and not a functional-safety-certified target. `ARCHITECTURE.md`'s own framing:
"entirely in software," QEMU/KVM VMs "managed via libvirt by default with a raw-QEMU microVM
backend option." The metrics this platform is built to produce (§12: p50/p95/p99 slice latency,
jitter, packet loss, OTA delivery latency, telemetry completeness) are all measured **above** the
virtualization layer, not inside it. Nothing in the platform's phase gates (H1–H4, `docs/TASKS.md`)
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
  (qemu-microvm or, per `NODE-PROVISIONING.md` §4/§5, eventually Cloud Hypervisor) even for a node
  that might genuinely be simulable as a sandboxed control loop with no real kernel underneath.
  **Wasmtime directly** (mature, audited, in production use well beyond research contexts) is worth
  prototyping for exactly this — decoupled from `treVM`/Ariel-OS specifically, which this repo has
  no reason to depend on. See §5.3.
- **`fdt-rs`** stays a legitimate, cheap-to-adopt-later component if/when this platform boots ARM
  guests that need synthetic device-tree injection (AAOS on ARM is on the roadmap). Not needed
  today; no action now; noted for when it is.

## 3. What already exists (do not re-derive)

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

## 4. The provisioning stack this repo is actually building

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

## 5. Design principles

### 5.1 Split spec translation from launch, at the grain that's real

One pure `VmSpec` (kernel/initrd/cmdline/pinned_cpus/endpoint) shared by every VM-shaped engine
(qemu-microvm today, libvirt, Cloud Hypervisor once spiked); one pure `ContainerSpec`
(image/entrypoint/env) for container-shaped engines. Neither is part of `ZoneBackend`'s
object-safe trait signature (an associated type would break `&dyn ZoneBackend`) — each is an
internal discipline a backend module follows, consolidating what `kernel_cmdline`/`bundle_paths`
already do today into one named, reusable spec per execution model.

### 5.2 A generic container-provisioning module — not owned by `fiveg`, not owned by `zones`

New module: `crates/vxedge-core/src/containers/mod.rs`. Owns a `bollard`-backed `ContainerClient`
and a `ContainerGroup` primitive (an infra container providing a shared netns, joined via
`NetworkMode: container:<infra_id>` — bollard has no native "pod" concept, so this makes the
group explicit). Consumed by **two** real call sites: `fiveg::lifecycle` (today's podman CLI
calls become `ContainerClient` calls) and the zone `container` backend's future OCI payload
(currently netns-only). Two real call sites from day one is what earns this as a seam under this
repo's own `service-boundaries` rule ("two implementations, or two call sites") — not a
speculative abstraction.

### 5.3 A lightweight capsule mode for control-loop nodes — prototyped, not assumed

Decoupled from `treVM`/Ariel-OS: a `WasmCapsuleBackend` (fourth `ZoneBackend` impl, gated behind
its own manifest `backend: wasm-capsule` value) that runs a `.wasm` module via `wasmtime` directly,
in-process, for zone nodes that are genuinely simulable as a sandboxed control loop rather than a
full guest kernel — a real, currently-unserved gap for the Zephyr/FreeRTOS "sensor/ECU node" class
(§9's own guest palette). This is a **prototype-and-evaluate** item, not committed infrastructure:
build one, run it against one real sensor-node manifest, and decide based on results whether it
earns permanent status. `wasmtime` itself is the only new dependency this needs — mature, widely
audited, no in-process-VMM ioctl work required.

### 5.4 Considered and rejected

- **Runtime backend registry.** `backend_for`'s static `match` already satisfies "dispatch once,
  at one site." A registry only earns its complexity if selection needs to be dynamic; `Backend`
  is a closed, manifest-declared enum — it doesn't.
- **Typestate lifecycle enum** (`Defined→Starting→Running→Stopped` as distinct types). Competes
  with `NodeState`/`Observable` as a second source of truth for the same fact; the reconciler
  model (`up`/`down` converge desired vs. observed) doesn't want a client-side FSM.
- **In-process raw-KVM hypervisor.** §2.

### 5.5 CLI vs. library — the decision test

Does adopting a backend's library avoid requiring anything beyond what the testbed already
installs for other reasons, or is there no meaningful CLI to shell out to in the first place (the
backend is API-first)? If yes to either, the library wins.

| Backend | CLI today | Library | Verdict |
|---|---|---|---|
| libvirt | `virsh` | `virt` crate | **Library.** `libvirtd` already required (Tier 2); `libvirt-dev` headers are one new doc line, not a new daemon family. Removes the last CLI-shell privilege-escalation exposure on the VM side — `virt`'s FFI runs in-process against `libvirtd`, authorized by group membership, no `sudo` at all. |
| Podman | `podman` CLI | `bollard` | **Library, close to free.** The REST-compatible socket exists on any Podman install but isn't enabled by default; must be the rootless **user** socket specifically (a different identity resolves a different, possibly-unbuilt image store — a real incident already lived through, 2026-07-17). |
| Cloud Hypervisor | `ch-remote` (itself a thin wrapper) | `cloud-hypervisor-client` | **Library, not close.** API-first by design; shelling to a wrapper-of-a-wrapper is strictly worse. |
| Raw `qemu-system-x86_64` | Direct process launch | None that fits (QMP is a hand-rollable protocol, not a maintained crate for this use case) | **No library to reach for — the actual finding.** Stop investing in `QemuMicrovmBackend` beyond its current (2026-08-06) fixed state; new VM-side effort goes to the Cloud Hypervisor spike instead. |

## 6. Testing approach (TDD, three tiers — this repo's existing convention, applied here)

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

## 7. Roadmap

See `docs/TASKS.md` Track V for the phased, numbered task list this document's design maps to.
Summary: Phase 1 (containers module + fiveg migration, libvirt→virt crate) is scoped and ready to
start; Phase 2 (Cloud Hypervisor spike) follows once Phase 1 lands; the WASM-capsule prototype
(§5.3) is an independent, parallel-track evaluation; the in-process-VMM direction (§2) is recorded
as reviewed and rejected, not silently dropped, so a future session doesn't re-propose it without
this document's reasoning in view.
