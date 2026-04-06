#!/usr/bin/env sh
# Staged formatting/lint (JS/TS/etc. via lint-staged), full TS graph, Prisma migration guard.
# Add Python or other checks in pre-commit-extra.sh (optional).
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 1

pnpm lint-staged
pnpm type-check
pnpm check:migration-safety

if [ -f scripts/husky/pre-commit-extra.sh ]; then
    sh scripts/husky/pre-commit-extra.sh
fi
