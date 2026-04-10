import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time

st.set_page_config(page_title="TEFAS Fon Takip", layout="wide")

st.title("📊 TEFAS Canlı Fon Takip Paneli")

# ==============================
# 🔌 TEFAS VERİ ÇEKME
# ==============================
@st.cache_data(ttl=300)
def fetch_tefas(fon_kodu):
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"

    payload = {
        "fontip": "YAT",
        "fonkod": fon_kodu,
        "bastarih": "01.01.2024",
        "bittarih": pd.Timestamp.today().strftime("%d.%m.%Y")
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    r = requests.post(url, data=payload, headers=headers)

    if r.status_code != 200:
        return pd.DataFrame()

    data = r.json().get("data", [])

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d.%m.%Y")
    df["Fiyat"] = df["Fiyat"].astype(float)

    return df.sort_values("Tarih")


# ==============================
# 📊 GETİRİ HESAPLAMA
# ==============================
def calc_returns(df):
    if len(df) < 2:
        return {"1G": 0, "1H": 0, "1A": 0}

    current = df.iloc[-1]["Fiyat"]

    def safe_get(days):
        filtered = df[df["Tarih"] >= df["Tarih"].max() - pd.Timedelta(days=days)]
        if len(filtered) == 0:
            return current
        return filtered.iloc[0]["Fiyat"]

    return {
        "1G": (current - safe_get(1)) / safe_get(1) * 100,
        "1H": (current - safe_get(7)) / safe_get(7) * 100,
        "1A": (current - safe_get(30)) / safe_get(30) * 100,
    }


# ==============================
# 📈 GRAFİK
# ==============================
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
        height=400,
        margin=dict(l=10, r=10, t=30, b=10)
    )

    fig.update_traces(hovertemplate="%{y:.4f} TL")

    return fig


# ==============================
# 📌 TAKİP EDİLEN FONLAR
# ==============================
fonlar = ["TLY", "PHE", "DFI"]

cols = st.columns(len(fonlar))

for i, fon in enumerate(fonlar):
    with cols[i]:
        df = fetch_tefas(fon)

        if df.empty:
            st.warning(f"{fon} verisi alınamadı")
            continue

        current = df.iloc[-1]["Fiyat"]
        prev = df.iloc[-2]["Fiyat"]

        change = (current - prev) / prev * 100
        color = "green" if change > 0 else "red"

        st.markdown(f"### {fon}")
        st.markdown(f"<h1 style='color:{color}'>{change:.2f}%</h1>", unsafe_allow_html=True)
        st.markdown(f"<p>{current:.4f} TL</p>", unsafe_allow_html=True)

        # DETAY PANEL
        with st.expander("Detayları Gör"):
            returns = calc_returns(df)

            st.write(f"📅 1 Gün: %{returns['1G']:.2f}")
            st.write(f"📅 1 Hafta: %{returns['1H']:.2f}")
            st.write(f"📅 1 Ay: %{returns['1A']:.2f}")

            fig = create_chart(df)
            st.plotly_chart(fig, use_container_width=True)


# ==============================
# 🔄 AUTO REFRESH
# ==============================
time.sleep(60)
st.rerun()
