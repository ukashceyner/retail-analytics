-- ABOUTME: Query to compare sales performance across regions.
-- ABOUTME: Uses CTE and window function for revenue share calculation.

-- Business Question: How do sales compare across regions?

WITH regional_metrics AS (
    SELECT
        region,
        COUNT(DISTINCT order_id) as total_orders,
        SUM(sale_price) as total_revenue,
        SUM(profit) as total_profit,
        AVG(profit_margin) as avg_margin
    FROM orders
    GROUP BY region
)
SELECT
    region,
    total_orders,
    ROUND(total_revenue::numeric, 2) as total_revenue,
    ROUND(total_profit::numeric, 2) as total_profit,
    ROUND(avg_margin::numeric, 2) as avg_margin,
    ROUND((total_revenue / SUM(total_revenue) OVER () * 100)::numeric, 2) as revenue_share_pct
FROM regional_metrics
ORDER BY total_revenue DESC;
