-- ABOUTME: Query to analyze shipping mode performance metrics.
-- ABOUTME: Compares revenue, profit, and order distribution by ship mode.

-- Business Question: How do different shipping modes perform?

SELECT
    COALESCE(ship_mode, 'Unknown') as ship_mode,
    COUNT(*) as order_count,
    ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ())::numeric, 2) as order_share_pct,
    ROUND(SUM(sale_price)::numeric, 2) as total_revenue,
    ROUND(SUM(profit)::numeric, 2) as total_profit,
    ROUND(AVG(sale_price)::numeric, 2) as avg_order_value,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_profit_margin,
    ROUND(AVG(quantity)::numeric, 2) as avg_quantity_per_order
FROM orders
GROUP BY ship_mode
ORDER BY order_count DESC;
