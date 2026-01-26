-- ABOUTME: Query to find states with highest profit margins.
-- ABOUTME: Filters to states with meaningful order volume.

-- Business Question: Which states have the highest profit margins?

SELECT
    state,
    region,
    COUNT(DISTINCT order_id) as total_orders,
    ROUND(SUM(sale_price)::numeric, 2) as total_revenue,
    ROUND(SUM(profit)::numeric, 2) as total_profit,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_profit_margin,
    ROUND((SUM(profit) / NULLIF(SUM(sale_price), 0) * 100)::numeric, 2) as overall_margin_pct
FROM orders
GROUP BY state, region
HAVING COUNT(DISTINCT order_id) >= 50  -- Filter to states with meaningful volume
ORDER BY avg_profit_margin DESC
LIMIT 15;
