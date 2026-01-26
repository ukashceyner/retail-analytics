-- ABOUTME: Query to analyze customer segments by revenue contribution.
-- ABOUTME: Calculates key metrics per segment with revenue share.

-- Business Question: How do different customer segments perform?

SELECT
    segment,
    COUNT(DISTINCT order_id) as total_orders,
    SUM(quantity) as total_units,
    ROUND(SUM(sale_price)::numeric, 2) as total_revenue,
    ROUND(SUM(profit)::numeric, 2) as total_profit,
    ROUND(AVG(sale_price)::numeric, 2) as avg_order_value,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_profit_margin,
    ROUND((SUM(sale_price) / SUM(SUM(sale_price)) OVER () * 100)::numeric, 2) as revenue_share_pct
FROM orders
GROUP BY segment
ORDER BY total_revenue DESC;
