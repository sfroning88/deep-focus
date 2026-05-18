# Tests

Last updates: **May 2026**

## Suite

```md
packages/python/src/tests/
├── orchestrator.py
├── endpoints.py
├── helpers.py
├── redis_clear.py
├── presets/
│ ├── accounting.txt
│ └── data.txt
└── scripts/
├── predict.py
└── train.py
```

All integration tests run through a single orchestrator at `packages/python`. The orchestrator spawns local `uvicorn` + `rq` processes per worker domain, seeds the local database, runs the selected workflow, then tears everything down.

```bash
cd packages/python
python -m src.tests.orchestrator [train|predict]
```

**Setup (local only):**

1. Start Docker Desktop
2. `pnpm use:local`
3. `pnpm redis:setup`
4. `cd packages/python`
5. Activate venv: `python3 -m venv .venv && source .venv/bin/activate && pip install -e .`
6. `python -m src.tests.orchestrator [train|predict]`

**Teardown:** `pnpm redis:nuke`
