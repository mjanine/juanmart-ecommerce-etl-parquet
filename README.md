# JuanMart E-Commerce ETL, Data Quarantine & Parquet Warehousing

## 📌 Overview
An end-to-end e-commerce data engineering pipeline developed for *JuanMart* retail operations. The system automates data profiling, quarantines corrupted or duplicate sales transactions to an audit log prior to transformation, performs regional median imputations, and serializes clean transactions into high-performance Apache Parquet columnar storage.

## 🛠 Tech Stack
* **Language:** Python 3.x, SQL
* **Data Processing & ETL:** pandas, NumPy, PyArrow (Parquet engine)
* **Data Cleansing & Profiling:** Jupyter Notebooks (`1.1_data_profiling.ipynb`)
* **Analytics & Data Warehousing:** SQL (`juanmart_scd_pipeline.sql`, `juanmart_schema_audit.sql`)

## ⚡ Core Architecture & Pipeline Logic (`1.2_juanmart_sanitizer.py`)

1. **Pre-Cleansing Data Isolation & Quarantine (`isolate_quarantined_records`):**
   * Scans raw sales data (`juanmart_raw_sales.csv`) to identify duplicate records and null values.
   * Exports corrupted and missing entries into an audit log (`quarantined_transactions.csv`) before executing transformations.
2. **Regional Nomenclature Standardization (`standardize_regions`):**
   * Maps inconsistent regional strings (`NCR`, `Metro Manila`, `calabarzon`, `Region IV-A`) to uniform administrative names (*National Capital Region*, *CALABARZON*).
3. **Context-Aware Imputation (`fill_missing_amount_paid`):**
   * Calculates regional median transaction values using `groupby("region")` and dynamically imputes missing `amount_paid` values based on geographic averages.
4. **Deduplication & ISO Date Standardization:**
   * Drops duplicate rows and converts `order_date` fields to standard `YYYY-MM-DD` ISO-8601 formatting.
5. **Columnar Serialization:**
   * Exports sanitized transaction records to compressed Snappy Apache Parquet format (`cleaned_juanmart_sales.parquet`) for downstream OLAP queries.

## 📊 Analytical Schema & SCD Pipeline
* **Star Schema Architecture (`juanmart_star_schema.png`):** Modeled dimension and fact tables for e-commerce order tracking.
* **Slowly Changing Dimensions (SCD):** SQL scripts (`juanmart_scd_pipeline.sql`) handle dimension history tracking and schema audits (`juanmart_schema_audit.sql`).

## 🚀 How to Run

1. Clone repository and install dependencies:
   ```bash
   pip install pandas pyarrow