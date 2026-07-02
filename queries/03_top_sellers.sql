-- Q3: Top sellers by revenue and order count
-- Business question: Which sellers drive the most revenue, and are the top sellers by
-- revenue the same as the top sellers by order volume?

SELECT
    s.seller_id,
    s.seller_state,
    COUNT(DISTINCT o.order_id) AS num_orders,
    ROUND(SUM(oi.price), 2) AS revenue,
    ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM olist_orders_dataset o
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
JOIN olist_sellers_dataset s ON oi.seller_id = s.seller_id
WHERE o.order_status = 'delivered'
GROUP BY 1, 2
ORDER BY revenue DESC
LIMIT 10;
