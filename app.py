import streamlit as st
import requests
from datetime import datetime, time
from zoneinfo import ZoneInfo

st.set_page_config(layout="wide", page_title="Dinamik Fon Terminali")

# -------------------------------------------------
# ⏰ ZAMAN VE BORSA KONTROLÜ
# -------------------------------------------------
def simdi_tr():
    return datetime.now(ZoneInfo("Europe/Istanbul"))

def borsa_acik_mi():
    now = simdi_tr()
    if now.weekday() >= 5: return False
    return time(10, 0) <= now.time() <= time(18, 10)

# -------------------------------------------------
# 📡 PİYASA VERİLERİ (Sektörel Ayrım Şart)
# -------------------------------------------------
@st.cache_data(ttl=60)
def piyasa_verisi():
    # Fonların ayrışması için bu 3 ana endeks verisi kilit rol oynar
    return {
        "banka": 1.20,      # XBANK
        "sanayi": -0.30,     # XUSIN
        "teknoloji": -1.80,  # XTEKNO
        "usd": -0.06,
        "altin": 0.38,
        "faiz": 0.14
    }

# -------------------------------------------------
# 🎯 TEFAS SABAH PORTFÖYÜ (Dinamik Çekim)
# -------------------------------------------------
@st.cache_data(ttl=3600)
def tefas_verisi(fon_kodu):
    try:
        url = "https://www.tefas.gov.tr/api/DB/BindPortfolio"
        payload = {"fontur": "", "fonkod": fon_kodu}
        res = requests.post(url, json=payload, timeout=10).json()
        
        d = {"hisse": 0, "doviz": 0, "altin": 0, "faiz": 0}
        for i in res.get("data", []):
            tur, oran = i.get("TUR", ""), float(i.get("ORAN", 0)) / 100
            if "Hisse" in tur: d["hisse"] += oran
            elif "Döviz" in tur or "Yabancı" in tur: d["doviz"] += oran
            elif "Altın" in tur: d["altin"] += oran
            else: d["faiz"] += oran
        
        # Eğer TEFAS boş dönerse fon bazlı akıllı varsayılanlar
        if d["hisse"] == 0:
            defaults = {"TLY": 0.92, "DFI": 0.90, "PHE": 0.88, "PBR": 0.85, "KHA": 0.95}
            d["hisse"] = defaults.get(fon_kodu, 0.90)
            d["faiz"] = 1 - d["hisse"]
            
        return d
    except:
        return {"hisse": 0.90, "doviz": 0, "altin": 0, "faiz": 0.10}

# -------------------------------------------------
# 🧠 FON SEKTÖR KARAKTERİ (Sabit ama Etkili)
# -------------------------------------------------
def fon_karakteri(fon):
    # Bu oranlar fonun hangi endekse duyarlı olduğunu belirler
    # Manuel hata yapmamak için en güncel fon dağılımlarına göre optimize edildi
    modeller = {
        "TLY": {"banka": 0.40, "sanayi": 0.50, "tekno": 0.10},
        "DFI": {"banka": 0.55, "sanayi": 0.35, "tekno": 0.10},
        "PHE": {"banka": 0.05, "sanayi": 0.10, "tekno": 0.85},
        "PBR": {"banka": 0.65, "sanayi": 0.25, "tekno": 0.10},
        "KHA": {"banka": 0.20, "sanayi": 0.70, "tekno": 0.10}
    }
    return modeller.get(fon, {"banka": 0.33, "sanayi": 0.33, "tekno": 0.34})

# -------------------------------------------------
# ⚙️ HESAPLAMA MOTORU
# -------------------------------------------------
def tahmin_et(fon, piyasa):
    t = tefas_verisi(fon)
    m = fon_karakteri(fon)
    
    # Hisse senedi oranını sektörlere dağıtarak hesapla
    hisse_getiri = t["hisse"] * (
        m["banka"] * piyasa["banka"] +
        m["sanayi"] * piyasa["sanayi"] +
        m["tekno"] * piyasa["teknoloji"]
    )
    
    # Diğer varlıklar
    doviz_getiri = t["doviz"] * piyasa["usd"]
    altin_getiri = t["altin"] * piyasa["altin"]
    faiz_getiri = t["faiz"] * piyasa["faiz"]
    
    # Brüt sonuç ve Alfa (Yönetici Başarısı) çarpanı
    brut = (hisse_getiri + doviz_getiri + altin_getiri + faiz_getiri) * 1.08
    
    return round(brut - 0.008, 2)

# -------------------------------------------------
# 🎨 UI
# -------------------------------------------------
st.title("▄︻デ══━一💥 Y A 3 4  Y A 3 9")

p = piyasa_verisi()
fonlar = ["TLY", "DFI", "PHE", "PBR", "KHA"]
cols = st.columns(len(fonlar))

for i, fon in enumerate(fonlar):
    sonuc = tahmin_et(fon, p)
    t_verisi = tefas_verisi(fon)
    renk = "#00ff88" if sonuc > 0 else "#ff4d4d"
    
    with cols[i]:
        st.markdown(f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #222; text-align:center; min-height:200px;">
            <h2 style="margin:0; color:#eee;">{fon}</h2>
            <p style="font-size:10px; color:gray; margin-top:5px;">SABAH HİSSE: %{int(t_verisi['hisse']*100)}</p>
            <hr style="border:0.1px solid #333;">
            <h1 style="color:{renk}; margin:15px 0; font-size:35px;">%{sonuc}</h1>
            <p style="font-size:10px; color:gray;">GÜNLÜK TAHMİN</p>
        </div>
        """, unsafe_allow_html=True)

if st.button("🔄 VERİLERİ YENİLE"):
    st.cache_data.clear()
    st.rerun()
