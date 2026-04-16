import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

# Sayfa Ayarları
st.set_page_config(page_title="YA 34 YA 39 | Terminal", layout="wide")

# Tasarım CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; }
    .tahmin-kart {
        background: linear-gradient(145deg, #064e3b, #022c22);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #10b981;
        color: white;
        min-height: 220px;
        margin-bottom: 10px;
    }
    .fon-kodu { font-size: 24px; font-weight: bold; }
    .fon-adi { font-size: 12px; color: #a7f3d0; margin-bottom: 25px; min-height: 40px; }
    .tahmin-etiket { font-size: 10px; font-weight: bold; opacity: 0.8; }
    .tahmin-deger { font-size: 32px; font-weight: bold; margin-top: 5px; }
    
    /* Buton Stilini Görseldeki Maviye Benzetme */
    div.stButton > button {
        background-color: #f2f2f2;
        color: black;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        float: left;
    }

    # Bu kısmı CSS style içine ekle:
"""
.tahmin-deger { 
    font-size: 32px; 
    font-weight: bold; 
    margin-top: 10px;
    text-shadow: 0px 0px 10px rgba(16, 185, 129, 0.5); /* Sayılara hafif bir parlama verir */
}
.tahmin-kart:hover {
    border: 1px solid #00f2ff; /* Kartın üzerine gelince mavi bir çerçeve belirir */
    transform: scale(1.02);
    transition: all 0.3s ease;
}
"""
    </style>
    """, unsafe_allow_html=True)

# 1. VERİ ÇEKME FONKSİYONU
@st.cache_data(ttl=60)
def get_bist_data():
    try:
        ticker = yf.Ticker("XU100.IS")
        data = ticker.history(period="2d")
        if len(data) >= 2:
            current_price = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            change = ((current_price - prev_close) / prev_close) * 100
            return float(change)
        return 0.35
    except:
        return 0.35

bist_degisim = get_bist_data()

# 2. ÜST BAŞLIK VE GÜNCELLEME BUTONU
header_col1, header_col2 = st.columns([0.8, 0.2])

with header_col1:
    st.markdown("<h1 style='color:white; font-family: monospace; letter-spacing: 5px; margin-top:0;'>YA 34 YA 39</h1>", unsafe_allow_html=True)

with header_col2:
    if st.button("🔄 VERİLERİ YENİLE"):
        st.cache_data.clear() # Önbelleği temizleyip yeni veri çeker
        st.rerun()

# 3. BIST100 ENDEKS KUTUSU
st.markdown(f"""
    <div style="background-color: #1e293b; width: 140px; padding: 10px; border-radius: 10px; border-left: 5px solid #10b981; margin-bottom: 30px;">
        <p style="color: #94a3b8; font-size: 10px; margin: 0;">BIST100 ENDEKS</p>
        <p style="color: #4ade80; font-size: 18px; font-weight: bold; margin: 0;">%+{bist_degisim:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

# 4. FON KARTLARI
fon_ayarlari = {
    "TLY": {"ad": "Tera Portföy Birinci Serbest", "katsayi": 0.77},
    "DFI": {"ad": "Atlas Portföy Serbest Fon", "katsayi": 0.88},
    "PHE": {"ad": "Pusula Portföy Hisse Fon", "katsayi": 0.91},
    "PBR": {"ad": "Pusula Portföy Birinci Değişken", "katsayi": 0.31},
    "KHA": {"ad": "İstanbul Portföy Birinci Değişken", "katsayi": 2.91}
}

cols = st.columns(5)
for i, (kod, info) in enumerate(fon_ayarlari.items()):
    hesaplanan_getiri = float(bist_degisim) * info["katsayi"]
    with cols[i]:
        st.markdown(f"""
            <div class="tahmin-kart">
                <div class="fon-kodu">{kod}</div>
                <div class="fon-adi">{info['ad']}</div>
                <div class="tahmin-etiket">GÜN SONU TAHMİNİ</div>
                <div class="tahmin-deger">%+{hesaplanan_getiri:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

# 5. ALT BİLGİ VE TÜRKİYE SAATİ
tr_saati = datetime.now(pytz.timezone('Europe/Istanbul')).strftime('%H:%M:%S')

st.markdown(f"""
    <hr style="border-color: #1e293b; margin-top: 50px;">
    <p style='color: gray; font-size: 12px;'>
        🕒 İstanbul Saati: {tr_saati} | Veriler Google/Yahoo üzerinden 15dk gecikmeli gelmektedir. Hesaplamalar tahmindir.
    </p>
    """, unsafe_allow_html=True)
