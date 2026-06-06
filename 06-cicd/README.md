# 06 — CI/CD for Data Pipelines

## Objective
Implement CI/CD workflows for data engineering projects — linting, testing, deployment automation.

## What's Included

### GitHub Actions Workflows
| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `dbt_ci.yml` | PR changes to `03-dbt-project/` | seed → build → test → docs |
| `sql_lint.yml` | PR changes to `*.sql` files | sqlfluff lint on SQL models |
| `python_test.yml` | PR changes to Python modules | Runs Delta/Medallion/Iceberg scripts |

### Local Tools
| Tool | Purpose |
|------|---------|
| `.sqlfluff` | SQL linting configuration |
| `.pre-commit-config.yaml` | Git hooks for auto-formatting |

## Getting Started

### 1. Install pre-commit hooks (local)
```bash
pip install pre-commit sqlfluff black ruff
pre-commit install
```

Now every `git commit` will auto-check:
- Python formatting (black)
- Python linting (ruff)
- SQL linting (sqlfluff)
- Trailing whitespace, YAML validity

### 2. Run sqlfluff manually
```bash
# Lint (check for issues)
sqlfluff lint 03-dbt-project/models/ --dialect duckdb

# Fix automatically
sqlfluff fix 03-dbt-project/models/ --dialect duckdb
```

### 3. GitHub Actions
Copy the `.github/workflows/` folder to your repo root:
```bash
cp -r 06-cicd/.github ../.github
```

Actions will run automatically on Pull Requests.

## Project Structure
```
06-cicd/
├── .github/
│   └── workflows/
│       ├── dbt_ci.yml          # dbt build + test
│       ├── sql_lint.yml        # SQL linting
│       └── python_test.yml     # Python script tests
├── .sqlfluff                   # SQL linter config
├── .pre-commit-config.yaml     # Pre-commit hooks
└── README.md
```

## Key Concepts

### CI/CD for Data Engineering
```
Developer writes code
    │
    ▼ git commit
Pre-commit hooks (local)
    │ format, lint
    ▼ git push
GitHub Actions (remote)
    │ build, test, lint
    ▼ PR approved
Deploy to production
```

### dbt Slim CI (Advanced)
In production, you don't re-run ALL models on every PR. Instead:
```bash
# Only run models that changed (comparing to production state)
dbt build --select state:modified+ --defer --state ./prod-manifest/
```

This is called **slim CI** — it uses dbt's state comparison to only test what changed.

### Environment Promotion
```
dev (your laptop)     → PR + tests pass
staging (shared env)  → integration tests
production (live)     → approved deploy
```

## Resources
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [sqlfluff Docs](https://docs.sqlfluff.com/)
- [pre-commit](https://pre-commit.com/)
- [dbt CI/CD Guide](https://docs.getdbt.com/docs/deploy/continuous-integration)
