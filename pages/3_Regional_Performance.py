# ABOUTME: Regional performance page showing geographic sales patterns.
# ABOUTME: Displays regional comparisons, state-level analysis, and shipping insights.

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import run_query, get_regions

st.set_page_config(page_title="Regional Performance", page_icon="🗺️", layout="wide")

st.title("Regional Performance Analysis")
st.divider()

# Filters
with st.sidebar:
    st.header("Filters")

    regions = get_regions()
    if regions:
        selected_regions = st.multiselect(
            "Select Regions",
            regions,
            default=regions
        )
    else:
        selected_regions = []
        st.info("Connect to database to load regions")

# Build filter
if selected_regions:
    regions_str = "','".join(selected_regions)
    region_filter = f"region IN ('{regions_str}')"
else:
    region_filter = "1=1"

# Regional Overview
st.subheader("Regional Performance Overview")

query_region = f"""
SELECT
    region,
    COUNT(DISTINCT order_id) as orders,
    ROUND(SUM(sale_price)::numeric, 2) as revenue,
    ROUND(SUM(profit)::numeric, 2) as profit,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_margin,
    ROUND((SUM(sale_price) / SUM(SUM(sale_price)) OVER () * 100)::numeric, 2) as revenue_share
FROM orders
WHERE {region_filter}
GROUP BY region
ORDER BY revenue DESC
"""

df_region = run_query(query_region)

if not df_region.empty:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df_region,
            x='region',
            y='revenue',
            color='avg_margin',
            color_continuous_scale='RdYlGn',
            title='Revenue by Region (color = profit margin)'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            df_region,
            values='revenue_share',
            names='region',
            title='Revenue Share by Region'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Regional KPI cards
    st.subheader("Regional KPIs")
    cols = st.columns(len(df_region))
    for i, row in df_region.iterrows():
        with cols[i]:
            st.metric(row['region'], f"${row['revenue']:,.0f}")
            st.caption(f"Margin: {row['avg_margin']:.1f}%")

st.divider()

# State-level analysis
st.subheader("Top Performing States")

query_state = f"""
SELECT
    state,
    region,
    COUNT(*) as orders,
    ROUND(SUM(sale_price)::numeric, 2) as revenue,
    ROUND(SUM(profit)::numeric, 2) as profit,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_margin
FROM orders
WHERE {region_filter}
GROUP BY state, region
HAVING COUNT(*) >= 20
ORDER BY revenue DESC
LIMIT 15
"""

df_state = run_query(query_state)

if not df_state.empty:
    fig = px.bar(
        df_state,
        x='state',
        y='revenue',
        color='region',
        title='Top 15 States by Revenue',
        labels={'revenue': 'Revenue ($)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # State data table
    st.dataframe(df_state, use_container_width=True)

st.divider()

# Shipping Mode Analysis
st.subheader("Shipping Mode Performance by Region")

query_shipping = f"""
SELECT
    region,
    COALESCE(ship_mode, 'Unknown') as ship_mode,
    COUNT(*) as orders,
    ROUND(SUM(sale_price)::numeric, 2) as revenue,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_margin
FROM orders
WHERE {region_filter}
GROUP BY region, ship_mode
ORDER BY region, revenue DESC
"""

df_shipping = run_query(query_shipping)

if not df_shipping.empty:
    fig = px.bar(
        df_shipping,
        x='region',
        y='orders',
        color='ship_mode',
        title='Order Distribution by Ship Mode and Region',
        barmode='stack'
    )
    st.plotly_chart(fig, use_container_width=True)

# City analysis
st.divider()
st.subheader("Top Cities by Revenue")

query_city = f"""
SELECT
    city,
    state,
    region,
    COUNT(*) as orders,
    ROUND(SUM(sale_price)::numeric, 2) as revenue
FROM orders
WHERE {region_filter}
GROUP BY city, state, region
ORDER BY revenue DESC
LIMIT 10
"""

df_city = run_query(query_city)

if not df_city.empty:
    fig = px.bar(
        df_city,
        x='revenue',
        y='city',
        color='region',
        orientation='h',
        title='Top 10 Cities by Revenue'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# Download
if not df_region.empty:
    csv = df_region.to_csv(index=False)
    st.download_button(
        label="Download Regional Data",
        data=csv,
        file_name="regional_performance.csv",
        mime="text/csv"
    )
