from pathlib import Path
import subprocess
import sys
import pandas as pd
import streamlit as st

from src.analytics import build_kpis, aggregate_daily_revenue, aggregate_by_category, aggregate_by_region
from src.visualization import revenue_trend_chart, category_chart, region_heatmap

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data/processed"
CLEAN_PATH = DATA_DIR / "clean_orders.csv"

st.set_page_config(page_title="DataPulse Analytics", page_icon="📊", layout="wide")
st.title("📊 DataPulse — Data Engineering & Analytics")
st.caption("A mini production-style ETL pipeline with quality checks, transformations, and interactive analytics.")

@st.cache_data
def load_processed_data(path: str, modified_time: float):
    return pd.read_csv(path, parse_dates=["order_date"])

if not CLEAN_PATH.exists():
    with st.spinner("Running the ETL pipeline for the first time..."):
        result = subprocess.run(
            [sys.executable, str(ROOT / "run_pipeline.py")],
            cwd=ROOT, capture_output=True, text=True
        )
    if result.returncode != 0:
        st.error("The ETL pipeline failed. Check the terminal output or reports/pipeline.log.")
        st.code(result.stderr or result.stdout)
        st.stop()

if not CLEAN_PATH.exists():
    st.error("No processed data found. Run `python run_pipeline.py` from the project folder.")
    st.stop()

df = load_processed_data(str(CLEAN_PATH), CLEAN_PATH.stat().st_mtime)
if df.empty:
    st.warning("The pipeline produced no valid rows. Check data/processed/rejected_rows.csv.")
    st.stop()

# Defensive typing for CSV-loaded columns.
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
for col in ["region", "category", "product", "customer_id"]:
    df[col] = df[col].fillna("Unknown").astype(str)

st.sidebar.header("Filters")
min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()
date_range = st.sidebar.date_input("Order date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
regions = sorted(df["region"].unique().tolist())
categories = sorted(df["category"].unique().tolist())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

filtered = df.copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[filtered["order_date"].dt.date.between(start_date, end_date)]
if selected_regions:
    filtered = filtered[filtered["region"].isin(selected_regions)]
else:
    filtered = filtered.iloc[0:0]
if selected_categories:
    filtered = filtered[filtered["category"].isin(selected_categories)]
else:
    filtered = filtered.iloc[0:0]

kpis = build_kpis(filtered)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Orders", f'{kpis["orders"]:,}')
c2.metric("Net revenue", f'₹{kpis["revenue"]:,.2f}')
c3.metric("Customers", f'{kpis["customers"]:,}')
c4.metric("Avg. order value", f'₹{kpis["avg_order_value"]:,.2f}')
c5.metric("Units sold", f'{kpis["units_sold"]:,}')

left, right = st.columns(2)
with left:
    st.pyplot(revenue_trend_chart(aggregate_daily_revenue(filtered)), clear_figure=True)
with right:
    st.pyplot(category_chart(aggregate_by_category(filtered)), clear_figure=True)

st.pyplot(region_heatmap(filtered), clear_figure=True)

st.subheader("Top products")
if filtered.empty:
    st.info("No rows match the selected filters.")
else:
    top_products = (filtered.groupby("product", as_index=False)
                    .agg(net_revenue=("net_revenue", "sum"), units_sold=("quantity", "sum"))
                    .sort_values("net_revenue", ascending=False).head(10))
    st.dataframe(top_products, use_container_width=True, hide_index=True)

with st.expander("Data quality report"):
    quality_path = DATA_DIR / "quality_report.csv"
    rejected_path = DATA_DIR / "rejected_rows.csv"
    if quality_path.exists():
        st.dataframe(pd.read_csv(quality_path), use_container_width=True, hide_index=True)
    if rejected_path.exists():
        rejected = pd.read_csv(rejected_path)
        st.write(f"Rejected rows: {len(rejected)}")
        if not rejected.empty:
            st.dataframe(rejected, use_container_width=True, hide_index=True)

st.subheader("Filtered records")
st.dataframe(filtered, use_container_width=True, hide_index=True)
st.download_button(
    "Download filtered CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="datapulse_filtered_orders.csv",
    mime="text/csv",
)
st.caption("Built with Pandas • NumPy • Matplotlib • Seaborn • Streamlit")
