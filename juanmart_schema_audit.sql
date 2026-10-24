-- ==============================================================================
-- JuanMart Data Warehouse - Schema Audit & Diagnostic Profiling Script
-- Objective: Identify data quality issues and potential normalization concerns
--            within a hypothetical source sales database or a staging area.
-- Target Engine: PostgreSQL
-- ==============================================================================

-- Assume a source transactional table (e.g., 'raw_sales') exists which
-- would be the origin of 'juanmart_raw_sales.csv' data.

--------------------------------------------------------------------------------
-- SECTION 1: DUPLICATION CHECKS
-- Identify duplicate records that could violate primary key constraints or
-- indicate redundant data.
--------------------------------------------------------------------------------

-- 1.1: Check for duplicate transaction_ids in the raw sales data
-- This is crucial for identifying records that should be unique.
SELECT
    transaction_id,
    COUNT(*) AS duplicate_count
FROM
    raw_sales -- Hypothetical source table mirroring juanmart_raw_sales.csv
GROUP BY
    transaction_id
HAVING
    COUNT(*) > 1
ORDER BY
    duplicate_count DESC;

-- 1.2: Check for complete duplicate rows (all columns identical)
SELECT
    transaction_id, cust_name, region, order_date, amount_paid, status,
    COUNT(*) AS complete_duplicate_count
FROM
    raw_sales
GROUP BY
    transaction_id, cust_name, region, order_date, amount_paid, status
HAVING
    COUNT(*) > 1
ORDER BY
    complete_duplicate_count DESC;

--------------------------------------------------------------------------------
-- SECTION 2: NULL VALUE ANALYSIS
-- Identify columns with missing values and assess their impact on data quality.
--------------------------------------------------------------------------------

-- 2.1: Percentage of NULLs per column in the raw sales data
SELECT
    'transaction_id' AS column_name,
    COUNT(*) FILTER (WHERE transaction_id IS NULL) AS null_count,
    COUNT(*) AS total_count,
    (COUNT(*) FILTER (WHERE transaction_id IS NULL) * 100.0 / COUNT(*)) AS null_percentage
FROM raw_sales
UNION ALL
SELECT
    'cust_name',
    COUNT(*) FILTER (WHERE cust_name IS NULL),
    COUNT(*),
    (COUNT(*) FILTER (WHERE cust_name IS NULL) * 100.0 / COUNT(*))
FROM raw_sales
UNION ALL
SELECT
    'region',
    COUNT(*) FILTER (WHERE region IS NULL),
    COUNT(*),
    (COUNT(*) FILTER (WHERE region IS NULL) * 100.0 / COUNT(*))
FROM raw_sales
UNION ALL
SELECT
    'order_date',
    COUNT(*) FILTER (WHERE order_date IS NULL),
    COUNT(*),
    (COUNT(*) FILTER (WHERE order_date IS NULL) * 100.0 / COUNT(*))
FROM raw_sales
UNION ALL
SELECT
    'amount_paid',
    COUNT(*) FILTER (WHERE amount_paid IS NULL),
    COUNT(*),
    (COUNT(*) FILTER (WHERE amount_paid IS NULL) * 100.0 / COUNT(*))
FROM raw_sales
UNION ALL
SELECT
    'status',
    COUNT(*) FILTER (WHERE status IS NULL),
    COUNT(*),
    (COUNT(*) FILTER (WHERE status IS NULL) * 100.0 / COUNT(*))
FROM raw_sales
ORDER BY null_percentage DESC;

--------------------------------------------------------------------------------
-- SECTION 3: DATA CONSISTENCY & DISTINCT VALUES
-- Analyze the consistency of categorical data and identify potential
-- data entry issues or variations requiring standardization.
--------------------------------------------------------------------------------

-- 3.1: Examine distinct values for the 'region' column
-- Helps identify inconsistent spellings or multiple representations.
SELECT
    region,
    COUNT(*) AS record_count
FROM
    raw_sales
GROUP BY
    region
ORDER BY
    record_count DESC;

-- 3.2: Examine distinct values for the 'status' column
-- Ensures that only expected status values are present.
SELECT
    status,
    COUNT(*) AS record_count
FROM
    raw_sales
GROUP BY
    status
ORDER BY
    record_count DESC;

-- 3.3: Check date format consistency (conceptual, depends on actual stored type)
-- If 'order_date' was stored as text, this would highlight mixed formats.
-- (This query assumes 'order_date' is text and checks for common patterns)
SELECT
    CASE
        WHEN order_date ~ '^\d{4}-\d{2}-\d{2}$' THEN 'YYYY-MM-DD'
        WHEN order_date ~ '^\d{4}/\d{2}/\d{2}$' THEN 'YYYY/MM/DD'
        ELSE 'OTHER_FORMAT'
    END AS detected_date_format,
    COUNT(*) AS count
FROM
    raw_sales
GROUP BY
    detected_date_format;

--------------------------------------------------------------------------------
-- SECTION 4: DATA RANGE & DISTRIBUTION
-- Understand the range and distribution of numerical data.
--------------------------------------------------------------------------------

-- 4.1: Summary statistics for 'amount_paid'
SELECT
    MIN(amount_paid) AS min_amount_paid,
    MAX(amount_paid) AS max_amount_paid,
    AVG(amount_paid) AS avg_amount_paid,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY amount_paid) AS q1_amount_paid,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY amount_paid) AS median_amount_paid,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY amount_paid) AS q3_amount_paid,
    STDDEV(amount_paid) AS stddev_amount_paid
FROM
    raw_sales;

--------------------------------------------------------------------------------
-- SECTION 5: REFERENTIAL INTEGRITY (Conceptual for source, actual for DW)
-- In a deconstructed 3NF schema, this would check relationships.
-- For the DW, we can check dim_customer integrity.
--------------------------------------------------------------------------------

-- 5.1: Check for orphaned records in dim_customer (if a fact table existed)
-- (This query is illustrative; requires a fact table with a customer_sk)
-- SELECT COUNT(*)
-- FROM fact_sales fs
-- LEFT JOIN dim_customer dc ON fs.customer_sk = dc.customer_sk
-- WHERE dc.customer_sk IS NULL;

-- 5.2: Check for multiple active records for the same customer in dim_customer (SCD Type 2 issue)
SELECT
    cust_name,
    COUNT(*) AS active_records_count
FROM
    dim_customer
WHERE
    is_current = TRUE
GROUP BY
    cust_name
HAVING
    COUNT(*) > 1;

--------------------------------------------------------------------------------
-- SECTION 6: SCHEMA METADATA REVIEW
-- Basic review of table and column definitions.
--------------------------------------------------------------------------------

-- 6.1: List columns and their data types for 'raw_sales'
SELECT
    column_name,
    data_type,
    character_maximum_length AS max_length,
    is_nullable
FROM
    information_schema.columns
WHERE
    table_schema = 'public' AND table_name = 'raw_sales' -- Adjust schema if necessary
ORDER BY
    ordinal_position;

-- 6.2: List columns and their data types for 'dim_customer'
SELECT
    column_name,
    data_type,
    character_maximum_length AS max_length,
    is_nullable
FROM
    information_schema.columns
WHERE
    table_schema = 'public' AND table_name = 'dim_customer' -- Adjust schema if necessary
ORDER BY
    ordinal_position;
