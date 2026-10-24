-- ==============================================================================
-- JuanMart Data Warehouse - SCD Type 2 Pipeline
-- Objective: Track historical customer address/region migrations
-- Target Engine: PostgreSQL
-- ==============================================================================

-- Step 1: Create the Customer Dimension Table (SCD Type 2)
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_sk SERIAL PRIMARY KEY,        -- Surrogate Key
    cust_name VARCHAR(255) NOT NULL,       -- Natural Key
    region VARCHAR(255),                   -- Tracked Attribute (Address/Region)
    effective_date DATE NOT NULL,          -- SCD2 Start Date
    expiration_date DATE,                  -- SCD2 End Date
    is_current BOOLEAN DEFAULT TRUE        -- SCD2 Active Flag
);

-- Step 2: Create a Staging Table for incoming daily customer data
CREATE TABLE IF NOT EXISTS stg_customer (
    cust_name VARCHAR(255),
    region VARCHAR(255),
    order_date DATE
);

-- ==============================================================================
-- Step 3: SCD Type 2 Upsert Logic
-- ==============================================================================

-- A. Expire old records where the customer's region has changed
UPDATE dim_customer
SET 
    expiration_date = CURRENT_DATE,
    is_current = FALSE
FROM stg_customer
WHERE dim_customer.cust_name = stg_customer.cust_name
  AND dim_customer.region <> stg_customer.region
  AND dim_customer.is_current = TRUE;

-- B. Insert new records (Both brand new customers AND updated records for existing customers)
INSERT INTO dim_customer (cust_name, region, effective_date, expiration_date, is_current)
SELECT 
    s.cust_name, 
    s.region, 
    CURRENT_DATE AS effective_date, 
    NULL AS expiration_date, 
    TRUE AS is_current
FROM stg_customer s
LEFT JOIN dim_customer d 
    ON s.cust_name = d.cust_name 
    AND s.region = d.region 
    AND d.is_current = TRUE
WHERE d.customer_sk IS NULL;