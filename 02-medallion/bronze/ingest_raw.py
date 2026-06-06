"""
BRONZE Layer - Raw Ingestion
Ingest raw CSV files into Delta tables with NO transformations.
Add metadata: ingestion timestamp, source filename.
"""
import pandas as pd
from datetime import datetime
from deltalake import write_deltalake

print("=" * 50)
print("  BRONZE Layer - Raw Ingestion")
print("=" * 50)

# ============================================================
# 1. Ingest Orders (as-is, no cleaning)
# ============================================================
print("\n--- Ingesting raw_orders.csv ---")
df_orders = pd.read_csv("../data/raw_orders.csv", dtype=str)  # Read everything as string (raw!)

# Add metadata columns
df_orders["_ingested_at"] = datetime.now().isoformat()
df_orders["_source_file"] = "raw_orders.csv"

print(f"Rows: {len(df_orders)}")
print(f"Columns: {list(df_orders.columns)}")
print(df_orders.head().to_string(index=False))

# Write to Bronze Delta table
write_deltalake("../lakehouse/bronze/orders", df_orders, mode="overwrite")
print("\n✅ Bronze orders written!")

# ============================================================
# 2. Ingest Customers (as-is, no cleaning)
# ============================================================
print("\n--- Ingesting raw_customers.csv ---")
df_customers = pd.read_csv("../data/raw_customers.csv", dtype=str)

df_customers["_ingested_at"] = datetime.now().isoformat()
df_customers["_source_file"] = "raw_customers.csv"

print(f"Rows: {len(df_customers)}")
print(f"Columns: {list(df_customers.columns)}")
print(df_customers.head().to_string(index=False))

write_deltalake("../lakehouse/bronze/customers", df_customers, mode="overwrite")
print("\n✅ Bronze customers written!")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 50)
print("  BRONZE Summary")
print("=" * 50)
print("  - Data loaded AS-IS (no transformations)")
print("  - All columns stored as strings (raw)")
print("  - Added _ingested_at and _source_file metadata")
print("  - Dirty data preserved (nulls, invalid dates, etc.)")
print("  - This is our 'source of truth' — never modify bronze!")
