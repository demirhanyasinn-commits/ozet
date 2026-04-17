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
    if now.weekday() >= 5: return False
    return time(10, 0) <= now.time() <= int_to_time(18, 10)

def int_to_time(h, m): return time(h, m)

# -------------------------------------------------
# 📡 PİYASA VERİSİ
# -------------------------------------------------
@st.cache_data(ttl=60)
def piyasa_verisi():
    # Burada manuel veri giriyorsun, ileride buraya bir API bağlaman isabeti artırır.
    return {
        "bank": 1.20,
        "sanayi": -0.30,
        "teknoloji": -1.80,
        "usd": -0.06,
        "altin": 0.38
    }

# -------------------------------------------------
# 🔥 TEFAS PORTFÖY ÇEK
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
            if "Hisse" in tur: hisse += oran
            elif "Döviz" in tur or "Yabancı" in tur: doviz += oran
            elif "Altın" in tur: altin += oran
            else: faiz += oran

        toplam = hisse + doviz + altin + faiz
        if toplam == 0: return {"hisse": 0.90, "doviz": 0.05, "altin": 0.0, "faiz": 0.05}

        return {
            "hisse": hisse / toplam,
            "doviz": doviz / toplam,
            "altin": altin / toplam,
            "faiz": faiz / toplam
        }
    except:
        # Genelde bu fonlar hisse ağırlıklıdır
        return {"hisse": 0.90, "doviz": 0.05, "altin": 0.0, "faiz": 0.05}

# -------------------------------------------------
# 🧠 FON KARAKTER MODELİ (Beta Katsayıları Eklendi)
# -------------------------------------------------
def hisse_model(fon):
    model = {
        "TLY": {"bank": 0.40, "sanayi": 0.50, "teknoloji": 0.10, "beta": 1.35},
        "DFI": {"bank": 0.50, "sanayi": 0.40, "teknoloji": 0.10, "beta": 1.30},
        "PHE": {"bank": 0.10, "sanayi": 0.10, "teknoloji": 0.80, "beta": 1.15},
        "PBR": {"bank": 0.60, "sanayi": 0.30, "teknoloji": 0.10, "beta": 1.10},
        "KHA": {"bank": 0.25, "sanayi": 0.60, "teknoloji": 0.15, "beta": 1.25}, # KHA eklendi
    }
    return model.get(fon, {"bank": 0.33, "sanayi": 0.33, "teknoloji": 0.34, "beta": 1.0})

# ... (Hesaplama fonksiyonu aynı kalacak)

# -------------------------------------------------
# 🎨 UI - FON LİSTESİ GÜNCELLEME
# -------------------------------------------------
# Fon listesine KHA'yı ekledik, kolon sayısı otomatik ayarlanacak
fonlar = ["TLY", "DFI", "PHE", "PBR", "KHA"]

cols = st.columns(len(fonlar))

for i, fon in enumerate(fonlar):
    try:
        sonuc = tahmin(fon, piyasa)
    except:
        sonuc = 0.0

    renk = "#00ff88" if sonuc > 0 else "#ff4d4d"
    ok = "▲" if sonuc > 0 else "▼"

    with cols[i]:
        st.markdown(f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #222; text-align:center;">
            <h2 style="margin:0; color:#eee; font-size:20px;">{fon}</h2>
            <p style="opacity:0.5; font-size:10px; margin-bottom:10px;">GÜN SONU TAHMİN</p>
            <h1 style="color:{renk}; margin:0; font-size:32px;">%{sonuc}</h1>
            <p style="color:{renk}; margin:0;">{ok}</p>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------
# 🔥 ANA HESAPLAMA
# -------------------------------------------------
def tahmin(fon, piyasa):
    w = tefas_portfoy(fon)
    m = hisse_model(fon)

    # Hisse tarafındaki ağırlıklı getiri
    hisse_getiri = (
        m["bank"] * piyasa["bank"] +
        m["sanayi"] * piyasa["sanayi"] +
        m["teknoloji"] * piyasa["teknoloji"]
    )

    # Beta çarpanı ile agresifliği ayarla
    hisse_etki = hisse_getiri * m["beta"]

    # Toplam Tahmin
    sonuc = (
        w["hisse"] * hisse_etki +
        w["doviz"] * piyasa["usd"] +
        w["altin"] * piyasa["altin"] +
        w["faiz"] * 0.02
    )

    # Günlük yönetim ücreti kesintisi (Yaklaşık)
    yonetim_ucreti = 0.008 
    sonuc -= yonetim_ucreti

    return round(sonuc, 2) # Gerçek sonuçlar genelde 2 hane gösterilir

# -------------------------------------------------
# 🎨 UI
# -------------------------------------------------
st.title("▄︻デ══━一💥 Y A 3 4  Y A 3 9")

piyasa = piyasa_verisi()
simdi = simdi_tr()
acik = borsa_acik_mi()
durum = "🟢 Borsa Açık" if acik else "🔴 Borsa Kapalı"

st.markdown(f"""
<div style="display:flex; justify-content: space-between; background:#111; padding:15px; border-radius:10px; border: 1px solid #333;">
    <div style="font-weight:bold; color:#fff;">{durum}</div>
    <div style="color:#00ff88;">🏦 Banka: %{piyasa['bank']}</div>
    <div style="color:#ffcc00;">🏭 Sanayi: %{piyasa['sanayi']}</div>
    <div style="color:#00d4ff;">💻 Tekno: %{piyasa['teknoloji']}</div>
    <div style="color:#ff4d4d;">💵 USD: %{piyasa['usd']}</div>
    <div style="color:#ffd700;">🥇 Altın: %{piyasa['altin']}</div>
</div>
""", unsafe_allow_html=True)

st.write("") # Boşluk

fonlar = ["TLY", "DFI", "PHE", "PBR"]
cols = st.columns(len(fonlar))

for i, fon in enumerate(fonlar):
    try:
        sonuc = tahmin(fon, piyasa)
    except:
        sonuc = 0.0

    renk = "#00ff88" if sonuc > 0 else "#ff4d4d"
    ok = "▲" if sonuc > 0 else "▼"

    with cols[i]:
        st.markdown(f"""
        <div style="background:#111; padding:25px; border-radius:15px; border:1px solid #222; text-align:center;">
            <h2 style="margin:0; color:#eee;">{fon}</h2>
            <p style="opacity:0.5; font-size:12px; margin-bottom:10px;">GÜN SONU TAHMİN</p>
            <h1 style="color:{renk}; margin:0; font-size:42px;">%{sonuc}</h1>
            <p style="color:{renk}; margin:0;">{ok}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption(f"Veri Zamanı: {simdi.strftime('%H:%M:%S')} | Tahminler piyasa duyarlılığına (Beta) göre normalize edilmiştir.")

if st.button("🔄 VERİLERİ YENİLE"):
    st.cache_data.clear()
    st.rerun()
