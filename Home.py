# ABOUTME: Main Streamlit dashboard entry point for retail analytics.
# ABOUTME: Displays KPI metrics, revenue trends, and navigation to detailed pages.

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.database import run_query, get_summary_stats

# Page configuration
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("Retail Orders Analytics Dashboard")
st.markdown("*Analyzing 9,900+ orders to drive business insights*")
st.divider()

# Sidebar
with st.sidebar:
    st.header("About This Project")
    st.markdown("""
    This dashboard analyzes retail order data to provide:
    - Sales performance metrics
    - Product analysis
    - Regional insights
    - Time-series trends

    **Tech Stack:**
    - Database: Supabase (PostgreSQL)
    - Frontend: Streamlit
    - Charts: Plotly
    """)

    st.divider()
    st.markdown("**Created by:** Lukasz")
    st.markdown("**Portfolio Project:** Data & Reporting Analyst")

# Load summary stats
stats = get_summary_stats()

# KPI Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Orders",
        value=f"{stats.get('total_orders', 0):,}"
    )

with col2:
    st.metric(
        label="Total Revenue",
        value=f"${stats.get('total_revenue', 0):,.2f}"
    )

with col3:
    st.metric(
        label="Total Profit",
        value=f"${stats.get('total_profit', 0):,.2f}"
    )

with col4:
    st.metric(
        label="Avg Profit Margin",
        value=f"{stats.get('avg_profit_margin', 0):.2f}%"
    )

st.divider()

# Revenue Trend Chart
st.subheader("Revenue Trend Over Time")

query_trend = """
SELECT
    DATE_TRUNC('month', order_date) as month,
    SUM(sale_price) as revenue,
    SUM(profit) as profit
FROM orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month
"""

df_trend = run_query(query_trend)

if not df_trend.empty:
    fig = px.line(
        df_trend,
        x='month',
        y='revenue',
        title='Monthly Revenue Trend',
        labels={'month': 'Month', 'revenue': 'Revenue ($)'}
    )
    fig.update_traces(line_color='#1f77b4', line_width=3)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Connect to database to view revenue trends.")

# Two column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Products by Revenue")

    query_products = """
    SELECT
        product_id,
        category,
        SUM(sale_price) as revenue
    FROM orders
    GROUP BY product_id, category
    ORDER BY revenue DESC
    LIMIT 10
    """

    df_products = run_query(query_products)

    if not df_products.empty:
        fig = px.bar(
            df_products,
            x='revenue',
            y='product_id',
            orientation='h',
            color='category',
            title='Top Revenue Products'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Connect to database to view top products.")

with col2:
    st.subheader("Sales by Region")

    query_region = """
    SELECT
        region,
        SUM(sale_price) as revenue
    FROM orders
    GROUP BY region
    ORDER BY revenue DESC
    """

    df_region = run_query(query_region)

    if not df_region.empty:
        fig = px.pie(
            df_region,
            values='revenue',
            names='region',
            title='Revenue Distribution by Region'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Connect to database to view regional sales.")

# Footer
st.divider()
st.markdown("""
**Navigation:** Use the sidebar to explore different analysis pages:
- **Executive Overview:** High-level business metrics
- **Product Analysis:** Deep dive into product performance
- **Regional Performance:** Geographic insights
- **Time Series:** Trends and seasonality analysis
""")
