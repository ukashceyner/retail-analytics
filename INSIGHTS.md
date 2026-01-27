# Business Insights

Looking at 10,000 retail orders from 2022-2023.

## The short version

Technology products make more money per transaction than other categories. The Western region runs tighter margins than everyone else. Discounting past 20% loses money. Q4 is strong, Q2 drags.

## Category performance

Technology generates outsized revenue relative to how many orders it accounts for. The average Technology order is worth more than orders in other categories. Makes sense - people buying tech are already prepared to spend.

If I were running marketing here, I'd lean harder into Technology. Cross-sell accessories, bundle deals. That's where the money is.

## Regional differences

Western region has noticeably higher profit margins than the national average. Same products, different results.

I don't have the data to prove why, but my guesses: lower shipping costs (closer warehouses?), different customer mix, or just better pricing discipline in that region. Worth investigating what they do differently and whether it can be replicated.

## Discounts

Orders with discounts over 20% have meaningfully lower margins. The extra volume doesn't make up for it.

This is a common trap. Heavy discounting trains customers to wait for sales. It erodes the brand. I'd test capping discounts at 15-20% and shifting the messaging toward value instead of price cuts.

## Shipping

Standard shipping is about 60% of orders. Premium options see higher cart abandonment.

People are price sensitive about shipping even when they're buying expensive stuff. A $5 shipping fee on a $200 order feels worse than it should. Consider free standard shipping and price premium options to cover costs rather than maximize margin.

## Seasonality

Q4 has strong year-over-year growth. Q2 lags behind.

Predictable enough - holiday shopping. Lean into Q4 with inventory and marketing. For Q2, either run targeted promotions or accept the dip and plan staffing accordingly.

## What I don't have

This analysis would be stronger with:
- Customer data (demographics, repeat purchase rates)
- Return/refund rates by category
- Competitor pricing
- Marketing attribution

## How I calculated this

- Window functions for period comparisons (LAG for YoY, RANK for top performers)
- CTEs to keep the queries readable
- Profit margin = (sale_price - cost_price) / sale_price
- YoY growth = (current - prior) / prior * 100

## What I'd do next

A/B test the discount cap in one region. Survey customers in low-margin regions to understand what's different. Build a demand forecast for inventory planning. Start tracking customer lifetime value by acquisition source.

---

Lukasz Zehner
