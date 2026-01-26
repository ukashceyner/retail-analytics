# ABOUTME: Executive overview page showing high-level KPIs and trends.
# ABOUTME: Displays year-over-year comparisons and segment analysis.

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import run_query, get_summary_stats

st.set_page_config(page_title="Executive Overview", page_icon="📊", layout="wide")

st.title("Executive Overview")
st.markdown("High-level business metrics and performance indicators")
st.divider()

# Year selector
col1, col2 = st.columns([1, 3])
with col1:
    year_query = "SELECT DISTINCT year FROM orders ORDER BY year"
    years_df = run_query(year_query)
    if not years_df.empty:
        selected_year = st.selectbox("Select Year", years_df['year'].tolist(), index=len(years_df)-1)
    else:
        selected_year = 2023

# KPIs for selected year
query_year_kpis = f"""
SELECT
    COUNT(*) as orders,
    SUM(sale_price) as revenue,
    SUM(profit) as profit,
    AVG(profit_margin) as avg_margin,
    AVG(sale_price) as avg_order_value
FROM orders
WHERE year = {selected_year}
"""

df_kpis = run_query(query_year_kpis)

if not df_kpis.empty:
    kpis = df_kpis.iloc[0]

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Orders", f"{kpis['orders']:,}")
    col2.metric("Revenue", f"${kpis['revenue']:,.0f}")
    col3.metric("Profit", f"${kpis['profit']:,.0f}")
    col4.metric("Avg Margin", f"{kpis['avg_margin']:.1f}%")
    col5.metric("Avg Order Value", f"${kpis['avg_order_value']:.2f}")

st.divider()

# Year-over-Year Comparison
st.subheader("Year-over-Year Performance")

query_yoy = """
SELECT
    year,
    SUM(sale_price) as revenue,
    SUM(profit) as profit,
    COUNT(*) as orders,
    AVG(profit_margin) as avg_margin
FROM orders
GROUP BY year
ORDER BY year
"""

df_yoy = run_query(query_yoy)

if not df_yoy.empty:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df_yoy,
            x='year',
            y=['revenue', 'profit'],
            barmode='group',
            title='Revenue vs Profit by Year',
            labels={'value': 'Amount ($)', 'variable': 'Metric'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            df_yoy,
            x='year',
            y='orders',
            title='Order Volume by Year',
            labels={'orders': 'Number of Orders'}
        )
        fig.update_traces(marker_color='#2ecc71')
        st.plotly_chart(fig, use_container_width=True)

# Segment Analysis
st.subheader("Customer Segment Analysis")

query_segment = """
SELECT
    segment,
    COUNT(*) as orders,
    SUM(sale_price) as revenue,
    SUM(profit) as profit,
    AVG(profit_margin) as avg_margin
FROM orders
GROUP BY segment
ORDER BY revenue DESC
"""

df_segment = run_query(query_segment)

if not df_segment.empty:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(
            df_segment,
            values='revenue',
            names='segment',
            title='Revenue by Segment'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            df_segment,
            x='segment',
            y='avg_margin',
            title='Average Profit Margin by Segment',
            labels={'avg_margin': 'Profit Margin (%)'}
        )
        fig.update_traces(marker_color='#9b59b6')
        st.plotly_chart(fig, use_container_width=True)

    # Data table
    st.subheader("Segment Details")
    display_df = df_segment.copy()
    display_df['revenue'] = display_df['revenue'].apply(lambda x: f"${x:,.2f}")
    display_df['profit'] = display_df['profit'].apply(lambda x: f"${x:,.2f}")
    display_df['avg_margin'] = display_df['avg_margin'].apply(lambda x: f"{x:.2f}%")
    st.dataframe(display_df, use_container_width=True)
