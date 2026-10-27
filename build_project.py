import sqlite3,csv,random,datetime,os
from pathlib import Path
p=Path(__file__).parent
random.seed(42)
brands={'Apple':[('iPhone 15',799,570),('iPhone 16',899,640),('iPhone 16 Pro',1099,790)],'Samsung':[('Galaxy S24',799,545),('Galaxy S25',899,620),('Galaxy A55',449,290)],'Google':[('Pixel 8',599,390),('Pixel 9',799,520)],'OnePlus':[('OnePlus 12',699,460),('OnePlus 13',899,610)],'Motorola':[('Moto G Power',299,175),('Edge 50',549,350)]}
locations=[('Cleveland','OH'),('Columbus','OH'),('Chicago','IL'),('Dallas','TX'),('Austin','TX'),('New York','NY'),('Seattle','WA'),('Los Angeles','CA'),('Atlanta','GA'),('Miami','FL')]
conn=sqlite3.connect(p/'mobile_sales.db');c=conn.cursor();c.executescript('''DROP TABLE IF EXISTS sales; DROP TABLE IF EXISTS products; DROP TABLE IF EXISTS customers; DROP TABLE IF EXISTS sales_reps;
CREATE TABLE products(product_id INTEGER PRIMARY KEY,brand TEXT NOT NULL,model TEXT NOT NULL,unit_cost REAL NOT NULL,list_price REAL NOT NULL);
CREATE TABLE customers(customer_id INTEGER PRIMARY KEY,customer_name TEXT NOT NULL,city TEXT NOT NULL,state TEXT NOT NULL);
CREATE TABLE sales_reps(rep_id INTEGER PRIMARY KEY,rep_name TEXT NOT NULL);
CREATE TABLE sales(sale_id INTEGER PRIMARY KEY,sale_date TEXT NOT NULL,customer_id INTEGER NOT NULL,product_id INTEGER NOT NULL,rep_id INTEGER NOT NULL,quantity INTEGER NOT NULL CHECK(quantity>0),unit_price REAL NOT NULL CHECK(unit_price>=0),discount_pct REAL NOT NULL CHECK(discount_pct BETWEEN 0 AND 1),payment_method TEXT NOT NULL,customer_rating INTEGER CHECK(customer_rating BETWEEN 1 AND 5),FOREIGN KEY(customer_id) REFERENCES customers(customer_id),FOREIGN KEY(product_id) REFERENCES products(product_id),FOREIGN KEY(rep_id) REFERENCES sales_reps(rep_id));''')
products=[(i,b,m,cost,price) for i,(b,m,cost,price) in enumerate(((b,m,cost,price) for b,models in brands.items() for m,price,cost in models),1)]
c.executemany('INSERT INTO products VALUES (?,?,?,?,?)',products)
customers=[(i,f'Customer {i:03d}',*random.choice(locations)) for i in range(1,251)]
c.executemany('INSERT INTO customers VALUES (?,?,?,?)',customers)
reps=[(i,n) for i,n in enumerate(['Alex Morgan','Taylor Lee','Jordan Patel','Casey Smith','Riley Chen','Avery Brown','Sam Wilson','Morgan Davis'],1)]
c.executemany('INSERT INTO sales_reps VALUES (?,?)',reps)
rows=[]
for i in range(1,1201):
    day=datetime.date(2024,1,1)+datetime.timedelta(days=random.randrange(731))
    prod=random.choice(products);discount=random.choices([0,.05,.10,.15,.20],[35,25,20,15,5])[0]
    rows.append((i,day.isoformat(),random.randint(1,250),prod[0],random.randint(1,8),random.choices([1,2,3],[78,18,4])[0],prod[4],discount,random.choice(['Credit Card','Debit Card','UPI','Cash','Financing']),random.choices([1,2,3,4,5],[3,5,12,35,45])[0]))
