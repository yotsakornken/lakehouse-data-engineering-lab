# 01 — Delta Lake & Open Table Formats

## Objective
Understand Delta Lake's ACID transactions, time travel, schema enforcement, and how it compares to other open table formats (Iceberg, Hudi).

## What You'll Build
- A PySpark pipeline that writes data in Delta format
- Demonstrate time travel (version history)
- Schema evolution examples
- MERGE (upsert) operations

## Key Concepts
- ACID transactions on data lakes
- Time travel & versioning
- Schema enforcement vs. schema evolution
- Delta log (transaction log)
- Compaction & OPTIMIZE + ZORDER

## Getting Started

### Prerequisites
- Python 3.9+
- PySpark 3.x
- `delta-spark` package

### Install
```bash
pip install pyspark delta-spark
```

### Run
```bash
python delta_basics.py
```

## Resources
- [Delta Lake Documentation](https://docs.delta.io/latest/index.html)
- [Delta Lake vs Iceberg vs Hudi](https://www.onehouse.ai/blog/apache-hudi-vs-delta-lake-vs-apache-iceberg-lakehouse-feature-comparison)
