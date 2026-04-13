#!/usr/bin/env bash
set -euo pipefail

# Runs `prisma migrate dev --create-only` with --name (does not apply to the DB).
# From repo root: pnpm db:migrate <name> [-- extra prisma args]
# Example: pnpm db:migrate init

NAME="${1:-}"
if [[ -z "$NAME" || "$NAME" == *"/"* || "$NAME" == *".."* ]]; then
  echo "error: invalid or missing migration name (first argument)" >&2
  echo "usage: pnpm db:migrate <migration_name>" >&2
  echo "example: pnpm db:migrate init" >&2
  exit 1
fi
shift

exec prisma migrate dev --create-only --name "$NAME" "$@"
