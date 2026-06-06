# Databricks notebook source
# MAGIC %md
# MAGIC # 05 - Databricks Workflows & Jobs
# MAGIC Orchestrate notebooks and tasks into production pipelines.
# MAGIC 
# MAGIC Workflows = Databricks' built-in orchestrator (like Airflow, but managed).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Workflow Concepts
# MAGIC 
# MAGIC ```
# MAGIC Workflow (Job)
# MAGIC ├── Task 1: Ingest (Auto Loader notebook)
# MAGIC ├── Task 2: Transform (Silver notebook)  ← depends on Task 1
# MAGIC ├── Task 3: Aggregate (Gold notebook)    ← depends on Task 2
# MAGIC └── Task 4: Quality Check (test notebook) ← depends on Task 3
# MAGIC ```
# MAGIC 
# MAGIC - **Task**: A single unit of work (notebook, SQL, Python script, dbt)
# MAGIC - **Job**: Collection of tasks with dependencies
# MAGIC - **Schedule**: Cron-based or triggered

# COMMAND ----------

# MAGIC %md
# MAGIC ## Task Parameters & Widgets
# MAGIC Pass parameters between notebooks using widgets

# COMMAND ----------

# Define parameters with widgets
dbutils.widgets.text("environment", "dev", "Environment")
dbutils.widgets.text("start_date", "2024-01-01", "Start Date")
dbutils.widgets.dropdown("mode", "incremental", ["full", "incremental"], "Load Mode")

# Get parameter values
env = dbutils.widgets.get("environment")
start_date = dbutils.widgets.get("start_date")
mode = dbutils.widgets.get("mode")

print(f"Running in: {env}")
print(f"Start date: {start_date}")
print(f"Mode: {mode}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Task Dependencies Pattern

# COMMAND ----------

# Task 1: Bronze ingestion
def ingest_bronze(source_path, target_table):
    """Ingest raw data to bronze layer"""
    df = (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaLocation", f"/checkpoints/{target_table}/schema")
        .option("header", "true")
        .load(source_path)
    )
    
    (
        df.writeStream
        .format("delta")
        .option("checkpointLocation", f"/checkpoints/{target_table}/")
        .trigger(availableNow=True)
        .toTable(target_table)
    )
    return target_table

# COMMAND ----------

# Task 2: Silver transformation
def transform_silver(bronze_table, silver_table):
    """Clean and transform bronze to silver"""
    df = spark.table(bronze_table)
    
    df_clean = (
        df
        .filter(col("product").isNotNull())
        .withColumn("quantity", col("quantity").cast("int"))
        .withColumn("unit_price", col("unit_price").cast("double"))
        .withColumn("total_amount", col("quantity") * col("unit_price"))
        .withColumn("_processed_at", current_timestamp())
    )
    
    df_clean.write.format("delta").mode("overwrite").saveAsTable(silver_table)
    return silver_table

# COMMAND ----------

# Task 3: Gold aggregation
def build_gold(silver_table, gold_table):
    """Build business-level aggregates"""
    df = spark.table(silver_table)
    
    df_gold = (
        df
        .filter(col("status") == "completed")
        .groupBy("product")
        .agg(
            sum("total_amount").alias("total_revenue"),
            count("*").alias("order_count")
        )
        .orderBy(col("total_revenue").desc())
    )
    
    df_gold.write.format("delta").mode("overwrite").saveAsTable(gold_table)
    return gold_table

# COMMAND ----------

# MAGIC %md
# MAGIC ## Running a Notebook from Another Notebook

# COMMAND ----------

# Call another notebook (blocking — waits for completion)
# result = dbutils.notebook.run("./02_unity_catalog", timeout_seconds=300, arguments={"env": "dev"})
# print(f"Result: {result}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Job Configuration (JSON)
# MAGIC This is what you'd define in the Databricks UI or via API:

# COMMAND ----------

# MAGIC %md
# MAGIC ```json
# MAGIC {
# MAGIC   "name": "medallion_pipeline",
# MAGIC   "schedule": {
# MAGIC     "quartz_cron_expression": "0 0 6 * * ?",
# MAGIC     "timezone_id": "Asia/Bangkok"
# MAGIC   },
# MAGIC   "tasks": [
# MAGIC     {
# MAGIC       "task_key": "ingest_bronze",
# MAGIC       "notebook_task": {
# MAGIC         "notebook_path": "/Repos/data-team/notebooks/01_ingest"
# MAGIC       },
# MAGIC       "cluster_key": "shared_cluster"
# MAGIC     },
# MAGIC     {
# MAGIC       "task_key": "transform_silver",
# MAGIC       "depends_on": [{"task_key": "ingest_bronze"}],
# MAGIC       "notebook_task": {
# MAGIC         "notebook_path": "/Repos/data-team/notebooks/02_transform"
# MAGIC       }
# MAGIC     },
# MAGIC     {
# MAGIC       "task_key": "build_gold",
# MAGIC       "depends_on": [{"task_key": "transform_silver"}],
# MAGIC       "notebook_task": {
# MAGIC         "notebook_path": "/Repos/data-team/notebooks/03_aggregate"
# MAGIC       }
# MAGIC     }
# MAGIC   ]
# MAGIC }
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Workflows vs Other Orchestrators
# MAGIC 
# MAGIC | Feature | Databricks Workflows | Airflow | Prefect |
# MAGIC |---------|---------------------|---------|---------|
# MAGIC | Setup | Zero (built-in) | Self-hosted or managed | Cloud/self-hosted |
# MAGIC | Best for | Databricks-native pipelines | Multi-system orchestration | Python-heavy flows |
# MAGIC | Task types | Notebook, SQL, dbt, JAR | Any operator | Any Python function |
# MAGIC | Monitoring | Built-in UI | Webserver UI | Cloud UI |
# MAGIC | Cost | Included in Databricks | Separate infrastructure | Separate |
# MAGIC 
# MAGIC **Use Workflows when**: All your processing is in Databricks
# MAGIC **Use Airflow when**: You orchestrate across many systems (APIs, databases, Spark, etc.)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key Takeaways
# MAGIC - Workflows = Databricks' built-in orchestrator (DAG of tasks)
# MAGIC - Tasks can be notebooks, SQL, dbt, or Python scripts
# MAGIC - Use `dbutils.widgets` for parameterized notebooks
# MAGIC - `trigger(availableNow=True)` + Workflows = scheduled incremental pipelines
# MAGIC - For Databricks-only pipelines, Workflows is simpler than Airflow
