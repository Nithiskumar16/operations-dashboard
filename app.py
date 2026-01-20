import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Operations Revenue Dashboard", layout="wide")
st.title("📊 Operations Revenue Dashboard")

# -----------------------------
# MANUAL MONTHLY TARGET
# -----------------------------
TOTAL_TARGET = 80_000_000  # 8 Cr

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# -----------------------------
# COLUMN VALIDATION
# -----------------------------
required_columns = [
    "VNO","Month","Week","Branch","Bill Amount",
    "BILL TYPE","Act. Weight(Main)","Load Type",
    "Consignment Freight Amount"
]

missing = [c for c in required_columns if c not in df.columns]
if missing:
    st.error("Missing columns in Excel")
    st.write(missing)
    st.stop()

# -----------------------------
# FILTERS
# -----------------------------
st.sidebar.header("Filters")

month = st.sidebar.multiselect(
    "Month",
    sorted(df["Month"].unique()),
    default=sorted(df["Month"].unique())
)

branch = st.sidebar.multiselect(
    "Branch",
    sorted(df["Branch"].unique()),
    default=sorted(df["Branch"].unique())
)

filtered = df[
    (df["Month"].isin(month)) &
    (df["Branch"].isin(branch))
]

# -----------------------------
# TARGET VS ACHIEVED
# -----------------------------
achieved = filtered["Bill Amount"].sum()
achievement_pct = (achieved / TOTAL_TARGET * 100) if TOTAL_TARGET else 0

c1, c2, c3 = st.columns(3)
c1.metric("🎯 Monthly Target", f"₹ {TOTAL_TARGET/1e7:.2f} Cr")
c2.metric("✅ Achieved Revenue", f"₹ {achieved/1e7:.2f} Cr")
c3.metric("📈 Achievement %", f"{achievement_pct:.1f}%")

# -----------------------------
# WEEK-WISE MOVEMENTS
# -----------------------------
st.subheader("🚚 Week-wise Movements (Branch-wise)")

mov = (
    filtered
    .groupby(["Week","Branch"])["VNO"]
    .nunique()
    .reset_index(name="No of Movements")
)

st.plotly_chart(
    px.line(mov, x="Week", y="No of Movements", color="Branch", markers=True),
    use_container_width=True
)

# -----------------------------
# BILLING STATUS
# -----------------------------
st.subheader("💰 Billing Status")

freight = filtered[
    (filtered["BILL TYPE"].str.lower()=="freight") &
    (filtered["Bill Amount"]>0)
]["Bill Amount"].sum()

non_freight = filtered[
    (filtered["BILL TYPE"].str.lower()!="freight") &
    (filtered["Bill Amount"]>0)
]["Bill Amount"].sum()

unbilled = filtered[
    filtered["Bill Amount"].fillna(0)==0
]["Consignment Freight Amount"].sum()

b1, b2, b3 = st.columns(3)
b1.metric("Freight Billed", f"₹ {freight/1e7:.2f} Cr")
b2.metric("Non-Freight Billed", f"₹ {non_freight/1e7:.2f} Cr")
b3.metric("Unbilled Amount", f"₹ {unbilled/1e7:.2f} Cr")

# -----------------------------
# BAG vs BULK TONNAGE
# -----------------------------
st.subheader("⚖️ Bag vs Bulk Tonnage")

tonnage = (
    filtered
    .groupby("Load Type")["Act. Weight(Main)"]
    .sum()
    .reset_index()
)

st.plotly_chart(
    px.pie(tonnage, names="Load Type", values="Act. Weight(Main)"),
    use_container_width=True
)

# -----------------------------
# DATA PREVIEW
# -----------------------------
st.subheader("📋 Data Preview")
st.dataframe(filtered)
