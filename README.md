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

## Interactive Dashboard

**[View live dashboard](https://n9hquan.github.io/ecommerce-sql-analytics/)** — all 10 findings below
as interactive Plotly charts (hover for exact values, zoom/pan), each labeled with its query number
for easy cross-reference. Hosted via GitHub Pages, no download needed.

> Prefer to run it locally? Clone the repo and open [`dashboard.html`](dashboard.html) directly, or
> regenerate it with `python build_dashboard.py`.

## Tools

- **DuckDB** — in-process SQL engine, queries CSVs directly, no install/server overhead
- **Python** — loads CSVs into DuckDB, executes queries, formats output
- **Plotly** — builds the interactive HTML dashboard ([`build_dashboard.py`](build_dashboard.py))
- All queries in [`queries/`](queries/), numbered in analysis order

## Business Questions, Findings & Insights

| # | Business Question | Finding | Insight |
|---|---|---|---|
| [1](queries/01_revenue_by_month.sql) | How is revenue trending month over month? | Steady growth through 2017, sharp Black Friday spike in **Nov 2017** (~$988K, 7,289 orders), then a 2018 plateau (~$850K-975K/month). AOV stayed flat (~$125-150). | **Growth was driven by order volume, not bigger baskets** — customer acquisition, not upsell, was the growth engine. |
| [2](queries/02_top_categories_by_revenue.sql) | Which product categories drive the most revenue? | **Health & Beauty** leads ($1.23M). **Watches & Gifts** has the highest AOV ($212) among top categories. | Two distinct category profiles exist: high-volume/lower-margin (Bed, Bath & Table) vs. low-volume/high-value niches (Watches & Gifts) — worth different marketing strategies. |
| [3](queries/03_top_sellers.sql) | Which sellers drive the most revenue? | 9 of the top 10 sellers are based in **São Paulo**. Revenue rank and order-volume rank don't always agree (some sellers win on AOV up to $626 rather than volume). | Seller base is geographically concentrated — a supply-side risk if SP logistics/labor conditions shift, and a signal for where to recruit new sellers outside SP. |
| [4](queries/04_delivery_performance.sql) | How long does delivery take, and how often is it late? | Average delivery time: **12.5 days**. **8.1% of orders arrive late**, averaging **~8.9 days late** when they are. | Lateness isn't a marginal miss — it's a substantial, ~9-day delay, which sets up finding #5. |
| [5](queries/05_delivery_delay_vs_review_score.sql) | Do late deliveries hurt review scores? | On-time orders average **4.29★** (9.2% bad reviews); late orders average **2.57★** (54% bad reviews). Days-late correlates with score at r = -0.235 among late orders. | **Headline finding.** On-time delivery is likely the single biggest lever for review scores — *being* late matters far more than *how* late. |
| [6](queries/06_customer_retention.sql) | How many customers come back for a second order? | **Only 3.0% of customers ever reorder.** Monthly cohort retention stays under 1% in every subsequent month, for every cohort. | Structural, not seasonal — customers are loyal to a need/product, not the Olist brand. Strategy should focus on first-order experience and acquisition quality (ties to #5), not lifecycle/retention campaigns. |
| [7](queries/07_revenue_by_state.sql) | Which states generate the most revenue? | **São Paulo drives 38.3% of revenue**; top 3 states (SP, RJ, MG) account for ~63%. Remote states (RR, AP, AC, AM) have higher AOV ($172-218) despite low order counts. | Revenue is geographically concentrated in Brazil's Southeast, mirroring the seller concentration in #3 — demand and supply cluster in the same region. |
| [8](queries/08_payment_types.sql) | How do customers pay? | **Credit card dominates** (73.9% of payments, 82% of value), averaging **3.51 installments**. Boleto is second (19%), always single-installment, lower AOV. | Reflects Brazil's installment-based credit culture — checkout flow and pricing should account for installment plans as the default payment expectation. |
| [9](queries/09_mom_revenue_growth.sql) | How fast is revenue growing month to month? | **+52.4% MoM in Nov 2017** (Black Friday), **-26.5% correction in Dec 2017**. Growth stabilizes to single digits from 2018 onward. | Confirms #1 in growth-rate terms and shows the business matured into a low-growth phase by mid-2018 — useful context for forecasting. |
| [10](queries/10_rfm_segmentation.sql) | Which customers are most valuable (RFM)? | Frequency barely varies (~1.0-1.3, per #6), so segments are driven by Recency × Monetary. **Lost/Churned**: 29,788 customers, $3.2M historical value. **Champions**: 3,268 customers, the only segment with real repeat behavior. | Per #6, most "Lost/Churned" customers were never going to return — that framing doesn't fit this one-and-done marketplace. **Champions are the best candidates if Olist wanted to build a loyalty program.** |

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
