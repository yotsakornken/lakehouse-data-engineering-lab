# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Structured Streaming
# MAGIC Real-time data processing with Spark Structured Streaming.
# MAGIC 
# MAGIC Key concept: **treat streaming data as an infinite table that keeps growing.**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Streaming Mental Model
# MAGIC ```
# MAGIC Traditional Batch:
# MAGIC   [Fixed Data] → Process → [Result]
# MAGIC 
# MAGIC Structured Streaming:
# MAGIC   [Growing Table] → Process continuously → [Updating Result]
# MAGIC     ↑ new rows keep arriving
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stream from Delta Table (CDC pattern)
# MAGIC Read changes from a Delta table as a stream

# COMMAND ----------

# Read a Delta table as a stream (only new inserts)
df_stream = (
    spark.readStream
    .format("delta")
    .table("bronze.raw_orders")
)

# Apply transformations (same as batch!)
from pyspark.sql.functions import col, current_timestamp, upper

df_transformed = (
    df_stream
    .filter(col("status") == "completed")
    .withColumn("total_amount", col("quantity") * col("unit_price"))
    .withColumn("processed_at", current_timestamp())
)

# Write to silver (streaming)
(
    df_transformed.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/mnt/checkpoints/silver_orders/")
    .trigger(availableNow=True)
    .toTable("silver.orders_stream")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Output Modes
# MAGIC 
# MAGIC | Mode | Description | Use Case |
# MAGIC |------|-------------|----------|
# MAGIC | `append` | Only new rows added | Raw ingestion, logs |
# MAGIC | `update` | Only changed rows | Aggregations with updates |
# MAGIC | `complete` | Full result rewritten | Small aggregation tables |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Real-time Aggregation Example

# COMMAND ----------

from pyspark.sql.functions import window, sum, count

# Stream from bronze
df_orders_stream = (
    spark.readStream
    .format("delta")
    .table("bronze.raw_orders")
)

# Real-time revenue by 1-hour windows
df_hourly_revenue = (
    df_orders_stream
    .filter(col("status") == "completed")
    .withColumn("total", col("quantity") * col("unit_price"))
    .groupBy(
        window(col("order_date").cast("timestamp"), "1 hour")
    )
    .agg(
        sum("total").alias("hourly_revenue"),
        count("*").alias("order_count")
    )
)

# Write with 'complete' mode (rewrites the whole result table)
(
    df_hourly_revenue.writeStream
    .format("delta")
    .outputMode("complete")
    .option("checkpointLocation", "/mnt/checkpoints/hourly_revenue/")
    .trigger(availableNow=True)
    .toTable("gold.hourly_revenue")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stream-to-Stream Join (Advanced)

# COMMAND ----------

# Join two streams (e.g., orders + payments)
# df_orders_stream = spark.readStream.table("bronze.orders")
# df_payments_stream = spark.readStream.table("bronze.payments")

# joined = df_orders_stream.join(
#     df_payments_stream,
#     on="order_id",
#     how="inner"
# )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Streaming vs Batch in Databricks
# MAGIC 
# MAGIC | Aspect | Batch | Streaming |
# MAGIC |--------|-------|-----------|
# MAGIC | Code | `spark.read` | `spark.readStream` |
# MAGIC | Output | `df.write` | `df.writeStream` |
# MAGIC | Latency | Minutes-hours | Seconds-minutes |
# MAGIC | Use case | Reports, backfill | Real-time dashboards, alerts |
# MAGIC | Cost | Lower (runs & stops) | Higher (always on) |
# MAGIC 
# MAGIC **Pro tip**: Use `trigger(availableNow=True)` for "near real-time" —
# MAGIC gets you streaming benefits with batch-like cost (scheduled runs).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key Takeaways
# MAGIC - Same DataFrame API for batch and streaming (just `read` → `readStream`)
# MAGIC - Delta tables can be BOTH source and sink for streams
# MAGIC - `trigger(availableNow=True)` = best of both worlds
# MAGIC - Checkpoints ensure exactly-once processing
# MAGIC - Structured Streaming + Delta = incremental pipelines
