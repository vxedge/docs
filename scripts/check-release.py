#!/usr/bin/env python3
"""Fail if this repo's citable version disagrees with what FACTS.md registers for it.

    python3 scripts/check-release.py

`project.version` and `project.released` in FACTS.md must match `version` and `date-released` in
CITATION.cff. Standard library only.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def citation(field: str) -> str:
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    m = re.search(rf'^{field}:\s*"?([^"\n]+)"?\s*$', text, re.M)
    return m.group(1).strip() if m else ""


def main() -> int:
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "facts.py"), "json", str(ROOT / "FACTS.md")],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    facts = json.loads(out)["facts"]
    problems = []
    for key, field in (("project.version", "version"), ("project.released", "date-released")):
        if str(facts.get(key, "")) != citation(field):
            problems.append(f"FACTS.md {key} is {facts.get(key)!r}, CITATION.cff {field} is {citation(field)!r}")
    if problems:
        print("\n".join(problems))
        return 1
    print("check-release: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
