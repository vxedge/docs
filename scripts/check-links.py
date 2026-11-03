#!/usr/bin/env python3
"""Fail on a relative Markdown link that points at a file this repo does not have.

    python3 scripts/check-links.py

Links to other sites, anchors within a page, and `mailto:` are not checked. A link's own anchor
(`FACTS.md#parity-ledger`) is checked for the file only. Standard library only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\]\(([^)\s]+)\)")
SKIP = ("http://", "https://", "mailto:", "#")


def main() -> int:
    broken = []
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts:
            continue
        for n, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for target in LINK.findall(line):
                if target.startswith(SKIP):
                    continue
                path = target.split("#", 1)[0]
                if path and not (md.parent / path).exists():
                    broken.append(f"{md.relative_to(ROOT)}:{n}: {target}")
    if broken:
        print("\n".join(broken))
        print("check-links: fix or remove the links above", file=sys.stderr)
        return 1
    print("check-links: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
