import requests
import pandas as pd

def fetch_tefas(fon_kodu):
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"

    payload = {
        "fontip": "YAT",
        "fonkod": fon_kodu,
        "bastarih": "01.01.2024",
        "bittarih": "10.04.2026"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    r = requests.post(url, data=payload, headers=headers)
    data = r.json()

    df = pd.DataFrame(data["data"])
    df["Tarih"] = pd.to_datetime(df["Tarih"])
    df["Fiyat"] = df["Fiyat"].astype(float)

    return df.sort_values("Tarih")
    def calc_returns(df):
    current = df.iloc[-1]["Fiyat"]

    def get_price(days):
        return df[df["Tarih"] >= df["Tarih"].max() - pd.Timedelta(days=days)].iloc[0]["Fiyat"]

    return {
        "1G": (current - get_price(1)) / get_price(1) * 100,
        "1H": (current - get_price(7)) / get_price(7) * 100,
        "1A": (current - get_price(30)) / get_price(30) * 100,
    }
    import plotly.graph_objects as go

def create_chart(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Tarih"],
        y=df["Fiyat"],
        mode="lines",
        name="Fiyat"
    ))

    fig.update_layout(
        template="plotly_dark",
        height=400
    )

    return fig
    import streamlit as st
import time

st.set_page_config(layout="wide")
st.title("📊 TEFAS Canlı Fon Takip")

fonlar = ["TLY", "PHE", "DFI"]

cols = st.columns(len(fonlar))

for i, fon in enumerate(fonlar):
    with cols[i]:
        df = fetch_tefas(fon)

        current = df.iloc[-1]["Fiyat"]
        prev = df.iloc[-2]["Fiyat"]

        change = (current - prev) / prev * 100

        color = "green" if change > 0 else "red"

        st.markdown(f"### {fon}")
        st.markdown(f"<h1 style='color:{color}'>{change:.2f}%</h1>", unsafe_allow_html=True)
        st.markdown(f"<p>{current:.4f} TL</p>", unsafe_allow_html=True)

        # DETAY
        with st.expander("Detay"):
            returns = calc_returns(df)

            st.write(f"1 Gün: %{returns['1G']:.2f}")
            st.write(f"1 Hafta: %{returns['1H']:.2f}")
            st.write(f"1 Ay: %{returns['1A']:.2f}")

            fig = create_chart(df)
            st.plotly_chart(fig, use_container_width=True)

# 🔄 AUTO REFRESH
time.sleep(60)
st.rerun()
