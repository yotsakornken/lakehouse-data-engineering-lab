# 05 — Apache Iceberg

## Objective
Explore Apache Iceberg as an open table format — understand its architecture, partitioning, and how it differs from Delta Lake.

## What You'll Build
- Create and query Iceberg tables with PySpark
- Partition evolution (no rewrite needed)
- Time travel queries
- Schema evolution
- Hidden partitioning

## Key Concepts
- Iceberg table format architecture (metadata, manifest lists, manifests, data files)
- Partition evolution
- Time travel & snapshot isolation
- Schema evolution without rewriting data
- Catalog options (Hive, REST, Glue, Nessie)
- Iceberg vs Delta Lake comparison

## Project Structure
```
05-iceberg/
├── iceberg_basics.py
├── partition_evolution.py
├── time_travel.py
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- PySpark 3.x
- `pyspark` with Iceberg runtime JAR

### Run
```bash
python iceberg_basics.py
```

## Resources
- [Apache Iceberg Documentation](https://iceberg.apache.org/docs/latest/)
- [Iceberg Spec](https://iceberg.apache.org/spec/)
