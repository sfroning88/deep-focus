# Python Nurse

For working with the **PYTHON NURSE**, a free and open source code review tool for `Python` apps.

This uses the public GitHub Action [sfroning88/python-nurse@v1.0.3](https://github.com/marketplace/actions/python-nurse) which combines services from `Ruff`, `mypy`, `Bandit`, `Vulture`, `Radon`, `SQLFluff`, and `markdownlint`.

## Applicable Apps

The **PYTHON NURSE** should be used for:

- `apps/backend` (FastAPI/Python for main API)
- `apps/ai` (FastAPI/Python worker for AI training)

## Tool Stack

The Python Nurse runs seven analysis tools in parallel:

1. **Ruff** - Fast linter + style checker (replaces flake8, isort, pyupgrade)
2. **mypy** - Static type checking
3. **Bandit** - Security scanning (SQL injection, hardcoded secrets)
4. **Vulture** - Dead code detection (unused classes, functions, variables)
5. **Radon** - Cyclomatic complexity & maintainability index scoring
6. **SQLFluff** - SQL linting for `.sql` files (PostgreSQL dialect)
7. **markdownlint** - Markdown style and consistency

## CLI Instructions

From the repo root, you can run individual tools:

```bash
cd apps/backend

# Ruff (linting)
ruff check .

# mypy (type checking)
mypy --ignore-missing-imports .

# Bandit (security)
bandit -r -ll .

# Vulture (dead code)
vulture --min-confidence 80 .

# Radon (complexity)
radon cc -s -n D .
radon mi -s -n B .

# SQLFluff (SQL linting)
sqlfluff lint --dialect postgres *.sql
```

## GitHub Actions

The Python Nurse runs automatically on pull requests that touch `apps/backend/**` files via the public GitHub Action.

The workflow (`.github/workflows/python-nurse.yml`) uses a matrix to run for each changed worker:

```yaml
strategy:
  fail-fast: false
  matrix:
    worker: ${{ fromJSON(needs.changes.outputs.workers) }}
steps:
  - uses: sfroning88/python-nurse@v1
    with:
      app-path: apps/${{ matrix.worker }}
      github-token: ${{ secrets.GITHUB_TOKEN }}
      score-preset: structure # balanced | structure | quality
```

**Score presets** (v1.0.2+): `balanced` (default), `structure` (Vulture/Radon/Bandit heavy), `quality` (Ruff/SQLFluff/markdownlint heavy). This repo uses `structure`.

The action automatically:

- Only analyzes files changed vs the base branch (diff-scoped)
- Posts a collapsible PR comment with findings and a nurse reaction image based on the score
- Uses `<!-- python-nurse -->` marker for comment deduplication
- Continues on error (no single tool kills the job)
- Installs all required tools and dependencies
- Calculates a 0-100 health score based on findings
