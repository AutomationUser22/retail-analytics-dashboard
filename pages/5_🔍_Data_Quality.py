"""
Page 5 — Data Quality Monitor

Live data quality dashboard showing warehouse health:
table stats, null checks, FK integrity, and freshness.
"""

import streamlit as st

from utils.data import get_table_stats, get_null_report, get_fk_orphan_report

st.set_page_config(page_title="Data Quality", page_icon="🔍", layout="wide")

st.title("🔍 Data Quality Monitor")
st.markdown("---")

# ── Overall status ──
null_report = get_null_report()
fk_report = get_fk_orphan_report()

total_nulls = null_report["null_count"].sum()
total_orphans = fk_report["orphaned_rows"].sum()
all_clear = total_nulls == 0 and total_orphans == 0

if all_clear:
    st.success("✅ All data quality checks passed — warehouse is healthy.")
else:
    issues = []
    if total_nulls > 0:
        issues.append(f"{total_nulls} null values in critical columns")
    if total_orphans > 0:
        issues.append(f"{total_orphans} orphaned foreign keys")
    st.error(f"⚠️ Issues detected: {'; '.join(issues)}")

st.markdown("---")

# ── Table Statistics ──
st.markdown("### Warehouse Table Statistics")

table_stats = get_table_stats()
cols = st.columns(len(table_stats))

for i, (_, row) in enumerate(table_stats.iterrows()):
    with cols[i]:
        table_type = "Dimension" if row["table"].startswith("dim_") else "Fact"
        st.metric(
            row["table"],
            f"{row['row_count']:,} rows",
        )
        st.caption(f"Type: {table_type}")

st.markdown("---")

# ── Null Report ──
st.markdown("### Completeness Check — Null Values in fact_sales")
st.caption("Critical columns should have zero null values.")

# Style the null report
def highlight_nulls(row):
    if row["null_count"] > 0:
        return ["background-color: #FFEBEE"] * len(row)
    return ["background-color: #E8F5E9"] * len(row)

styled_nulls = null_report.style.apply(highlight_nulls, axis=1).format({
    "total_rows": "{:,}",
    "null_count": "{:,}",
    "null_pct": "{:.2f}%",
})
st.dataframe(null_report, use_container_width=True, hide_index=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("Columns Checked", len(null_report))
with col2:
    passed = len(null_report[null_report["null_count"] == 0])
    st.metric("Columns with Zero Nulls", f"{passed}/{len(null_report)}")

st.markdown("---")

# ── Referential Integrity ──
st.markdown("### Referential Integrity — Foreign Key Validation")
st.caption("Every foreign key in fact_sales should resolve to a valid dimension record.")

st.dataframe(fk_report, use_container_width=True, hide_index=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("FK Relationships Checked", len(fk_report))
with col2:
    fk_passed = len(fk_report[fk_report["orphaned_rows"] == 0])
    st.metric("Valid Relationships", f"{fk_passed}/{len(fk_report)}")

st.markdown("---")

# ── Quality Summary ──
st.markdown("### Quality Summary")

total_checks = len(null_report) + len(fk_report)
total_passed = passed + fk_passed

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Checks Run", total_checks)
with col2:
    st.metric("Checks Passed", f"{total_passed}/{total_checks}")
with col3:
    pct = total_passed / total_checks * 100 if total_checks > 0 else 0
    st.metric("Pass Rate", f"{pct:.0f}%")

if all_clear:
    st.balloons()
