-- Databricks notebook source
-- MAGIC %md
-- MAGIC # 02 - Unity Catalog
-- MAGIC Three-level namespace: **Catalog → Schema → Table**
-- MAGIC 
-- MAGIC Unity Catalog provides:
-- MAGIC - Centralized governance across workspaces
-- MAGIC - Fine-grained access control
-- MAGIC - Data lineage tracking
-- MAGIC - Audit logging

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Three-Level Namespace
-- MAGIC ```
-- MAGIC catalog.schema.table
-- MAGIC ```
-- MAGIC 
-- MAGIC - **Catalog** = top-level container (like a database server)
-- MAGIC - **Schema** = logical grouping (like a database)
-- MAGIC - **Table** = the actual data
-- MAGIC 
-- MAGIC Example: `production.sales.orders`

-- COMMAND ----------

-- Create a catalog (requires admin privileges)
-- CREATE CATALOG IF NOT EXISTS dev_catalog;

-- Use the catalog
-- USE CATALOG dev_catalog;

-- Create schemas (our medallion layers!)
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- COMMAND ----------

-- Create tables in the proper namespace
CREATE TABLE IF NOT EXISTS bronze.raw_orders (
    order_id INT,
    customer_id STRING,
    product STRING,
    quantity INT,
    unit_price DOUBLE,
    order_date STRING,
    status STRING,
    _ingested_at TIMESTAMP
);

-- COMMAND ----------

-- Insert sample data
INSERT INTO bronze.raw_orders (order_id, customer_id, product, quantity, unit_price, order_date, status, _ingested_at)
VALUES
    (1001, 'C001', 'Laptop', 1, 45000, '2024-01-15', 'completed', CURRENT_TIMESTAMP()),
    (1002, 'C002', 'Mouse', 2, 590, '2024-01-15', 'completed', CURRENT_TIMESTAMP()),
    (1003, 'C001', 'Keyboard', 1, 1890, '2024-01-16', 'completed', CURRENT_TIMESTAMP()),
    (1004, 'C003', 'Monitor', 1, 12500, '2024-01-16', 'pending', CURRENT_TIMESTAMP()),
    (1005, 'C002', 'USB Cable', 3, 190, '2024-01-17', 'completed', CURRENT_TIMESTAMP());

-- COMMAND ----------

-- Query with full namespace
SELECT * FROM bronze.raw_orders;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Silver Layer with Transformations

-- COMMAND ----------

CREATE OR REPLACE TABLE silver.orders AS
SELECT
    order_id,
    customer_id,
    product,
    quantity,
    unit_price,
    quantity * unit_price AS total_amount,
    CAST(order_date AS DATE) AS order_date,
    LOWER(TRIM(status)) AS status,
    CURRENT_TIMESTAMP AS _processed_at
FROM bronze.raw_orders
WHERE product IS NOT NULL;

-- COMMAND ----------

SELECT * FROM silver.orders;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Gold Layer - Business Aggregates

-- COMMAND ----------

CREATE OR REPLACE TABLE gold.daily_revenue AS
SELECT
    order_date,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(total_amount) AS total_revenue,
    SUM(quantity) AS total_items,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM silver.orders
WHERE status = 'completed'
GROUP BY order_date
ORDER BY order_date;

-- COMMAND ----------

SELECT * FROM gold.daily_revenue;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Governance Features

-- COMMAND ----------

-- View table lineage
-- DESCRIBE TABLE EXTENDED silver.orders;

-- Grant access (requires Unity Catalog)
-- GRANT SELECT ON TABLE gold.daily_revenue TO `analysts@company.com`;
-- GRANT USAGE ON SCHEMA gold TO `analysts@company.com`;

-- View grants
-- SHOW GRANTS ON TABLE gold.daily_revenue;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Key Takeaways
-- MAGIC - Unity Catalog = 3-level namespace (catalog.schema.table)
-- MAGIC - Maps perfectly to medallion architecture (bronze/silver/gold schemas)
-- MAGIC - Centralized access control with GRANT/REVOKE
-- MAGIC - Built-in data lineage (who uses what)
-- MAGIC - Audit logs for compliance
