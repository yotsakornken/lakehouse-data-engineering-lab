# lakehouse-data-engineering-lab
> Hands-on implementations of modern data engineering patterns — Delta Lake, dbt, medallion architecture, and CI/CD pipelines on Azure.

---

## Overview

A self-study project covering end-to-end modern data engineering on the lakehouse paradigm. Each module is a standalone mini-project that builds on the previous one, progressing from open table formats to full CI/CD deployment. Designed as a portfolio to demonstrate practical skills aligned with industry certifications.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        GOLD                              │
│         Business aggregates, KPI tables, star schema     │
├─────────────────────────────────────────────────────────┤
│                       SILVER                             │
│       Cleaned, conformed, deduplicated, typed            │
├─────────────────────────────────────────────────────────┤
│                       BRONZE                             │
│           Raw ingestion, append-only, no transforms      │
└─────────────────────────────────────────────────────────┘
         ▲                                    │
         │   Ingestion (Auto Loader,          ▼
         │    Spark Structured Streaming)   Serving
         │                                 (BI / ML)
    Raw Sources
  (CSV, JSON, API)
```

## Tech Stack

| Layer | Tool |
|-------|------|
| Table format | Delta Lake, Apache Iceberg |
| Transformation | dbt-core, PySpark |
| Orchestration | Databricks Workflows, GitHub Actions |
| Warehouse | Databricks (Unity Catalog), DuckDB (local) |
| BI | Power BI / Metabase (optional) |

---

## Project Structure

```
lakehouse-data-engineering-lab/
├── 01-delta-lake/        # Delta Lake fundamentals
├── 02-medallion/         # Bronze → Silver → Gold pipeline
├── 03-dbt-project/       # dbt transformations & testing
├── 04-databricks/        # Databricks platform features
├── 05-iceberg/           # Apache Iceberg exploration
├── 06-cicd/              # CI/CD for data pipelines
├── docs/                 # Architecture diagrams & notes
└── README.md
```

---

## Modules

### 01 — Delta Lake & Open Table Formats
ACID transactions, time travel, schema evolution, MERGE operations with PySpark + Delta Lake.

### 02 — Medallion Architecture
End-to-end Bronze → Silver → Gold pipeline demonstrating layered data quality progression.

### 03 — dbt Project
Modular SQL transformations with staging/intermediate/mart layers, tests, docs, and incremental models.

### 04 — Databricks
Unity Catalog, Auto Loader, Structured Streaming, and Workflow orchestration on the Lakehouse platform.

### 05 — Iceberg
Apache Iceberg table format — partition evolution, time travel, hidden partitioning, and catalog options.

### 06 — CI/CD
GitHub Actions for dbt, sqlfluff linting, pre-commit hooks, and environment promotion strategies.

---

## Key Concepts Demonstrated

- ACID transactions on object storage (Delta Lake & Iceberg)
- Medallion architecture (Bronze/Silver/Gold) for data quality layering
- dbt-driven transformations with testing, documentation, and CI
- Incremental processing & idempotent pipelines
- Unity Catalog governance and 3-level namespace
- CI/CD automation for analytics engineering workflows

## Results / Takeaways

_To be updated as modules are completed._

---

## How to Run

### Prerequisites
```bash
python 3.9+
pip install pyspark delta-spark dbt-core dbt-duckdb sqlfluff pre-commit
```

### Setup
```bash
git clone https://github.com/yotsakornken/lakehouse-data-engineering-lab.git
cd lakehouse-data-engineering-lab
pip install -r requirements.txt  # (coming soon)
```

---

## Certifications Targeted

- [ ] Databricks Data Engineer Associate
- [ ] DP-700 Microsoft Fabric
- [ ] dbt Analytics Engineering

---

## References

- [Delta Lake Docs](https://docs.delta.io/latest/index.html)
- [Apache Iceberg Docs](https://iceberg.apache.org/docs/latest/)
- [dbt Documentation](https://docs.getdbt.com/)
- [Databricks Academy](https://www.databricks.com/learn)
- [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)

---

*Built as part of a 3-month lakehouse self-study roadmap.*
