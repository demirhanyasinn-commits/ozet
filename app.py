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
        background-color: #00f2ff;
        color: black;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        float: right;
    }
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
    st.markdown("<h1 style='color:white; font-family:
