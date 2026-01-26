-- ABOUTME: Query to find best-performing month for each category.
-- ABOUTME: Uses ROW_NUMBER with PARTITION BY to rank months within categories.

-- Business Question: Which month performs best for each product category?

WITH monthly_category_sales AS (
    SELECT
        category,
        month,
        month_name,
        SUM(sale_price) as revenue,
        SUM(profit) as profit,
        COUNT(*) as order_count
    FROM orders
    GROUP BY category, month, month_name
),
ranked AS (
    SELECT
        category,
        month,
        month_name,
        revenue,
        profit,
        order_count,
        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY revenue DESC
        ) as rank
    FROM monthly_category_sales
)
SELECT
    category,
    month_name as best_month,
    ROUND(revenue::numeric, 2) as revenue,
    ROUND(profit::numeric, 2) as profit,
    order_count
FROM ranked
WHERE rank = 1
ORDER BY revenue DESC;
