"""
Delta Lake Basics - Module 01
Using deltalake (delta-rs) for a lightweight local experience.
No Java/Spark/Hadoop required!
"""
import pandas as pd
from deltalake import DeltaTable, write_deltalake

print("=" * 50)
print("  Delta Lake Basics - Module 01")
print("=" * 50)

# ============================================================
# 1. Create sample data
# ============================================================
data = {
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "role": ["Data Engineer", "Analytics Engineer", "ML Engineer"],
    "salary": [95000, 90000, 105000],
}
df = pd.DataFrame(data)

print("\n--- Original DataFrame ---")
print(df.to_string(index=False))

# ============================================================
# 2. Write as Delta table
# ============================================================
delta_path = "./delta-table"
write_deltalake(delta_path, df, mode="overwrite")
print(f"\n✅ Delta table written to {delta_path}")

# ============================================================
# 3. Read it back
# ============================================================
dt = DeltaTable(delta_path)
df_read = dt.to_pandas()
print("\n--- Read from Delta table ---")
print(df_read.to_string(index=False))

# ============================================================
# 4. Check version history
# ============================================================
print(f"\n--- Table version: {dt.version()} ---")

# ============================================================
# 5. Append more data (creates version 1)
# ============================================================
new_data = {
    "id": [4, 5],
    "name": ["Diana", "Eve"],
    "role": ["Platform Engineer", "Data Scientist"],
    "salary": [98000, 102000],
}
df_new = pd.DataFrame(new_data)
write_deltalake(delta_path, df_new, mode="append")
print("\n✅ Appended new data (version 1)")

# Read updated table
dt = DeltaTable(delta_path)
print(f"\n--- Table version: {dt.version()} ---")
print(f"--- Total rows: {len(dt.to_pandas())} ---")
print(dt.to_pandas().to_string(index=False))

# ============================================================
# 6. Time travel - read version 0
# ============================================================
dt_v0 = DeltaTable(delta_path, version=0)
print("\n--- Time Travel: Version 0 ---")
print(dt_v0.to_pandas().to_string(index=False))

# ============================================================
# 7. Show table history
# ============================================================
print("\n--- Table History ---")
history = dt.history()
for entry in history:
    print(f"  Version {entry['version']}: {entry['timestamp']} - {entry['operation']}")

print("\n🎉 Done! Delta Lake basics complete.")
