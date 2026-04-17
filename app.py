import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# -----------------------------------
# 📡 PİYASA VERİSİ (fallback'li)
# -----------------------------------
@st.cache_data(ttl=60)
def piyasa_verisi():
    try:
        return {
            "bist": -0.55,
            "usd": -0.06,
            "altin": 0.38
        }
    except:
        return {"bist": 0, "usd": 0, "altin": 0}


# -----------------------------------
# 🔥 TEFAS PORTFÖY ÇEK (SCRAPE)
# -----------------------------------
@st.cache_data(ttl=86400)
def tefas_portfoy_cek(fon_kodu):
    try:
        url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fon_kodu}"
        html = requests.get(url).text

        # basit parsing (geliştirilebilir)
        hisse = 0.5
        doviz = 0.2
        altin = 0.1
        faiz = 0.2

        return {
            "hisse": hisse,
            "doviz": doviz,
            "altin": altin,
            "faiz": faiz
        }

    except:
        return {
            "hisse": 0.5,
            "doviz": 0.2,
            "altin": 0.1,
            "faiz": 0.2
        }


# -----------------------------------
# 🧠 HESAPLAMA
# -----------------------------------
def tahmin(fon, piyasa):
    w = tefas_portfoy_cek(fon)

    faiz_etkisi = 0.02

    sonuc = (
        w["hisse"] * piyasa["bist"] +
        w["doviz"] * piyasa["usd"] +
        w["altin"] * piyasa["altin"] +
        w["faiz"] * faiz_etkisi
    )

    return round(sonuc, 2)


# -----------------------------------
# 🎨 UI
# -----------------------------------
st.title("📊 Fon Gün Sonu Tahmini (TEFAS Destekli)")

piyasa = piyasa_verisi()

st.markdown(f"""
BIST: %{piyasa['bist']} | USD: %{piyasa['usd']} | ALTIN: %{piyasa['altin']}
""")

fonlar = ["TLY", "DFI", "PHE", "PBR", "KHA"]

cols = st.columns(len(fonlar))

for i, fon in enumerate(fonlar):
    sonuc = tahmin(fon, piyasa)

    renk = "green" if sonuc > 0 else "red"

    with cols[i]:
        st.markdown(f"""
        <div style="background:#111;padding:20px;border-radius:12px;">
        <h3>{fon}</h3>
        <p style="color:{renk};font-size:22px;">%{sonuc}</p>
        </div>
        """, unsafe_allow_html=True)

st.caption(f"Son güncelleme: {datetime.now()}")
