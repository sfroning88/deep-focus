#!/bin/sh
set -e

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

usage() {
  echo "Usage: $0 {up|nuke|push|status}"
  echo ""
  echo "  up      Build image (if needed) and start local Postgres + Redis"
  echo "  nuke    Destroy containers, volumes, and image — full teardown"
  echo "  push    Push Prisma schema to local database (--accept-data-loss)"
  echo "  status  Show container status and verify extensions"
  exit 1
}

cmd_up() {
  echo "Building image and starting local containers..."
  docker compose build
  docker compose up -d
  echo "Waiting for Postgres to be healthy..."
  maxWaitSeconds=120
  elapsed=0
  until docker exec local-postgres pg_isready -U admin -d postgres > /dev/null 2>&1; do
    elapsed=$((elapsed + 1))
    if [ "$elapsed" -ge "$maxWaitSeconds" ]; then
      echo "Postgres did not become ready within ${maxWaitSeconds}s (pg_isready kept failing)." >&2
      exit 1
    fi
    sleep 1
  done
  echo "Postgres is ready."
}

cmd_nuke() {
  echo "Destroying containers, volumes, and image..."
  docker compose down -v --rmi local
  echo "Local DB nuked."
  echo "Optional cleanups (errors ignored)..."
  docker system prune -a --volumes -f 2>/dev/null || true
  rm -rf "$HOME/Library/Containers/com.docker.docker" 2>/dev/null || true
}

cmd_push() {
  echo "Pushing Prisma schema to local database..."
  dbUrl="${DATABASE_URL:-}"
  if [ -z "$dbUrl" ]; then
    echo "DATABASE_URL is not set; refuse prisma db push." >&2
    exit 1
  fi
  dbUrlLower=$(printf '%s' "$dbUrl" | tr '[:upper:]' '[:lower:]')
  case "$dbUrlLower" in
    *localhost*|*127.0.0.1*) ;;
    *)
      echo "DATABASE_URL must point at localhost or 127.0.0.1; refusing destructive db push." >&2
      echo "Current host is not allowed for --accept-data-loss." >&2
      exit 1
      ;;
  esac
  npx prisma db push --accept-data-loss
  echo "Schema pushed."
}

cmd_status() {
  echo "=== Container Status ==="
  docker compose ps
  echo ""
  echo "=== Installed Extensions ==="
  docker exec local-postgres psql -U admin -d postgres -c "SELECT extname, extversion FROM pg_extension ORDER BY extname;"
  echo ""
  echo "=== Schemas ==="
  docker exec local-postgres psql -U admin -d postgres -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema' ORDER BY schema_name;"
}

case "${1:-}" in
  up)     cmd_up ;;
  nuke)   cmd_nuke ;;
  push)   cmd_push ;;
  status) cmd_status ;;
  *)      usage ;;
esac