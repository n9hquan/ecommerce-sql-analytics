-- Q10: RFM-style customer segmentation
-- Business question: Which customers are most valuable, based on Recency, Frequency,
-- and Monetary value of their purchases?
-- NOTE: given Q6's finding that only 3% of customers ever repeat-purchase, Frequency
-- will be near-constant (mostly 1) for this dataset; segmentation here is driven
-- primarily by Recency and Monetary value, with Frequency mainly separating out the
-- small repeat-customer group.
-- Recency = days between customer's last order and the most recent date in the dataset.
-- Scored 1 (worst) to 5 (best) per dimension using quintiles (NTILE), then combined
-- into an RFM segment label.

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        oi.price
    FROM olist_orders_dataset o
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
),
max_date AS (
    SELECT MAX(order_purchase_timestamp) AS ref_date FROM customer_orders
),
rfm_raw AS (
    SELECT
        co.customer_unique_id,
        DATE_DIFF('day', MAX(co.order_purchase_timestamp), m.ref_date) AS recency_days,
        COUNT(DISTINCT co.order_id) AS frequency,
        ROUND(SUM(co.price), 2) AS monetary
    FROM customer_orders co
    CROSS JOIN max_date m
    GROUP BY 1, m.ref_date
),
rfm_scored AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm_raw
)
SELECT
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 4 AND m_score >= 3 THEN 'Recent High-Value'
        WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'At-Risk High-Value'
        WHEN r_score <= 2 THEN 'Lost / Churned'
        ELSE 'Regular'
    END AS segment,
    COUNT(*) AS num_customers,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency), 2) AS avg_frequency,
    ROUND(AVG(monetary), 2) AS avg_monetary,
    ROUND(SUM(monetary), 2) AS total_monetary
FROM rfm_scored
GROUP BY 1
ORDER BY total_monetary DESC;
