"""
Apache Iceberg - Schema Evolution
Add, rename, and reorder columns without rewriting data.
"""
import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField, LongType, StringType, DoubleType
)

print("=" * 50)
print("  Apache Iceberg - Schema Evolution")
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
    catalog.create_namespace("evolution")
except Exception:
    pass

try:
    catalog.drop_table("evolution.team")
except Exception:
    pass

schema = Schema(
    NestedField(field_id=1, name="id", field_type=LongType(), required=False),
    NestedField(field_id=2, name="name", field_type=StringType(), required=False),
    NestedField(field_id=3, name="role", field_type=StringType(), required=False),
    NestedField(field_id=4, name="salary", field_type=DoubleType(), required=False),
)

table = catalog.create_table("evolution.team", schema=schema)
print(f"\n--- Original Schema ---")
print(table.schema())

# Write initial data
data = pa.table({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "role": ["Data Engineer", "Analytics Engineer", "ML Engineer"],
    "salary": [95000.0, 90000.0, 105000.0],
})
table.overwrite(data)
print("\nData written:")
print(table.scan().to_pandas().to_string(index=False))

# ============================================================
# 2. ADD a column
# ============================================================
print("\n--- Evolution 1: ADD column 'department' ---")

with table.update_schema() as update:
    update.add_column("department", StringType())

table = catalog.load_table("evolution.team")
print(f"Schema after ADD: {table.schema()}")

# Write data with new column
new_data = pa.table({
    "id": [4],
    "name": ["Diana"],
    "role": ["Platform Engineer"],
    "salary": [98000.0],
    "department": ["Infrastructure"],
})
table.append(new_data)

print("\nData (old rows have null for 'department'):")
print(table.scan().to_pandas().to_string(index=False))

# ============================================================
# 3. RENAME a column
# ============================================================
print("\n--- Evolution 2: RENAME 'role' to 'job_title' ---")

with table.update_schema() as update:
    update.rename_column("role", "job_title")

table = catalog.load_table("evolution.team")
print(f"Schema after RENAME: {table.schema()}")
print(table.scan().to_pandas().to_string(index=False))

# ============================================================
# 4. Make column optional/required
# ============================================================
print("\n--- Evolution 3: Make 'name' optional ---")

with table.update_schema() as update:
    update.make_column_optional("name")

table = catalog.load_table("evolution.team")
# Check if name is now optional
for field in table.schema().fields:
    if field.name == "name":
        print(f"  'name' required = {field.required}")

# ============================================================
# 5. Iceberg vs Delta Schema Evolution
# ============================================================
print("\n" + "=" * 50)
print("  Comparison: Schema Evolution")
print("=" * 50)
print("""
| Operation           | Delta Lake            | Apache Iceberg         |
|---------------------|-----------------------|------------------------|
| Add column          | schema_mode='merge'   | update_schema().add    |
| Rename column       | Not supported*        | update_schema().rename |
| Drop column         | Not supported*        | update_schema().delete |
| Reorder columns     | Not supported         | update_schema().move   |
| Type widening       | Limited               | Supported (int→long)   |
| Metadata only?      | Yes                   | Yes                    |

* Delta supports these via column mapping mode since Delta 2.0
""")

print("\n🎉 Schema evolution complete!")
print("Key takeaways:")
print("  - Iceberg schema evolution is METADATA-ONLY (no data rewrite)")
print("  - Can add, rename, drop, reorder columns")
print("  - Old data files are still readable (nulls for new columns)")
print("  - Each field has a unique ID — renames don't break anything")
