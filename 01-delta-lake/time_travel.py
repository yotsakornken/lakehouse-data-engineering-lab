"""
Delta Lake - Time Travel
Demonstrates reading historical versions and restoring previous states.
"""
import pandas as pd
from deltalake import DeltaTable, write_deltalake

print("=" * 50)
print("  Delta Lake - Time Travel")
print("=" * 50)

delta_path = "./delta-timetravel"

# ============================================================
# 1. Create version 0
# ============================================================
data_v0 = {
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "salary": [95000, 90000, 105000],
}
write_deltalake(delta_path, pd.DataFrame(data_v0), mode="overwrite")
print("\n--- Version 0: Initial data ---")
print(DeltaTable(delta_path).to_pandas().to_string(index=False))

# ============================================================
# 2. Create version 1 (salary update via overwrite)
# ============================================================
data_v1 = {
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "salary": [100000, 95000, 110000],  # Everyone got a raise!
}
write_deltalake(delta_path, pd.DataFrame(data_v1), mode="overwrite")
print("\n--- Version 1: After raises ---")
print(DeltaTable(delta_path).to_pandas().to_string(index=False))

# ============================================================
# 3. Create version 2 (add new employees)
# ============================================================
data_new = {
    "id": [4, 5],
    "name": ["Diana", "Eve"],
    "salary": [98000, 102000],
}
write_deltalake(delta_path, pd.DataFrame(data_new), mode="append")
print("\n--- Version 2: New hires added ---")
print(DeltaTable(delta_path).to_pandas().to_string(index=False))

# ============================================================
# 4. Create version 3 (oops, accidentally delete everyone!)
# ============================================================
data_oops = {
    "id": [999],
    "name": ["Oops"],
    "salary": [0],
}
write_deltalake(delta_path, pd.DataFrame(data_oops), mode="overwrite")
print("\n--- Version 3: Accidental overwrite! 😱 ---")
print(DeltaTable(delta_path).to_pandas().to_string(index=False))

# ============================================================
# 5. Time travel - read any previous version
# ============================================================
print("\n" + "=" * 50)
print("  TIME TRAVEL")
print("=" * 50)

for version in range(4):
    dt = DeltaTable(delta_path, version=version)
    df = dt.to_pandas()
    print(f"\n--- Reading Version {version} ({len(df)} rows) ---")
    print(df.to_string(index=False))

# ============================================================
# 6. Restore to version 2 (before the accident)
# ============================================================
print("\n" + "=" * 50)
print("  RESTORE")
print("=" * 50)

dt = DeltaTable(delta_path)
print(f"\nCurrent version: {dt.version()} (the broken one)")

# Restore by reading v2 and overwriting
df_restore = DeltaTable(delta_path, version=2).to_pandas()
write_deltalake(delta_path, df_restore, mode="overwrite")

dt = DeltaTable(delta_path)
print(f"After restore, version: {dt.version()}")
print("\n--- Restored data (from version 2) ---")
print(dt.to_pandas().to_string(index=False))

# ============================================================
# 7. Full history
# ============================================================
print("\n--- Complete Version History ---")
dt = DeltaTable(delta_path)
for entry in dt.history():
    print(f"  v{entry['version']}: {entry['operation']:12s} | {entry['timestamp']}")

print("\n🎉 Time travel complete!")
print("Key takeaways:")
print("  - Every write creates a new version")
print("  - Can read ANY previous version by number")
print("  - Can 'restore' by reading old version + overwriting")
print("  - History shows full audit trail of all operations")
print("  - VACUUM deletes old files — time travel won't work after that!")
