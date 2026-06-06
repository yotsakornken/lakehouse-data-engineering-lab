"""
Apache Iceberg - Time Travel & Snapshots
Demonstrates reading historical versions of Iceberg tables.
"""
import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog

print("=" * 50)
print("  Apache Iceberg - Time Travel & Snapshots")
print("=" * 50)

# ============================================================
# 1. Connect to catalog
# ============================================================
catalog = SqlCatalog(
    "local",
    **{
        "uri": "sqlite:///./iceberg_catalog.db",
        "warehouse": "./iceberg-warehouse",
    },
)

try:
    catalog.create_namespace("timetravel")
except Exception:
    pass

# ============================================================
# 2. Create table and write multiple versions
# ============================================================
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, LongType, StringType, DoubleType

schema = Schema(
    NestedField(field_id=1, name="id", field_type=LongType(), required=False),
    NestedField(field_id=2, name="name", field_type=StringType(), required=False),
    NestedField(field_id=3, name="salary", field_type=DoubleType(), required=False),
)

try:
    catalog.drop_table("timetravel.salaries")
except Exception:
    pass

table = catalog.create_table("timetravel.salaries", schema=schema)

# Version 1: Initial data
print("\n--- Writing Version 1 (initial) ---")
v1_data = pa.table({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "salary": [95000.0, 90000.0, 105000.0],
})
table.overwrite(v1_data)
print(table.scan().to_pandas().to_string(index=False))

# Version 2: Salary updates
print("\n--- Writing Version 2 (raises) ---")
v2_data = pa.table({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "salary": [100000.0, 95000.0, 110000.0],
})
table.overwrite(v2_data)
print(table.scan().to_pandas().to_string(index=False))

# Version 3: New hires
print("\n--- Writing Version 3 (new hires) ---")
v3_data = pa.table({
    "id": [4, 5],
    "name": ["Diana", "Eve"],
    "salary": [98000.0, 102000.0],
})
table.append(v3_data)
print(table.scan().to_pandas().to_string(index=False))

# ============================================================
# 3. List all snapshots
# ============================================================
print("\n--- Snapshot History ---")
table = catalog.load_table("timetravel.salaries")

for snapshot in table.snapshots():
    print(f"  Snapshot ID: {snapshot.snapshot_id}")
    print(f"  Timestamp: {snapshot.timestamp_ms}")
    print(f"  Operation: {snapshot.summary.operation if snapshot.summary else 'N/A'}")
    print()

# ============================================================
# 4. Time Travel - Read previous snapshots
# ============================================================
print("--- Time Travel ---")
snapshots = list(table.snapshots())

if len(snapshots) >= 2:
    # Read the first snapshot (version 1)
    first_snapshot_id = snapshots[0].snapshot_id
    print(f"\nReading first snapshot (ID: {first_snapshot_id}):")
    scan_v1 = table.scan(snapshot_id=first_snapshot_id)
    print(scan_v1.to_pandas().to_string(index=False))

    # Read second snapshot (version 2)
    second_snapshot_id = snapshots[1].snapshot_id
    print(f"\nReading second snapshot (ID: {second_snapshot_id}):")
    scan_v2 = table.scan(snapshot_id=second_snapshot_id)
    print(scan_v2.to_pandas().to_string(index=False))

# Read current (latest)
print(f"\nCurrent (latest) version:")
print(table.scan().to_pandas().to_string(index=False))

# ============================================================
# 5. Iceberg vs Delta Lake Time Travel
# ============================================================
print("\n" + "=" * 50)
print("  Comparison: Iceberg vs Delta Time Travel")
print("=" * 50)
print("""
| Feature           | Delta Lake              | Apache Iceberg          |
|-------------------|-------------------------|-------------------------|
| Version ID        | Sequential (0, 1, 2...) | Snapshot IDs (random)   |
| Access by         | Version number or time  | Snapshot ID or time     |
| Storage           | _delta_log/ (JSON)      | metadata/ (Avro/JSON)   |
| Cleanup           | VACUUM                  | expire_snapshots        |
""")

print("\n🎉 Time travel complete!")
