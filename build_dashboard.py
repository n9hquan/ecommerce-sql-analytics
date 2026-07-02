"""
Builds a modern, self-contained interactive HTML dashboard from the project's
SQL query results, using DuckDB + Plotly. Each finding gets its own styled
card section with a title and one-line takeaway. Run after olist.duckdb has
been built (see README "How to reproduce").
"""
import duckdb
import plotly.graph_objects as go
import plotly.io as pio

TEMPLATE = "plotly_white"
PALETTE = {
    "blue": "#2E86AB",
    "magenta": "#A23B72",
    "orange": "#F18F01",
    "red": "#C73E1D",
    "green": "#5B8C5A",
    "ink": "#3B1F2B",
}

con = duckdb.connect("olist.duckdb")


def q(path):
    return con.execute(open(path).read()).df()


def fig_to_div(fig, height=420):
    fig.update_layout(
        template=TEMPLATE,
        margin=dict(l=40, r=20, t=10, b=40),
        height=height,
        font=dict(family="Inter, -apple-system, Segoe UI, sans-serif", size=13, color="#2b2b2b"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return pio.to_html(fig, include_plotlyjs=False, full_html=False, config={"displaylogo": False})


cards = []  # list of (title, takeaway, div_html)

# ---------- 1. Revenue by month ----------
df = q("queries/01_revenue_by_month.sql")
df = df[(df["month"] >= "2017-01-01") & (df["month"] <= "2018-08-01")]
fig = go.Figure(go.Scatter(x=df["month"], y=df["revenue"], mode="lines+markers",
                            line=dict(color=PALETTE["blue"], width=3), marker=dict(size=6),
                            fill="tozeroy", fillcolor="rgba(46,134,171,0.08)"))
fig.update_yaxes(title="Revenue (R$)")
cards.append(("Q1 · Monthly Revenue Trend",
              "Steady growth through 2017 with a sharp Black Friday spike in Nov 2017, then a stable plateau in 2018.",
              fig_to_div(fig)))

# ---------- 2. Top categories ----------
df = q("queries/02_top_categories_by_revenue.sql").sort_values("revenue")
fig = go.Figure(go.Bar(x=df["revenue"], y=df["category"], orientation="h",
                        marker_color=PALETTE["blue"],
                        text=df["revenue"].map(lambda v: f"R${v:,.0f}"), textposition="outside"))
fig.update_xaxes(title="Revenue (R$)")
cards.append(("Q2 · Top 10 Product Categories by Revenue",
              "Health & Beauty leads overall; Watches & Gifts has the highest average order value among top categories.",
              fig_to_div(fig)))

# ---------- 3. Top sellers ----------
df = q("queries/03_top_sellers.sql")
df["seller_short"] = df["seller_id"].str[:8] + "…" + " (" + df["seller_state"] + ")"
fig = go.Figure(go.Bar(x=df["seller_short"], y=df["revenue"], marker_color=PALETTE["magenta"]))
fig.update_yaxes(title="Revenue (R$)")
fig.update_xaxes(tickangle=-30)
cards.append(("Q3 · Top 10 Sellers by Revenue",
              "9 of the top 10 sellers are based in São Paulo (SP) — strong geographic seller concentration.",
              fig_to_div(fig)))

# ---------- 4/5. Delivery performance + review score ----------
df5 = q("queries/05_delivery_delay_vs_review_score.sql")
fig = go.Figure()
fig.add_trace(go.Bar(x=df5["delivery_bucket"], y=df5["avg_review_score"],
                      marker_color=[PALETTE["blue"], PALETTE["red"]],
                      text=df5["avg_review_score"], textposition="outside", name="Avg Score"))
fig.update_yaxes(title="Average Review Score (1-5)", range=[0, 5.5])
cards.append(("Q4-5 · Delivery Performance vs. Review Score",
              "On-time orders average 4.29★ (9% bad reviews); late orders average 2.57★ (54% bad reviews).",
              fig_to_div(fig)))

# ---------- 6. Cohort retention ----------
df6 = q("queries/06b_cohort_retention.sql")
df6 = df6[(df6["month_offset"] >= 1) & (df6["month_offset"] <= 5)]
df6_avg = df6.groupby("month_offset", as_index=False)["pct_retained"].mean()
fig = go.Figure(go.Scatter(x=df6_avg["month_offset"], y=df6_avg["pct_retained"], mode="lines+markers",
                            line=dict(color=PALETTE["red"], width=3), marker=dict(size=8)))
fig.update_xaxes(title="Months Since First Order", dtick=1)
fig.update_yaxes(title="Avg % of Cohort Retained")
cards.append(("Q6 · Customer Cohort Retention",
              "Retention drops under 1% in every month after the first purchase — only 3% of customers ever reorder.",
              fig_to_div(fig)))

# ---------- 7. Revenue by state ----------
df = q("queries/07_revenue_by_state.sql")
fig = go.Figure(go.Bar(x=df["customer_state"], y=df["revenue"], marker_color=PALETTE["ink"]))
fig.update_yaxes(title="Revenue (R$)")
cards.append(("Q7 · Revenue by Customer State",
              "São Paulo alone drives 38% of revenue; the top 3 states account for ~63%.",
              fig_to_div(fig)))

# ---------- 8. Payment types ----------
df = q("queries/08_payment_types.sql")
df = df[df["payment_type"] != "not_defined"]
fig = go.Figure(go.Pie(labels=df["payment_type"], values=df["num_payments"], hole=0.5,
                        marker=dict(colors=[PALETTE["blue"], PALETTE["orange"], PALETTE["green"],
                                             PALETTE["magenta"]])))
cards.append(("Q8 · Payment Type Distribution",
              "Credit card dominates at 74% of payments, averaging 3.51 installments per purchase.",
              fig_to_div(fig)))

# ---------- 9. MoM growth ----------
df = q("queries/09_mom_revenue_growth.sql").dropna()
colors = [PALETTE["blue"] if v >= 0 else PALETTE["red"] for v in df["pct_mom_growth"]]
fig = go.Figure(go.Bar(x=df["month"], y=df["pct_mom_growth"], marker_color=colors))
fig.update_yaxes(title="MoM Growth %")
cards.append(("Q9 · Month-over-Month Revenue Growth",
              "Nov 2017 Black Friday spike (+52%) followed by a Dec correction (-27%); growth stabilizes in 2018.",
              fig_to_div(fig)))

# ---------- 10. RFM segmentation ----------
df = q("queries/10_rfm_segmentation.sql")
fig = go.Figure()
fig.add_trace(go.Bar(x=df["segment"], y=df["total_monetary"], name="Total Revenue (R$)",
                      marker_color=PALETTE["green"]))
fig.update_yaxes(title="Total Revenue (R$)")
cards.append(("Q10a · RFM Segment — Total Revenue",
              "Recent High-Value customers drive the most revenue; Lost/Churned still represents R$3.2M in past value.",
              fig_to_div(fig)))

fig = go.Figure()
fig.add_trace(go.Bar(x=df["segment"], y=df["num_customers"], name="Customers",
                      marker_color=PALETTE["magenta"]))
fig.update_yaxes(title="Number of Customers")
cards.append(("Q10b · RFM Segment — Customer Count",
              "Champions (repeat, high-value, recent) are the smallest but most loyal segment — best fit for a loyalty program.",
              fig_to_div(fig)))

con.close()

# ---------- Assemble HTML ----------
card_html = ""
for title, takeaway, div in cards:
    qnum, qtitle = title.split(" · ", 1)
    card_html += f"""
    <section class="card">
      <div class="card-header">
        <span class="qbadge">{qnum}</span>
        <h2>{qtitle}</h2>
        <p class="takeaway">{takeaway}</p>
      </div>
      <div class="chart">{div}</div>
    </section>
"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Olist E-Commerce Analytics Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #f5f6fa;
    --card-bg: #ffffff;
    --ink: #1f2430;
    --muted: #6b7280;
    --accent: #2E86AB;
    --border: #e6e8ee;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--ink);
  }}
  header {{
    background: linear-gradient(135deg, #1f2430 0%, #2E86AB 100%);
    color: white;
    padding: 56px 32px 40px;
    text-align: center;
  }}
  header h1 {{
    margin: 0 0 8px;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.02em;
  }}
  header p {{
    margin: 0;
    font-size: 1.05rem;
    opacity: 0.85;
    max-width: 640px;
    margin: 0 auto;
  }}
  main {{
    max-width: 1180px;
    margin: -28px auto 60px;
    padding: 0 24px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 24px;
  }}
  .card {{
    background: var(--card-bg);
    border-radius: 16px;
    border: 1px solid var(--border);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 8px 24px rgba(31,36,48,0.06);
    overflow: hidden;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
  }}
  .card:hover {{
    box-shadow: 0 4px 8px rgba(0,0,0,0.06), 0 16px 32px rgba(31,36,48,0.1);
    transform: translateY(-2px);
  }}
  .card-header {{
    padding: 20px 24px 4px;
    position: relative;
  }}
  .qbadge {{
    display: inline-block;
    background: var(--accent);
    color: white;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    padding: 3px 9px;
    border-radius: 999px;
    margin-bottom: 8px;
  }}
  .card-header h2 {{
    margin: 0 0 6px;
    font-size: 1.05rem;
    font-weight: 700;
  }}
  .takeaway {{
    margin: 0 0 8px;
    font-size: 0.88rem;
    color: var(--muted);
    line-height: 1.4;
  }}
  .chart {{
    padding: 0 8px 8px;
  }}
  footer {{
    text-align: center;
    padding: 24px;
    color: var(--muted);
    font-size: 0.85rem;
  }}
  footer a {{ color: var(--accent); }}
</style>
</head>
<body>
<header>
  <h1>Olist E-Commerce Analytics Dashboard</h1>
  <p>SQL business-case analysis of ~100k real Brazilian marketplace orders (2016-2018), built with DuckDB + Plotly.</p>
</header>
<main>
{card_html}
</main>
<footer>
  Data source: <a href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce" target="_blank">Olist Brazilian E-Commerce (Kaggle)</a>
  &middot; Full queries and writeup: <a href="README.md">README</a>
</footer>
</body>
</html>
"""

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard written to dashboard.html")
