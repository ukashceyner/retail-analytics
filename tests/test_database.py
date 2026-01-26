# ABOUTME: Unit tests for the database connection utility module.
# ABOUTME: Tests connection handling and query execution with mocked Streamlit.

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock


class TestRunQuery:
    """Tests for the run_query function."""

    @patch('utils.database.get_database_connection')
    def test_run_query_returns_dataframe(self, mock_get_conn):
        """Should return a DataFrame from SQL query."""
        from utils.database import run_query

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        with patch('pandas.read_sql') as mock_read_sql:
            mock_read_sql.return_value = pd.DataFrame({'col': [1, 2, 3]})
            result = run_query("SELECT * FROM orders")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3

    @patch('utils.database.get_database_connection')
    def test_run_query_returns_empty_on_error(self, mock_get_conn):
        """Should return empty DataFrame when connection fails."""
        from utils.database import run_query

        mock_get_conn.return_value = None
        result = run_query("SELECT * FROM orders")

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    @patch('utils.database.get_database_connection')
    def test_run_query_handles_query_error(self, mock_get_conn):
        """Should return empty DataFrame on query error."""
        from utils.database import run_query

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        with patch('pandas.read_sql') as mock_read_sql:
            mock_read_sql.side_effect = Exception("Query failed")
            result = run_query("SELECT * FROM invalid_table")

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestGetSummaryStats:
    """Tests for the get_summary_stats function."""

    @patch('utils.database.run_query')
    def test_get_summary_stats_returns_dict(self, mock_run_query):
        """Should return dictionary of summary statistics."""
        from utils.database import get_summary_stats

        mock_run_query.return_value = pd.DataFrame({
            'total_orders': [1000],
            'total_revenue': [50000.00],
            'total_profit': [10000.00],
            'avg_order_value': [50.00],
            'avg_profit_margin': [20.00]
        })

        result = get_summary_stats()

        assert isinstance(result, dict)
        assert result['total_orders'] == 1000
        assert result['total_revenue'] == 50000.00

    @patch('utils.database.run_query')
    def test_get_summary_stats_returns_empty_dict_on_error(self, mock_run_query):
        """Should return empty dict when query returns empty."""
        from utils.database import get_summary_stats

        mock_run_query.return_value = pd.DataFrame()

        result = get_summary_stats()

        assert isinstance(result, dict)
        assert result == {}


class TestGetCategories:
    """Tests for category/region lookup functions."""

    @patch('utils.database.run_query')
    def test_get_categories_returns_list(self, mock_run_query):
        """Should return list of unique categories."""
        from utils.database import get_categories

        mock_run_query.return_value = pd.DataFrame({
            'category': ['Furniture', 'Office Supplies', 'Technology']
        })

        result = get_categories()

        assert isinstance(result, list)
        assert len(result) == 3
        assert 'Furniture' in result

    @patch('utils.database.run_query')
    def test_get_regions_returns_list(self, mock_run_query):
        """Should return list of unique regions."""
        from utils.database import get_regions

        mock_run_query.return_value = pd.DataFrame({
            'region': ['South', 'West', 'East', 'Central']
        })

        result = get_regions()

        assert isinstance(result, list)
        assert len(result) == 4


class TestGetDateRange:
    """Tests for date range function."""

    @patch('utils.database.run_query')
    def test_get_date_range_returns_tuple(self, mock_run_query):
        """Should return tuple of (min_date, max_date)."""
        from utils.database import get_date_range

        mock_run_query.return_value = pd.DataFrame({
            'min_date': [pd.Timestamp('2022-01-01')],
            'max_date': [pd.Timestamp('2023-12-31')]
        })

        min_date, max_date = get_date_range()

        assert min_date == pd.Timestamp('2022-01-01')
        assert max_date == pd.Timestamp('2023-12-31')

    @patch('utils.database.run_query')
    def test_get_date_range_handles_empty(self, mock_run_query):
        """Should return None tuple when no data."""
        from utils.database import get_date_range

        mock_run_query.return_value = pd.DataFrame()

        min_date, max_date = get_date_range()

        assert min_date is None
        assert max_date is None
