# ABOUTME: Data cleaning and transformation module for retail orders dataset.
# ABOUTME: Loads raw CSV, cleans columns, calculates derived fields, and exports clean data.

import pandas as pd
import numpy as np


def load_raw_data(input_path: str) -> pd.DataFrame:
    """
    Load raw CSV data with proper NA value handling.

    Args:
        input_path: Path to the raw CSV file.

    Returns:
        DataFrame with raw data, placeholder values converted to NaN.
    """
    na_values = ['Not Available', 'unknown', 'NA', 'N/A', '']
    df = pd.read_csv(input_path, na_values=na_values)
    return df


def transform_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform column names and data types, add calculated fields.

    Args:
        df: Raw DataFrame to transform.

    Returns:
        Transformed DataFrame with snake_case columns and calculated fields.
    """
    df = df.copy()

    # Rename columns to snake_case
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # Convert order_date to datetime
    df['order_date'] = pd.to_datetime(df['order_date'], format='%Y-%m-%d')

    # Calculate derived fields
    df['discount'] = df['list_price'] * df['discount_percent'] / 100
    df['sale_price'] = df['list_price'] - df['discount']
    df['profit'] = df['sale_price'] - df['cost_price']

    # Handle division by zero for profit_margin
    df['profit_margin'] = np.where(
        df['sale_price'] != 0,
        (df['profit'] / df['sale_price'] * 100).round(2),
        0
    )

    # Extract date components
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month
    df['month_name'] = df['order_date'].dt.strftime('%B')
    df['quarter'] = df['order_date'].dt.quarter

    # Clean categorical data - strip whitespace and title case
    df['category'] = df['category'].str.strip().str.title()
    df['sub_category'] = df['sub_category'].str.strip().str.title()
    df['region'] = df['region'].str.strip().str.title()

    return df


def clean_retail_orders(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Full data cleaning pipeline for retail orders.

    Loads raw data, applies transformations, and saves cleaned output.

    Args:
        input_path: Path to raw CSV file.
        output_path: Path to save cleaned CSV file.

    Returns:
        Cleaned DataFrame.
    """
    # Load raw data
    df = load_raw_data(input_path)

    # Apply transformations
    df = transform_columns(df)

    # Save cleaned data
    df.to_csv(output_path, index=False)

    print(f"Cleaned data saved to {output_path}")
    print(f"Total rows: {len(df):,}")
    print(f"Date range: {df['order_date'].min()} to {df['order_date'].max()}")

    return df


if __name__ == "__main__":
    clean_retail_orders('data/raw/orders.csv', 'data/processed/orders_clean.csv')
