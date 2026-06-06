"""
GOLD Layer - Business Aggregates
Read from Silver, create business-level tables (star schema / KPIs).
"""
import pandas as pd
from datetime import datetime
from deltalake import DeltaTable, write_deltalake

print("=" * 50)
print("  GOLD Layer - Business Aggregates")
print("=" * 50)

# ============================================================
# 1. Read from Silver
# ============================================================
print("\n--- Reading from Silver ---")
df_orders = DeltaTable("../lakehouse/silver/orders").to_pandas()
df_customers = DeltaTable("../lakehouse/silver/customers").to_pandas()
print(f"Silver orders: {len(df_orders)} rows")
print(f"Silver customers: {len(df_customers)} rows")

# ============================================================
# 2. Gold Table: Customer Summary (dim + metrics)
# ============================================================
print("\n--- Building: gold_customer_summary ---")

# Join orders with customers
df_joined = df_orders.merge(df_customers, on="customer_id", how="left")

# Only completed orders for revenue metrics
df_completed = df_joined[df_joined["status"] == "completed"]

customer_summary = df_completed.groupby(
    ["customer_id", "name", "email", "city"]
).agg(
    total_orders=("order_id", "count"),
    total_revenue=("total_amount", "sum"),
    avg_order_value=("total_amount", "mean"),
    first_order_date=("order_date", "min"),
    last_order_date=("order_date", "max"),
).reset_index()

customer_summary["_gold_created_at"] = datetime.now().isoformat()

print(customer_summary.to_string(index=False))

write_deltalake("../lakehouse/gold/customer_summary", customer_summary, mode="overwrite")
print("\n✅ gold_customer_summary written!")

# ============================================================
# 3. Gold Table: Daily Revenue
# ============================================================
print("\n--- Building: gold_daily_revenue ---")

# Filter valid dates and completed orders
df_valid = df_completed.dropna(subset=["order_date"])
df_valid["order_date_str"] = df_valid["order_date"].dt.strftime("%Y-%m-%d")

daily_revenue = df_valid.groupby("order_date_str").agg(
    total_orders=("order_id", "count"),
    total_revenue=("total_amount", "sum"),
    total_items=("quantity", "sum"),
    unique_customers=("customer_id", "nunique"),
).reset_index()

daily_revenue.rename(columns={"order_date_str": "order_date"}, inplace=True)
daily_revenue["_gold_created_at"] = datetime.now().isoformat()

print(daily_revenue.to_string(index=False))

write_deltalake("../lakehouse/gold/daily_revenue", daily_revenue, mode="overwrite")
print("\n✅ gold_daily_revenue written!")

# ============================================================
# 4. Gold Table: Product Performance
# ============================================================
print("\n--- Building: gold_product_performance ---")

product_perf = df_completed.groupby("product").agg(
    total_sold=("quantity", "sum"),
    total_revenue=("total_amount", "sum"),
    order_count=("order_id", "count"),
    avg_unit_price=("unit_price", "mean"),
).reset_index()

product_perf = product_perf.sort_values("total_revenue", ascending=False)
product_perf["revenue_rank"] = range(1, len(product_perf) + 1)
product_perf["_gold_created_at"] = datetime.now().isoformat()

print(product_perf.to_string(index=False))

write_deltalake("../lakehouse/gold/product_performance", product_perf, mode="overwrite")
print("\n✅ gold_product_performance written!")

# ============================================================
# 5. Summary KPIs
# ============================================================
print("\n" + "=" * 50)
print("  GOLD Summary - Business KPIs")
print("=" * 50)
print(f"  Total customers with orders: {len(customer_summary)}")
print(f"  Total revenue (completed): ฿{customer_summary['total_revenue'].sum():,.0f}")
print(f"  Avg order value: ฿{customer_summary['avg_order_value'].mean():,.0f}")
print(f"  Top product: {product_perf.iloc[0]['product']} (฿{product_perf.iloc[0]['total_revenue']:,.0f})")
print(f"  Best customer: {customer_summary.sort_values('total_revenue', ascending=False).iloc[0]['name']}")

print("\n" + "=" * 50)
print("  Medallion Architecture Complete! 🏅")
print("=" * 50)
print("""
  Bronze (raw)     → Exact copy of source, no transforms
  Silver (clean)   → Typed, deduplicated, null-handled
  Gold (business)  → Aggregated KPIs, ready for dashboards

  Lakehouse structure:
  lakehouse/
  ├── bronze/
  │   ├── orders/        (Delta)
  │   └── customers/     (Delta)
  ├── silver/
  │   ├── orders/        (Delta)
  │   └── customers/     (Delta)
  └── gold/
      ├── customer_summary/      (Delta)
      ├── daily_revenue/         (Delta)
      └── product_performance/   (Delta)
""")
