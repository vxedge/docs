#!/usr/bin/env bash
# Fail if reader-facing docs carry authoring-process or tooling-provenance wording.
# Contributor files (AGENTS.md) are not reader docs and are skipped.
set -eu
cd "$(dirname "$0")/.."
pat='gemini|chatgpt|openai|vibe[- ]?cod|pasted (in)?to|task history|future session|this session|co-authored-by|CLAUDE\.md|\.claude/|master spec'
hits=$(grep -rniE "$pat" --include='*.md' --include='*.drawio' . | grep -v '^\./AGENTS\.md' || true)
if [ -n "$hits" ]; then echo "$hits"; echo "check-wording: remove the wording above from reader-facing docs" >&2; exit 1; fi
echo "check-wording: ok"
