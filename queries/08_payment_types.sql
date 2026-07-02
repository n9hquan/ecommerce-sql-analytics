-- Q8: Payment type distribution and average installments
-- Business question: How do customers pay, and how much do they rely on installment plans?

SELECT
    p.payment_type,
    COUNT(*) AS num_payments,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_payments,
    ROUND(SUM(p.payment_value), 2) AS total_value,
    ROUND(AVG(p.payment_value), 2) AS avg_payment_value,
    ROUND(AVG(p.payment_installments), 2) AS avg_installments
FROM olist_order_payments_dataset p
GROUP BY 1
ORDER BY num_payments DESC;
