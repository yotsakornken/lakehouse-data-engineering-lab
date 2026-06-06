"""
Apache Iceberg - Basics
Create, write, and read Iceberg tables using PyIceberg.
"""
import pandas as pd
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField, LongType, StringType, DoubleType, DateType
)
import pyarrow as pa

print("=" * 50)
print("  Apache Iceberg - Basics")
print("=" * 50)

# ============================================================
# 1. Create a local catalog (SQLite-backed)
# ============================================================
catalog = SqlCatalog(
    "local",
    **{
        "uri": "sqlite:///./iceberg_catalog.db",
        "warehouse": "./iceberg-warehouse",
    },
)

# Create a namespace (like a schema/database)
try:
    catalog.create_namespace("company")
    print("\n✅ Namespace 'company' created")
except Exception:
    print("\n📋 Namespace 'company' already exists")

# ============================================================
# 2. Define schema and create table
# ============================================================
schema = Schema(
    NestedField(field_id=1, name="id", field_type=LongType(), required=False),
    NestedField(field_id=2, name="name", field_type=StringType(), required=False),
    NestedField(field_id=3, name="role", field_type=StringType(), required=False),
    NestedField(field_id=4, name="salary", field_type=DoubleType(), required=False),
)

try:
    catalog.drop_table("company.employees")
except Exception:
    pass

table = catalog.create_table("company.employees", schema=schema)
print("✅ Table 'company.employees' created")

print(f"\nTable schema: {table.schema()}")

# ============================================================
# 3. Write data using PyArrow
# ============================================================
print("\n--- Writing data ---")

df = pa.table({
    "id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "role": ["Data Engineer", "Analytics Engineer", "ML Engineer",
             "Platform Engineer", "Data Scientist"],
    "salary": [95000.0, 90000.0, 105000.0, 98000.0, 102000.0],
})

table.overwrite(df)
print(f"✅ Written {len(df)} rows")

# ============================================================
# 4. Read data back
# ============================================================
print("\n--- Reading data ---")
scan = table.scan()
result = scan.to_pandas()
print(result.to_string(index=False))

# ============================================================
# 5. Append more data
# ============================================================
print("\n--- Appending data ---")

df_new = pa.table({
    "id": [6, 7],
    "name": ["Frank", "Grace"],
    "role": ["DevOps Engineer", "Data Analyst"],
    "salary": [91000.0, 85000.0],
})

table.append(df_new)
print(f"✅ Appended {len(df_new)} rows")

# Read updated table
result = table.scan().to_pandas()
print(f"\nTotal rows now: {len(result)}")
print(result.to_string(index=False))

# ============================================================
# 6. Filtered scan (predicate pushdown)
# ============================================================
print("\n--- Filtered scan (salary > 95000) ---")
from pyiceberg.expressions import GreaterThan

scan_filtered = table.scan(row_filter=GreaterThan("salary", 95000.0))
result_filtered = scan_filtered.to_pandas()
print(result_filtered.to_string(index=False))

# ============================================================
# 7. Table metadata
# ============================================================
print("\n--- Table Metadata ---")
print(f"  Table location: {table.location()}")
print(f"  Current snapshot: {table.current_snapshot()}")
print(f"  Schema: {table.schema()}")

print("\n🎉 Iceberg basics complete!")
print("Key takeaways:")
print("  - Iceberg uses a CATALOG to manage tables (not just files)")
print("  - Schema is defined with typed fields")
print("  - PyArrow is the data format for read/write")
print("  - Predicate pushdown = only read relevant data files")
