import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

# 1. TASARIM: Dinamik Renk CSS
st.set_page_config(page_title="YA 34 YA 39 | Terminal", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    /* Pozitif Kart Tasarımı */
    .card-pos {
        background: linear-gradient(145deg, #064e3b, #022c22);
        border-radius: 15px; padding: 20px; border: 1px solid #10b981;
        color: white; min-height: 200px; transition: 0.3s;
    }
    /* Negatif Kart Tasarımı */
    .card-neg {
        background: linear-gradient(145deg, #450a0a, #2d0606);
        border-radius: 15px; padding: 20px; border: 1px solid #ef4444;
        color: white; min-height: 200px; transition: 0.3s;
    }
    .tahmin-deger { font-size: 34px; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. HASSAS VERİ ÇEKME MOTORU
@st.cache_data(ttl=60)
def get_precise_data():
    try:
        # Veriyi 1 dakikalık çekerek o günkü net değişimi buluyoruz
        ticker = yf.Ticker("XU100.IS")
        df = ticker.history(period="1d", interval="1m")
        if df.empty:
            # Seans kapalıysa dünkü veriye bak
            df = ticker.history(period="2d")
            change = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        else:
            # Açılış fiyatına göre gerçek değişim
            change = ((df['Close'].iloc[-1] - df['Open'].iloc[0]) / df['Open'].iloc[0]) * 100
        return float(change)
    except:
        return 0.0

bist_degisim = get_precise_data()

# 3. FON PARAMETRELERİ (Öğrenen Katsayılar)
# Endeks -0.54 iken fonun -0.80 yazmaması için beta değerlerini 1'in altına veya civarına çekiyoruz.
fon_ayarlari = {
    "TLY": {"ad": "Tera 1. Serbest", "beta": 0.85, "alfa": 0.08},
    "DFI": {"ad": "Atlas Serbest", "beta": 0.90, "alfa": 0.04},
    "PHE": {"ad": "Pusula Hisse", "beta": 1.02, "alfa": 0.01},
    "PBR": {"ad": "Pusula 1. Değişken", "beta": 0.35, "alfa": 0.12},
    "KHA": {"ad": "İstanbul 1. Değişken", "beta": 0.65, "alfa": 0.06}
}

# 4. ARAYÜZ
st.markdown("<h1 style='color:white; font-family: monospace;'>YA 34 YA 39</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#94a3b8;'>BIST100 Güncel Değişim: <b style='color:#4ade80;'>%{bist_degisim:.2f}</b></p>", unsafe_allow_html=True)

cols = st.columns(5)
for i, (kod, info) in enumerate(fon_ayarlari.items()):
    # Hesaplama: (Borsa * Beta) + Sabit Getiri (Alfa)
    tahmin = (bist_degisim * info['beta']) + info['alfa']
    
    # Renk Sınıfı Belirleme
    card_class = "card-pos" if tahmin >= 0 else "card-neg"
    text_color = "#4ade80" if tahmin >= 0 else "#f87171"
    
    with cols[i]:
        st.markdown(f"""
            <div class="{card_class}">
                <div style="font-size:22px; font-weight:bold;">{kod}</div>
                <div style="font-size:10px; color:#94a3b8; height:40px;">{info['ad']}</div>
                <div style="font-size:10px; opacity:0.7;">GÜN SONU TAHMİNİ</div>
                <div class="tahmin-deger" style="color:{text_color};">%{"+" if tahmin >= 0 else ""}{tahmin:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

# 5. ALT BİLGİ VE YENİLEME
c1, c2 = st.columns([0.8, 0.2])
with c2:
    if st.button("🔄 VERİLERİ ZORLA YENİLE"):
        st.cache_data.clear()
        st.rerun()

tr_saati = datetime.now(pytz.timezone('Europe/Istanbul')).strftime('%H:%M:%S')
st.markdown(f"<p style='color:gray; font-size:12px; margin-top:50px;'>🕒 Son Güncelleme: {tr_saati} | Renkler getiriye göre otomatik değişir.</p>", unsafe_allow_html=True)
