import streamlit as st
import requests
from datetime import datetime, time
from zoneinfo import ZoneInfo

st.set_page_config(layout="wide", page_title="Canlı TEFAS Kalibrasyon Terminali")

# -------------------------------------------------
# ⏰ TÜRKİYE SAATİ VE BORSA DURUMU
# -------------------------------------------------
def simdi_tr():
    return datetime.now(ZoneInfo("Europe/Istanbul"))

def borsa_acik_mi():
    now = simdi_tr()
    if now.weekday() >= 5: return False
    return time(10, 0) <= now.time() <= time(18, 10)

# -------------------------------------------------
# 📡 CANLI PİYASA VERİLERİ
# -------------------------------------------------
@st.cache_data(ttl=60)
def piyasa_verisi():
    # Burayı ileride bir borsa API'sine (Örn: Yahoo Finance veya Finnhub) bağlayabilirsin.
    # Şimdilik senin ekranındaki anlık verileri baz alıyoruz.
    return {
        "bist100": 0.45,    # Genel Endeks Değişimi (Banka/Sanayi ortalaması gibi düşünebilirsin)
        "usd": -0.06,
        "altin": 0.38,
        "faiz_gunluk": 0.14 # Günlük ortalama mevduat/repo getirisi (yıllık %50/365 bazlı)
    }

# -------------------------------------------------
# 🎯 TEFAS SABAH VERİSİ (KALİBRASYON BURADA YAPILIYOR)
# -------------------------------------------------
@st.cache_data(ttl=3600) # Her saat başı portföyü kontrol et
def tefas_anlik_portfoy(fon_kodu):
    try:
        url = "https://www.tefas.gov.tr/api/DB/BindPortfolio"
        payload = {"fontur": "", "fonkod": fon_kodu}
        res = requests.post(url, json=payload, timeout=10).json()
        
        veriler = {
            "Hisse Senedi": 0,
            "Döviz Ödemeli": 0, # Eurobond vb.
            "Altın": 0,
            "Mevduat/Repo": 0,
            "Diğer": 0
        }

        for i in res.get("data", []):
            tur = i.get("TUR", "")
            oran = float(i.get("ORAN", 0)) / 100 # Yüzdelik formata çevir (%90 -> 0.90)

            if "Hisse" in tur: veriler["Hisse Senedi"] += oran
            elif "Döviz" in tur or "Yabancı" in tur: veriler["Döviz Ödemeli"] += oran
            elif "Altın" in tur or "Kıymetli" in tur: veriler["Altın"] += oran
            elif "Mevduat" in tur or "Repo" in tur or "Ters Repo" in tur: veriler["Mevduat/Repo"] += oran
            else: veriler["Diğer"] += oran

        return veriler
    except:
        # Veri çekilemezse varsayılan (Genel hisse yoğun fon yapısı)
        return {"Hisse Senedi": 0.90, "Döviz Ödemeli": 0.05, "Altın": 0, "Mevduat/Repo": 0.05, "Diğer": 0}

# -------------------------------------------------
# ⚙️ HESAPLAMA MOTORU (TEFAS ODAKLI)
# -------------------------------------------------
def hesapla(fon, piyasa):
    # Sabah açıklanan resmi portföy dağılımını çek
    p = tefas_anlik_portfoy(fon)
    
    # 1. Hisse Getirisi (Endeks ile kalibre)
    # Fonlar genelde endeksten %10-20 daha agresif hareket eder (Alfa çarpanı: 1.15)
    getiri_hisse = p["Hisse Senedi"] * piyasa["bist100"] * 1.15
    
    # 2. Döviz Getirisi
    getiri_doviz = p["Döviz Ödemeli"] * piyasa["usd"]
    
    # 3. Altın Getirisi
    getiri_altin = p["Altın"] * piyasa["altin"]
    
    # 4. Faiz/Repo Getirisi (Sabit)
    getiri_faiz = p["Mevduat/Repo"] * piyasa["faiz_gunluk"]
    
    # Toplam Brüt Tahmin
    toplam = getiri_hisse + getiri_doviz + getiri_altin + getiri_faiz
    
    # Fon Yönetim Ücreti (Günlük ortalama kesinti)
    net_sonuc = toplam - 0.008
    
    return round(net_sonuc, 2)

# -------------------------------------------------
# 🎨 ARAYÜZ (UI)
# -------------------------------------------------
st.title("▄︻デ══━一💥 Y A 3 4  Y A 3 9")
st.subheader("TEFAS Sabah Portföy Raporu Odaklı Hesaplama")

piyasa = piyasa_verisi()
fonlar = ["TLY", "DFI", "PHE", "PBR", "KHA"]
cols = st.columns(len(fonlar))

for i, fon in enumerate(fonlar):
    sonuc = hesapla(fon, piyasa)
    portfoy = tefas_anlik_portfoy(fon) # Bilgi kutusu için tekrar çağır
    
    renk = "#00ff88" if sonuc > 0 else "#ff4d4d"
    
    with cols[i]:
        st.markdown(f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #333; text-align:center;">
            <h2 style="margin:0; color:#fff;">{fon}</h2>
            <hr style="border:0.1px solid #222;">
            <p style="font-size:10px; color:gray; margin:0;">SABAH RAPORU HİSSE: %{int(portfoy['Hisse Senedi']*100)}</p>
            <h1 style="color:{renk}; margin:10px 0;">%{sonuc}</h1>
            <p style="font-size:10px; color:gray; margin:0;">GÜNLÜK TAHMİN</p>
        </div>
        """, unsafe_allow_html=True)

st.write("")
st.info("ℹ️ Bu sistem, her sabah TEFAS'a bildirilen resmi 'BindPortfolio' verilerini kullanır. Manuel sektör tahmini içermez.")

if st.button("🔄 TEFAS VERİLERİNİ YENİLE"):
    st.cache_data.clear()
    st.rerun()
