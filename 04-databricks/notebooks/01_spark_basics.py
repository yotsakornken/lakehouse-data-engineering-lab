# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Spark Basics on Databricks
# MAGIC Covers: SparkSession, DataFrames, transformations, actions
# MAGIC 
# MAGIC **Run this in Databricks Community Edition or any Databricks workspace**

# COMMAND ----------

# In Databricks, SparkSession is pre-configured as `spark`
# No need to create one manually!

# Create sample data
data = [
    (1, "Alice", "Data Engineer", 95000),
    (2, "Bob", "Analytics Engineer", 90000),
    (3, "Charlie", "ML Engineer", 105000),
    (4, "Diana", "Platform Engineer", 98000),
    (5, "Eve", "Data Scientist", 102000),
]
columns = ["id", "name", "role", "salary"]

df = spark.createDataFrame(data, columns)
display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transformations vs Actions
# MAGIC - **Transformations** = lazy (filter, select, groupBy) — builds a plan
# MAGIC - **Actions** = trigger execution (show, count, collect, write)

# COMMAND ----------

# Transformation: filter high earners
high_earners = df.filter(df.salary > 95000)

# Transformation: select specific columns
names_only = df.select("name", "role")

# Action: show results (triggers computation)
print("High earners:")
display(high_earners)

print(f"\nTotal employees: {df.count()}")
print(f"High earners count: {high_earners.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## SQL Interface
# MAGIC Databricks lets you switch between DataFrame API and SQL seamlessly

# COMMAND ----------

# Register as temp view
df.createOrReplaceTempView("employees")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Now you can query with SQL!
# MAGIC SELECT role, AVG(salary) as avg_salary, COUNT(*) as headcount
# MAGIC FROM employees
# MAGIC GROUP BY role
# MAGIC ORDER BY avg_salary DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write as Delta Table
# MAGIC In Databricks, Delta is the DEFAULT format — no extra config needed!

# COMMAND ----------

# Write to a managed Delta table
df.write.format("delta").mode("overwrite").saveAsTable("default.employees")

# Read it back
df_delta = spark.table("default.employees")
display(df_delta)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check table history (time travel metadata)
# MAGIC DESCRIBE HISTORY default.employees

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key Takeaways
# MAGIC - Databricks provides `spark` session automatically
# MAGIC - `display()` replaces `.show()` for pretty output
# MAGIC - Delta Lake is the default format
# MAGIC - You can mix Python and SQL in the same notebook (`%sql` magic)
# MAGIC - Everything is versioned automatically
