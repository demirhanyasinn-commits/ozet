import streamlit as st
import requests
from datetime import datetime, time
from zoneinfo import ZoneInfo

st.set_page_config(layout="wide")

# -------------------------------------------------
# ⏰ TÜRKİYE SAATİ
# -------------------------------------------------
def simdi_tr():
    return datetime.now(ZoneInfo("Europe/Istanbul"))

# -------------------------------------------------
# 🟢 BORSA AÇIK MI?
# -------------------------------------------------
def borsa_acik_mi():
    now = simdi_tr()

    if now.weekday() >= 5:
        return False

    acilis = time(10, 0)
    kapanis = time(18, 10)

    return acilis <= now.time() <= kapanis

# -------------------------------------------------
# 📡 PİYASA VERİSİ (API BAĞLANABİLİR)
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
# 🔥 TEFAS PORTFÖY ÇEK (GERÇEK)
# -------------------------------------------------
@st.cache_data(ttl=86400)
def tefas_portfoy(fon):
    try:
        url = "https://www.tefas.gov.tr/api/DB/BindPortfolio"
        payload = {"fontur": "", "fonkod": fon}

        res = requests.post(url, json=payload, timeout=10).json()

        hisse = doviz = altin = faiz = 0

        for i in res.get("data", []):
            tur = i.get("TUR", "")
            oran = float(i.get("ORAN", 0))

            if "Hisse" in tur:
                hisse += oran
            elif "Döviz" in tur:
                doviz += oran
            elif "Altın" in tur:
                altin += oran
            else:
                faiz += oran

        toplam = hisse + doviz + altin + faiz

        if toplam == 0:
            return {"hisse": 0.5, "doviz": 0.2, "altin": 0.1, "faiz": 0.2}

        return {
            "hisse": hisse / toplam,
            "doviz": doviz / toplam,
            "altin": altin / toplam,
            "faiz": faiz / toplam
        }

    except:
        return {"hisse": 0.5, "doviz": 0.2, "altin": 0.1, "faiz": 0.2}

# -------------------------------------------------
# 🧠 FON KARAKTER MODELİ
# -------------------------------------------------
def hisse_model(fon):
    model = {
        "TLY": {"bank": 0.35, "sanayi": 0.45, "teknoloji": 0.20},
        "DFI": {"bank": 0.45, "sanayi": 0.35, "teknoloji": 0.20},
        "PHE": {"bank": 0.10, "sanayi": 0.20, "teknoloji": 0.70},
        "PBR": {"bank": 0.55, "sanayi": 0.30, "teknoloji": 0.15},
        "KHA": {"bank": 0.25, "sanayi": 0.50, "teknoloji": 0.25},
    }
    return model.get(fon, {"bank": 0.33, "sanayi": 0.33, "teknoloji": 0.34})

# -------------------------------------------------
# 🔥 ANA HESAPLAMA
# -------------------------------------------------
def tahmin(fon, piyasa):
    w = tefas_portfoy(fon)
    sektor = hisse_model(fon)

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

    # 🔴 Borsa kapalıysa stabilize et
    if not borsa_acik_mi():
        sonuc *= 0.7

    return round(sonuc, 3)

# -------------------------------------------------
# 🎨 UI
# -------------------------------------------------
st.title("📊 PRO Fon Gün Sonu Tahmin Sistemi")

piyasa = piyasa_verisi()
simdi = simdi_tr()

durum = "🟢 Borsa Açık" if borsa_acik_mi() else "🔴 Borsa Kapalı"

st.markdown(f"""
<div style="display:flex;gap:20px;background:#111;padding:10px;border-radius:10px;">
<div>{durum}</div>
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

st.caption(f"Son güncelleme: {simdi.strftime('%d.%m.%Y %H:%M:%S')}")

# -------------------------------------------------
# 🔄 YENİLE BUTONU
# -------------------------------------------------
if st.button("🔄 VERİLERİ YENİLE"):
    st.cache_data.clear()
    st.rerun()
