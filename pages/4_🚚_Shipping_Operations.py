"""
Page 4 — Shipping & Operations

Shipping mode analysis, cost trends, and efficiency metrics.
"""

import streamlit as st
from datetime import datetime

from utils.data import get_shipping_analysis, get_shipping_trend, get_date_range
from utils.charts import bar_chart, stacked_bar, pie_chart, line_chart

st.set_page_config(page_title="Shipping & Operations", page_icon="🚚", layout="wide")

st.title("🚚 Shipping & Operations")
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

# ── Shipping KPIs ──
shipping = get_shipping_analysis(start_str, end_str)

if not shipping.empty:
    total_shipping = shipping["total_shipping_cost"].sum()
    total_revenue = shipping["revenue"].sum()
    total_orders = shipping["orders"].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Shipping Cost", f"${total_shipping:,.0f}")
    with col2:
        st.metric("Shipping % of Revenue", f"{total_shipping/total_revenue*100:.1f}%")
    with col3:
        st.metric("Avg Shipping/Order Line", f"${shipping['avg_shipping_cost'].mean():.2f}")
    with col4:
        st.metric("Total Order Lines", f"{shipping['order_lines'].sum():,}")

    st.markdown("---")

    # ── Mode breakdown ──
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Order Distribution by Ship Mode")
        fig = pie_chart(shipping, values="order_lines", names="ship_mode",
                        height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### Revenue by Ship Mode")
        fig = bar_chart(shipping, x="ship_mode", y="revenue",
                        title="", height=380)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Detailed metrics table ──
    st.markdown("### Shipping Mode Details")
    display_cols = shipping[["ship_mode", "ship_category", "avg_ship_days",
                             "order_lines", "orders", "revenue",
                             "total_shipping_cost", "avg_shipping_cost",
                             "shipping_pct_revenue"]].copy()
    display_cols.columns = ["Ship Mode", "Category", "Avg Days", "Order Lines",
                            "Orders", "Revenue ($)", "Total Ship Cost ($)",
                            "Avg Ship Cost ($)", "Ship % of Revenue"]
    st.dataframe(display_cols, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Shipping cost efficiency ──
    st.markdown("### Shipping Cost vs Revenue by Mode")
    st.caption("Higher revenue with lower shipping cost % indicates better efficiency.")

    fig = bar_chart(shipping, x="ship_mode", y="shipping_pct_revenue",
                    title="", height=350)
    fig.update_layout(yaxis_title="Shipping Cost as % of Revenue")
    fig.update_traces(marker_color=["#00C9A7" if v < 2.5 else "#F5A623" if v < 3.5 else "#E74C3C"
                                     for v in shipping["shipping_pct_revenue"]])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Monthly shipping trend ──
    st.markdown("### Monthly Shipping Cost Trend")

    trend = get_shipping_trend(start_str, end_str)
    if not trend.empty:
        fig = stacked_bar(trend, x="period", y="shipping_cost", color="ship_mode",
                          title="", height=400)
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Shipping Cost ($)",
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No shipping data available for the selected date range.")
