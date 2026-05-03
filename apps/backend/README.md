# Focus Backend API

FastAPI service for Focus full stack AI/ML app.

## Shared Python package

Cross-worker infrastructure lives in **`packages/python`** as the **`focus_python`** installable package (`pyproject.toml` at `packages/python/`). The app pins it via **`-e ../../packages/python`** in `requirements.in` / `requirements.txt`.

Use it for config, database pool, structured logging, Redis/RQ queue helpers, shared enums, shared utils, and FastAPI helpers (`dependency`, `error`, `exception`, `middleware`).

App-only wiring stays under **`src/core/`** (for example `health.py`, `lifespan.py`). **`src/main.py`** composes FastAPI with `focus_python` and those modules.

## Local development

Run installs from **`apps/backend`** so the editable path resolves. Use **Python 3.13** (same as **`python:3.13-slim`** in the Dockerfile); on macOS/Homebrew this is typically `python3`.

```sh
cd apps/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

After editing **`requirements.in`**, regenerate the lockfile:

```sh
pip install pip-tools
pip-compile -c constraints.txt -o requirements.txt requirements.in
```

**API:**

```sh
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

**Local Database:**

```sh
pnpm use:local
pnpm db:setup
pnpm prisma db push --accept-data-loss
```

**Testing:**

```sh
source venv/bin/activate
python tests/box.py
```

## Deployment

The **`Dockerfile`** expects the **repository root** as build context. **`WORKDIR`** is **`/repo/apps/backend`** so **`../../packages/python`** matches **`/repo/packages/python`**. Render **`buildFilter`** paths include **`packages/python/**`\*\* so shared-package changes trigger rebuilds.

## Routes

- **`src/core/health.py`** — **`/health`**, **`/ready`**
- **`src/integrations/predictions/router.py`** — Trained AI

Conventions:

- **`APIRouter`** with **`prefix`**; auth via **`Depends(dependency.get_token_header)`** from **`focus_python`**
- Request and response models from **`integrations/*/schemas`**
- **`response_model`** on route decorators where appropriate
- **`structlog`** via **`focus_python`**: **`bind_context`** (correlation_id, path) and **`bind_job_context`** (property_id) for multi-tenant traces

Raise HTTP errors with **`error(...)`** from **`focus_python`** (application error type). Register handlers once in **`main.py`** with **`exception.register_exception_handlers(app)`**.

## Services

- **`src/integrations/predictions/`** — access `sk-learn` trained AI on snapshot data

Import shared infrastructure from **`focus_python`** (**`config`**, **`db_pool`**, **`logging`**, **`queue`**, **`error`**, **`dependency`**, etc.), not from a local **`core`** package for those concerns.

Patterns:

- **`queue.enqueue_jobs(jobs)`** for batch enqueue (each job: func, args, optional job_id, job_timeout, tags, metadata, …)
- Optional dependencies: if something required for a route is missing, respond with **`error(..., status_code=503)`** (or appropriate code)

## Queue and Utils

- Default queue name: **`predictions-default`**
- **`queue.get_connection()`** — Redis
- **`queue.enqueue_jobs(jobs)`** — batch enqueue
- **`SchemaUtils`** — schema helpers from **`focus_python`**
