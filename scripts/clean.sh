#!/bin/sh
set -e

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Cleaning build artifacts under $ROOT ..."

echo "  - node_modules, .next, .turbo, dist directories"
find . -type d \
  \( -name node_modules -o -name .next -o -name .turbo -o -name dist \) \
  -prune -exec rm -rf {} +

echo "  - .tsbuildinfo files"
find . -type f -name "*.tsbuildinfo" \
  -not -path "*/node_modules/*" \
  -exec rm -f {} +

echo "  - Prisma generated client (packages/db/prisma/src/generated)"
rm -rf packages/db/prisma/src/generated

echo "  - macOS Finder duplicates (e.g. 'foo 2.ts', 'foo 3.js')"
find . -type f \
  \( \
    -name "* [0-9].ts"   -o -name "* [0-9].tsx"  -o \
    -name "* [0-9].js"   -o -name "* [0-9].jsx"  -o \
    -name "* [0-9].mjs"  -o -name "* [0-9].cjs"  -o \
    -name "* [0-9].json" -o -name "* [0-9].d.ts" -o \
    -name "* [0-9].md"   -o -name "* [0-9].py"   \
  \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.next/*" \
  -exec rm -f {} +

echo ""
echo "Done!"
echo "Next: pnpm install && pnpm --filter @focus/db db:generate"
