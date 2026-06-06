# Databricks notebook source
# MAGIC %md
# MAGIC # 06 - Delta Live Tables (DLT)
# MAGIC Declarative pipelines: you define WHAT, Databricks handles HOW.
# MAGIC 
# MAGIC DLT = Auto-managed medallion architecture
# MAGIC - Automatic dependency resolution
# MAGIC - Built-in data quality (expectations)
# MAGIC - Auto-scaling & error handling
# MAGIC - No manual orchestration needed

# COMMAND ----------

# MAGIC %md
# MAGIC ## DLT vs Regular Notebooks
# MAGIC 
# MAGIC | Regular Notebooks | Delta Live Tables |
# MAGIC |---|---|
# MAGIC | You manage execution order | DLT resolves dependencies |
# MAGIC | Manual error handling | Built-in retry & quarantine |
# MAGIC | Manual data quality checks | Declarative expectations |
# MAGIC | You manage infra | Auto-scaling clusters |

# COMMAND ----------

# MAGIC %md
# MAGIC ## DLT Pipeline Code
# MAGIC Note: DLT uses special decorators. This code ONLY runs inside a DLT pipeline.

# COMMAND ----------

import dlt
from pyspark.sql.functions import col, current_timestamp

# ============================================================
# BRONZE: Raw ingestion with Auto Loader
# ============================================================
@dlt.table(
    name="bronze_orders",
    comment="Raw orders ingested from landing zone"
)
def bronze_orders():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .load("/mnt/landing/orders/")
        .withColumn("_ingested_at", current_timestamp())
    )


# ============================================================
# SILVER: Cleaned data with quality expectations
# ============================================================
@dlt.table(
    name="silver_orders",
    comment="Cleaned and validated orders"
)
@dlt.expect_or_drop("valid_quantity", "quantity > 0")
@dlt.expect_or_drop("valid_product", "product IS NOT NULL")
@dlt.expect("valid_price", "unit_price > 0")  # Warn but keep
def silver_orders():
    return (
        dlt.read_stream("bronze_orders")
        .withColumn("quantity", col("quantity").cast("int"))
        .withColumn("unit_price", col("unit_price").cast("double"))
        .withColumn("total_amount", col("quantity") * col("unit_price"))
        .withColumn("order_date", col("order_date").cast("date"))
        .withColumn("status", col("status"))
    )


# ============================================================
# GOLD: Business aggregates
# ============================================================
@dlt.table(
    name="gold_daily_revenue",
    comment="Daily revenue aggregation for dashboards"
)
def gold_daily_revenue():
    return (
        dlt.read("silver_orders")
        .filter(col("status") == "completed")
        .groupBy("order_date")
        .agg(
            {"total_amount": "sum", "order_id": "count"}
        )
        .withColumnRenamed("sum(total_amount)", "total_revenue")
        .withColumnRenamed("count(order_id)", "total_orders")
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## DLT Expectations (Data Quality)
# MAGIC 
# MAGIC | Decorator | Behavior |
# MAGIC |-----------|----------|
# MAGIC | `@dlt.expect("name", "condition")` | Warn, keep row |
# MAGIC | `@dlt.expect_or_drop("name", "condition")` | Drop failing rows |
# MAGIC | `@dlt.expect_or_fail("name", "condition")` | Fail the whole pipeline |
# MAGIC 
# MAGIC This is BUILT-IN data quality — no separate framework needed!

# COMMAND ----------

# MAGIC %md
# MAGIC ## DLT Pipeline Configuration (JSON)
# MAGIC ```json
# MAGIC {
# MAGIC   "name": "medallion_dlt_pipeline",
# MAGIC   "target": "production",
# MAGIC   "continuous": false,
# MAGIC   "development": true,
# MAGIC   "notebook_paths": [
# MAGIC     "/Repos/data-team/notebooks/06_delta_live_tables"
# MAGIC   ],
# MAGIC   "clusters": [
# MAGIC     {
# MAGIC       "label": "default",
# MAGIC       "autoscale": {
# MAGIC         "min_workers": 1,
# MAGIC         "max_workers": 4
# MAGIC       }
# MAGIC     }
# MAGIC   ]
# MAGIC }
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key Takeaways
# MAGIC - DLT = declarative medallion pipelines (you define tables, DLT handles the rest)
# MAGIC - `@dlt.table` decorator defines a table
# MAGIC - `@dlt.expect*` adds data quality rules inline
# MAGIC - `dlt.read()` / `dlt.read_stream()` creates dependencies automatically
# MAGIC - Best for: standard medallion pipelines where you want minimal ops work
# MAGIC - NOT for: complex logic, external API calls, non-Databricks targets
