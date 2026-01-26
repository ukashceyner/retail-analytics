-- ABOUTME: Query to track category performance trends over time.
-- ABOUTME: Shows monthly revenue by category for trend analysis.

-- Business Question: How do category sales trend over time?

SELECT
    year,
    month,
    month_name,
    category,
    COUNT(*) as order_count,
    ROUND(SUM(sale_price)::numeric, 2) as revenue,
    ROUND(SUM(profit)::numeric, 2) as profit,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_margin,
    SUM(SUM(sale_price)) OVER (
        PARTITION BY category
        ORDER BY year, month
    ) as cumulative_revenue
FROM orders
GROUP BY year, month, month_name, category
ORDER BY category, year, month;
