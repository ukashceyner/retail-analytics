# ABOUTME: Unit tests for the retail orders data cleaning module.
# ABOUTME: Tests data loading, column transformations, calculated fields, and output.

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

# Import will fail until we implement the module - that's expected in TDD
try:
    from sql.clean_data import clean_retail_orders, load_raw_data, transform_columns
except ImportError:
    # Module not yet implemented - tests will fail as expected
    pass


class TestLoadRawData:
    """Tests for loading raw CSV data."""

    def test_load_raw_data_returns_dataframe(self, sample_csv_file):
        """Loading raw data should return a pandas DataFrame."""
        from sql.clean_data import load_raw_data

        df = load_raw_data(sample_csv_file)
        assert isinstance(df, pd.DataFrame)

    def test_load_raw_data_handles_na_values(self, sample_csv_file):
        """NA placeholder values should be converted to NaN."""
        from sql.clean_data import load_raw_data

        df = load_raw_data(sample_csv_file)
        # "Not Available" and "unknown" should become NaN
        assert df['Ship Mode'].isna().sum() >= 1

    def test_load_raw_data_preserves_row_count(self, sample_csv_file):
        """Loading should preserve all data rows."""
        from sql.clean_data import load_raw_data

        df = load_raw_data(sample_csv_file)
        # Sample has 5 data rows
        assert len(df) == 5


class TestTransformColumns:
    """Tests for column name and data type transformations."""

    def test_column_names_are_snake_case(self, sample_dataframe):
        """All column names should be snake_case after transformation."""
        from sql.clean_data import transform_columns

        df = transform_columns(sample_dataframe)
        for col in df.columns:
            assert ' ' not in col, f"Column '{col}' contains spaces"
            assert col == col.lower(), f"Column '{col}' is not lowercase"

    def test_order_date_is_datetime(self, sample_dataframe):
        """order_date column should be datetime type."""
        from sql.clean_data import transform_columns

        df = transform_columns(sample_dataframe)
        assert pd.api.types.is_datetime64_any_dtype(df['order_date'])

    def test_calculated_field_discount(self, sample_dataframe):
        """discount = list_price * discount_percent / 100."""
        from sql.clean_data import transform_columns

        df = transform_columns(sample_dataframe)
        # First row: list_price=260, discount_percent=2 -> discount=5.2
        expected_discount = 260 * 2 / 100
        assert df.loc[0, 'discount'] == pytest.approx(expected_discount)

    def test_calculated_field_sale_price(self, sample_dataframe):
        """sale_price = list_price - discount."""
        from sql.clean_data import transform_columns

        df = transform_columns(sample_dataframe)
        # First row: list_price=260, discount=5.2 -> sale_price=254.8
        expected_sale_price = 260 - (260 * 2 / 100)
        assert df.loc[0, 'sale_price'] == pytest.approx(expected_sale_price)

    def test_calculated_field_profit(self, sample_dataframe):
        """profit = sale_price - cost_price."""
        from sql.clean_data import transform_columns

        df = transform_columns(sample_dataframe)
        # First row: sale_price=254.8, cost_price=240 -> profit=14.8
        expected_profit = (260 - (260 * 2 / 100)) - 240
        assert df.loc[0, 'profit'] == pytest.approx(expected_profit)

    def test_calculated_field_profit_margin(self, sample_dataframe):
        """profit_margin = (profit / sale_price * 100), rounded to 2 decimals."""
        from sql.clean_data import transform_columns

        df = transform_columns(sample_dataframe)
        sale_price = 260 - (260 * 2 / 100)
        profit = sale_price - 240
        expected_margin = round(profit / sale_price * 100, 2)
        assert df.loc[0, 'profit_margin'] == pytest.approx(expected_margin)

    def test_date_components_extracted(self, sample_dataframe):
        """Year, month, month_name, and quarter should be extracted from order_date."""
        from sql.clean_data import transform_columns

        df = transform_columns(sample_dataframe)
        # First row: 2023-03-01
        assert df.loc[0, 'year'] == 2023
        assert df.loc[0, 'month'] == 3
        assert df.loc[0, 'month_name'] == 'March'
        assert df.loc[0, 'quarter'] == 1

    def test_categorical_data_cleaned(self, sample_dataframe):
        """Categorical columns should be stripped and title-cased."""
        from sql.clean_data import transform_columns

        df = transform_columns(sample_dataframe)
        # Check category, sub_category, region are clean
        assert df['category'].iloc[0] == 'Furniture'
        assert df['sub_category'].iloc[0] == 'Bookcases'
        assert df['region'].iloc[0] == 'South'


