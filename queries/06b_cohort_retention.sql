-- Q6b: Monthly cohort retention
-- For each customer's first-purchase month (cohort), what % of that cohort placed
-- another order in each subsequent month offset (0 = cohort month, 1 = next month, etc.)

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        date_trunc('month', o.order_purchase_timestamp) AS order_month
    FROM olist_orders_dataset o
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
),
first_purchase AS (
    SELECT customer_unique_id, MIN(order_month) AS cohort_month
    FROM customer_orders
    GROUP BY 1
),
cohort_activity AS (
    SELECT
        f.cohort_month,
        DATE_DIFF('month', f.cohort_month, co.order_month) AS month_offset,
        co.customer_unique_id
    FROM customer_orders co
    JOIN first_purchase f ON co.customer_unique_id = f.customer_unique_id
),
cohort_size AS (
    SELECT cohort_month, COUNT(DISTINCT customer_unique_id) AS cohort_customers
    FROM first_purchase
    GROUP BY 1
)
SELECT
    a.cohort_month,
    a.month_offset,
    COUNT(DISTINCT a.customer_unique_id) AS active_customers,
    s.cohort_customers,
    ROUND(100.0 * COUNT(DISTINCT a.customer_unique_id) / s.cohort_customers, 2) AS pct_retained
FROM cohort_activity a
JOIN cohort_size s ON a.cohort_month = s.cohort_month
GROUP BY 1, 2, s.cohort_customers
ORDER BY 1, 2;
