-- ABOUTME: Query to calculate year-over-year revenue growth.
-- ABOUTME: Uses LAG window function to compare consecutive years.

-- Business Question: What is the year-over-year growth rate?

WITH yearly_revenue AS (
    SELECT
        year,
        SUM(sale_price) as revenue,
        SUM(profit) as profit,
        COUNT(*) as order_count
    FROM orders
    GROUP BY year
)
SELECT
    year,
    ROUND(revenue::numeric, 2) as revenue,
    ROUND(profit::numeric, 2) as profit,
    order_count,
    LAG(revenue) OVER (ORDER BY year) as prev_year_revenue,
    ROUND(
        ((revenue - LAG(revenue) OVER (ORDER BY year)) /
        NULLIF(LAG(revenue) OVER (ORDER BY year), 0) * 100)::numeric, 2
    ) as yoy_growth_pct
FROM yearly_revenue
ORDER BY year;
