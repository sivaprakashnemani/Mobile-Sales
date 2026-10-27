-- Mobile Sales Analysis | SQLite compatible | run one query at a time in DB Browser > Execute SQL
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
