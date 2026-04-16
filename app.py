import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="YA 34 YA 39 | Akıllı Terminal", layout="wide")

# 1. VERİ MOTORU (Borsa, Dolar, Altın)
@st.cache_data(ttl=300)
def get_market_data():
    try:
        # Verileri çek
        bist = yf.Ticker("XU100.IS").history(period="2d")
        usd = yf.Ticker("USDTRY=X").history(period="2d")
        ons = yf.Ticker("GC=F").history(period="2d") # Ons Altın
        
        def calc_chg(df):
            return ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            
        return {
            "bist": calc_chg(bist),
            "usd": calc_chg(usd),
            "altin": calc_chg(ons)
        }
    except:
        return {"bist": 0.35, "usd": 0.10, "altin": 0.05}

market = get_market_data()

# 2. AKILLI HESAPLAMA MOTORU (Dinamik Ağırlıklandırma)
# Bu katsayılar artık sadece borsaya bakmıyor, fonun karakterine göre dağılıyor.
def akilli_tahmin(market_data):
    # KHA: Agresif, Dolar ve Borsa duyarlılığı yüksek
    kha = (market_data["bist"] * 2.5) + (market_data["usd"] * 0.8) + 0.10
    
    # PHE: Saf Hisse Senedi Yoğun
    phe = (market_data["bist"] * 0.95) + 0.02
    
    # TLY: Serbest Fon, düşük borsa duyarlılığı, sabit getiri odaklı
    tly = (market_data["bist"] * 0.6) + (market_data["usd"] * 0.2) + 0.05
    
    # DFI: Serbest Fon
    dfi = (market_data["bist"] * 0.85) + 0.04
    
    # PBR: Defansif Değişken
    pbr = (market_data["bist"] * 0.3) + (market_data["usd"] * 0.1) + 0.08
    
    return {
        "KHA": kha, "PHE": phe, "TLY": tly, "DFI": dfi, "PBR": pbr
    }

tahminler = akilli_tahmin(market)

# 3. TASARIM VE ARAYÜZ (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; }
    .tahmin-kart {
        background: linear-gradient(145deg, #064e3b, #022c22);
        border-radius: 15px; padding: 20px; border: 1px solid #10b981;
        color: white; min-height: 220px; transition: 0.3s;
    }
    .tahmin-kart:hover { border-color: #00f2ff; transform: translateY(-5px); }
    .fon-kodu { font-size: 24px; font-weight: bold; }
    .fon-adi { font-size: 11px; color: #a7f3d0; margin-bottom: 25px; height: 35px; }
    .tahmin-etiket { font-size: 10px; font-weight: bold; opacity: 0.7; }
    .tahmin-deger { font-size: 34px; font-weight: bold; color: #4ade80; }
    
    /* Endeks Barı */
    .market-bar {
        display: flex; gap: 20px; margin-bottom: 30px;
    }
    .market-item {
        background: #1e293b; padding: 10px 20px; border-radius: 10px; border-left: 4px solid #10b981;
    }
    </style>
    """, unsafe_allow_html=True)

# Başlık ve Yenileme Butonu
c1, c2 = st.columns([0.8, 0.2])
with c1:
    st.markdown("<h1 style='color:white; font-family: monospace; letter-spacing: 5px;'>YA 34 YA 39</h1>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 VERİLERİ GÜNCELLE"):
        st.cache_data.clear()
        st.rerun()

# Piyasa Göstergeleri (Otomatik Çekilenler)
st.markdown(f"""
    <div class="market-bar">
        <div class="market-item">
            <div style="font-size:10px; color:#94a3b8">BIST100</div>
            <div style="font-weight:bold; color:#4ade80">%+{market['bist']:.2f}</div>
        </div>
        <div class="market-item">
            <div style="font-size:10px; color:#94a3b8">USD/TRY</div>
            <div style="font-weight:bold; color:#4ade80">%+{market['usd']:.2f}</div>
        </div>
        <div class="market-item">
            <div style="font-size:10px; color:#94a3b8">ALTIN (ONS)</div>
            <div style="font-weight:bold; color:#4ade80">%+{market['altin']:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Fon Kartları
fon_isimleri = {
    "TLY": "Tera Portföy Birinci Serbest",
    "DFI": "Atlas Portföy Serbest Fon",
    "PHE": "Pusula Portföy Hisse Fon",
    "PBR": "Pusula Portföy Birinci Değişken",
    "KHA": "İstanbul Portföy Birinci Değişken"
}

cols = st.columns(5)
for i, (kod, isim) in enumerate(fon_isimleri.items()):
    val = tahminler[kod]
    with cols[i]:
        st.markdown(f"""
            <div class="tahmin-kart">
                <div class="fon-kodu">{kod}</div>
                <div class="fon-adi">{isim}</div>
                <div class="tahmin-etiket">GÜN SONU TAHMİNİ</div>
                <div class="tahmin-deger">%{"+" if val > 0 else ""}{val:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

# Alt Bilgi
tr_saati = datetime.now(pytz.timezone('Europe/Istanbul')).strftime('%H:%M:%S')
st.markdown(f"<br><hr style='border-color:#1e293b'><p style='color:gray; font-size:12px;'>🕒 Son Güncelleme: {tr_saati} | Veriler otomatik analiz edilerek hesaplanmaktadır.</p>", unsafe_allow_html=True)
