#!/usr/bin/env python3
"""Read FACTS.md, the registry of every number and state vxedge publishes.

    python3 scripts/facts.py json [FACTS.md]      # the registry as JSON (the website vendors this)
    python3 scripts/facts.py check [FILE ...]     # validate FACTS.md, then check FILEs against it

`check` with no files checks this repo's own pages that quote results (RESULTS.md, README.md,
ROADMAP.md). Point it at other repos' READMEs to check those too, e.g.
`python3 scripts/facts.py check ../vxperiments/README.md ../.github/profile/README.md`.

A FILE passes when every measurement-shaped number in it (a number followed by a unit such as
µs, ×, %, mbit, MB, probes or reps, or an "N of N" count) is a number some fact in FACTS.md
carries. This catches a number that was typed instead of quoted. It cannot tell a quoted number
that sits in the wrong sentence; review does that.

Format rules are stated at the top of FACTS.md. Standard library only.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "FACTS.md"
DEFAULT_CHECK = ["RESULTS.md", "README.md", "ROADMAP.md"]

KEY = re.compile(r"^`([a-z0-9][a-z0-9_.-]*)`$")
# Tables under these H3 headings hold measurements (FACTS.md §2); everything else is not.
MEASURED_HEADING = re.compile(r"^### (H\d|Other completed)")
STATES = {
    "state": {"measured", "live", "building", "planned", "real", "emulated", "caveat",
              "done", "in progress", "specified", "backlog"},
}
UNITS = r"µs|ms|×|%|mbit|MB|GB|KB|min|pps|probes|reps|repetitions|archives|deliveries|arms|loads|s\b"
MEASURE = re.compile(
    rf"(?<![\w.])[−-]?~?(\d[\d ]*(?:\.\d+)?M?)(?:\s?[–-]\s?(\d+(?:\.\d+)?))?\s?(?:{UNITS})"
    r"|(?<![\w.])(\d+) of (\d+)\b"
)
NUMBER = re.compile(r"\d[\d ]*(?:\.\d+)?M?|\d+")


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def plain(md: str) -> str:
    """Markdown cell → display text: drop backticks and link targets, keep the words."""
    md = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)
    return md.replace("`", "").strip()


def slug(header: str) -> str:
    m = re.match(r"[A-Za-z0-9]+", header)
    if not m:
        raise SystemExit(f"FACTS.md: column header {header!r} has no leading word to key on")
    return m.group(0).lower()


def parse(path: Path = FACTS) -> dict:
    text = path.read_text(encoding="utf-8")
    facts: dict[str, str] = {}
    measured: list[str] = []
    tables: dict[str, dict] = {}
    errors: list[str] = []
    heading, measuring = "", False
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            heading, measuring = line, False
        elif line.startswith("### "):
            heading, measuring = line, bool(MEASURED_HEADING.match(line))
        if not (line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1])):
            i += 1
            continue
        head = cells(line)
        rows = []
        i += 2
        while i < len(lines) and lines[i].startswith("|"):
            rows.append(cells(lines[i]))
            i += 1
        if head[0] != "Key":
            continue
        scalar = len(head) > 1 and head[1] == "Value"
        slugs = [slug(h) for h in head[1:]]
        if len(set(slugs)) != len(slugs):
            errors.append(f"{heading}: two columns share a key word: {slugs}")
        for r in rows:
            m = KEY.match(r[0])
            if not m or len(r) != len(head):
                errors.append(f"{heading}: malformed row {r!r}")
                continue
            key = m.group(1)
            vals = {s: plain(c) for s, c in zip(slugs, r[1:])}
            for col, allowed in STATES.items():
                if col in vals and vals[col] not in allowed:
                    errors.append(f"{key}: state {vals[col]!r} is not one of {sorted(allowed)}")
            entries = {key: vals["value"]} if scalar else {f"{key}.{s}": v for s, v in vals.items()}
            if not scalar:
                tid = key.rsplit(".", 1)[0] if "." in key else key
                t = tables.setdefault(tid, {"headers": head[1:], "cols": slugs, "keys": []})
                if t["headers"] != head[1:]:
                    errors.append(f"{key}: table {tid!r} has two different header rows")
                t["keys"].append(key)
            for k, v in entries.items():
                if k in facts:
                    errors.append(f"{k}: defined twice")
                facts[k] = v
                if measuring:
                    measured.append(k)
        continue
    if errors:
        raise SystemExit("FACTS.md is invalid:\n  " + "\n  ".join(errors))
    return {
        "source": "vxedge/docs/FACTS.md",
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "facts": facts,
        "measured": measured,
        "tables": tables,
    }


def norm(n: str) -> str:
    return n.replace(" ", "")


def check(files: list[str]) -> int:
    reg = parse()
    known = {norm(n) for v in reg["facts"].values() for n in NUMBER.findall(v)}
    bad = 0
    for f in files:
        p = Path(f) if Path(f).is_absolute() or Path(f).exists() else ROOT / f
        text = p.read_text(encoding="utf-8")
        for ln, line in enumerate(text.splitlines(), 1):
            for m in MEASURE.finditer(line):
                for n in (g for g in m.groups() if g):
                    if norm(n) not in known:
                        print(f"{f}:{ln}: {m.group(0).strip()!r} — {n} is not a registered fact")
                        bad += 1
    print(f"{len(reg['facts'])} facts, {len(reg['measured'])} measured; "
          + ("ok" if not bad else f"{bad} unregistered number(s)"))
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("json", "check"):
        print(__doc__)
        return 2
    if argv[0] == "json":
        path = Path(argv[1]) if len(argv) > 1 else FACTS
        json.dump(parse(path), sys.stdout, ensure_ascii=False, indent=1, sort_keys=True)
        sys.stdout.write("\n")
        return 0
    return check(argv[1:] or DEFAULT_CHECK)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
