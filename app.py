import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Smart Expense Dashboard",
    page_icon="💰",
    layout="wide"
)

DATA_DIR = "data"
PERSONAL_PATH = os.path.join(DATA_DIR, "personal_finance_clean.csv")
BPS_PATH = os.path.join(DATA_DIR, "bps_commodity_clean.csv")

@st.cache_data
def load_data():
    pf = pd.read_csv(PERSONAL_PATH, parse_dates=["date"]) if os.path.exists(PERSONAL_PATH) else None
    bps = pd.read_csv(BPS_PATH) if os.path.exists(BPS_PATH) else None
    return pf, bps

def recommend_allocation(income, needs_pct, wants_pct, savings_pct):
    total = needs_pct + wants_pct + savings_pct

    ratios = {
        "Kebutuhan Pokok": needs_pct / total,
        "Kebutuhan Sekunder": wants_pct / total,
        "Tabungan": savings_pct / total,
    }

    return pd.DataFrame([
        {
            "Kategori": k,
            "Persentase": v * 100,
            "Nominal": income * v
        }
        for k, v in ratios.items()
    ])

st.title("Smart Expense - Dashboard Data Science")
st.caption("Insight pengeluaran dan rekomendasi alokasi dana.")

pf, bps = load_data()

with st.sidebar:
    st.header("Input Rekomendasi")
    income = st.number_input(
        "Jumlah uang/gaji",
        min_value=0.0,
        value=5_000_000.0,
        step=100_000.0
    )

    needs_pct = st.slider("Kebutuhan pokok (%)", 0, 100, 50)
    wants_pct = st.slider("Kebutuhan sekunder (%)", 0, 100, 30)
    savings_pct = st.slider("Tabungan (%)", 0, 100, 20)

allocation = recommend_allocation(
    income,
    needs_pct,
    wants_pct,
    savings_pct
)

cols = st.columns(3)

for col, (_, row) in zip(cols, allocation.iterrows()):
    col.metric(
        row["Kategori"],
        f"Rp {row['Nominal']:,.0f}".replace(",", ".")
    )

c1, c2 = st.columns(2)

with c1:
    st.dataframe(allocation, use_container_width=True)

with c2:
    fig = px.pie(
        allocation,
        names="Kategori",
        values="Nominal",
        title="Proporsi Alokasi Dana"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Insight Transaksi")

if pf is None:
    st.warning("Data cleaning belum tersedia. Jalankan notebook terlebih dahulu.")
else:
    expense = pf[pf["type_clean"] == "expense"]

    by_bucket = (
        expense
        .groupby("bucket", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )

    by_cat = (
        expense
        .groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
        .head(10)
    )

    monthly = (
        pf
        .groupby(["month", "type_clean"], as_index=False)["amount"]
        .sum()
    )

    st.plotly_chart(
        px.bar(
            by_bucket,
            x="bucket",
            y="amount",
            title="Pengeluaran per Bucket"
        ),
        use_container_width=True
    )

    st.plotly_chart(
        px.bar(
            by_cat,
            x="category",
            y="amount",
            title="Top 10 Kategori Pengeluaran"
        ),
        use_container_width=True
    )

    st.plotly_chart(
        px.line(
            monthly,
            x="month",
            y="amount",
            color="type_clean",
            title="Tren Bulanan Income vs Expense"
        ),
        use_container_width=True
    )

st.divider()
st.subheader("Benchmark BPS")

if bps is not None:
    top = bps.sort_values("national_amount", ascending=False).head(12)

    st.dataframe(top, use_container_width=True)

    st.plotly_chart(
        px.bar(
            top,
            x="commodity_id",
            y="national_amount",
            title="Top Komoditas Pengeluaran Nasional"
        ),
        use_container_width=True
    )
