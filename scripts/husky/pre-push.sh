#!/usr/bin/env sh
# Production build gate (see root package.json "build"; expand when more apps ship).
# Add Python or other checks in pre-push-extra.sh (optional).
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 1

pnpm build

if [ -f scripts/husky/pre-push-extra.sh ]; then
    sh scripts/husky/pre-push-extra.sh
fi
