#!/usr/bin/env bash
# One command to rebuild the interactive site and open it.
# Usage: ./build.sh        (from this folder)
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc is not installed. Run: brew install pandoc"
  exit 1
fi

python3 scripts/build.py
open index.html
