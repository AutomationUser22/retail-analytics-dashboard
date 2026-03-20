"""
Page 2 — Product Analytics

Sub-category performance, discount impact analysis, and top products.
"""

import streamlit as st
from datetime import datetime

from utils.data import (
    get_subcategory_performance, get_discount_impact,
    get_top_products, get_date_range,
)
from utils.charts import (
    bar_chart, scatter_chart, CATEGORY_COLORS,
)

st.set_page_config(page_title="Product Analytics", page_icon="📦", layout="wide")

st.title("📦 Product Analytics")
st.markdown("---")

# ── Date range filter ──
min_date, max_date = get_date_range()
min_dt = datetime.strptime(min_date, "%Y-%m-%d")
max_dt = datetime.strptime(max_date, "%Y-%m-%d")

col_start, col_end = st.columns(2)
with col_start:
    start_date = st.date_input("Start Date", value=min_dt, min_value=min_dt, max_value=max_dt)
with col_end:
    end_date = st.date_input("End Date", value=max_dt, min_value=min_dt, max_value=max_dt)

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

# ── Category filter ──
category_filter = st.multiselect(
    "Filter by Category",
    options=["Technology", "Furniture", "Office Supplies"],
    default=["Technology", "Furniture", "Office Supplies"],
)

# ── Sub-category Performance ──
st.markdown("### Sub-Category Performance")

subcat = get_subcategory_performance(start_str, end_str)
if category_filter:
    subcat = subcat[subcat["category"].isin(category_filter)]

if not subcat.empty:
    fig = bar_chart(
        subcat.sort_values("revenue", ascending=True),
        x="sub_category", y="revenue",
        color="category", orientation="h",
        color_map=CATEGORY_COLORS,
        title="Revenue by Sub-Category",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    with st.expander("View Detailed Data"):
        st.dataframe(
            subcat[["category", "sub_category", "revenue", "profit",
                    "margin_pct", "avg_discount_pct", "units_sold", "orders"]]
            .sort_values("revenue", ascending=False)
            .reset_index(drop=True),
            use_container_width=True,
        )

st.markdown("---")

# ── Discount Impact ──
st.markdown("### Discount vs Profit Margin")
st.caption("Each bubble is a sub-category. Larger bubble = more revenue. "
           "Products in the bottom-right are losing money from heavy discounting.")

discount = get_discount_impact(start_str, end_str)
if category_filter:
    # Need to get category info from subcategory data
    cat_map = subcat.set_index("sub_category")["category"].to_dict()
    discount["category"] = discount["sub_category"].map(cat_map)
    discount = discount[discount["category"].isin(category_filter)]

if not discount.empty:
    fig = scatter_chart(
        discount,
        x="avg_discount_pct", y="margin_pct",
        size="revenue", text="sub_category",
        title="", height=450,
    )
    fig.update_layout(
        xaxis_title="Average Discount %",
        yaxis_title="Profit Margin %",
    )
    # Add reference lines
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5,
                  annotation_text="Break-even")
    fig.add_vline(x=discount["avg_discount_pct"].median(), line_dash="dash",
                  line_color="gray", opacity=0.3)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Top Products ──
st.markdown("### Top 10 Products by Revenue")

top_products = get_top_products(start_str, end_str, limit=10)
if category_filter:
    top_products = top_products[top_products["category"].isin(category_filter)].head(10)

if not top_products.empty:
    fig = bar_chart(
        top_products,
        x="product_name", y="revenue",
        color="category",
        color_map=CATEGORY_COLORS,
        title="",
        height=400,
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
