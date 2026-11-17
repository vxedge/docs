#!/usr/bin/env bash
# Test check-wording.sh: clean text passes, and each retired identity phrase fails when planted.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "vxedge is a virtual vehicle with environmental parity. The testbed host is one machine." > "$tmp/README.md"
"$here/check-wording.sh" "$tmp" >/dev/null || { echo "test-check-wording: clean text was refused" >&2; exit 1; }

fail=0
while IFS= read -r phrase; do
    for file in README.md CITATION.cff; do
        rm -f "$tmp/README.md" "$tmp/CITATION.cff"
        echo "vxedge is $phrase the zonal vehicle." > "$tmp/$file"
        if "$here/check-wording.sh" "$tmp" >/dev/null 2>&1; then
            echo "test-check-wording: '$phrase' in $file was not refused" >&2
            fail=1
        fi
    done
done <<'PHRASES'
an SDV network-slicing testbed for
a slicing testbed for
an all-software SDV testbed for
an all-software testbed for
an open testbed for
an open research testbed for
a platform that maps 5G network slices onto
a platform for mapping 5G network slices onto
an SDV testbed for
the vxedge testbed for
PHRASES
[ "$fail" -eq 0 ] || exit 1
echo "test-check-wording: ok"
