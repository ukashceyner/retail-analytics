# ABOUTME: Time series analysis page showing trends and seasonality.
# ABOUTME: Displays monthly trends, quarterly comparisons, and growth metrics.

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import run_query, get_categories

st.set_page_config(page_title="Time Series Analysis", page_icon="📈", layout="wide")

st.title("Time Series Analysis")
st.divider()

# Filters
with st.sidebar:
    st.header("Filters")

    categories = get_categories()
    if categories:
        selected_category = st.selectbox(
            "Select Category",
            ["All Categories"] + categories
        )
    else:
        selected_category = "All Categories"

    metric_choice = st.radio(
        "Select Metric",
        ["Revenue", "Profit", "Orders"]
    )

# Build filter
if selected_category != "All Categories":
    category_filter = f"category = '{selected_category}'"
else:
    category_filter = "1=1"

metric_map = {
    "Revenue": "SUM(sale_price)",
    "Profit": "SUM(profit)",
    "Orders": "COUNT(*)"
}
metric_col = metric_map[metric_choice]

# Monthly Trend
st.subheader(f"Monthly {metric_choice} Trend")

query_monthly = f"""
SELECT
    year,
    month,
    month_name,
    {metric_col} as value
FROM orders
WHERE {category_filter}
GROUP BY year, month, month_name
ORDER BY year, month
"""

df_monthly = run_query(query_monthly)

if not df_monthly.empty:
    df_monthly['period'] = df_monthly['year'].astype(str) + '-' + df_monthly['month'].astype(str).str.zfill(2)

    fig = px.line(
        df_monthly,
        x='period',
        y='value',
        title=f'Monthly {metric_choice}',
        labels={'period': 'Month', 'value': metric_choice},
        markers=True
    )
    fig.update_traces(line_width=2)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Year-over-Year by Month
st.subheader("Year-over-Year Comparison by Month")

query_yoy_month = f"""
SELECT
    month,
    month_name,
    year,
    {metric_col} as value
FROM orders
WHERE {category_filter}
GROUP BY month, month_name, year
ORDER BY month, year
"""

df_yoy_month = run_query(query_yoy_month)

if not df_yoy_month.empty:
    fig = px.bar(
        df_yoy_month,
        x='month_name',
        y='value',
        color='year',
        barmode='group',
        title=f'{metric_choice} by Month (Year Comparison)',
        labels={'value': metric_choice, 'month_name': 'Month'},
        category_orders={'month_name': ['January', 'February', 'March', 'April',
                                         'May', 'June', 'July', 'August',
                                         'September', 'October', 'November', 'December']}
    )
    st.plotly_chart(fig, use_container_width=True)

# Quarterly Analysis
st.divider()
st.subheader("Quarterly Performance")

query_quarterly = f"""
SELECT
    year,
    quarter,
    {metric_col} as value,
    COUNT(DISTINCT order_id) as orders,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_margin
FROM orders
WHERE {category_filter}
GROUP BY year, quarter
ORDER BY year, quarter
"""

df_quarterly = run_query(query_quarterly)

if not df_quarterly.empty:
    df_quarterly['quarter_label'] = 'Q' + df_quarterly['quarter'].astype(str) + ' ' + df_quarterly['year'].astype(str)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df_quarterly,
            x='quarter_label',
            y='value',
            title=f'Quarterly {metric_choice}',
            labels={'value': metric_choice, 'quarter_label': 'Quarter'}
        )
        fig.update_traces(marker_color='#3498db')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.line(
            df_quarterly,
            x='quarter_label',
            y='avg_margin',
            title='Quarterly Profit Margin Trend',
            labels={'avg_margin': 'Profit Margin (%)', 'quarter_label': 'Quarter'},
            markers=True
        )
        fig.update_traces(line_color='#e74c3c')
        st.plotly_chart(fig, use_container_width=True)

# Category trends over time
st.divider()
st.subheader("Category Performance Over Time")

query_cat_trend = f"""
SELECT
    year,
    quarter,
    category,
    SUM(sale_price) as revenue
FROM orders
GROUP BY year, quarter, category
ORDER BY year, quarter, category
"""

df_cat_trend = run_query(query_cat_trend)

if not df_cat_trend.empty:
    df_cat_trend['period'] = 'Q' + df_cat_trend['quarter'].astype(str) + ' ' + df_cat_trend['year'].astype(str)

    fig = px.area(
        df_cat_trend,
        x='period',
        y='revenue',
        color='category',
        title='Revenue by Category Over Time',
        labels={'revenue': 'Revenue ($)', 'period': 'Quarter'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Growth metrics
st.divider()
st.subheader("Growth Metrics")

query_growth = """
WITH yearly AS (
    SELECT
        year,
        SUM(sale_price) as revenue,
        SUM(profit) as profit,
        COUNT(*) as orders
    FROM orders
    GROUP BY year
)
SELECT
    year,
    revenue,
    profit,
    orders,
    LAG(revenue) OVER (ORDER BY year) as prev_revenue,
    ROUND(((revenue - LAG(revenue) OVER (ORDER BY year)) /
           NULLIF(LAG(revenue) OVER (ORDER BY year), 0) * 100)::numeric, 2) as revenue_growth
FROM yearly
ORDER BY year
"""

df_growth = run_query(query_growth)

if not df_growth.empty:
    col1, col2, col3 = st.columns(3)

    for i, row in df_growth.iterrows():
        growth = row.get('revenue_growth')
        growth_str = f"{growth:+.1f}%" if growth else "N/A"

        if i == 0:
            with col1:
                st.metric(
                    f"{int(row['year'])} Revenue",
                    f"${row['revenue']:,.0f}",
                    growth_str if growth else None
                )
        else:
            with col2:
                st.metric(
                    f"{int(row['year'])} Revenue",
                    f"${row['revenue']:,.0f}",
                    growth_str
                )

# Data download
if not df_monthly.empty:
    csv = df_monthly.to_csv(index=False)
    st.download_button(
        label="Download Monthly Data",
        data=csv,
        file_name="time_series_data.csv",
        mime="text/csv"
    )
