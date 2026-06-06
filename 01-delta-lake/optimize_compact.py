"""
Delta Lake - OPTIMIZE & Compaction
Demonstrates file compaction and Z-ordering for query performance.
"""
import pandas as pd
import numpy as np
from deltalake import DeltaTable, write_deltalake

print("=" * 50)
print("  Delta Lake - OPTIMIZE & Compaction")
print("=" * 50)

delta_path = "./delta-optimize"

# ============================================================
# 1. Create many small files (simulating frequent small writes)
# ============================================================
print("\n--- Writing 10 small batches (simulating micro-batches) ---")

np.random.seed(42)
roles = ["Data Engineer", "Analytics Engineer", "ML Engineer",
         "Platform Engineer", "Data Scientist", "DevOps Engineer"]
departments = ["Engineering", "Analytics", "Research", "Infrastructure"]

for i in range(10):
    batch = {
        "id": list(range(i * 100, (i + 1) * 100)),
        "name": [f"Employee_{j}" for j in range(i * 100, (i + 1) * 100)],
        "role": [roles[j % len(roles)] for j in range(100)],
        "department": [departments[j % len(departments)] for j in range(100)],
        "salary": np.random.randint(70000, 130000, 100).tolist(),
    }
    df_batch = pd.DataFrame(batch)
    if i == 0:
        write_deltalake(delta_path, df_batch, mode="overwrite")
    else:
        write_deltalake(delta_path, df_batch, mode="append")

dt = DeltaTable(delta_path)
files_before = dt.file_uris()
print(f"Total rows: {len(dt.to_pandas())}")
print(f"Number of files BEFORE optimize: {len(files_before)}")

# ============================================================
# 2. OPTIMIZE - compact small files into larger ones
# ============================================================
print("\n--- Running OPTIMIZE (compaction) ---")
result = dt.optimize.compact()
print(f"Compaction result: {result}")

dt = DeltaTable(delta_path)
files_after = dt.file_uris()
print(f"Number of files AFTER optimize: {len(files_after)}")
print(f"Files reduced: {len(files_before)} -> {len(files_after)}")

# ============================================================
# 3. Z-ORDER - co-locate data for better query performance
# ============================================================
print("\n--- Running Z-ORDER on 'department' column ---")
dt = DeltaTable(delta_path)
result = dt.optimize.z_order(columns=["department"])
print(f"Z-order result: {result}")

dt = DeltaTable(delta_path)
files_zorder = dt.file_uris()
print(f"Files after Z-ORDER: {len(files_zorder)}")

# ============================================================
# 4. VACUUM - remove old files no longer referenced
# ============================================================
print("\n--- Table versions before VACUUM ---")
for entry in dt.history():
    print(f"  v{entry['version']}: {entry['operation']}")

print("\n--- Running VACUUM (remove old files) ---")
# retention_hours=0 is for demo only; in production use 168 (7 days)
dt.vacuum(retention_hours=0, enforce_retention_duration=False, dry_run=False)
print("Vacuum complete! Old data files removed.")

# ============================================================
# 5. Verify data integrity after all operations
# ============================================================
print("\n--- Final verification ---")
dt = DeltaTable(delta_path)
final_df = dt.to_pandas()
print(f"Total rows: {len(final_df)}")
print(f"Total files: {len(dt.file_uris())}")
print(f"Current version: {dt.version()}")
print("\nSample data:")
print(final_df.head(10).to_string(index=False))

print("\n🎉 OPTIMIZE & Compaction complete!")
print("Key takeaways:")
print("  - Many small files = slow queries (small file problem)")
print("  - OPTIMIZE compact() merges small files into larger ones")
print("  - Z-ORDER co-locates related data for data skipping")
print("  - VACUUM removes old files (careful with retention period!)")
print("  - After VACUUM, time travel to old versions won't work")
