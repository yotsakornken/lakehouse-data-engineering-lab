# 02 — Medallion Architecture

## Objective
Implement the Bronze → Silver → Gold layered data architecture pattern used in lakehouses.

## What You'll Build
- **Bronze**: Raw ingestion layer (append-only, no transformations)
- **Silver**: Cleaned & conformed layer (deduplication, type casting, null handling)
- **Gold**: Business-level aggregates (star schema, KPI tables)

## Key Concepts
- Layered data quality progression
- Idempotent ingestion patterns
- Incremental processing
- Data lineage across layers
- Separation of concerns (raw vs. curated vs. aggregated)

## Project Structure
```
02-medallion/
├── bronze/
│   └── ingest_raw.py
├── silver/
│   └── clean_transform.py
├── gold/
│   └── aggregate.py
├── data/
│   └── sample_input.csv
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- PySpark 3.x with Delta Lake

### Run
```bash
python bronze/ingest_raw.py
python silver/clean_transform.py
python gold/aggregate.py
```

## Resources
- [Databricks Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)