class TestCleanRetailOrders:
    """Integration tests for the full cleaning pipeline."""

    def test_clean_retail_orders_creates_output_file(self, sample_csv_file, tmp_path):
        """clean_retail_orders should create the output CSV file."""
        from sql.clean_data import clean_retail_orders

        output_path = tmp_path / "orders_clean.csv"
        clean_retail_orders(sample_csv_file, str(output_path))
        assert output_path.exists()

    def test_clean_retail_orders_returns_dataframe(self, sample_csv_file, tmp_path):
        """clean_retail_orders should return the cleaned DataFrame."""
        from sql.clean_data import clean_retail_orders

        output_path = tmp_path / "orders_clean.csv"
        result = clean_retail_orders(sample_csv_file, str(output_path))
        assert isinstance(result, pd.DataFrame)

    def test_clean_retail_orders_output_has_all_columns(self, sample_csv_file, tmp_path):
        """Output should have all original columns plus calculated fields."""
        from sql.clean_data import clean_retail_orders

        output_path = tmp_path / "orders_clean.csv"
        df = clean_retail_orders(sample_csv_file, str(output_path))

        expected_columns = [
            'order_id', 'order_date', 'ship_mode', 'segment', 'country',
            'city', 'state', 'postal_code', 'region', 'category',
            'sub_category', 'product_id', 'cost_price', 'list_price',
            'quantity', 'discount_percent', 'discount', 'sale_price',
            'profit', 'profit_margin', 'year', 'month', 'month_name', 'quarter'
        ]
        for col in expected_columns:
            assert col in df.columns, f"Missing column: {col}"

    def test_saved_csv_is_readable(self, sample_csv_file, tmp_path):
        """The saved CSV should be readable and match the returned DataFrame."""
        from sql.clean_data import clean_retail_orders

        output_path = tmp_path / "orders_clean.csv"
        df_returned = clean_retail_orders(sample_csv_file, str(output_path))
        df_loaded = pd.read_csv(output_path)

        assert len(df_returned) == len(df_loaded)
        assert list(df_returned.columns) == list(df_loaded.columns)


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_handles_zero_values(self, tmp_path):
        """Should handle rows with zero cost/list prices without division errors."""
        from sql.clean_data import clean_retail_orders

        # Create CSV with zero values
        csv_content = """Order Id,Order Date,Ship Mode,Segment,Country,City,State,Postal Code,Region,Category,Sub Category,Product Id,cost price,List Price,Quantity,Discount Percent
1,2023-01-01,Standard Class,Consumer,United States,City,State,12345,South,Furniture,Chairs,PRD-001,0,0,1,5"""

        input_path = tmp_path / "zero_values.csv"
        input_path.write_text(csv_content)
        output_path = tmp_path / "output.csv"

        # Should not raise an error
        df = clean_retail_orders(str(input_path), str(output_path))
        assert len(df) == 1
        # profit_margin should handle division by zero gracefully
        assert df.loc[0, 'profit_margin'] == 0 or pd.isna(df.loc[0, 'profit_margin'])

    def test_handles_missing_ship_mode(self, tmp_path):
        """Should convert 'Not Available' and 'unknown' to NaN."""
        from sql.clean_data import clean_retail_orders

        csv_content = """Order Id,Order Date,Ship Mode,Segment,Country,City,State,Postal Code,Region,Category,Sub Category,Product Id,cost price,List Price,Quantity,Discount Percent
1,2023-01-01,Not Available,Consumer,United States,City,State,12345,South,Furniture,Chairs,PRD-001,100,150,1,10
2,2023-01-02,unknown,Consumer,United States,City,State,12345,South,Furniture,Tables,PRD-002,200,250,2,5"""

        input_path = tmp_path / "na_values.csv"
        input_path.write_text(csv_content)
        output_path = tmp_path / "output.csv"

        df = clean_retail_orders(str(input_path), str(output_path))
        assert df['ship_mode'].isna().sum() == 2


# Fixtures

@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    csv_content = """Order Id,Order Date,Ship Mode,Segment,Country,City,State,Postal Code,Region,Category,Sub Category,Product Id,cost price,List Price,Quantity,Discount Percent
1,2023-03-01,Second Class,Consumer,United States,Henderson,Kentucky,42420,South,Furniture,Bookcases,FUR-BO-10001798,240,260,2,2
2,2023-08-15,Second Class,Consumer,United States,Henderson,Kentucky,42420,South,Furniture,Chairs,FUR-CH-10000454,600,730,3,3
3,2023-01-10,Not Available,Corporate,United States,Los Angeles,California,90036,West,Office Supplies,Labels,OFF-LA-10000240,10,10,2,5
4,2022-06-18,Standard Class,Consumer,United States,Fort Lauderdale,Florida,33311,South,Furniture,Tables,FUR-TA-10000577,780,960,5,2
5,2022-07-13,unknown,Consumer,United States,Fort Lauderdale,Florida,33311,South,Office Supplies,Storage,OFF-ST-10000760,20,20,2,5"""

    csv_path = tmp_path / "orders.csv"
    csv_path.write_text(csv_content)
    return str(csv_path)


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing transformations."""
    data = {
        'Order Id': [1, 2, 3, 4, 5],
        'Order Date': ['2023-03-01', '2023-08-15', '2023-01-10', '2022-06-18', '2022-07-13'],
        'Ship Mode': ['Second Class', 'Second Class', None, 'Standard Class', None],
        'Segment': ['Consumer', 'Consumer', 'Corporate', 'Consumer', 'Consumer'],
        'Country': ['United States'] * 5,
        'City': ['Henderson', 'Henderson', 'Los Angeles', 'Fort Lauderdale', 'Fort Lauderdale'],
        'State': ['Kentucky', 'Kentucky', 'California', 'Florida', 'Florida'],
        'Postal Code': [42420, 42420, 90036, 33311, 33311],
        'Region': ['South', 'South', 'West', 'South', 'South'],
        'Category': ['Furniture', 'Furniture', 'Office Supplies', 'Furniture', 'Office Supplies'],
        'Sub Category': ['Bookcases', 'Chairs', 'Labels', 'Tables', 'Storage'],
        'Product Id': ['FUR-BO-10001798', 'FUR-CH-10000454', 'OFF-LA-10000240', 'FUR-TA-10000577', 'OFF-ST-10000760'],
        'cost price': [240, 600, 10, 780, 20],
        'List Price': [260, 730, 10, 960, 20],
        'Quantity': [2, 3, 2, 5, 2],
        'Discount Percent': [2, 3, 5, 2, 5]
    }
    return pd.DataFrame(data)
