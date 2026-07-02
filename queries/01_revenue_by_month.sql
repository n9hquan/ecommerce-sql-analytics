-- Q1: Revenue by month
-- Business question: How has revenue trended month over month?
-- Revenue = sum of order_items.price (product revenue only, excludes freight)
-- Only count orders that were actually delivered (excludes canceled/unavailable orders)

SELECT
    date_trunc('month', o.order_purchase_timestamp) AS month,
    COUNT(DISTINCT o.order_id) AS num_orders,
    ROUND(SUM(oi.price), 2) AS revenue,
    ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM olist_orders_dataset o
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 1;
