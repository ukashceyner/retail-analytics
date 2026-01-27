# Retail Orders Analytics Dashboard

**Live:** https://retail-analytics-eyjhn2gz3nwofsnyqy6ebe.streamlit.app/

## What this is

An analytics dashboard for retail order data. Takes a CSV, cleans it, loads it into Postgres, and serves it up through an interactive Streamlit app. Nothing fancy, just a solid end-to-end data project.

## What it does

- Shows revenue, profit, and order volume at a glance
- Breaks down performance by product category
- Compares regions against each other
- Tracks monthly trends and year-over-year changes
- Lets you filter by date, category, region
- Exports filtered data to CSV

## Stack

| Layer | Tech |
|-------|------|
| Database | Supabase (Postgres) |
| Backend | Python, pandas, psycopg2 |
| Frontend | Streamlit |
| Charts | Plotly |
| Hosting | Streamlit Community Cloud |

## The data

About 10,000 orders from 2022-2023. Includes order details, product info, pricing, shipping, geography. Originally from Kaggle.

## Project layout

```
retail-analytics/
├── Home.py                 # Entry point
├── pages/
│   ├── 1_Executive_Overview.py
│   ├── 2_Product_Analysis.py
│   ├── 3_Regional_Performance.py
│   └── 4_Time_Series.py
├── utils/
│   └── database.py
├── sql/
│   ├── schema.sql
│   ├── clean_data.py
│   ├── seed_data.py
│   └── queries/            # 10 analysis queries
├── data/
│   ├── raw/orders.csv
│   └── processed/orders_clean.csv
└── tests/
```

## SQL stuff

The queries in `sql/queries/` use window functions (RANK, LAG), CTEs, and CASE expressions. Here's the YoY growth query:

```sql
WITH yearly_revenue AS (
    SELECT year, SUM(sale_price) as revenue
    FROM orders GROUP BY year
)
SELECT year, revenue,
    LAG(revenue) OVER (ORDER BY year) as prev_year,
    ROUND(((revenue - LAG(revenue) OVER (ORDER BY year)) /
        LAG(revenue) OVER (ORDER BY year) * 100)::numeric, 2) as yoy_pct
FROM yearly_revenue;
```

## Running locally

```bash
git clone https://github.com/ukashceyner/retail-analytics.git
cd retail-analytics
pip install -r requirements.txt

# Add your Supabase credentials to .streamlit/secrets.toml

python sql/clean_data.py
python sql/seed_data.py
streamlit run Home.py
```

## What I found

See [INSIGHTS.md](INSIGHTS.md) for the full writeup. Short version: Technology products have the highest order values. Western region has better margins than everywhere else. Heavy discounts (>20%) don't pay off. Q4 is strong, Q2 is weak.

## Author

Lukasz Zehner - [LinkedIn](https://www.linkedin.com/in/lukasz-zehner-4b7b6688/) / [GitHub](https://github.com/ukashceyner)
