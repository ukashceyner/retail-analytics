# ABOUTME: Database seeding module for loading cleaned data into Supabase.
# ABOUTME: Handles connection setup, data loading, and verification.

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """
    Get database URL from environment variables.

    Returns:
        Database connection URL string.

    Raises:
        ValueError: If SUPABASE_DATABASE_URL is not set.
    """
    url = os.getenv('SUPABASE_DATABASE_URL')
    if not url:
        raise ValueError(
            "SUPABASE_DATABASE_URL environment variable is not set. "
            "Copy .env.example to .env and fill in your Supabase credentials."
        )
    return url


def load_cleaned_data(csv_path: str) -> pd.DataFrame:
    """
    Load cleaned CSV data for database insertion.

    Args:
        csv_path: Path to the cleaned CSV file.

    Returns:
        DataFrame with order_date parsed as datetime.
    """
    df = pd.read_csv(csv_path, parse_dates=['order_date'])
    return df


def seed_database(csv_path: str) -> int:
    """
    Load cleaned data into Supabase PostgreSQL database.

    Args:
        csv_path: Path to the cleaned CSV file.

    Returns:
        Number of rows loaded.
    """
    # Get database URL
    database_url = get_database_url()

    # Create SQLAlchemy engine
    engine = create_engine(database_url)

    # Load cleaned data
    df = load_cleaned_data(csv_path)

    print(f"Loading {len(df):,} rows into Supabase...")

    # Drop dependent view first (if exists)
    with engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS order_summary CASCADE"))
        conn.commit()
        print("Dropped existing view...")

    # Load to database (replace existing data)
    df.to_sql(
        'orders',
        engine,
        if_exists='replace',
        index=False,
        method='multi',
        chunksize=1000
    )

    print("Data loaded successfully!")

    # Recreate the summary view
    view_sql = text("""
    CREATE OR REPLACE VIEW order_summary AS
    SELECT
        COUNT(*) as total_orders,
        SUM(sale_price) as total_revenue,
        SUM(profit) as total_profit,
        AVG(sale_price) as avg_order_value,
        AVG(profit_margin) as avg_profit_margin,
        MIN(order_date) as first_order_date,
        MAX(order_date) as last_order_date
    FROM orders
    """)
    with engine.connect() as conn:
        conn.execute(view_sql)
        conn.commit()
        print("Recreated order_summary view...")

    # Clean up
    engine.dispose()

    return len(df)


def verify_load() -> int:
    """
    Verify data was loaded correctly by querying row count.

    Returns:
        Number of rows in the orders table.
    """
    database_url = get_database_url()
    engine = create_engine(database_url)

    result = pd.read_sql("SELECT COUNT(*) as count FROM orders", engine)
    count = result['count'].iloc[0]

    engine.dispose()

    return count


if __name__ == "__main__":
    csv_path = 'data/processed/orders_clean.csv'

    print("Starting database seed...")
    row_count = seed_database(csv_path)
    print(f"Loaded {row_count:,} rows")

    print("\nVerifying load...")
    db_count = verify_load()
    print(f"Database contains {db_count:,} rows")

    if row_count == db_count:
        print("\nSeed completed successfully!")
    else:
        print(f"\nWarning: Row count mismatch! CSV: {row_count}, DB: {db_count}")
