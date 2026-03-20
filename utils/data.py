"""
Database Utility — Central data access layer for the dashboard.

All SQL queries go through this module. Each function runs a query
against the star schema warehouse and returns a pandas DataFrame.
Uses Streamlit's caching to avoid re-querying on every interaction.
"""

import sqlite3
import os

import pandas as pd
import streamlit as st


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "warehouse.db")


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection to the warehouse."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# ══════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY QUERIES
# ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_kpis(start_date: str, end_date: str) -> dict:
    """Get headline KPIs for the selected date range."""
    con = get_connection()
    row = pd.read_sql(f"""
        SELECT
            ROUND(SUM(f.sales_amount), 2)                          AS total_revenue,
            ROUND(SUM(f.profit), 2)                                AS total_profit,
            ROUND(SUM(f.profit) / NULLIF(SUM(f.sales_amount), 0) * 100, 1) AS profit_margin,
            COUNT(DISTINCT f.order_id)                             AS total_orders,
            ROUND(SUM(f.sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS avg_order_value,
            SUM(f.quantity)                                        AS units_sold,
            COUNT(DISTINCT f.customer_key)                         AS active_customers
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
    """, con).iloc[0]
    con.close()
    return row.to_dict()


@st.cache_data(ttl=300)
def get_previous_kpis(start_date: str, end_date: str) -> dict:
    """Get KPIs for the previous period (for comparison deltas)."""
    con = get_connection()

    # Calculate the length of the current period
    days_diff = pd.read_sql(f"""
        SELECT JULIANDAY('{end_date}') - JULIANDAY('{start_date}') AS days
    """, con).iloc[0]["days"]

    prev_end = start_date
    prev_start_row = pd.read_sql(f"""
        SELECT DATE('{start_date}', '-{int(days_diff)} days') AS prev_start
    """, con).iloc[0]
    prev_start = prev_start_row["prev_start"]

    row = pd.read_sql(f"""
        SELECT
            ROUND(SUM(f.sales_amount), 2)                          AS total_revenue,
            ROUND(SUM(f.profit), 2)                                AS total_profit,
            ROUND(SUM(f.profit) / NULLIF(SUM(f.sales_amount), 0) * 100, 1) AS profit_margin,
            COUNT(DISTINCT f.order_id)                             AS total_orders,
            ROUND(SUM(f.sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS avg_order_value,
            SUM(f.quantity)                                        AS units_sold,
            COUNT(DISTINCT f.customer_key)                         AS active_customers
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{prev_start}' AND '{prev_end}'
    """, con).iloc[0]
    con.close()
    return row.to_dict()


