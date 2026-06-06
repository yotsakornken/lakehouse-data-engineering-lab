"""
SILVER Layer - Clean & Conform
Read from Bronze, apply data quality rules, write cleaned data.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from deltalake import DeltaTable, write_deltalake

print("=" * 50)
print("  SILVER Layer - Clean & Conform")
print("=" * 50)

# ============================================================
# 1. Read from Bronze
# ============================================================
print("\n--- Reading from Bronze ---")
df_orders = DeltaTable("../lakehouse/bronze/orders").to_pandas()
df_customers = DeltaTable("../lakehouse/bronze/customers").to_pandas()
print(f"Bronze orders: {len(df_orders)} rows")
print(f"Bronze customers: {len(df_customers)} rows")

# ============================================================
# 2. Clean Orders
# ============================================================
print("\n--- Cleaning Orders ---")

# Track data quality issues
quality_issues = []

# 2a. Replace 'NULL' strings with actual NaN
df_orders.replace("NULL", np.nan, inplace=True)
df_orders.replace("", np.nan, inplace=True)

# 2b. Drop rows with null product (can't process without knowing what was ordered)
null_products = df_orders["product"].isna().sum()
if null_products > 0:
    quality_issues.append(f"Dropped {null_products} rows with null product")
df_orders = df_orders.dropna(subset=["product"])

# 2c. Cast types
df_orders["quantity"] = pd.to_numeric(df_orders["quantity"], errors="coerce")
df_orders["unit_price"] = pd.to_numeric(df_orders["unit_price"], errors="coerce")

# 2d. Parse dates, mark invalid ones
df_orders["order_date"] = pd.to_datetime(df_orders["order_date"], errors="coerce")
invalid_dates = df_orders["order_date"].isna().sum()
if invalid_dates > 0:
    quality_issues.append(f"Found {invalid_dates} rows with invalid dates (set to null)")

# 2e. Fill null quantity with 1 (default assumption)
null_qty = df_orders["quantity"].isna().sum()
if null_qty > 0:
    quality_issues.append(f"Filled {null_qty} null quantities with 1")
df_orders["quantity"] = df_orders["quantity"].fillna(1).astype(int)

# 2f. Fill null status with 'unknown'
df_orders["status"] = df_orders["status"].fillna("unknown")

# 2g. Calculate total_amount
df_orders["total_amount"] = df_orders["quantity"] * df_orders["unit_price"]

# 2h. Add processing metadata
df_orders["_processed_at"] = datetime.now().isoformat()

# Remove bronze metadata columns
df_orders = df_orders.drop(columns=["_ingested_at", "_source_file"])

print(f"After cleaning: {len(df_orders)} rows")
print(f"Quality issues found:")
for issue in quality_issues:
    print(f"  ⚠️  {issue}")

# ============================================================
# 3. Clean Customers
# ============================================================
print("\n--- Cleaning Customers ---")

df_customers.replace("NULL", np.nan, inplace=True)
df_customers.replace("", np.nan, inplace=True)

# Fill null city with 'Unknown'
null_cities = df_customers["city"].isna().sum()
if null_cities > 0:
    print(f"  ⚠️  Filled {null_cities} null cities with 'Unknown'")
df_customers["city"] = df_customers["city"].fillna("Unknown")

# Fill null email with placeholder
null_emails = df_customers["email"].isna().sum()
if null_emails > 0:
    print(f"  ⚠️  Filled {null_emails} null emails with 'no-email@placeholder.com'")
df_customers["email"] = df_customers["email"].fillna("no-email@placeholder.com")

# Parse date
df_customers["registered_date"] = pd.to_datetime(df_customers["registered_date"], errors="coerce")

# Add processing metadata
df_customers["_processed_at"] = datetime.now().isoformat()
df_customers = df_customers.drop(columns=["_ingested_at", "_source_file"])

print(f"After cleaning: {len(df_customers)} rows")

# ============================================================
# 4. Write to Silver
# ============================================================
write_deltalake("../lakehouse/silver/orders", df_orders, mode="overwrite")
write_deltalake("../lakehouse/silver/customers", df_customers, mode="overwrite")

print("\n✅ Silver orders written!")
print("✅ Silver customers written!")

# ============================================================
# 5. Show results
# ============================================================
print("\n--- Silver Orders (sample) ---")
print(df_orders.head(10).to_string(index=False))
print("\n--- Silver Customers ---")
print(df_customers.to_string(index=False))

print("\n" + "=" * 50)
print("  SILVER Summary")
print("=" * 50)
print("  - Cast columns to proper types (int, float, datetime)")
print("  - Handled nulls (drop, fill, or flag)")
print("  - Removed dirty/unprocessable rows")
print("  - Added computed columns (total_amount)")
print("  - Data is now QUERYABLE and TRUSTWORTHY")
