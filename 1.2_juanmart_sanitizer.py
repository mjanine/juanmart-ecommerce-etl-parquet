import pandas as pd


def load_data(filepath):
    """Load raw dataset from CSV file."""
    return pd.read_csv(filepath)


def isolate_quarantined_records(df):
    """Isolate failed/corrupted records (duplicates and missing values) to a log."""
    # Find all duplicates and rows with any missing data
    duplicates = df[df.duplicated(keep=False)]
    missing_data = df[df.isnull().any(axis=1)]
    
    # Combine into a single quarantine DataFrame and save to CSV
    quarantined_df = pd.concat([duplicates, missing_data]).drop_duplicates()
    quarantined_df.to_csv('quarantined_transactions.csv', index=False)
    print(f"Logged {len(quarantined_df)} corrupted/anomalous records to 'quarantined_transactions.csv'.")
    
    return df


def drop_duplicates(df):
    """Drop duplicate rows from the dataset."""
    initial_count = len(df)
    df_clean = df.drop_duplicates()
    print(f"Dropped {initial_count - len(df_clean)} duplicate rows.")
    return df_clean


def standardize_regions(df):
    """Standardize regional names to uniform naming conventions."""
    region_mapping = {
        "NCR": "National Capital Region",
        "Metro Manila": "National Capital Region",
        "ncr": "National Capital Region",
        "Manila": "National Capital Region",
        "CALABARZON": "CALABARZON",
        "calabarzon": "CALABARZON",
        "Region IV-A": "CALABARZON",
    }

    df["region"] = df["region"].map(region_mapping).fillna(df["region"])
    return df


def fill_missing_amount_paid(df):
    """Fill missing values in amount_paid using the median value of each region."""
    df["amount_paid"] = df.groupby("region")["amount_paid"].transform(
        lambda x: x.fillna(x.median())
    )
    return df


def standardize_order_dates(df):
    """Convert order_date strings to uniform YYYY-MM-DD format."""
    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed").dt.strftime(
        "%Y-%m-%d"
    )
    return df


def clean_juanmart_data(input_path, output_path):
    """Main pipeline to run all cleansing functions and export the clean dataset."""
    df = load_data(input_path)

    # 0. Quarantine anomalous data before altering the dataset
    df = isolate_quarantined_records(df)

    # 1. Standardize regions FIRST so median calculation per region is accurate
    df = standardize_regions(df)

    # 2. Fill missing amount_paid using regional median
    df = fill_missing_amount_paid(df)

    # 3. Drop duplicate rows
    df = drop_duplicates(df)

    # 4. Standardize dates to YYYY-MM-DD
    df = standardize_order_dates(df)

    # Export clean dataset to Parquet format
    df.to_parquet(output_path, index=False)
    print(f"Data successfully cleaned and saved to: {output_path}")
    return df


if __name__ == "__main__":
    clean_juanmart_data("juanmart_raw_sales.csv", "cleaned_juanmart_sales.parquet")