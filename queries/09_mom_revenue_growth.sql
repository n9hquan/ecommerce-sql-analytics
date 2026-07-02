-- Q9: Month-over-month revenue growth
-- Business question: How fast is revenue growing/shrinking month to month?
-- Excludes 2016-09 and 2016-12 (single-order noise months, see Q1) to keep growth
-- rates meaningful; also excludes 2018-09 onward since the dataset cuts off mid-month.

WITH monthly_revenue AS (
    SELECT
        date_trunc('month', o.order_purchase_timestamp) AS month,
        SUM(oi.price) AS revenue
    FROM olist_orders_dataset o
    JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
      AND date_trunc('month', o.order_purchase_timestamp) BETWEEN '2017-01-01' AND '2018-08-01'
    GROUP BY 1
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(LAG(revenue) OVER (ORDER BY month), 2) AS prev_month_revenue,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month), 2) AS pct_mom_growth
FROM monthly_revenue
ORDER BY month;
