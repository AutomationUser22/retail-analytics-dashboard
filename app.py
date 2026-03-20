"""
Retail Data Warehouse — BI Dashboard

Main entry point. Run with: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar branding ──
st.sidebar.markdown("## 📊 Retail Analytics")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "Interactive dashboard built on a star schema warehouse. "
    "Select a page from the navigation above."
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data Source:** Retail Data Warehouse  \n"
    "**Schema:** Star (Kimball)  \n"
    "**Tables:** 4 dimensions + 1 fact"
)

# ── Landing page ──
st.title("📊 Retail Analytics Dashboard")
st.markdown("---")

st.markdown("""
### Welcome

This dashboard provides interactive analytics on top of a **star schema data warehouse**
built by the [Retail Data Warehouse ETL Pipeline](https://github.com/09vinayak/retail-data-warehouse-etl).

**Navigate using the sidebar** to explore:

| Page | What It Shows |
|------|---------------|
| **Executive Summary** | KPIs, revenue trends, category & region breakdown |
| **Product Analytics** | Sub-category performance, discount impact, top products |
| **Customer Analytics** | Segmentation, regional heatmap, top customers, order frequency |
| **Shipping & Operations** | Shipping mode analysis, cost trends, efficiency metrics |
| **Data Quality** | Warehouse health — row counts, null checks, FK integrity |

### Architecture

```
Raw CSV → Extract → Transform (Star Schema) → Load (SQLite) → This Dashboard
                                                    ↑
                                              4 Dimensions + 1 Fact Table
                                              24 Automated Quality Checks
```
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Dimension Tables", "4")
with col2:
    st.metric("Fact Table", "1")
with col3:
    st.metric("Quality Checks", "24/24 ✓")
