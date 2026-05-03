#!/bin/sh
set -e

# Run from anywhere: removes node_modules, .next, and .turbo trees under the monorepo root.
ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Removing node_modules, .next, and .turbo under $ROOT ..."
find . -type d \( -name node_modules -o -name .next -o -name .turbo \) -prune -exec rm -rf {} +
echo "Done. Run pnpm install from the repo root if you removed node_modules."