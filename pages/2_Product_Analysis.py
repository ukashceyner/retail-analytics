# ABOUTME: Product analysis page for deep diving into product performance.
# ABOUTME: Shows category comparisons, top/bottom products, and profitability.

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import run_query, get_categories, get_date_range

st.set_page_config(page_title="Product Analysis", page_icon="📦", layout="wide")

st.title("Product Performance Analysis")
st.divider()

# Filters in sidebar
with st.sidebar:
    st.header("Filters")

    # Get categories
    categories = get_categories()
    if categories:
        selected_categories = st.multiselect(
            "Select Categories",
            categories,
            default=categories
        )
    else:
        selected_categories = []
        st.info("Connect to database to load categories")

    # Date range
    min_date, max_date = get_date_range()
    if min_date and max_date:
        date_filter = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    else:
        date_filter = None

# Build filter clause
if selected_categories:
    categories_str = "','".join(selected_categories)
    category_filter = f"category IN ('{categories_str}')"
else:
    category_filter = "1=1"

if date_filter and len(date_filter) == 2:
    date_clause = f"order_date BETWEEN '{date_filter[0]}' AND '{date_filter[1]}'"
else:
    date_clause = "1=1"

# Category Performance
st.subheader("Category Performance Comparison")

query_category = f"""
SELECT
    category,
    COUNT(DISTINCT order_id) as orders,
    SUM(quantity) as units_sold,
    ROUND(SUM(sale_price)::numeric, 2) as revenue,
    ROUND(SUM(profit)::numeric, 2) as profit,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_margin
FROM orders
WHERE {category_filter} AND {date_clause}
GROUP BY category
ORDER BY revenue DESC
"""

df_category = run_query(query_category)

if not df_category.empty:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df_category,
            x='category',
            y='revenue',
            title='Revenue by Category',
            color='profit',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            df_category,
            x='revenue',
            y='avg_margin',
            size='orders',
            text='category',
            title='Revenue vs Profit Margin',
            labels={'revenue': 'Revenue ($)', 'avg_margin': 'Profit Margin (%)'}
        )
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)

    # Data table with download
    st.subheader("Detailed Category Data")
    st.dataframe(df_category, use_container_width=True)

    csv = df_category.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="category_analysis.csv",
        mime="text/csv"
    )

st.divider()

# Top/Bottom performers
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Products by Revenue")
    query_top = f"""
    SELECT product_id, category, sub_category,
           ROUND(SUM(sale_price)::numeric, 2) as revenue,
           ROUND(AVG(profit_margin)::numeric, 2) as margin
    FROM orders
    WHERE {category_filter} AND {date_clause}
    GROUP BY product_id, category, sub_category
    ORDER BY revenue DESC
    LIMIT 10
    """
    df_top = run_query(query_top)
    if not df_top.empty:
        st.dataframe(df_top, use_container_width=True)

with col2:
    st.subheader("Bottom 10 Products by Revenue")
    query_bottom = f"""
    SELECT product_id, category, sub_category,
           ROUND(SUM(sale_price)::numeric, 2) as revenue,
           ROUND(AVG(profit_margin)::numeric, 2) as margin
    FROM orders
    WHERE {category_filter} AND {date_clause}
    GROUP BY product_id, category, sub_category
    ORDER BY revenue ASC
    LIMIT 10
    """
    df_bottom = run_query(query_bottom)
    if not df_bottom.empty:
        st.dataframe(df_bottom, use_container_width=True)

# Sub-category analysis
st.divider()
st.subheader("Sub-Category Performance")

query_subcat = f"""
SELECT
    category,
    sub_category,
    COUNT(*) as orders,
    ROUND(SUM(sale_price)::numeric, 2) as revenue,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_margin
FROM orders
WHERE {category_filter} AND {date_clause}
GROUP BY category, sub_category
ORDER BY revenue DESC
"""

df_subcat = run_query(query_subcat)

if not df_subcat.empty:
    fig = px.treemap(
        df_subcat,
        path=['category', 'sub_category'],
        values='revenue',
        color='avg_margin',
        color_continuous_scale='RdYlGn',
        title='Revenue by Category and Sub-Category (color = profit margin)'
    )
    st.plotly_chart(fig, use_container_width=True)

# Insights
st.info("""
**Key Insights:**
- Use filters to focus on specific categories or time periods
- Larger bubbles in the scatter plot indicate more orders
- Treemap color indicates profit margin (green = higher margin)
- Download data for further analysis
""")
