-- ABOUTME: Query to find top 10 revenue-generating products.
-- ABOUTME: Uses ranking window function to order by total revenue.

-- Business Question: Which products generate the most revenue?

SELECT
    product_id,
    category,
    sub_category,
    SUM(sale_price) as total_revenue,
    SUM(quantity) as total_units_sold,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_profit_margin,
    RANK() OVER (ORDER BY SUM(sale_price) DESC) as revenue_rank
FROM orders
GROUP BY product_id, category, sub_category
ORDER BY total_revenue DESC
LIMIT 10;
