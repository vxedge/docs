#!/usr/bin/env bash
# Fail if reader-facing docs carry authoring-process or tooling-provenance wording, or a retired
# description of vxedge. Contributor files (AGENTS.md) are not reader docs and are skipped.
#
#   scripts/check-wording.sh [dir]     # dir defaults to this repository
set -eu
cd "${1:-$(dirname "$0")/..}"
pat='gemini|chatgpt|openai|vibe[- ]?cod|pasted (in)?to|task history|future session|this session|co-authored-by|CLAUDE\.md|\.claude/|master spec|honestly|genuinely|truthfully'
hits=$(grep -rniE "$pat" --include='*.md' --include='*.drawio' . | grep -v '^\./AGENTS\.md' || true)
if [ -n "$hits" ]; then echo "$hits"; echo "check-wording: remove the wording above from reader-facing docs" >&2; exit 1; fi

# Retired descriptions of vxedge. It is described by `project.summary` and `project.description` in
# FACTS.md; 5G slicing is one family of its measured cases. "Testbed" alone stays allowed in body
# text. CHANGELOG.md is history and keeps its words.
retired='slicing testbed|all-software( SDV)? testbed|open( research)? testbed|maps 5G network slices onto|mapping 5G network slices onto|SDV testbed|the vxedge testbed'
hits=$(grep -rniE "$retired" --include='*.md' --include='*.cff' --include='*.drawio' . | grep -vE '^\./(AGENTS|CHANGELOG)\.md' || true)
if [ -n "$hits" ]; then echo "$hits"; echo "check-wording: the wording above is a retired description of vxedge; quote project.summary or project.description from FACTS.md" >&2; exit 1; fi
echo "check-wording: ok"
