-- Q5: Delivery delay vs. review score
-- Business question: Do late deliveries correlate with worse review scores?
-- Bucket orders into on-time vs. late (vs. estimated date) and compare avg review score.
-- Also compute a direct correlation between days-late and review score for late orders.

WITH order_delay AS (
    SELECT
        o.order_id,
        DATE_DIFF('day', o.order_estimated_delivery_date, o.order_delivered_customer_date) AS days_late,
        CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
             THEN 'late' ELSE 'on_time' END AS delivery_bucket
    FROM olist_orders_dataset o
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
    d.delivery_bucket,
    COUNT(*) AS num_orders,
    ROUND(AVG(r.review_score), 2) AS avg_review_score,
    ROUND(100.0 * SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_bad_reviews
FROM order_delay d
JOIN olist_order_reviews_dataset r ON d.order_id = r.order_id
GROUP BY 1
ORDER BY 1;