@st.cache_data(ttl=300)
def get_monthly_revenue(start_date: str, end_date: str) -> pd.DataFrame:
    """Monthly revenue and profit trend."""
    con = get_connection()
    df = pd.read_sql(f"""
        SELECT d.year, d.month, d.month_name,
               ROUND(SUM(f.sales_amount), 2) AS revenue,
               ROUND(SUM(f.profit), 2) AS profit,
               ROUND(SUM(f.profit) / NULLIF(SUM(f.sales_amount), 0) * 100, 1) AS margin_pct,
               COUNT(DISTINCT f.order_id) AS orders
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month
    """, con)
    con.close()
    df["period"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
    return df


@st.cache_data(ttl=300)
def get_revenue_by_category(start_date: str, end_date: str) -> pd.DataFrame:
    """Revenue breakdown by product category."""
    con = get_connection()
    df = pd.read_sql(f"""
        SELECT p.category,
               ROUND(SUM(f.sales_amount), 2) AS revenue,
               ROUND(SUM(f.profit), 2) AS profit
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY p.category
        ORDER BY revenue DESC
    """, con)
    con.close()
    return df


@st.cache_data(ttl=300)
def get_revenue_by_region(start_date: str, end_date: str) -> pd.DataFrame:
    """Revenue breakdown by region."""
    con = get_connection()
    df = pd.read_sql(f"""
        SELECT c.region,
               ROUND(SUM(f.sales_amount), 2) AS revenue,
               ROUND(SUM(f.profit), 2) AS profit,
               COUNT(DISTINCT f.order_id) AS orders
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY c.region
        ORDER BY revenue DESC
    """, con)
    con.close()
    return df


# ══════════════════════════════════════════════════════════════
# PRODUCT ANALYTICS QUERIES
# ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_subcategory_performance(start_date: str, end_date: str) -> pd.DataFrame:
    """Revenue and profit by sub-category."""
    con = get_connection()
    df = pd.read_sql(f"""
        SELECT p.category, p.sub_category,
               ROUND(SUM(f.sales_amount), 2) AS revenue,
               ROUND(SUM(f.profit), 2) AS profit,
               ROUND(SUM(f.profit) / NULLIF(SUM(f.sales_amount), 0) * 100, 1) AS margin_pct,
               ROUND(AVG(f.discount) * 100, 1) AS avg_discount_pct,
               SUM(f.quantity) AS units_sold,
               COUNT(DISTINCT f.order_id) AS orders
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY p.category, p.sub_category
        ORDER BY revenue DESC
    """, con)
    con.close()
    return df


@st.cache_data(ttl=300)
def get_discount_impact(start_date: str, end_date: str) -> pd.DataFrame:
    """Discount rate vs profit margin by sub-category."""
    con = get_connection()
    df = pd.read_sql(f"""
        SELECT p.sub_category,
               ROUND(AVG(f.discount) * 100, 1) AS avg_discount_pct,
               ROUND(SUM(f.profit) / NULLIF(SUM(f.sales_amount), 0) * 100, 1) AS margin_pct,
               ROUND(SUM(f.sales_amount), 2) AS revenue
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY p.sub_category
    """, con)
    con.close()
    return df


@st.cache_data(ttl=300)
def get_top_products(start_date: str, end_date: str, limit: int = 10) -> pd.DataFrame:
    """Top products by revenue."""
    con = get_connection()
    df = pd.read_sql(f"""
        SELECT p.product_name, p.category, p.sub_category,
               ROUND(SUM(f.sales_amount), 2) AS revenue,
               ROUND(SUM(f.profit), 2) AS profit,
               SUM(f.quantity) AS units_sold
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY p.product_name, p.category, p.sub_category
        ORDER BY revenue DESC
        LIMIT {limit}
    """, con)
    con.close()
    return df


# ══════════════════════════════════════════════════════════════
# CUSTOMER ANALYTICS QUERIES
# ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_segment_performance(start_date: str, end_date: str) -> pd.DataFrame:
    """Revenue by customer segment."""
    con = get_connection()
    df = pd.read_sql(f"""
        SELECT c.segment,
               ROUND(SUM(f.sales_amount), 2) AS revenue,
               ROUND(SUM(f.profit), 2) AS profit,
               COUNT(DISTINCT c.customer_key) AS customers,
               COUNT(DISTINCT f.order_id) AS orders,
               ROUND(SUM(f.sales_amount) / NULLIF(COUNT(DISTINCT c.customer_key), 0), 2) AS revenue_per_customer
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY c.segment
        ORDER BY revenue DESC
    """, con)
    con.close()
    return df


@st.cache_data(ttl=300)
def get_segment_region_heatmap(start_date: str, end_date: str) -> pd.DataFrame:
    """Revenue by segment × region for heatmap."""
    con = get_connection()
    df = pd.read_sql(f"""
        SELECT c.segment, c.region,
               ROUND(SUM(f.sales_amount), 2) AS revenue
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY c.segment, c.region
    """, con)
    con.close()
    return df


@st.cache_data(ttl=300)
def get_top_customers(start_date: str, end_date: str, limit: int = 10) -> pd.DataFrame:
    """Top customers by lifetime value."""
    con = get_connection()
    df = pd.read_sql(f"""
        SELECT c.customer_name, c.segment, c.region, c.city,
               ROUND(SUM(f.sales_amount), 2) AS lifetime_value,
               ROUND(SUM(f.profit), 2) AS total_profit,
               COUNT(DISTINCT f.order_id) AS total_orders,
               ROUND(AVG(f.sales_amount), 2) AS avg_order_value
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY c.customer_name, c.segment, c.region, c.city
        ORDER BY lifetime_value DESC
        LIMIT {limit}
    """, con)
    con.close()
    return df


@st.cache_data(ttl=300)
def get_customer_order_distribution(start_date: str, end_date: str) -> pd.DataFrame:
    """Distribution of order frequency per customer."""
    con = get_connection()
    df = pd.read_sql(f"""
        WITH customer_orders AS (
            SELECT c.customer_key,
                   COUNT(DISTINCT f.order_id) AS order_count
            FROM fact_sales f
            JOIN dim_customer c ON f.customer_key = c.customer_key
            JOIN dim_date d ON f.date_key = d.date_key
            WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY c.customer_key
        )
        SELECT order_count, COUNT(*) AS num_customers
        FROM customer_orders
        GROUP BY order_count
        ORDER BY order_count
    """, con)
    con.close()
    return df


# ══════════════════════════════════════════════════════════════
# SHIPPING & OPERATIONS QUERIES
# ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_shipping_analysis(start_date: str, end_date: str) -> pd.DataFrame:
    """Shipping mode performance analysis."""
    con = get_connection()
    df = pd.read_sql(f"""
        SELECT sm.ship_mode, sm.ship_category, sm.avg_ship_days,
               COUNT(*) AS order_lines,
               COUNT(DISTINCT f.order_id) AS orders,
               ROUND(SUM(f.sales_amount), 2) AS revenue,
               ROUND(SUM(f.shipping_cost), 2) AS total_shipping_cost,
               ROUND(AVG(f.shipping_cost), 2) AS avg_shipping_cost,
               ROUND(SUM(f.shipping_cost) / NULLIF(SUM(f.sales_amount), 0) * 100, 1) AS shipping_pct_revenue
        FROM fact_sales f
        JOIN dim_ship_mode sm ON f.ship_mode_key = sm.ship_mode_key
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY sm.ship_mode, sm.ship_category, sm.avg_ship_days
        ORDER BY order_lines DESC
    """, con)
    con.close()
    return df


@st.cache_data(ttl=300)
def get_shipping_trend(start_date: str, end_date: str) -> pd.DataFrame:
    """Monthly shipping cost trend by mode."""
    con = get_connection()
    df = pd.read_sql(f"""
        SELECT d.year, d.month, sm.ship_mode,
               ROUND(SUM(f.shipping_cost), 2) AS shipping_cost,
               COUNT(DISTINCT f.order_id) AS orders
        FROM fact_sales f
        JOIN dim_ship_mode sm ON f.ship_mode_key = sm.ship_mode_key
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.full_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY d.year, d.month, sm.ship_mode
        ORDER BY d.year, d.month
    """, con)
    con.close()
    df["period"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
    return df


# ══════════════════════════════════════════════════════════════
# DATA QUALITY QUERIES
# ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_table_stats() -> pd.DataFrame:
    """Row counts and basic stats for all warehouse tables."""
    con = get_connection()
    tables = ["dim_date", "dim_customer", "dim_product", "dim_ship_mode", "fact_sales"]
    stats = []
    for table in tables:
        row_count = pd.read_sql(f"SELECT COUNT(*) AS cnt FROM {table}", con).iloc[0]["cnt"]
        stats.append({"table": table, "row_count": int(row_count)})
    con.close()
    return pd.DataFrame(stats)


@st.cache_data(ttl=300)
def get_null_report() -> pd.DataFrame:
    """Null counts for critical columns in fact_sales."""
    con = get_connection()
    critical_cols = ["sale_key", "order_id", "customer_key", "product_key",
                     "date_key", "ship_mode_key", "sales_amount", "profit"]
    results = []
    for col in critical_cols:
        total = pd.read_sql(f"SELECT COUNT(*) AS cnt FROM fact_sales", con).iloc[0]["cnt"]
        nulls = pd.read_sql(f"SELECT COUNT(*) AS cnt FROM fact_sales WHERE {col} IS NULL", con).iloc[0]["cnt"]
        results.append({
            "column": col,
            "total_rows": int(total),
            "null_count": int(nulls),
            "null_pct": round(nulls / total * 100, 2) if total > 0 else 0,
        })
    con.close()
    return pd.DataFrame(results)


@st.cache_data(ttl=300)
def get_fk_orphan_report() -> pd.DataFrame:
    """Check for orphaned foreign keys in fact_sales."""
    con = get_connection()
    fk_checks = [
        ("customer_key", "dim_customer", "customer_key"),
        ("product_key", "dim_product", "product_key"),
        ("date_key", "dim_date", "date_key"),
        ("ship_date_key", "dim_date", "date_key"),
        ("ship_mode_key", "dim_ship_mode", "ship_mode_key"),
    ]
    results = []
    for fk_col, dim_table, dim_pk in fk_checks:
        orphans = pd.read_sql(f"""
            SELECT COUNT(*) AS cnt
            FROM fact_sales f
            LEFT JOIN {dim_table} d ON f.{fk_col} = d.{dim_pk}
            WHERE d.{dim_pk} IS NULL AND f.{fk_col} IS NOT NULL
        """, con).iloc[0]["cnt"]
        results.append({
            "foreign_key": f"fact_sales.{fk_col}",
            "references": f"{dim_table}.{dim_pk}",
            "orphaned_rows": int(orphans),
            "status": "PASS ✓" if orphans == 0 else f"FAIL ✗ ({orphans})",
        })
    con.close()
    return pd.DataFrame(results)


@st.cache_data(ttl=300)
def get_date_range() -> tuple:
    """Get the min and max dates in the warehouse."""
    con = get_connection()
    row = pd.read_sql("""
        SELECT MIN(d.full_date) AS min_date, MAX(d.full_date) AS max_date
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
    """, con).iloc[0]
    con.close()
    return row["min_date"], row["max_date"]
