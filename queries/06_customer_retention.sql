-- Q6: Customer repeat-purchase rate and cohort retention
-- Business question: How many customers come back for a second order, and how does
-- retention evolve after a customer's first purchase month?
-- IMPORTANT: customer_id is unique PER ORDER in this dataset; the true customer
-- identity is customer_unique_id, so all repeat-purchase logic must use that.

-- Part A: overall repeat-purchase rate
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp
    FROM olist_orders_dataset o
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
),
order_counts AS (
    SELECT customer_unique_id, COUNT(*) AS num_orders
    FROM customer_orders
    GROUP BY 1
)
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN num_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN num_orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_repeat_customers
FROM order_counts;
