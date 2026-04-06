#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/create-migration.sh <name>
# Example: ./scripts/create-migration.sh __init__

NAME="${1:-}"
if [[ -z "$NAME" || "$NAME" == *"/"* || "$NAME" == *".."* ]]; then
    echo "error: invalid or missing migration name" >&2
    exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ROOT}/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "error: .env not found" >&2
    exit 1
fi
set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

if [[ -z "${DIRECT_URL:-}" ]]; then
    echo "error: DIRECT_URL not set" >&2
    exit 1
fi

if [[ ! -d "${ROOT}/prisma" ]]; then
    echo "error: prisma directory not found" >&2
    exit 1
fi

MIG_DIR="${ROOT}/prisma/migrations/${NAME}"
mkdir -p "$MIG_DIR"

cd "$ROOT"
npx prisma migrate diff \
    --from-config-datasource \
    --to-schema-datamodel ./prisma \
    --script >"${MIG_DIR}/migration.sql"

if [[ ! -s "${MIG_DIR}/migration.sql" ]]; then
    echo "no"
else
    echo "yes"
fi
