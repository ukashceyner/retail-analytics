-- ABOUTME: Query to analyze how discounts impact profitability.
-- ABOUTME: Groups orders by discount tier to show margin impact.

-- Business Question: How do discounts affect profit margins?

WITH discount_tiers AS (
    SELECT
        *,
        CASE
            WHEN discount_percent = 0 THEN 'No Discount'
            WHEN discount_percent <= 5 THEN '1-5%'
            WHEN discount_percent <= 10 THEN '6-10%'
            WHEN discount_percent <= 15 THEN '11-15%'
            WHEN discount_percent <= 20 THEN '16-20%'
            ELSE '>20%'
        END as discount_tier
    FROM orders
)
SELECT
    discount_tier,
    COUNT(*) as order_count,
    ROUND(AVG(discount_percent)::numeric, 2) as avg_discount,
    ROUND(SUM(sale_price)::numeric, 2) as total_revenue,
    ROUND(SUM(profit)::numeric, 2) as total_profit,
    ROUND(AVG(profit_margin)::numeric, 2) as avg_profit_margin,
    ROUND((SUM(profit) / NULLIF(SUM(sale_price), 0) * 100)::numeric, 2) as overall_margin_pct
FROM discount_tiers
GROUP BY discount_tier
ORDER BY avg_discount;
