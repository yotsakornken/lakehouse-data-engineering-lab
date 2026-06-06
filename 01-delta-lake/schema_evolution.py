"""
Delta Lake - Schema Evolution
Demonstrates adding new columns without rewriting the table.
"""
import pandas as pd
from deltalake import DeltaTable, write_deltalake

print("=" * 50)
print("  Delta Lake - Schema Evolution")
print("=" * 50)

delta_path = "./delta-schema-evolution"

# ============================================================
# 1. Write initial table (v0)
# ============================================================
data_v0 = {
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "role": ["Data Engineer", "Analytics Engineer", "ML Engineer"],
    "salary": [95000, 90000, 105000],
}
df_v0 = pd.DataFrame(data_v0)
write_deltalake(delta_path, df_v0, mode="overwrite")

print("\n--- Version 0: Original schema ---")
dt = DeltaTable(delta_path)
print(f"Schema: {dt.schema()}")
print(dt.to_pandas().to_string(index=False))

# ============================================================
# 2. Append data WITH a new column (schema evolution)
# ============================================================
data_v1 = {
    "id": [4, 5],
    "name": ["Diana", "Eve"],
    "role": ["Platform Engineer", "Data Scientist"],
    "salary": [98000, 102000],
    "department": ["Infrastructure", "Research"],  # NEW COLUMN
}
df_v1 = pd.DataFrame(data_v1)

# schema_mode="merge" allows adding new columns
write_deltalake(delta_path, df_v1, mode="append", schema_mode="merge")

print("\n--- Version 1: After schema evolution (new 'department' column) ---")
dt = DeltaTable(delta_path)
print(f"Schema: {dt.schema()}")
print(dt.to_pandas().to_string(index=False))
# Note: old rows have null for 'department'

# ============================================================
# 3. Overwrite with even more columns
# ============================================================
data_v2 = {
    "id": [6],
    "name": ["Frank"],
    "role": ["DevOps Engineer"],
    "salary": [91000],
    "department": ["Operations"],
    "start_year": [2024],  # ANOTHER NEW COLUMN
}
df_v2 = pd.DataFrame(data_v2)
write_deltalake(delta_path, df_v2, mode="append", schema_mode="merge")

print("\n--- Version 2: Another new column 'start_year' ---")
dt = DeltaTable(delta_path)
print(f"Schema: {dt.schema()}")
print(dt.to_pandas().to_string(index=False))

# ============================================================
# 4. Schema enforcement - what happens with wrong types?
# ============================================================
print("\n--- Schema Enforcement Demo ---")
try:
    bad_data = {
        "id": ["not_an_int"],  # Wrong type! Should be int
        "name": ["Test"],
        "role": ["Test"],
        "salary": ["not_a_number"],  # Wrong type!
    }
    df_bad = pd.DataFrame(bad_data)
    write_deltalake(delta_path, df_bad, mode="append")
    print("Written successfully (types were coerced)")
except Exception as e:
    print(f"Blocked! Error: {type(e).__name__}: {e}")

print("\n🎉 Schema evolution complete!")
print("Key takeaways:")
print("  - schema_mode='merge' allows adding new columns on append")
print("  - Old rows get null for new columns")
print("  - Delta enforces types (schema enforcement)")
