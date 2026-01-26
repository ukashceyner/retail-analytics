# ABOUTME: Database connection and query utilities for Streamlit dashboard.
# ABOUTME: Provides cached connection handling and common query functions.

import os
import pandas as pd
from typing import Optional, Tuple, List, Dict, Any

# Check if running in Streamlit context
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


def get_database_url() -> Optional[str]:
    """
    Get database URL from Streamlit secrets or environment variables.

    Returns:
        Database URL string or None if not configured.
    """
    # Try Streamlit secrets first
    if STREAMLIT_AVAILABLE:
        try:
            return st.secrets["database"]["url"]
        except (KeyError, FileNotFoundError):
            pass

    # Fall back to environment variable
    return os.getenv('SUPABASE_DATABASE_URL')


def get_database_connection():
    """
    Create database connection using psycopg2.

    Returns:
        Database connection or None if connection fails.
    """
    if not PSYCOPG2_AVAILABLE:
        return None

    url = get_database_url()
    if not url:
        return None

    try:
        conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        if STREAMLIT_AVAILABLE:
            st.error(f"Failed to connect to database: {e}")
        return None


def run_query(query: str) -> pd.DataFrame:
    """
    Execute SQL query and return results as DataFrame.

    Args:
        query: SQL query string to execute.

    Returns:
        DataFrame with query results, or empty DataFrame on error.
    """
    conn = get_database_connection()
    if conn is None:
        return pd.DataFrame()

    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        if STREAMLIT_AVAILABLE:
            st.error(f"Query error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def get_summary_stats() -> Dict[str, Any]:
    """
    Get high-level summary statistics from order_summary view.

    Returns:
        Dictionary of summary statistics, or empty dict on error.
    """
    query = "SELECT * FROM order_summary"
    df = run_query(query)

    if df.empty:
        return {}

    return df.to_dict('records')[0]


def get_categories() -> List[str]:
    """
    Get list of unique product categories.

    Returns:
        List of category names.
    """
    query = "SELECT DISTINCT category FROM orders ORDER BY category"
    df = run_query(query)

    if df.empty:
        return []

    return df['category'].tolist()


def get_regions() -> List[str]:
    """
    Get list of unique regions.

    Returns:
        List of region names.
    """
    query = "SELECT DISTINCT region FROM orders ORDER BY region"
    df = run_query(query)

    if df.empty:
        return []

    return df['region'].tolist()


def get_date_range() -> Tuple[Optional[pd.Timestamp], Optional[pd.Timestamp]]:
    """
    Get min and max order dates from database.

    Returns:
        Tuple of (min_date, max_date), or (None, None) if no data.
    """
    query = "SELECT MIN(order_date) as min_date, MAX(order_date) as max_date FROM orders"
    df = run_query(query)

    if df.empty:
        return None, None

    return df['min_date'].iloc[0], df['max_date'].iloc[0]


def get_segments() -> List[str]:
    """
    Get list of unique customer segments.

    Returns:
        List of segment names.
    """
    query = "SELECT DISTINCT segment FROM orders ORDER BY segment"
    df = run_query(query)

    if df.empty:
        return []

    return df['segment'].tolist()
