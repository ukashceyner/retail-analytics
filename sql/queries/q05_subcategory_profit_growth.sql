-- ABOUTME: Query to find sub-categories with highest profit growth YoY.
-- ABOUTME: Compares 2022 vs 2023 profit by sub-category.

-- Business Question: Which sub-categories show the highest profit growth?

WITH yearly_subcategory AS (
    SELECT
        sub_category,
        year,
        SUM(profit) as profit,
        SUM(sale_price) as revenue
    FROM orders
    GROUP BY sub_category, year
),
pivoted AS (
    SELECT
        sub_category,
        SUM(CASE WHEN year = 2022 THEN profit ELSE 0 END) as profit_2022,
        SUM(CASE WHEN year = 2023 THEN profit ELSE 0 END) as profit_2023,
        SUM(CASE WHEN year = 2022 THEN revenue ELSE 0 END) as revenue_2022,
        SUM(CASE WHEN year = 2023 THEN revenue ELSE 0 END) as revenue_2023
    FROM yearly_subcategory
    GROUP BY sub_category
)
SELECT
    sub_category,
    ROUND(profit_2022::numeric, 2) as profit_2022,
    ROUND(profit_2023::numeric, 2) as profit_2023,
    ROUND((profit_2023 - profit_2022)::numeric, 2) as profit_change,
    ROUND(
        CASE WHEN profit_2022 != 0
            THEN ((profit_2023 - profit_2022) / ABS(profit_2022) * 100)
            ELSE NULL
        END::numeric, 2
    ) as profit_growth_pct
FROM pivoted
ORDER BY profit_growth_pct DESC NULLS LAST;
