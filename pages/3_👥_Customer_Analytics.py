"""
Page 3 — Customer Analytics

Segmentation, regional heatmap, top customers, order frequency.
"""

import streamlit as st
from datetime import datetime

from utils.data import (
    get_segment_performance, get_segment_region_heatmap,
    get_top_customers, get_customer_order_distribution, get_date_range,
)
from utils.charts import (
    bar_chart, pie_chart, heatmap, SEGMENT_COLORS, REGION_COLORS,
)

st.set_page_config(page_title="Customer Analytics", page_icon="👥", layout="wide")

st.title("👥 Customer Analytics")
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

# ── Segment KPIs ──
st.markdown("### Customer Segment Performance")

segment = get_segment_performance(start_str, end_str)
if not segment.empty:
    cols = st.columns(len(segment))
    for i, (_, row) in enumerate(segment.iterrows()):
        with cols[i]:
            st.metric(row["segment"], f"${row['revenue']:,.0f}")
            st.caption(
                f"{row['customers']:,.0f} customers · "
                f"{row['orders']:,.0f} orders · "
                f"${row['revenue_per_customer']:,.0f}/customer"
            )

st.markdown("---")

# ── Segment breakdown & Heatmap ──
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### Revenue by Segment")
    if not segment.empty:
        fig = pie_chart(segment, values="revenue", names="segment",
                        color_map=SEGMENT_COLORS, height=380)
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### Segment × Region Revenue")
    heatmap_data = get_segment_region_heatmap(start_str, end_str)
    if not heatmap_data.empty:
        fig = heatmap(heatmap_data, x="region", y="segment",
                      values="revenue", height=380)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Top Customers ──
st.markdown("### Top 10 Customers by Lifetime Value")

top_customers = get_top_customers(start_str, end_str, limit=10)
if not top_customers.empty:
    fig = bar_chart(
        top_customers,
        x="customer_name", y="lifetime_value",
        color="segment",
        color_map=SEGMENT_COLORS,
        title="",
        height=400,
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Detailed Customer Data"):
        st.dataframe(
            top_customers[["customer_name", "segment", "region", "city",
                          "lifetime_value", "total_profit", "total_orders", "avg_order_value"]]
            .reset_index(drop=True),
            use_container_width=True,
        )

st.markdown("---")

# ── Order Frequency Distribution ──
st.markdown("### Order Frequency Distribution")
st.caption("How many orders do customers typically place?")

order_dist = get_customer_order_distribution(start_str, end_str)
if not order_dist.empty:
    fig = bar_chart(
        order_dist,
        x="order_count", y="num_customers",
        title="",
        height=350,
    )
    fig.update_layout(
        xaxis_title="Number of Orders",
        yaxis_title="Number of Customers",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Summary stats
    total_customers = order_dist["num_customers"].sum()
    one_time = order_dist[order_dist["order_count"] == 1]["num_customers"].sum()
    repeat = total_customers - one_time

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Active Customers", f"{total_customers:,}")
    with col2:
        st.metric("One-Time Buyers", f"{one_time:,} ({one_time/total_customers*100:.1f}%)")
    with col3:
        st.metric("Repeat Buyers", f"{repeat:,} ({repeat/total_customers*100:.1f}%)")
