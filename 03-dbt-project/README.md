# 03 — dbt Project

## Objective
Build a dbt project demonstrating data transformations, testing, documentation, and CI/CD integration.

## What You'll Build
- Staging, intermediate, and mart models (layered DAG)
- Source freshness checks
- Generic and singular tests
- Documentation with `dbt docs generate`
- Macros and Jinja templating

## Key Concepts
- Modular SQL transformations
- ref() and source() functions
- Incremental models
- Snapshot (SCD Type 2)
- Packages (dbt_utils, codegen)
- Slim CI with state comparison

## Project Structure
```
03-dbt-project/
├── models/
│   ├── staging/
│   ├── intermediate/
│   └── marts/
├── tests/
├── macros/
├── seeds/
├── snapshots/
├── dbt_project.yml
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- dbt-core + adapter (e.g., `dbt-duckdb` for local dev)

### Install
```bash
pip install dbt-core dbt-duckdb
```

### Run
```bash
dbt debug
dbt seed
dbt run
dbt test
dbt docs generate && dbt docs serve
```

## Resources
- [dbt Documentation](https://docs.getdbt.com/)
- [dbt Best Practices](https://docs.getdbt.com/best-practices)
