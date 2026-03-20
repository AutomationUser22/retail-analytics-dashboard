# Retail Analytics Dashboard

Interactive BI dashboard built on a star schema data warehouse, powered by Streamlit and Plotly.

![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

## Live Demo

> **[Launch Dashboard on Streamlit Cloud](https://retail-analytics-dashboard-vinayak.streamlit.app/)**

## What This Does

Connects directly to the warehouse built by the [Retail Data Warehouse ETL Pipeline](https://github.com/AutomationUser22/retail-data-warehouse-etl) and provides 5 interactive analytics pages:

| Page | What It Shows | Business Question |
|------|---------------|-------------------|
| **Executive Summary** | KPIs with period-over-period deltas, revenue/profit trends, category & region breakdown | How is the business doing overall? |
| **Product Analytics** | Sub-category performance, discount vs margin scatter plot, top products | What should we sell more of? Where are we losing money? |
| **Customer Analytics** | Segment performance, segment×region heatmap, top customers, order frequency | Who are our best customers and where are they? |
| **Shipping & Operations** | Ship mode distribution, cost trends, efficiency metrics | Are we spending too much on shipping? |
| **Data Quality** | Row counts, null checks, FK integrity, pass/fail indicators | Can I trust this data? |

## Architecture

```
┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│   ETL Pipeline       │     │   SQLite Warehouse   │     │   Streamlit App      │
│   (retail-data-project)│──▶│   Star Schema        │────▶│   5 Dashboard Pages  │
│   Extract/Transform/ │     │   4 dims + 1 fact    │     │   Plotly Charts      │
│   Load/Quality       │     │   24 quality checks  │     │   Interactive Filters │
└──────────────────────┘     └──────────────────────┘     └──────────────────────┘
```

## Project Structure

```
├── app.py                        # Main entry point & landing page
├── pages/
│   ├── 1_📈_Executive_Summary.py  # KPIs, trends, breakdowns
│   ├── 2_📦_Product_Analytics.py  # Sub-category, discount impact
│   ├── 3_👥_Customer_Analytics.py # Segments, heatmap, top customers
│   ├── 4_🚚_Shipping_Operations.py # Ship mode analysis, cost trends
│   └── 5_🔍_Data_Quality.py      # Warehouse health monitoring
├── utils/
│   ├── data.py                   # SQL queries & data access layer
│   └── charts.py                 # Standardized Plotly chart builders
├── .streamlit/
│   └── config.toml               # Theme & server configuration
├── warehouse.db                  # Star schema warehouse (from Project 1)
├── requirements.txt
└── README.md
```

## Quick Start

```bash
# Clone
git clone https://github.com/AutomationUser22/retail-analytics-dashboard.git
cd retail-analytics-dashboard

# Install dependencies
pip install -r requirements.txt

# Generate the warehouse (if you don't have one)
# Option A: Copy from retail-data-warehouse-etl after running its pipeline
# Option B: Clone retail-data-warehouse-etl and run: python -m src.pipeline

# Launch the dashboard
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`.

## Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Select this repo → `app.py` as the main file
5. Click Deploy

The dashboard will be live at `https://your-app-name.streamlit.app` within minutes.

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Dashboard | Streamlit | Python-native, zero frontend code, built-in caching |
| Charts | Plotly | Interactive (hover, zoom, filter), publication quality |
| Data | SQLite | Direct connection to star schema warehouse |
| Styling | Custom theme | Consistent brand colors across all charts |

## Key Design Decisions

1. **Centralized data layer** (`utils/data.py`) — All SQL queries in one place, cached with `@st.cache_data`. No SQL scattered across page files.
2. **Standardized chart builders** (`utils/charts.py`) — Consistent colors, fonts, and layout across every visualization. Change the theme once, it updates everywhere.
3. **Date range filter on every page** — Every metric is time-sliceable. Period-over-period comparison on KPIs.
4. **Data quality as a first-class page** — Not an afterthought. Shows the warehouse is trustworthy before anyone looks at the analytics.

## Connection to retail-data-warehouse-etl

This dashboard reads directly from `warehouse.db` — the output of the ETL pipeline. If you rerun the pipeline with new data, the dashboard automatically reflects the updated warehouse on next page load. This mirrors the production pattern of a BI tool (QuickSight, Tableau) sitting on top of a data warehouse (Redshift, Snowflake).

## License

MIT
