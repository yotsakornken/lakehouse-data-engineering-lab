"""
Delta Lake - MERGE (Upsert)
Demonstrates updating existing rows and inserting new ones in a single operation.
"""
import pandas as pd
from deltalake import DeltaTable, write_deltalake

print("=" * 50)
print("  Delta Lake - MERGE (Upsert)")
print("=" * 50)

delta_path = "./delta-merge"

# ============================================================
# 1. Create initial table
# ============================================================
data = {
    "id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "role": ["Data Engineer", "Analytics Engineer", "ML Engineer",
             "Platform Engineer", "Data Scientist"],
    "salary": [95000, 90000, 105000, 98000, 102000],
}
df = pd.DataFrame(data)
write_deltalake(delta_path, df, mode="overwrite")

print("\n--- Initial table ---")
dt = DeltaTable(delta_path)
print(dt.to_pandas().to_string(index=False))

# ============================================================
# 2. Prepare source data for MERGE
#    - id=2 (Bob): salary update (90000 -> 95000)
#    - id=3 (Charlie): role change
#    - id=6 (Frank): new employee (insert)
# ============================================================
source_data = {
    "id": [2, 3, 6],
    "name": ["Bob", "Charlie", "Frank"],
    "role": ["Analytics Engineer", "AI Engineer", "DevOps Engineer"],
    "salary": [95000, 110000, 91000],
}
df_source = pd.DataFrame(source_data)

print("\n--- Source data (incoming changes) ---")
print(df_source.to_string(index=False))

# ============================================================
# 3. Execute MERGE
#    - MATCH on 'id'
#    - When matched: update all columns
#    - When not matched: insert new row
# ============================================================
dt.merge(
    source=df_source,
    predicate="s.id = t.id",
    source_alias="s",
    target_alias="t",
).when_matched_update_all() \
 .when_not_matched_insert_all() \
 .execute()

print("\n--- After MERGE (upsert) ---")
dt = DeltaTable(delta_path)
result = dt.to_pandas().sort_values("id").reset_index(drop=True)
print(result.to_string(index=False))

# ============================================================
# 4. Conditional MERGE - only update if salary increased
# ============================================================
print("\n\n--- Conditional MERGE demo ---")

conditional_source = {
    "id": [1, 2, 5],
    "name": ["Alice", "Bob", "Eve"],
    "role": ["Data Engineer", "Analytics Engineer", "Data Scientist"],
    "salary": [90000, 100000, 99000],  # Alice lower, Bob higher, Eve lower
}
df_conditional = pd.DataFrame(conditional_source)

print("Source (only update if new salary > current):")
print(df_conditional.to_string(index=False))

dt = DeltaTable(delta_path)
dt.merge(
    source=df_conditional,
    predicate="s.id = t.id",
    source_alias="s",
    target_alias="t",
).when_matched_update(
    updates={"salary": "s.salary", "role": "s.role", "name": "s.name"},
    predicate="s.salary > t.salary",  # Only update if salary goes UP
).execute()

print("\nAfter conditional MERGE (only Bob got updated):")
dt = DeltaTable(delta_path)
result = dt.to_pandas().sort_values("id").reset_index(drop=True)
print(result.to_string(index=False))

# ============================================================
# 5. Show version history
# ============================================================
print("\n--- Version History ---")
for entry in dt.history():
    print(f"  v{entry['version']}: {entry['operation']} - {entry['timestamp']}")

print("\n🎉 MERGE/Upsert complete!")
print("Key takeaways:")
print("  - MERGE = upsert (update + insert in one atomic operation)")
print("  - Can add conditional predicates (e.g., only update if value increased)")
print("  - Each merge creates a new version (full audit trail)")
