import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Fon Tahmin", layout="wide")

# -----------------------------
# 📊 FON PORTFÖY AĞIRLIKLARI
# -----------------------------
FON_PORTFOY = {
    "TLY": {"hisse": 0.60, "doviz": 0.10, "altin": 0.10, "faiz": 0.20},
    "DFI": {"hisse": 0.70, "doviz": 0.10, "altin": 0.05, "faiz": 0.15},
    "PHE": {"hisse": 0.85, "doviz": 0.05, "altin": 0.00, "faiz": 0.10},
    "PBR": {"hisse": 0.50, "doviz": 0.20, "altin": 0.10, "faiz": 0.20},
    "KHA": {"hisse": 0.40, "doviz": 0.30, "altin": 0.10, "faiz": 0.20},
}

# -----------------------------
# 🌐 CANLI VERİ ÇEK
# -----------------------------
@st.cache_data(ttl=60)
def veri_cek():
    try:
        url = "https://api.collectapi.com/economy/liveBorsa"
        headers = {
            "authorization": "apikey 123456",  # kendi API key koy
            "content-type": "application/json"
        }
        res = requests.get(url, headers=headers).json()

        data = res["result"]

        def find(name):
            for x in data:
                if name in x["name"]:
                    return float(x["rate"].replace(",", "."))
            return 0

        return {
            "bist": find("BIST 100"),
            "usd": find("USD/TRY"),
            "altin": find("ALTIN"),
        }

    except:
        # fallback (demo değer)
        return {"bist": -0.55, "usd": -0.06, "altin": 0.38}

# -----------------------------
# 🧠 HESAPLAMA
# -----------------------------
def tahmin_hesapla(fon, bist, usd, altin):
    w = FON_PORTFOY[fon]

    faiz_etkisi = 0.02  # sabit küçük katkı

    sonuc = (
        w["hisse"] * bist +
        w["doviz"] * usd +
        w["altin"] * altin +
        w["faiz"] * faiz_etkisi
    )

    return round(sonuc, 2)

# -----------------------------
# 🎨 ÜST BAR
# -----------------------------
veri = veri_cek()

st.markdown(f"""
<div style="
display:flex;
gap:20px;
padding:10px;
background:#111;
border-radius:10px;
">
<div>📊 BIST100: <b>{veri['bist']}%</b></div>
<div>💵 USD: <b>{veri['usd']}%</b></div>
<div>🥇 ALTIN: <b>{veri['altin']}%</b></div>
</div>
""", unsafe_allow_html=True)

st.title("YA 34   YA 39")

# -----------------------------
# 📦 KARTLAR
# -----------------------------
fonlar = list(FON_PORTFOY.keys())
cols = st.columns(len(fonlar))

for i, fon in enumerate(fonlar):
    tahmin = tahmin_hesapla(
        fon,
        veri["bist"],
        veri["usd"],
        veri["altin"]
    )

    renk = "#00ff88" if tahmin > 0 else "#ff4d4d"

    with cols[i]:
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #1c1c1c, #111);
            border-radius:16px;
            padding:20px;
            border:1px solid #222;
            text-align:left;
            min-height:140px;
        ">
            <h3 style="margin:0;">{fon}</h3>
            <p style="opacity:0.7; font-size:12px;">GÜN SONU TAHMİNİ</p>
            <h1 style="color:{renk};">%{tahmin}</h1>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# ⏱️ ALT BİLGİ
# -----------------------------
st.markdown(f"""
<p style="opacity:0.6; font-size:12px;">
Son Güncelleme: {datetime.now().strftime("%H:%M:%S")}
</p>
""", unsafe_allow_html=True)

# -----------------------------
# 🔁 YENİLE BUTONU
# -----------------------------
if st.button("🔄 VERİLERİ ZORLA YENİLE"):
    st.cache_data.clear()
    st.rerun()
