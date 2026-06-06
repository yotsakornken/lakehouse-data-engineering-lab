# 04 — Databricks

## Objective
Explore Databricks-specific features: Unity Catalog, Auto Loader, Structured Streaming, Workflows, and Delta Live Tables.

## Notebooks

| # | Topic | Key Concepts |
|---|-------|--------------|
| 01 | Spark Basics | DataFrames, transformations vs actions, Delta as default |
| 02 | Unity Catalog | 3-level namespace, schemas as medallion layers, governance |
| 03 | Auto Loader | `cloudFiles`, incremental ingestion, schema evolution |
| 04 | Structured Streaming | readStream, output modes, trigger options |
| 05 | Workflows | Job orchestration, task dependencies, widgets |
| 06 | Delta Live Tables | Declarative pipelines, expectations, auto-managed |

## How to Use
These notebooks are designed to run in **Databricks**:
1. Sign up for [Databricks Community Edition](https://community.cloud.databricks.com/) (free)
2. Import notebooks: Workspace → Import → Upload `.py` or `.sql` files
3. Attach to a cluster and run cell by cell

## Notebook Format
Files use the `# COMMAND ----------` separator and `# MAGIC %md` for markdown cells.
This is the standard Databricks notebook source format that can be imported directly.

## Architecture Covered
```
Landing Zone (S3/ADLS)
    │
    ▼ Auto Loader
Unity Catalog
├── bronze schema (raw)
├── silver schema (clean)
└── gold schema (business)
    │
    ▼ Workflows / DLT
Dashboards & ML
```

## Certifications Alignment
- Databricks Data Engineer Associate
  - Spark DataFrames
  - Delta Lake on Databricks
  - Unity Catalog governance
  - Auto Loader & Structured Streaming
  - Workflow orchestration
