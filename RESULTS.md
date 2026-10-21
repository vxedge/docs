# Results

What vxedge has measured so far, one row per hypothesis, with the caveat that matters most for
each. Hypotheses are defined in [`ARCHITECTURE.md`](ARCHITECTURE.md) §2; methodology in §12. Acronyms are defined in [`ACRONYMS.md`](ACRONYMS.md).
Every number below comes from a frozen summary in
[`vxperiments/results/`](https://github.com/vxedge/vxperiments/tree/main/results), which records
the input manifest's sha256 alongside it. Each one is registered in [`FACTS.md`](FACTS.md), which
also holds the full per-load and per-arm tables. This page explains the numbers; that file is where
they are quoted from.

## Summary

| Hypothesis | Experiment | Verdict | Headline number |
|---|---|---|---|
| **H1** (isolation): VLAN + tc queue-tree reservations keep ADAS p99 near baseline under infotainment load | `exp-001` | **Holds** | ADAS p99 at 600 mbit load: 81.9 µs vs 89.6 µs baseline (0.91×; threshold 2.0×) |
| **H2**: real S-NSSAI slicing vs static VLAN mapping | `exp-010` | **Holds** | p99 growth, baseline → 600 mbit: S-NSSAI 0.95× vs VLAN 0.91× (tolerance 1.1×) |
| **H3**: virtual-ECU packaging affects zone-to-compute latency | `exp-002` → `exp-002b` | **Holds** | Virtio transport is the dominant factor: MMIO → PCI Δp50 −26.0 µs (IQR 2.2 µs) |
| **H4**: co-located OTA does not compromise the ADAS slice | `exp-003` | **Holds** | ADAS p50: 52.2 µs baseline vs 51.9 µs under OTA burst (Δ −0.3 µs, inside the 6.0 µs IQR) |

Every campaign above is 5 repetitions per arm or load point, 1000 pps × 60 s per point
(60 000 probes), with a 10 s warmup discarded. Each result has been reproduced by an independent
second campaign (`--repro`) that reached the same verdict.

## H1: isolation (`exp-001`)

The ADAS tail does not grow with load: p99 is 89.6 µs idle and 81.9 µs at 600 mbit, and loss is
0.0 % at every level. Full table: [`FACTS.md` § H1](FACTS.md#h1--isolation-exp-001).

**Caveat:** the gateway shares its host with the zones it serves, and timestamps are taken
in userspace (SO_TIMESTAMPING is a tracked follow-up). An earlier version of this campaign
measured loopback delivery instead of the gateway path, because probe and reflector sat in the
same network namespace. That defect was fixed with real netns isolation and is now covered by a
CI regression test. The numbers above are the corrected re-run.
Summary: [`vxperiments/results/exp-001/exp-001-summary.md`](https://github.com/vxedge/vxperiments/blob/main/results/exp-001/exp-001-summary.md)

**Repeats on a newer kernel.** Two further runs on kernel 7.0.0-38-generic (input sha
`ac2496e3f58e…`, 25 archives each) keep the verdict: p99 at the highest load is 0.94× and 1.00× of idle,
against 0.91× in the frozen run, and the second repeat sits inside the first's IQR on 12 of 15 metric ×
load pairs (values in [`FACTS.md` § H1](FACTS.md#h1--isolation-exp-001)). Both read a few microseconds
below the frozen run at the two highest loads. The cause is not isolated; the kernel change is the leading
suspect and has not been tested. The frozen numbers stay the published ones; these are supplementary checks.

**Workspace hashes.** A workspace's input hash covers every file in it, comments included, so it changes with any
edit. The hash of a current checkout of `exp-001-ws` therefore matches neither the frozen campaign's nor the
repeats': a header comment in `run.sh` was edited after the repeats ([vxperiments#3](https://github.com/vxedge/vxperiments/pull/3)). Compare against the commit
the archive names, not against the hash of whatever is checked out.

## H2: real slicing vs static mapping (`exp-010`)

S-NSSAI PDU sessions through Open5GS + UERANSIM, compared against `exp-001`'s VLAN arm. The
S-NSSAI path has a higher absolute floor (p99 ≈ 317–337 µs, since it crosses a software UPF and
GTP-U), but its tail grows no faster under load than the VLAN path does, which is what the
hypothesis tests.

**Caveat:** the first campaign did **not** hold, because nothing in the 5G path applied
per-slice QoS. The fix was real HTB enforcement on the slice path. Configuring
5QI/AMBR alone was checked first and changed nothing. The campaign was
then re-run with host-noise mitigations (CPU governor, core pinning, randomized load order).
All intermediate campaigns are kept in the results directory.
Summary: [`vxperiments/results/exp-010/exp-010-summary.md`](https://github.com/vxedge/vxperiments/blob/main/results/exp-010/exp-010-summary.md)

## H3: virtualization choice (`exp-002b`)

Six packaging arms, from `container` to `microvm-mmio`, with p50/p99, CPU and RSS per arm:
[`FACTS.md` § H3](FACTS.md#h3--virtualization-choice-exp-002b).

Decomposition: virtio transport (MMIO vs PCI) −26.0 µs; libvirt vs raw QEMU −17.3 µs, likely
because libvirt enables vhost/optimized virtio settings that a bare QEMU invocation does not;
vhost-net alone −9.5 µs. Machine type
(q35 vs microvm) has no measurable effect (−0.3 µs, within IQR).

**Caveat:** `exp-002`'s original conclusion ("microVMs are slowest") was right about the
ranking but wrong about the cause. `exp-002b` was designed specifically to separate the factors.
Summary: [`vxperiments/results/exp-002b/exp-002b-summary.md`](https://github.com/vxedge/vxperiments/blob/main/results/exp-002b/exp-002b-summary.md)

## H4: OTA co-location (`exp-003`)

Both arms, with p50/p95/p99 and OTA deliveries (361 ok, 0 failed per repetition):
[`FACTS.md` § H4](FACTS.md#h4--ota-co-location-exp-003).

**Caveat:** the v1 OTA transport binds a plain host address. That means this measures host-level CPU and
scheduling contention between OTA and the ADAS probe, not gateway-QoS-enforced network
contention. A second campaign moved the absolute numbers outside the first campaign's IQR, which is
session-to-session host drift, but it did not change the comparative verdict.
Summary: [`vxperiments/results/exp-003/exp-003-summary.md`](https://github.com/vxedge/vxperiments/blob/main/results/exp-003/exp-003-summary.md)

## Other completed experiments

- **`exp-005`**: cold-start / first-packet latency after zone boot. The effect was confirmed in 20 of 20
  repetitions. It explains the inflated first-arm tails seen incidentally in `exp-001`/`002`/`003`.
- **`exp-014`**: wiring-harness topology as a variable: star vs daisy-chained zones. The expected
  hop-count effect holds.

## Methodology caveats that apply to everything above

These are properties of the host *class* used for phase 1–2, not of one machine:

- Shared-host gateway: vxgateway runs on the same host as the zones.
- Non-PREEMPT_RT kernel, `performance` CPU governor, measurement cores pinned.
- Userspace monotonic timestamps.

Host requirements per experiment tier are in [`TESTBED-SETUP.md`](TESTBED-SETUP.md).
