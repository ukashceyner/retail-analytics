# ABOUTME: Unit tests for the database seeding module.
# ABOUTME: Tests data loading functions with mocked database connections.

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import os


class TestGetDatabaseUrl:
    """Tests for database URL retrieval."""

    def test_get_database_url_from_env(self, monkeypatch):
        """Should retrieve database URL from environment variable."""
        from sql.seed_data import get_database_url

        monkeypatch.setenv('SUPABASE_DATABASE_URL', 'postgresql://test:pass@host/db')
        url = get_database_url()
        assert url == 'postgresql://test:pass@host/db'

    def test_get_database_url_raises_when_missing(self, monkeypatch):
        """Should raise error when database URL is not set."""
        from sql.seed_data import get_database_url

        monkeypatch.delenv('SUPABASE_DATABASE_URL', raising=False)
        with pytest.raises(ValueError, match="SUPABASE_DATABASE_URL"):
            get_database_url()


class TestLoadCleanedData:
    """Tests for loading cleaned CSV data."""

    def test_load_cleaned_data_returns_dataframe(self, sample_clean_csv):
        """Should return a DataFrame from the cleaned CSV."""
        from sql.seed_data import load_cleaned_data

        df = load_cleaned_data(sample_clean_csv)
        assert isinstance(df, pd.DataFrame)

    def test_load_cleaned_data_parses_dates(self, sample_clean_csv):
        """Should parse order_date as datetime."""
        from sql.seed_data import load_cleaned_data

        df = load_cleaned_data(sample_clean_csv)
        assert pd.api.types.is_datetime64_any_dtype(df['order_date'])

    def test_load_cleaned_data_preserves_columns(self, sample_clean_csv):
        """Should preserve all expected columns."""
        from sql.seed_data import load_cleaned_data

        df = load_cleaned_data(sample_clean_csv)
        expected_cols = ['order_id', 'order_date', 'ship_mode', 'category', 'region']
        for col in expected_cols:
            assert col in df.columns


class TestSeedDatabase:
    """Tests for the database seeding function."""

    @patch('sql.seed_data.create_engine')
    def test_seed_database_creates_engine(self, mock_create_engine, sample_clean_csv, monkeypatch):
        """Should create SQLAlchemy engine with correct URL."""
        from sql.seed_data import seed_database

        monkeypatch.setenv('SUPABASE_DATABASE_URL', 'postgresql://test:pass@host/db')
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        seed_database(sample_clean_csv)

        mock_create_engine.assert_called_once_with('postgresql://test:pass@host/db')

    @patch('sql.seed_data.create_engine')
    def test_seed_database_loads_data_to_table(self, mock_create_engine, sample_clean_csv, monkeypatch):
        """Should load DataFrame to 'orders' table."""
        from sql.seed_data import seed_database

        monkeypatch.setenv('SUPABASE_DATABASE_URL', 'postgresql://test:pass@host/db')
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        # Mock the to_sql call on DataFrame
        with patch.object(pd.DataFrame, 'to_sql') as mock_to_sql:
            seed_database(sample_clean_csv)
            mock_to_sql.assert_called_once()
            call_args = mock_to_sql.call_args
            assert call_args[0][0] == 'orders'  # table name

    @patch('sql.seed_data.create_engine')
    def test_seed_database_disposes_engine(self, mock_create_engine, sample_clean_csv, monkeypatch):
        """Should dispose engine connection after loading."""
        from sql.seed_data import seed_database

        monkeypatch.setenv('SUPABASE_DATABASE_URL', 'postgresql://test:pass@host/db')
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        seed_database(sample_clean_csv)

        mock_engine.dispose.assert_called_once()

    @patch('sql.seed_data.create_engine')
    def test_seed_database_returns_row_count(self, mock_create_engine, sample_clean_csv, monkeypatch):
        """Should return the number of rows loaded."""
        from sql.seed_data import seed_database

        monkeypatch.setenv('SUPABASE_DATABASE_URL', 'postgresql://test:pass@host/db')
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        row_count = seed_database(sample_clean_csv)

        assert row_count == 3  # Sample CSV has 3 rows


class TestVerifyLoad:
    """Tests for verifying data was loaded correctly."""

    @patch('sql.seed_data.create_engine')
    @patch('pandas.read_sql')
    def test_verify_load_queries_count(self, mock_read_sql, mock_create_engine, monkeypatch):
        """Should query database for row count."""
        from sql.seed_data import verify_load

        monkeypatch.setenv('SUPABASE_DATABASE_URL', 'postgresql://test:pass@host/db')
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_read_sql.return_value = pd.DataFrame({'count': [100]})

        count = verify_load()

        assert count == 100
        mock_read_sql.assert_called_once()
        assert 'COUNT(*)' in mock_read_sql.call_args[0][0]


# Fixtures

@pytest.fixture
def sample_clean_csv(tmp_path):
    """Create a sample cleaned CSV file for testing."""
    csv_content = """order_id,order_date,ship_mode,segment,country,city,state,postal_code,region,category,sub_category,product_id,cost_price,list_price,quantity,discount_percent,discount,sale_price,profit,profit_margin,year,month,month_name,quarter
1,2023-03-01,Second Class,Consumer,United States,Henderson,Kentucky,42420,South,Furniture,Bookcases,FUR-BO-10001798,240,260,2,2,5.2,254.8,14.8,5.81,2023,3,March,1
2,2023-08-15,Second Class,Consumer,United States,Henderson,Kentucky,42420,South,Furniture,Chairs,FUR-CH-10000454,600,730,3,3,21.9,708.1,108.1,15.27,2023,8,August,3
3,2023-01-10,,Corporate,United States,Los Angeles,California,90036,West,Office Supplies,Labels,OFF-LA-10000240,10,10,2,5,0.5,9.5,-0.5,-5.26,2023,1,January,1"""

    csv_path = tmp_path / "orders_clean.csv"
    csv_path.write_text(csv_content)
    return str(csv_path)
