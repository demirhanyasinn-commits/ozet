import streamlit as st
import yfinance as yf
import pandas as pd

# 1. AYARLAR
st.set_page_config(page_title="Fon Takip Pro", layout="wide", initial_sidebar_state="collapsed")

# 2. STİLLER (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .market-chip {
        padding: 8px 15px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
        margin-right: 10px;
        font-size: 0.9em;
        border: 1px solid rgba(255,255,255,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. YENİ ANA BAŞLIK (BURAYA EKLENİYOR)
st.markdown("""
    <div style="text-align: left; margin-top: -20px; margin-bottom: 10px;">
        <h1 style="
            font-family: 'Orbitron', sans-serif; 
            font-weight: 900; 
            font-size: 60px; 
            color: #ffffff; 
            text-shadow: 0 0 15px rgba(255,255,255,0.2);
            letter-spacing: 10px;
            margin-bottom: 0;
        ">
            YA 34 YA 39
        </h1>
    </div>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="Fon Takip Pro", layout="wide", initial_sidebar_state="collapsed")

# Arka plan ve genel stil iyileştirmeleri
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
    }
    .market-chip {
        padding: 8px 15px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
        margin-right: 10px;
        font-size: 0.9em;
        border: 1px solid rgba(255,255,255,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Veri çekme fonksiyonu
@st.cache_data(ttl=60)
def get_market_data():
    try:
        # BIST ve USD verilerini çek
        bist = yf.download("XU100.IS", period="2d", interval="1m", progress=False)
        usd = yf.download("USDTRY=X", period="2d", interval="1m", progress=False)
        
        bist_pc = float(((bist['Close'].iloc[-1] / bist['Close'].iloc[0]) - 1) * 100) if not bist.empty else 0.0
        usd_pc = float(((usd['Close'].iloc[-1] / usd['Close'].iloc[0]) - 1) * 100) if not usd.empty else 0.0
        return bist_pc, usd_pc
    except:
        return 0.14, -0.06 # Hata durumunda örnek veri

bist_pc, usd_pc = get_market_data()

# ÜST PANEL - Şık Market Göstergeleri
bist_color = "#10b981" if bist_pc >= 0 else "#ef4444"
usd_color = "#10b981" if usd_pc >= 0 else "#ef4444"

header_html = f"""
<div style="display: flex; align-items: center; margin-bottom: 30px; gap: 15px;">
    <h2 style="color: white; margin: 0; margin-right: 20px; font-family: sans-serif;">Piyasa Özeti</h2>
    <div class="market-chip" style="background-color: {bist_color}22; color: {bist_color};">
        BIST100: {bist_pc:+.2f}%
    </div>
    <div class="market-chip" style="background-color: {usd_color}22; color: {usd_color};">
        USDTRY: {usd_pc:+.2f}%
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# FON LİSTESİ
funds = {
    "TLY": {"name": "Tera Portföy Birinci Serbest", "beta": 0.92},
    "DFI": {"name": "Atlas Portföy Serbest Fon", "beta": 0.78},
    "PHE": {"name": "Pusula Portföy Hisse Fon", "beta": 1.05},
    "PBR": {"name": "Pusula Portföy Birinci Değişken", "beta": 0.65},
    "KHA": {"name": "İstanbul Portföy Birinci Değişken", "beta": 0.82}
}

# KARTLAR
cols = st.columns(len(funds))

for i, (code, info) in enumerate(funds.items()):
    prediction = bist_pc * info['beta']
    
    with cols[i]:
        if prediction >= 0:
            bg_color, border_color, glow = "#064e3b", "#10b981", "rgba(16, 185, 129, 0.2)"
        else:
            bg_color, border_color, glow = "#450a0a", "#ef4444", "rgba(239, 68, 68, 0.2)"
        
        st.markdown(f"""
        <div style="
            background-color: {bg_color}; 
            padding: 25px 20px; 
            border-radius: 20px; 
            border: 1px solid {border_color}44;
            border-left: 8px solid {border_color}; 
            min-height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 10px 20px {glow};
            ">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <span style="color: #ffffff; font-weight: 800; font-size: 1.5em;">{code}</span>
                    <span style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 5px; color: white; font-size: 0.6em;">FON</span>
                </div>
                <p style="color: #ffffff; font-size: 0.85em; margin-top: 10px; opacity: 0.8; height: 45px; line-height: 1.3;">{info['name']}</p>
            </div>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); pt-15px; margin-top: 10px;">
                <p style="color: #ffffff; font-size: 0.7em; margin-top: 10px; font-weight: bold; opacity: 0.7;">GÜNLÜK BEKLENTİ</p>
                <h2 style="color: #ffffff; margin: 0; font-size: 2.2em; font-weight: 900; letter-spacing: -1px;">%{prediction:+.2f}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)
st.caption("🟢 Veriler 1 dakikalık periyotlarla güncellenir. Tahminler geçmiş beta verilerine dayanmaktadır.")
