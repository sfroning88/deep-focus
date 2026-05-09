# Config

Author: Sean Froning
Created Date: 5.9.2026
Documentation for shared focus_python package

## Shared Python package

Cross-worker infrastructure lives in **`packages/python`** as the **`focus_python`** installable package (`pyproject.toml` at `packages/python/`). The app pins it via **`-e ../../packages/python`** in `requirements.in` / `requirements.txt`.

Use it for config, database pool, structured logging, Redis/RQ queue helpers, shared enums, shared utils, and FastAPI helpers (`dependency`, `error`, `exception`, `middleware`).

App-only wiring stays under **`src/core/`** (for example `health.py`, `lifespan.py`). **`src/main.py`** composes FastAPI with `focus_python` and those modules.

**Local Redis:**

Postgres and storage buckets live on Supabase; only Redis runs locally for the RQ queue.

```sh
pnpm use:local
pnpm redis:up
```

**Testing:**

```sh
source .venv/bin/activate
python -m src.tests.orchestrator <train|predict>
```

## Deployment

The **`Dockerfile`** expects the **repository root** as build context. **`WORKDIR`** is **`/repo/apps/[fastapi-app]`** so **`../../packages/python`** matches **`/repo/packages/python`**. Render **`buildFilter`** paths include **`packages/python/**`\*\* so shared-package changes trigger rebuilds.

## Routes

Conventions:

- **`APIRouter`** with **`prefix`**; auth via **`Depends(dependency.get_token_header)`** from **`focus_python`**
- Request and response models from **`integrations/*/schemas`**
- **`response_model`** on route decorators where appropriate
- **`structlog`** via **`focus_python`**: **`bind_context`** (correlation_id, path) and **`bind_job_context`** (property_id) for multi-tenant traces

Raise HTTP errors with **`error(...)`** from **`focus_python`** (application error type). Register handlers once in **`main.py`** with **`exception.register_exception_handlers(app)`**.

## Services

Import shared infrastructure from **`focus_python`** (**`config`**, **`db_pool`**, **`logging`**, **`queue`**, **`error`**, **`dependency`**, etc.), not from a local **`core`** package for those concerns.

Patterns:

- **`queue.enqueue_jobs(jobs)`** for batch enqueue (each job: func, args, optional job_id, job_timeout, tags, metadata, …)
- Optional dependencies: if something required for a route is missing, respond with **`error(..., status_code=503)`** (or appropriate code)

## Queue and Utils

- Default queue name: **`predictions-default`**
- **`queue.get_connection()`** — Redis
- **`queue.enqueue_jobs(jobs)`** — batch enqueue
- **`SharedUtils`** — schema helpers from **`focus_python`**
