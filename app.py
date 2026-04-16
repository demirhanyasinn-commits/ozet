import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

# 1. SAYFA AYARLARI VE CSS (Dinamik Renkler İçin Geliştirildi)
st.set_page_config(page_title="YA 34 YA 39 | Akıllı Terminal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; }
    
    /* Pozitif (Yeşil) Kart Tasarımı */
    .card-positive {
        background: linear-gradient(145deg, #064e3b, #022c22);
        border-radius: 15px; padding: 20px; border: 1px solid #10b981;
        color: white; min-height: 200px; transition: 0.3s;
    }
    
    /* Negatif (Kırmızı) Kart Tasarımı */
    .card-negative {
        background: linear-gradient(145deg, #450a0a, #2d0606);
        border-radius: 15px; padding: 20px; border: 1px solid #ef4444;
        color: white; min-height: 200px; transition: 0.3s;
    }

    .fon-kodu { font-size: 24px; font-weight: bold; }
    .fon-adi { font-size: 11px; color: #94a3b8; margin-bottom: 20px; height: 35px; }
    .tahmin-etiket { font-size: 10px; font-weight: bold; opacity: 0.7; }
    .tahmin-deger { font-size: 34px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ ÇEKME MOTORU
@st.cache_data(ttl=60)
def get_market_data():
    try:
        # BIST100 ve USDTRY verilerini çekiyoruz
        bist = yf.Ticker("XU100.IS").history(period="2d")
        usd = yf.Ticker("USDTRY=X").history(period="2d")
        
        bist_chg = ((bist['Close'].iloc[-1] - bist['Close'].iloc[-2]) / bist['Close'].iloc[-2]) * 100
        usd_chg = ((usd['Close'].iloc[-1] - usd['Close'].iloc[-2]) / usd['Close'].iloc[-2]) * 100
        return float(bist_chg), float(usd_chg)
    except:
        return 0.35, 0.05

bist_degisim, usd_degisim = get_market_data()

# 3. FON PARAMETRELERİ (Önceki sapmalara göre optimize edildi)
# Alfa: Sabit getiri payı, Beta: Endeks duyarlılığı
fon_ayarlari = {
    "TLY": {"ad": "Tera Portföy Birinci Serbest", "alfa": 0.12, "beta": 1.45},
    "DFI": {"ad": "Atlas Portföy Serbest Fon", "alfa": 0.05, "beta": 0.95},
    "PHE": {"ad": "Pusula Portföy Hisse Fon", "alfa": 0.02, "beta": 1.10},
    "PBR": {"ad": "Pusula Portföy Birinci Değişken", "alfa": 0.10, "beta": 0.35},
    "KHA": {"ad": "İstanbul Portföy Birinci Değişken", "alfa": 0.08, "beta": 0.75}
}

# 4. ÜST BAŞLIK VE YENİLEME
c1, c2 = st.columns([0.8, 0.2])
with c1:
    st.markdown("<h1 style='color:white; font-family: monospace; letter-spacing: 5px;'>YA 34 YA 39</h1>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 VERİLERİ YENİLE"):
        st.cache_data.clear()
        st.rerun()

# Piyasa Göstergeleri
st.markdown(f"""
    <div style="display: flex; gap: 15px; margin-bottom: 25px;">
        <div style="background:#1e293b; padding:10px; border-radius:10px; border-left:4px solid {'#10b981' if bist_degisim >= 0 else '#ef4444'};">
            <p style="color:#94a3b8; font-size:10px; margin:0;">BIST100</p>
            <p style="color:{'#4ade80' if bist_degisim >= 0 else '#f87171'}; font-size:16px; font-weight:bold; margin:0;">%{"+" if bist_degisim >= 0 else ""}{bist_degisim:.2f}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. DİNAMİK RENKLİ FON KARTLARI
cols = st.columns(5)
for i, (kod, info) in enumerate(fon_ayarlari.items()):
    # Hesaplama: (Borsa * Beta) + Sabit Getiri
    tahmin = (bist_degisim * info['beta']) + info['alfa']
    
    # Renk Sınıfı Belirleme
    card_class = "card-positive" if tahmin >= 0 else "card-negative"
    text_color = "#4ade80" if tahmin >= 0 else "#f87171"
    
    with cols[i]:
        st.markdown(f"""
            <div class="{card_class}">
                <div class="fon-kodu">{kod}</div>
                <div class="fon-adi">{info['ad']}</div>
                <div class="tahmin-etiket">GÜN SONU TAHMİNİ</div>
                <div class="tahmin-deger" style="color: {text_color};">%{"+" if tahmin >= 0 else ""}{tahmin:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

# 6. ALT BİLGİ VE SAAT
tr_saati = datetime.now(pytz.timezone('Europe/Istanbul')).strftime('%H:%M:%S')
st.markdown(f"""
    <br><hr style="border-color: #1e293b;">
    <p style='color: gray; font-size: 12px;'>
        🕒 İstanbul Saati: {tr_saati} | Kart renkleri fonun pozitif/negatif durumuna göre anlık değişmektedir.
    </p>
    """, unsafe_allow_html=True)
