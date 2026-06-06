# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Auto Loader (cloudFiles)
# MAGIC Incrementally ingest new files as they arrive in cloud storage.
# MAGIC 
# MAGIC Auto Loader:
# MAGIC - Detects NEW files automatically (no manual tracking)
# MAGIC - Handles schema evolution
# MAGIC - Exactly-once processing guarantee
# MAGIC - Scales to millions of files

# COMMAND ----------

# MAGIC %md
# MAGIC ## How Auto Loader Works
# MAGIC ```
# MAGIC Cloud Storage (S3/ADLS/GCS)
# MAGIC     │  new files arrive
# MAGIC     ▼
# MAGIC Auto Loader (cloudFiles)
# MAGIC     │  detects & reads only NEW files
# MAGIC     ▼
# MAGIC Delta Table (Bronze)
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Basic Auto Loader Pattern

# COMMAND ----------

# Configuration
source_path = "/mnt/landing/orders/"  # Where new files land
checkpoint_path = "/mnt/checkpoints/orders/"  # Tracks which files are processed
target_table = "bronze.raw_orders_stream"

# Auto Loader reads new files incrementally
df_stream = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", checkpoint_path)
    .option("header", "true")
    .load(source_path)
)

# Add metadata: which file did this row come from?
from pyspark.sql.functions import current_timestamp, input_file_name

df_enriched = (
    df_stream
    .withColumn("_ingested_at", current_timestamp())
    .withColumn("_source_file", input_file_name())
)

# Write to Delta table (streaming)
(
    df_enriched.writeStream
    .format("delta")
    .option("checkpointLocation", checkpoint_path)
    .outputMode("append")
    .trigger(availableNow=True)  # Process all new files, then stop
    .toTable(target_table)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Auto Loader with Schema Evolution
# MAGIC If source files gain new columns over time, Auto Loader handles it!

# COMMAND ----------

# Schema evolution: automatically add new columns
df_stream_evolved = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/mnt/checkpoints/events/")
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns")  # Key option!
    .load("/mnt/landing/events/")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Trigger Modes
# MAGIC 
# MAGIC | Mode | Use Case |
# MAGIC |------|----------|
# MAGIC | `trigger(availableNow=True)` | Process all new files, then stop (batch-like) |
# MAGIC | `trigger(processingTime="5 minutes")` | Check every 5 minutes |
# MAGIC | No trigger (default) | Continuous streaming |
# MAGIC 
# MAGIC For most data engineering: use `availableNow=True` in scheduled jobs

# COMMAND ----------

# MAGIC %md
# MAGIC ## Auto Loader vs COPY INTO
# MAGIC 
# MAGIC | Feature | Auto Loader | COPY INTO |
# MAGIC |---------|-------------|-----------|
# MAGIC | File tracking | Automatic (checkpoint) | Manual (idempotent) |
# MAGIC | Schema evolution | Yes | No |
# MAGIC | Scale | Millions of files | Thousands of files |
# MAGIC | Incremental | Always | Skips already-loaded files |
# MAGIC | Recommended | ✅ Yes | Legacy / simple cases |

# COMMAND ----------

# MAGIC %md
# MAGIC ## COPY INTO (Alternative for simple cases)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- COPY INTO is simpler but less powerful
# MAGIC COPY INTO bronze.raw_orders
# MAGIC FROM '/mnt/landing/orders/'
# MAGIC FILEFORMAT = CSV
# MAGIC FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true')
# MAGIC COPY_OPTIONS ('mergeSchema' = 'true');

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key Takeaways
# MAGIC - Auto Loader = `spark.readStream.format("cloudFiles")` 
# MAGIC - It only processes NEW files (checkpoint tracks state)
# MAGIC - Handles schema changes automatically
# MAGIC - `availableNow=True` = "process what's new, then stop" (perfect for scheduled jobs)
# MAGIC - Always better than COPY INTO for production workloads
