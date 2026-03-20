"""
Page 1 — Executive Summary

KPI cards with period-over-period comparison, revenue trend,
category breakdown, and regional performance.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.data import (
    get_kpis, get_previous_kpis, get_monthly_revenue,
    get_revenue_by_category, get_revenue_by_region, get_date_range,
)
from utils.charts import (
    line_chart, bar_chart, pie_chart, CATEGORY_COLORS, REGION_COLORS,
)

st.set_page_config(page_title="Executive Summary", page_icon="📈", layout="wide")

st.title("📈 Executive Summary")
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

# ── KPI Cards ──
st.markdown("### Key Performance Indicators")

kpis = get_kpis(start_str, end_str)
prev_kpis = get_previous_kpis(start_str, end_str)


def calc_delta(current, previous):
    if previous and previous != 0:
        return f"{((current - previous) / abs(previous)) * 100:+.1f}%"
    return None


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Revenue",
        f"${kpis['total_revenue']:,.0f}",
        delta=calc_delta(kpis["total_revenue"], prev_kpis.get("total_revenue")),
    )
with col2:
    st.metric(
        "Total Profit",
        f"${kpis['total_profit']:,.0f}",
        delta=calc_delta(kpis["total_profit"], prev_kpis.get("total_profit")),
    )
with col3:
    st.metric(
        "Profit Margin",
        f"{kpis['profit_margin']}%",
        delta=calc_delta(kpis["profit_margin"], prev_kpis.get("profit_margin")),
    )
with col4:
    st.metric(
        "Total Orders",
        f"{kpis['total_orders']:,.0f}",
        delta=calc_delta(kpis["total_orders"], prev_kpis.get("total_orders")),
    )
with col5:
    st.metric(
        "Avg Order Value",
        f"${kpis['avg_order_value']:,.0f}",
        delta=calc_delta(kpis["avg_order_value"], prev_kpis.get("avg_order_value")),
    )

st.markdown("---")

# ── Revenue & Profit Trend ──
st.markdown("### Monthly Revenue & Profit Trend")

monthly = get_monthly_revenue(start_str, end_str)
if not monthly.empty:
    fig = line_chart(monthly, x="period", y="revenue", y2="profit",
                     title="", height=400)
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue ($)",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for the selected date range.")

# ── Category & Region breakdown ──
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### Revenue by Category")
    cat_data = get_revenue_by_category(start_str, end_str)
    if not cat_data.empty:
        fig = pie_chart(cat_data, values="revenue", names="category",
                        color_map=CATEGORY_COLORS, height=350)
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### Revenue by Region")
    region_data = get_revenue_by_region(start_str, end_str)
    if not region_data.empty:
        fig = bar_chart(region_data, x="region", y="revenue",
                        color="region", color_map=REGION_COLORS, height=350)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ── Margin trend ──
st.markdown("### Profit Margin Trend")
if not monthly.empty:
    fig = line_chart(monthly, x="period", y="margin_pct",
                     title="", height=300)
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Margin %",
    )
    fig.update_traces(line=dict(color="#00C9A7"))
    st.plotly_chart(fig, use_container_width=True)