c.executemany('INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?)',rows)
conn.commit()
for table in ['products','customers','sales_reps','sales']:
    cur=c.execute(f'SELECT * FROM {table}')
    with open(p/f'{table}.csv','w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow([x[0] for x in cur.description]);w.writerows(cur)
queries='''-- Mobile Sales Analysis | SQLite compatible | run one query at a time in DB Browser > Execute SQL
-- Revenue = quantity * unit_price * (1 - discount_pct)
-- Estimated profit = revenue - (quantity * unit_cost); excludes taxes, shipping and overhead.

-- 01. Dataset overview
SELECT COUNT(*) AS transactions, COUNT(DISTINCT customer_id) AS unique_customers,
       SUM(quantity) AS units_sold,
       ROUND(SUM(quantity*unit_price*(1-discount_pct)),2) AS total_revenue
FROM sales;

-- 02. Total estimated profit and profit margin
SELECT ROUND(SUM(s.quantity*s.unit_price*(1-s.discount_pct)-s.quantity*p.unit_cost),2) AS estimated_profit,
       ROUND(100.0*SUM(s.quantity*s.unit_price*(1-s.discount_pct)-s.quantity*p.unit_cost)/NULLIF(SUM(s.quantity*s.unit_price*(1-s.discount_pct)),0),2) AS profit_margin_pct
FROM sales s JOIN products p ON s.product_id=p.product_id;

-- 03. Brand revenue ranking (JOIN, GROUP BY, ORDER BY)
SELECT p.brand, COUNT(*) AS transactions, SUM(s.quantity) AS units_sold,
       ROUND(SUM(s.quantity*s.unit_price*(1-s.discount_pct)),2) AS revenue
FROM sales s JOIN products p ON s.product_id=p.product_id
GROUP BY p.brand ORDER BY revenue DESC;

-- 04. Top 5 mobile models by units sold
SELECT p.brand,p.model,SUM(s.quantity) AS units_sold,
       ROUND(SUM(s.quantity*s.unit_price*(1-s.discount_pct)),2) AS revenue
FROM sales s JOIN products p ON s.product_id=p.product_id
GROUP BY p.product_id ORDER BY units_sold DESC LIMIT 5;

-- 05. Monthly revenue trend
SELECT strftime('%Y-%m',sale_date) AS sale_month, COUNT(*) AS orders,
       ROUND(SUM(quantity*unit_price*(1-discount_pct)),2) AS revenue
FROM sales GROUP BY sale_month ORDER BY sale_month;

-- 06. Sales by state and city
SELECT c.state,c.city,SUM(s.quantity) AS units_sold,
       ROUND(SUM(s.quantity*s.unit_price*(1-s.discount_pct)),2) AS revenue
FROM sales s JOIN customers c ON s.customer_id=c.customer_id
GROUP BY c.state,c.city ORDER BY revenue DESC;

-- 07. Payment method breakdown
SELECT payment_method,COUNT(*) AS transactions,
       ROUND(SUM(quantity*unit_price*(1-discount_pct)),2) AS revenue
FROM sales GROUP BY payment_method ORDER BY revenue DESC;

-- 08. Customer satisfaction by brand
SELECT p.brand,ROUND(AVG(s.customer_rating),2) AS avg_rating,COUNT(*) AS rated_transactions
FROM sales s JOIN products p ON s.product_id=p.product_id
WHERE s.customer_rating IS NOT NULL GROUP BY p.brand ORDER BY avg_rating DESC;

-- 09. Sales representative leaderboard
SELECT r.rep_name,COUNT(*) AS transactions,
       ROUND(SUM(s.quantity*s.unit_price*(1-s.discount_pct)),2) AS revenue
FROM sales s JOIN sales_reps r ON s.rep_id=r.rep_id
GROUP BY r.rep_id ORDER BY revenue DESC;

-- 10. Most profitable models (estimated)
SELECT p.brand,p.model,
       ROUND(SUM(s.quantity*(s.unit_price*(1-s.discount_pct)-p.unit_cost)),2) AS estimated_profit
FROM sales s JOIN products p ON s.product_id=p.product_id
GROUP BY p.product_id ORDER BY estimated_profit DESC;

-- 11. Repeat customers (HAVING)
SELECT c.customer_id,c.customer_name,COUNT(*) AS purchases,
       ROUND(SUM(s.quantity*s.unit_price*(1-s.discount_pct)),2) AS lifetime_value
FROM sales s JOIN customers c ON s.customer_id=c.customer_id
GROUP BY c.customer_id HAVING COUNT(*)>1 ORDER BY lifetime_value DESC LIMIT 15;

-- 12. High-value sales using a CTE
WITH order_values AS (
 SELECT sale_id,sale_date,quantity*unit_price*(1-discount_pct) AS order_value FROM sales
)
SELECT sale_id,sale_date,ROUND(order_value,2) AS order_value
FROM order_values WHERE order_value > 1500 ORDER BY order_value DESC LIMIT 20;

-- 13. Brand revenue rank using window functions (SQLite 3.25+)
WITH brand_sales AS (
 SELECT p.brand, SUM(s.quantity*s.unit_price*(1-s.discount_pct)) AS revenue
 FROM sales s JOIN products p ON s.product_id=p.product_id GROUP BY p.brand
)
SELECT brand,ROUND(revenue,2) AS revenue,DENSE_RANK() OVER(ORDER BY revenue DESC) AS revenue_rank
FROM brand_sales ORDER BY revenue_rank;

-- 14. Quarterly revenue comparison
SELECT strftime('%Y',sale_date) AS year,
       ((CAST(strftime('%m',sale_date) AS INTEGER)-1)/3)+1 AS quarter,
       ROUND(SUM(quantity*unit_price*(1-discount_pct)),2) AS revenue
FROM sales GROUP BY year,quarter ORDER BY year,quarter;

-- 15. Average order value
SELECT ROUND(AVG(quantity*unit_price*(1-discount_pct)),2) AS average_order_value
FROM sales;
'''
(p/'analysis_queries.sql').write_text(queries,encoding='utf-8')
(p/'README.md').write_text('''# Mobile Sales Analysis | SQLite SQL Portfolio Project

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
''',encoding='utf-8')
print('sales',c.execute('select count(*) from sales').fetchone()[0]);print('revenue',c.execute('select round(sum(quantity*unit_price*(1-discount_pct)),2) from sales').fetchone()[0]);conn.close()
