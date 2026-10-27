# Mobile Sales Analysis | SQLite SQL Portfolio Project

## Overview
Analyze **1,200 synthetic mobile phone sales transactions** across 2024–2025 using SQLite. This project demonstrates SQL joins, aggregations, filtering, CTEs, HAVING, date analysis, and window functions.

## Files
- `mobile_sales.db` — complete ready-to-open SQLite database
- `analysis_queries.sql` — 15 independent analytical queries
- `sales.csv`, `products.csv`, `customers.csv`, `sales_reps.csv` — source data
- `build_project.py` — reproducible dataset and database generator (Python 3 standard library only)

## Run in DB Browser for SQLite
1. Open DB Browser for SQLite.
2. Choose **Open Database**, select `mobile_sales.db`.
3. Select **Browse Data** to inspect the `sales`, `products`, `customers`, and `sales_reps` tables.
4. Select **Execute SQL**. Open `analysis_queries.sql`, select one query at a time, and click **Execute** (play icon).
5. Confirm results appear below the SQL editor. You can export query results to CSV.

## Data model
`sales` is the transaction fact table; it references `products`, `customers`, and `sales_reps` by ID. Date is stored as ISO-8601 text, compatible with SQLite `strftime`.

## Business metrics
- Revenue = quantity × unit_price × (1 − discount_pct)
- Estimated gross profit = revenue − quantity × unit_cost
- Gross profit excludes shipping, tax, refunds, and operating expenses.
- Customer ratings are simulated transaction ratings on a 1–5 scale.

## Portfolio highlights
- Explored transaction, product, customer, and sales representative data using relational joins.
- Calculated revenue, units sold, average order value, and estimated gross profit.
- Analyzed monthly trends, top brands/models, regional performance, and customer purchase behavior.
- Applied CTEs, HAVING, and `DENSE_RANK()` window function to answer business questions.

## Limitations
All records are **fictional/synthetic**, not actual company sales. Prices, costs, customer names, and performance outcomes are illustrative. Do not describe this as professional work or real business impact.

## Suggested Power BI visuals
Revenue/units/orders KPI cards; monthly revenue line chart; brand revenue bar chart; top-model bar chart; city/state revenue map; payment-method donut chart; sales rep leaderboard; slicers for brand, state, year.
