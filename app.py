import streamlit as st
import requests
from datetime import datetime, time
from zoneinfo import ZoneInfo

# Sayfa Genişliği
st.set_page_config(layout="wide", page_title="Fon Tahmin Terminali")

# -------------------------------------------------
# ⏰ TÜRKİYE SAATİ FONKSİYONU
# -------------------------------------------------
def simdi_tr():
    return datetime.now(ZoneInfo("Europe/Istanbul"))

# -------------------------------------------------
# 🟢 BORSA DURUM KONTROLÜ
# -------------------------------------------------
def borsa_acik_mi():
    now = simdi_tr()
    # Cumartesi = 5, Pazar = 6
    if now.weekday() >= 5: 
        return False
    # 10:00 - 18:10 arası açık kabul edilir
    acilis = time(10, 0)
    kapanis = time(18, 10)
    return acilis <= now.time() <= kapanis

# -------------------------------------------------
# 📡 PİYASA VERİLERİ (MANUEL VERİ GİRİŞİ)
# -------------------------------------------------
@st.cache_data(ttl=60)
def piyasa_verisi():
    # Bu veriler senin ekranındaki üst bant verileridir
    return {
        "bank": 1.20,       # XBANK
        "sanayi": -0.30,    # XUSIN
        "teknoloji": -1.80, # XTEKNO
        "usd": -0.06,       # Dolar/TL değişim
        "altin": 0.38       # Ons/Gram Altın değişim
    }

# -------------------------------------------------
# 🔥 TEFAS VERİ ÇEKME VE PORTFÖY ANALİZİ
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
            elif "Döviz" in tur or "Yabancı" in tur: 
                doviz += oran
            elif "Altın" in tur: 
                altin += oran
            else: 
                faiz += oran

        toplam = hisse + doviz + altin + faiz
        if toplam == 0: 
            return {"hisse": 0.90, "doviz": 0.05, "altin": 0.0, "faiz": 0.05}

        return {
            "hisse": hisse / toplam,
            "doviz": doviz / toplam,
            "altin": altin / toplam,
            "faiz": faiz / toplam
        }
    except:
        # Hata durumunda varsayılan agresif fon yapısı
        return {"hisse": 0.85, "doviz": 0.05, "altin": 0.0, "faiz": 0.10}

# -------------------------------------------------
# 🧠 FON KARAKTER MODELİ (BETA & SEKTÖR)
# -------------------------------------------------
def hisse_model(fon):
    # Beta: Fonun endekse göre ne kadar agresif olduğunu belirler (1.30 = %30 daha fazla tepki)
    model = {
        "TLY": {"bank": 0.40, "sanayi": 0.50, "teknoloji": 0.10, "beta": 1.35},
        "DFI": {"bank": 0.50, "sanayi": 0.40, "teknoloji": 0.10, "beta": 1.32},
        "PHE": {"bank": 0.10, "sanayi": 0.15, "teknoloji": 0.75, "beta": 1.15},
        "PBR": {"bank": 0.60, "sanayi": 0.30, "teknoloji": 0.10, "beta": 1.12},
        "KHA": {"bank": 0.55, "sanayi": 0.35, "teknoloji": 0.10, "beta": 1.20},
    }
    return model.get(fon, {"bank": 0.33, "sanayi": 0.33, "teknoloji": 0.34, "beta": 1.0})

# -------------------------------------------------
# 🔥 TAHMİN HESAPLAMA MOTORU
# -------------------------------------------------
def tahmin(fon, piyasa):
    w = tefas_portfoy(fon)
    m = hisse_model(fon)

    # Hisse senedi kısmının kendi içindeki ağırlıklı getirisi
    hisse_getiri_ham = (
        m["bank"] * piyasa["bank"] +
        m["sanayi"] * piyasa["sanayi"] +
        m["teknoloji"] * piyasa["teknoloji"]
    )

    # Beta çarpanı (Agresiflik) uygulaması
    hisse_etki = hisse_getiri_ham * m["beta"]

    # Ana formül: Portföy dağılımı * Getiriler
    sonuc = (
        w["hisse"] * hisse_etki +
        w["doviz"] * piyasa["usd"] +
        w["altin"] * piyasa["altin"] +
        w["faiz"] * 0.02 # Ortalama günlük repo/faiz getirisi
    )

    # Fon yönetim ücreti düşümü (Günlük yaklaşık %0.008)
    sonuc -= 0.008

    return round(sonuc, 2)

# -------------------------------------------------
# 🎨 KULLANICI ARAYÜZÜ (UI)
# -------------------------------------------------
st.title("▄︻デ══━一💥 Y A 3 4  Y A 3 9")

piyasa = piyasa_verisi()
simdi = simdi_tr()
acik = borsa_acik_mi()
durum_text = "🟢 Borsa Açık" if acik else "🔴 Borsa Kapalı"

# Üst Bilgi Paneli
st.markdown(f"""
<div style="display:flex; justify-content: space-between; background:#111; padding:15px; border-radius:10px; border: 1px solid #333; margin-bottom:20px;">
    <div style="font-weight:bold; color:#fff;">{durum_text}</div>
    <div style="color:#00ff88;">🏦 Banka: %{piyasa['bank']}</div>
    <div style="color:#ffcc00;">🏭 Sanayi: %{piyasa['sanayi']}</div>
    <div style="color:#00d4ff;">💻 Tekno: %{piyasa['teknoloji']}</div>
    <div style="color:#ff4d4d;">💵 USD: %{piyasa['usd']}</div>
    <div style="color:#ffd700;">🥇 Altın: %{piyasa['altin']}</div>
</div>
""", unsafe_allow_html=True)

# Tahmin Edilecek Fonlar
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
        <div style="
            background:#111; 
            padding:25px; 
            border-radius:15px; 
            border:1px solid #222; 
            text-align:center;
            min-height: 180px;
        ">
            <h2 style="margin:0; color:#eee; font-size:22px;">{fon}</h2>
            <p style="opacity:0.5; font-size:11px; margin-bottom:15px;">GÜN SONU TAHMİN</p>
            <h1 style="color:{renk}; margin:0; font-size:38px;">%{sonuc}</h1>
            <p style="color:{renk}; margin:0; font-size:20px;">{ok}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption(f"Son Güncelleme: {simdi.strftime('%d.%m.%Y %H:%M:%S')} | Tahminler Beta katsayısı ve yönetim ücreti düşülerek hesaplanmıştır.")

# -------------------------------------------------
# 🔄 YENİLEME MEKANİZMASI
# -------------------------------------------------
if st.button("🔄 VERİLERİ VE TAHMİNLERİ YENİLE"):
    st.cache_data.clear()
    st.rerun()
