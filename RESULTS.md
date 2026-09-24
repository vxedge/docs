# RESULTS.md — measured results

What vxedge has measured so far, one row per hypothesis, with the caveat that matters most for
each. Hypotheses are defined in [`ARCHITECTURE.md`](ARCHITECTURE.md) §2; methodology in §12.
Every number below comes from a frozen summary in
[`vxperiments/results/`](https://github.com/vxedge/vxperiments/tree/main/results), which records
the input manifest's sha256 alongside it.

## Summary

| Hypothesis | Experiment | Verdict | Headline number |
|---|---|---|---|
| **H1** — isolation: VLAN + tc queue-tree reservations keep ADAS p99 near baseline under infotainment load | `exp-001` | **Holds** | ADAS p99 at 600 mbit load: 81.9 µs vs 89.6 µs baseline (0.91×; threshold 2.0×) |
| **H2** — real S-NSSAI slicing vs static VLAN mapping | `exp-010` | **Holds** | p99 growth, baseline → 600 mbit: S-NSSAI 0.95× vs VLAN 0.91× (tolerance 1.1×) |
| **H3** — virtual-ECU packaging affects zone-to-compute latency | `exp-002` → `exp-002b` | **Holds** | Virtio transport is the dominant factor: MMIO → PCI Δp50 −26.0 µs (IQR 2.2 µs) |
| **H4** — co-located OTA does not compromise the ADAS slice | `exp-003` | **Holds** | ADAS p50: 52.2 µs baseline vs 51.9 µs under OTA burst (Δ −0.3 µs, inside the 6.0 µs IQR) |

Every campaign above is 5 repetitions per arm or load point, 1000 pps × 60 s per point
(60 000 probes), with a 10 s warmup discarded. Each result has been reproduced by an independent
second campaign (`--repro`) that reached the same verdict.

## H1 — isolation (`exp-001`)

| load (mbit) | p50 µs (IQR) | p95 µs (IQR) | p99 µs (IQR) | loss % |
|---:|---:|---:|---:|---:|
| 0 | 49.9 (0.8) | 71.4 (6.7) | 89.6 (6.4) | 0.0 |
| 100 | 51.1 (3.0) | 72.0 (6.1) | 87.5 (7.0) | 0.0 |
| 250 | 49.8 (1.9) | 70.1 (3.3) | 84.5 (4.7) | 0.0 |
| 400 | 50.6 (1.3) | 72.3 (3.1) | 85.2 (4.2) | 0.0 |
| 600 | 51.4 (1.8) | 69.2 (2.8) | 81.9 (5.0) | 0.0 |

**Caveat:** the gateway shares its host with the zones it serves, and timestamps are taken
in userspace (SO_TIMESTAMPING is a tracked follow-up). An earlier version of this campaign
measured loopback delivery instead of the gateway path, because probe and reflector sat in the
same network namespace. That defect was fixed with real netns isolation and is now covered by a
CI regression test. The numbers above are the corrected re-run.
[Summary](https://github.com/vxedge/vxperiments/blob/main/results/exp-001/exp-001-summary.md)

## H2 — real slicing vs static mapping (`exp-010`)

S-NSSAI PDU sessions through Open5GS + UERANSIM, compared against `exp-001`'s VLAN arm. The
S-NSSAI path has a higher absolute floor (p99 ≈ 317–337 µs, since it crosses a software UPF and
GTP-U), but its tail grows no faster under load than the VLAN path does, which is what the
hypothesis tests.

**Caveat:** the first campaign did **not** hold, because nothing in the 5G path applied
per-slice QoS. The fix was real HTB enforcement on the slice path. We checked first whether
5QI/AMBR configuration alone would do it, and it did not change anything. The campaign was
then re-run with host-noise mitigations (CPU governor, core pinning, randomized load order).
All intermediate campaigns are kept in the results directory.
[Summary](https://github.com/vxedge/vxperiments/blob/main/results/exp-010/exp-010-summary.md)

## H3 — virtualization choice (`exp-002b`)

| arm | p50 µs (IQR) | p99 µs (IQR) | CPU % | RSS MB |
|---|---:|---:|---:|---:|
| container | 54.6 (1.3) | 94.4 (2.8) | 4.3 | 7.3 |
| libvirt-q35 | 70.3 (1.6) | 117.6 (2.4) | 8.2 | 166.2 |
| q35-vhost | 78.1 (2.5) | 122.9 (4.4) | 9.1 | 150.6 |
| q35-pci | 87.6 (2.0) | 138.6 (2.6) | 11.3 | 150.9 |
| microvm-pci | 87.9 (2.2) | 138.2 (3.2) | 11.4 | 150.2 |
| microvm-mmio | 113.9 (2.0) | 165.0 (6.3) | 15.0 | 146.4 |

Decomposition: virtio transport (MMIO vs PCI) −26.0 µs; libvirt vs raw QEMU −17.3 µs, likely
because libvirt enables vhost/optimized virtio settings that a bare QEMU invocation does not;
vhost-net alone −9.5 µs. Machine type
(q35 vs microvm) has no measurable effect (−0.3 µs, within IQR).

**Caveat:** `exp-002`'s original conclusion ("microVMs are slowest") was right about the
ranking but wrong about the cause. `exp-002b` was designed specifically to separate the factors.
[Summary](https://github.com/vxedge/vxperiments/blob/main/results/exp-002b/exp-002b-summary.md)

## H4 — OTA co-location (`exp-003`)

| arm | p50 µs (IQR) | p95 µs (IQR) | p99 µs (IQR) | OTA deliveries ok/fail |
|---|---:|---:|---:|---:|
| baseline | 52.2 (6.0) | 80.7 (4.9) | 97.7 (5.6) | n/a |
| ota-burst | 51.9 (1.7) | 79.9 (6.3) | 93.1 (5.5) | 361 / 0 |

**Caveat:** the v1 OTA transport binds a plain host address. That means this measures host-level CPU and
scheduling contention between OTA and the ADAS probe, not gateway-QoS-enforced network
contention. A second campaign moved the absolute numbers outside the first campaign's IQR, which is
session-to-session host drift, but it did not change the comparative verdict.
[Summary](https://github.com/vxedge/vxperiments/blob/main/results/exp-003/exp-003-summary.md)

## Other completed experiments

- **`exp-005`** — cold-start / first-packet latency after zone boot. The effect was confirmed in 20 of 20
  repetitions. It explains the inflated first-arm tails seen incidentally in `exp-001`/`002`/`003`.
- **`exp-014`** — wiring-harness topology as a variable: star vs daisy-chained zones. The expected
  hop-count effect holds.

## Methodology caveats that apply to everything above

These are properties of the host *class* used for phase 1–2, not of one machine:

- Shared-host gateway: vxgateway runs on the same host as the zones.
- Non-PREEMPT_RT kernel, `performance` CPU governor, measurement cores pinned.
- Userspace monotonic timestamps.

Host requirements per experiment tier are in [`TESTBED-SETUP.md`](TESTBED-SETUP.md).
