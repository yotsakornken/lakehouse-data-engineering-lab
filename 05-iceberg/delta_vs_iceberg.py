"""
Apache Iceberg vs Delta Lake - Side by Side Comparison
A reference summary of when to use which format.
"""

print("=" * 60)
print("  Delta Lake vs Apache Iceberg — Comparison Guide")
print("=" * 60)

print("""
┌────────────────────┬──────────────────────┬───────────────────────┐
│ Feature            │ Delta Lake           │ Apache Iceberg        │
├────────────────────┼──────────────────────┼───────────────────────┤
│ Creator            │ Databricks           │ Netflix → Apache      │
│ Open source        │ Yes (Linux Found.)   │ Yes (Apache Found.)   │
│ File format        │ Parquet              │ Parquet (+ ORC/Avro)  │
│ Metadata           │ _delta_log/ (JSON)   │ metadata/ (Avro)      │
│ Catalog            │ Built-in (Unity)     │ Pluggable (REST/Hive) │
├────────────────────┼──────────────────────┼───────────────────────┤
│ ACID               │ ✅                    │ ✅                     │
│ Time travel        │ ✅ (by version #)     │ ✅ (by snapshot ID)    │
│ Schema evolution   │ ✅ (add columns)      │ ✅ (add/rename/drop)   │
│ Partition evolution│ ❌ (rewrite needed)   │ ✅ (metadata only!)    │
│ Hidden partitions  │ ❌                    │ ✅                     │
│ Column rename      │ ⚠️ (column mapping)  │ ✅ (native)            │
│ Row-level updates  │ ✅ (MERGE)            │ ✅ (MERGE + MOR/COW)   │
│ Compaction         │ OPTIMIZE             │ rewrite_data_files     │
│ Z-Order            │ ✅                    │ ✅ (sort order)         │
├────────────────────┼──────────────────────┼───────────────────────┤
│ Best with          │ Databricks, Spark    │ Multi-engine (Spark,  │
│                    │                      │  Flink, Trino, Presto)│
│ Governance         │ Unity Catalog        │ Nessie, Polaris, REST │
│ Community          │ Databricks-led       │ Vendor-neutral        │
└────────────────────┴──────────────────────┴───────────────────────┘
""")

print("""
When to choose DELTA LAKE:
  ✅ You're on Databricks (native, best integration)
  ✅ Your team is Spark-only
  ✅ You want simplest setup (just Parquet + JSON log)
  ✅ Unity Catalog for governance

When to choose ICEBERG:
  ✅ Multi-engine environment (Spark + Trino + Flink + Presto)
  ✅ You need partition evolution (large tables, changing access patterns)
  ✅ Vendor-neutral strategy (avoid lock-in)
  ✅ Need advanced schema evolution (renames, reorder)

The Reality (2024+):
  - Both are converging in features
  - Databricks now supports Iceberg read (UniForm)
  - Many companies use BOTH
  - Choice often depends on existing platform, not features
""")

print("""
Architecture Comparison:

Delta Lake:
  data/
  ├── part-00000.parquet
  ├── part-00001.parquet
  └── _delta_log/
      ├── 000000.json      (commit 0)
      ├── 000001.json      (commit 1)
      └── 000010.checkpoint.parquet

Apache Iceberg:
  data/
  ├── file1.parquet
  └── file2.parquet
  metadata/
  ├── v1.metadata.json     (table metadata)
  ├── snap-123.avro        (snapshot → manifest list)
  └── manifest-abc.avro    (manifest → data files)
""")

print("🎉 That's the big picture!")
print("For cert exams: know the DIFFERENCES, especially partition evolution.")
