"""
Apache Iceberg - Partition Evolution
Change partitioning WITHOUT rewriting data — Iceberg's killer feature!
"""
import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField, LongType, StringType, DoubleType, DateType
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import MonthTransform, DayTransform, YearTransform

print("=" * 50)
print("  Apache Iceberg - Partition Evolution")
print("=" * 50)

# ============================================================
# 1. Setup
# ============================================================
catalog = SqlCatalog(
    "local",
    **{
        "uri": "sqlite:///./iceberg_catalog.db",
        "warehouse": "./iceberg-warehouse",
    },
)

try:
    catalog.create_namespace("partitions")
except Exception:
    pass

try:
    catalog.drop_table("partitions.orders")
except Exception:
    pass

# ============================================================
# 2. Create table with MONTH partitioning
# ============================================================
schema = Schema(
    NestedField(field_id=1, name="order_id", field_type=LongType(), required=False),
    NestedField(field_id=2, name="product", field_type=StringType(), required=False),
    NestedField(field_id=3, name="amount", field_type=DoubleType(), required=False),
    NestedField(field_id=4, name="order_date", field_type=DateType(), required=False),
)

# Partition by month
partition_spec = PartitionSpec(
    PartitionField(
        source_id=4, field_id=1000, transform=MonthTransform(), name="order_month"
    )
)

table = catalog.create_table(
    "partitions.orders",
    schema=schema,
    partition_spec=partition_spec,
)

print(f"\n--- Initial Partition Spec ---")
print(f"Partition: {table.spec()}")

# Write some data
import datetime

data_jan = pa.table({
    "order_id": [1, 2, 3],
    "product": ["Laptop", "Mouse", "Keyboard"],
    "amount": [45000.0, 590.0, 1890.0],
    "order_date": [
        datetime.date(2024, 1, 15),
        datetime.date(2024, 1, 16),
        datetime.date(2024, 1, 17),
    ],
})

data_feb = pa.table({
    "order_id": [4, 5, 6],
    "product": ["Monitor", "Headset", "Webcam"],
    "amount": [12500.0, 2490.0, 1990.0],
    "order_date": [
        datetime.date(2024, 2, 10),
        datetime.date(2024, 2, 15),
        datetime.date(2024, 2, 20),
    ],
})

table.append(data_jan)
table.append(data_feb)

print("\nData written (partitioned by MONTH):")
print(table.scan().to_pandas().to_string(index=False))

# ============================================================
# 3. Evolve partition: change to DAY partitioning
# ============================================================
print("\n--- Partition Evolution: MONTH → DAY ---")
print("(No data rewrite needed! Old files keep month partitioning,")
print(" new files use day partitioning)")

# Note: PyIceberg partition evolution API
# In real Iceberg (Spark/Flink), you'd do:
#   ALTER TABLE orders REPLACE PARTITION FIELD order_month WITH days(order_date)

# For demo, show the concept:
print("""
-- In Spark SQL:
ALTER TABLE partitions.orders
REPLACE PARTITION FIELD order_month
WITH days(order_date);

-- What happens:
-- Old data files: still partitioned by month (not rewritten!)
-- New data files: partitioned by day
-- Query planner handles BOTH automatically
""")

# ============================================================
# 4. Hidden Partitioning explained
# ============================================================
print("=" * 50)
print("  Hidden Partitioning (Iceberg's Magic)")
print("=" * 50)
print("""
Traditional (Hive-style) partitioning:
  /data/year=2024/month=01/day=15/file.parquet
  → User MUST know partition columns
  → Query: WHERE year=2024 AND month=1 AND day=15

Iceberg's Hidden Partitioning:
  /data/file.parquet (stored wherever)
  → User just writes: WHERE order_date = '2024-01-15'
  → Iceberg AUTOMATICALLY prunes partitions
  → No need to know partition structure!

Transform types:
  - years(date)    → partition by year
  - months(date)   → partition by month
  - days(date)     → partition by day
  - hours(ts)      → partition by hour
  - bucket(N, col) → hash into N buckets
  - truncate(L, col) → truncate string to L chars
""")

# ============================================================
# 5. Iceberg vs Delta vs Hive Partitioning
# ============================================================
print("=" * 50)
print("  Partitioning Comparison")
print("=" * 50)
print("""
| Feature              | Hive/Parquet    | Delta Lake      | Apache Iceberg    |
|----------------------|-----------------|-----------------|-------------------|
| Partition columns    | Physical dirs   | Physical dirs   | Hidden (metadata) |
| User awareness       | Must know       | Must know       | Transparent       |
| Change partitioning  | Rewrite ALL     | Rewrite ALL     | Metadata only!    |
| Transforms           | None            | None            | year/month/bucket |
| Over-partitioning    | Common problem  | Common problem  | Less likely       |
""")

print("\n🎉 Partition evolution complete!")
print("Key takeaways:")
print("  - Iceberg partitions are HIDDEN — users don't need to know them")
print("  - Can CHANGE partitioning without rewriting old data")
print("  - Old files keep old partitioning, new files use new scheme")
print("  - Transforms (month, day, bucket) are more flexible than directory-based")
print("  - This is Iceberg's #1 advantage over Delta Lake for large tables")
