# E-Commerce SQL Analytics — Olist Brazilian E-Commerce

A SQL-driven business analysis of ~100k real orders from [Olist](https://olist.com), a Brazilian
multi-seller e-commerce marketplace, covering 2016-09 to 2018-08. Built with **DuckDB** (SQL directly
on CSV data, no server required) and **Python** for orchestration.

## Dataset

Public dataset: [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
(Kaggle), 9 relational tables covering orders, customers, order items, payments, reviews, products,
sellers, and geolocation.

**Key modeling note:** `customer_id` is unique *per order*, not per customer. The true customer
identity is `customer_unique_id`. All repeat-purchase / cohort logic in this project uses
`customer_unique_id` — a common gotcha in this dataset.

## Tools

- **DuckDB** — in-process SQL engine, queries CSVs directly, no install/server overhead
- **Python** — loads CSVs into DuckDB, executes queries, formats output
- All queries in [`queries/`](queries/), numbered in analysis order

## Business Questions & Key Findings

### 1. Revenue by month ([`01_revenue_by_month.sql`](queries/01_revenue_by_month.sql))
Steady growth through 2017, sharp Black Friday spike in **Nov 2017** (~$988K, 7,289 orders), then a
2018 plateau around $850K-975K/month. Average order value stayed flat (~$125-150) throughout —
**growth was driven by order volume, not bigger baskets.**

### 2. Top product categories by revenue ([`02_top_categories_by_revenue.sql`](queries/02_top_categories_by_revenue.sql))
**Health & Beauty** leads ($1.23M). **Watches & Gifts** stands out with the highest AOV ($212) among
top categories — a high-value, lower-frequency niche vs. high-volume/lower-margin categories like
Bed, Bath & Table.

### 3. Top sellers ([`03_top_sellers.sql`](queries/03_top_sellers.sql))
9 of the top 10 sellers by revenue are based in São Paulo — strong geographic concentration. Revenue
rank and order-volume rank don't always agree: some top sellers win on AOV (up to $626) rather than
volume.

### 4. Delivery performance ([`04_delivery_performance.sql`](queries/04_delivery_performance.sql))
Average delivery time: **12.5 days**. **8.1% of orders arrive late**, and when late, they're late by
**~8.9 days on average** — not a marginal miss.

### 5. Delivery delay vs. review score ([`05_delivery_delay_vs_review_score.sql`](queries/05_delivery_delay_vs_review_score.sql))
**Headline finding.** On-time orders average a **4.29** review score (9.2% bad reviews); late orders
average **2.57** (54% bad reviews) — nearly a 6x jump in bad-review rate. Among late orders, days-late
correlates with score at **r = -0.235** (moderate) — meaning the binary fact of being late matters more
than exactly how late. **On-time delivery is likely the single biggest lever for review scores.**

### 6. Customer retention ([`06_customer_retention.sql`](queries/06_customer_retention.sql), [`06b_cohort_retention.sql`](queries/06b_cohort_retention.sql))
**Only 3.0% of customers ever place a second order.** Monthly cohort retention is consistently under
1% in every subsequent month. This is a structural feature of the marketplace model (customers are
loyal to a need/product, not the Olist brand) — the real insight is that there's essentially no
organic retention to grow, which should redirect strategy toward acquisition quality and first-order
experience (tying back to finding #5) rather than lifecycle/retention campaigns.

### 7. Revenue by state ([`07_revenue_by_state.sql`](queries/07_revenue_by_state.sql))
**São Paulo alone drives 38.3% of revenue**; the top 3 states (SP, RJ, MG — Brazil's Southeast) account
for ~63%. Smaller/remote states (RR, AP, AC, AM) show far fewer orders but noticeably higher AOV
($172-218) — plausibly reflecting shipping-cost pass-through or lower-frequency/higher-value buying
in underserved regions.

### 8. Payment types ([`08_payment_types.sql`](queries/08_payment_types.sql))
**Credit card dominates (73.9% of payments, 82% of value)**, averaging **3.51 installments** —
consistent with Brazil's installment-based credit culture. Boleto (bank slip) is second (19%),
always single-installment, with lower average order value — suggesting a more cash-conscious segment.

### 9. Month-over-month revenue growth ([`09_mom_revenue_growth.sql`](queries/09_mom_revenue_growth.sql))
Confirms the Black Friday spike from #1 in growth-rate terms: **+52.4% MoM in Nov 2017**, followed by
a **-26.5% correction in Dec 2017**. Growth stabilizes to single digits from 2018 onward — the
business matured into a low-growth phase by mid-2018.

### 10. RFM customer segmentation ([`10_rfm_segmentation.sql`](queries/10_rfm_segmentation.sql))
Given finding #6, Frequency barely varies across customers (~1.0-1.3), so segments are really driven
by Recency × Monetary value. **Lost/Churned is the largest concerning segment** (29,788 customers,
$3.2M historical value, 412 days since last order on average) — but per finding #6, most of this
group was never going to return regardless, since one-and-done is the platform norm. **Champions**
(3,268 customers, the only segment with genuine repeat behavior) are the best candidates for a
loyalty program, if Olist wanted to build one.

## How to reproduce

```bash
pip install duckdb
python -c "
import duckdb, glob, os
con = duckdb.connect('olist.duckdb')
for f in sorted(glob.glob('data/*.csv')):
    name = os.path.splitext(os.path.basename(f))[0]
    con.execute(f\"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_csv_auto('{f}')\")
"
```

Then run any query file against `olist.duckdb`, e.g.:

```bash
python -c "
import duckdb
con = duckdb.connect('olist.duckdb')
print(con.execute(open('queries/01_revenue_by_month.sql').read()).df())
"
```
