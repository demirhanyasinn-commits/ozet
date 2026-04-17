import streamlit as st
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

simdi = datetime.now(ZoneInfo("Europe/Istanbul"))

st.caption(f"Son güncelleme: {simdi.strftime('%d.%m.%Y %H:%M:%S')}")

st.set_page_config(layout="wide")

# -------------------------------------------------
# 📡 PİYASA VERİSİ (MANUEL / API BAĞLANABİLİR)
# -------------------------------------------------
@st.cache_data(ttl=60)
def piyasa_verisi():
    return {
        "bank": 1.20,       # XBANK
        "sanayi": -0.30,    # XUSIN
        "teknoloji": -1.80,
        "usd": -0.06,
        "altin": 0.38
    }

# -------------------------------------------------
# 🔥 TEFAS PORTFÖY (GERÇEK)
# -------------------------------------------------
@st.cache_data(ttl=86400)
def tefas_portfoy(fon):
    url = "https://www.tefas.gov.tr/api/DB/BindPortfolio"

    payload = {"fontur": "", "fonkod": fon}

    res = requests.post(url, json=payload).json()

    hisse = doviz = altin = faiz = 0

    for i in res["data"]:
        tur = i["TUR"]
        oran = float(i["ORAN"])

        if "Hisse" in tur:
            hisse += oran
        elif "Döviz" in tur:
            doviz += oran
        elif "Altın" in tur:
            altin += oran
        else:
            faiz += oran

    toplam = hisse + doviz + altin + faiz

    return {
        "hisse": hisse / toplam,
        "doviz": doviz / toplam,
        "altin": altin / toplam,
        "faiz": faiz / toplam
    }

# -------------------------------------------------
# 🧠 FON KARAKTER MODELİ (KRİTİK)
# -------------------------------------------------
def hisse_dagilim_modeli(fon):
    modeller = {
        "TLY": {"bank": 0.35, "sanayi": 0.45, "teknoloji": 0.20},
        "DFI": {"bank": 0.45, "sanayi": 0.35, "teknoloji": 0.20},
        "PHE": {"bank": 0.10, "sanayi": 0.20, "teknoloji": 0.70},
        "PBR": {"bank": 0.55, "sanayi": 0.30, "teknoloji": 0.15},
        "KHA": {"bank": 0.25, "sanayi": 0.50, "teknoloji": 0.25},
    }
    return modeller.get(fon, {"bank": 0.33, "sanayi": 0.33, "teknoloji": 0.34})

# -------------------------------------------------
# 🔥 ANA HESAP MOTORU
# -------------------------------------------------
def tahmin(fon, piyasa):
    w = tefas_portfoy(fon)
    sektor = hisse_dagilim_modeli(fon)

    hisse_etki = (
        sektor["bank"] * piyasa["bank"] +
        sektor["sanayi"] * piyasa["sanayi"] +
        sektor["teknoloji"] * piyasa["teknoloji"]
    )

    sonuc = (
        w["hisse"] * hisse_etki +
        w["doviz"] * piyasa["usd"] +
        w["altin"] * piyasa["altin"] +
        w["faiz"] * 0.02
    )

    return round(sonuc, 3)

# -------------------------------------------------
# 🎨 UI
# -------------------------------------------------
st.title("📊 PRO Fon Gün Sonu Tahmin Sistemi")

piyasa = piyasa_verisi()

st.markdown(f"""
<div style="display:flex;gap:20px;background:#111;padding:10px;border-radius:10px;">
<div>🏦 Banka: %{piyasa['bank']}</div>
<div>🏭 Sanayi: %{piyasa['sanayi']}</div>
<div>💻 Teknoloji: %{piyasa['teknoloji']}</div>
<div>💵 USD: %{piyasa['usd']}</div>
<div>🥇 Altın: %{piyasa['altin']}</div>
</div>
""", unsafe_allow_html=True)

fonlar = ["TLY", "DFI", "PHE", "PBR"]

cols = st.columns(len(fonlar))

for i, fon in enumerate(fonlar):
    try:
        sonuc = tahmin(fon, piyasa)
    except:
        sonuc = 0

    renk = "#00ff88" if sonuc > 0 else "#ff4d4d"

    with cols[i]:
        st.markdown(f"""
        <div style="
            background:#111;
            padding:20px;
            border-radius:15px;
            border:1px solid #222;
        ">
        <h3>{fon}</h3>
        <p style="opacity:0.6;">GÜN SONU TAHMİN</p>
        <h1 style="color:{renk};">%{sonuc}</h1>
        </div>
        """, unsafe_allow_html=True)

st.caption(f"Son güncelleme: {datetime.now()}")
