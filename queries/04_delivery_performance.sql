-- Q4: Average delivery time and % of late deliveries
-- Business question: How long does delivery typically take, and how often does
-- Olist miss its own estimated delivery date?
-- Delivery time = delivered date - purchase date (calendar days)
-- Late = actual delivered date later than the estimated delivery date

SELECT
    COUNT(*) AS num_delivered_orders,
    ROUND(AVG(DATE_DIFF('day', order_purchase_timestamp, order_delivered_customer_date)), 2) AS avg_delivery_days,
    ROUND(
        100.0 * SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS pct_late_deliveries,
    ROUND(AVG(
        CASE WHEN order_delivered_customer_date > order_estimated_delivery_date
        THEN DATE_DIFF('day', order_estimated_delivery_date, order_delivered_customer_date)
        END
    ), 2) AS avg_days_late_when_late
FROM olist_orders_dataset
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL;
