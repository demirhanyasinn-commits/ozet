import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone

# 1. SAYFA AYARLARI
st.set_page_config(page_title="YA 34 YA 39 | Fon Takip", layout="wide", initial_sidebar_state="collapsed")

# 2. GÖRSEL STİLLER
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .market-chip {
        padding: 8px 18px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
        margin-right: 12px;
        font-size: 0.95em;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stButton>button {
        background-color: #10b981;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #059669;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ANA BAŞLIK
st.markdown("""
    <div style="text-align: left; margin-top: -25px; margin-bottom: 5px;">
        <h1 style="font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 65px; color: #ffffff; letter-spacing: 12px; margin-bottom: 0;">
            YA 34 YA 39
        </h1>
    </div>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

# 4. PİYASA VERİSİ ÇEKME
@st.cache_data(ttl=1) 
def get_market_data():
    try:
        bist = yf.download("XU100.IS", period="5d", interval="1m", progress=False)
        usd = yf.download("USDTRY=X", period="5d", interval="1m", progress=False)
        
        bist_pc = float(((bist['Close'].iloc[-1] / bist['Close'].iloc[-2]) - 1) * 100) if not bist.empty else 0.0
        usd_pc = float(((usd['Close'].iloc[-1] / usd['Close'].iloc[-2]) - 1) * 100) if not usd.empty else 0.0
        return bist_pc, usd_pc
    except:
        return 0.0, 0.0

# GÜNCELLEME BUTONU VE SAAT HESABI
# İstanbul saati için UTC+3 ayarı
tr_tz = timezone(timedelta(hours=3))
simdi_tr = datetime.now(tr_tz).strftime('%H:%M:%S')

col1, col2 = st.columns([0.82, 0.18])
with col2:
    if st.button("🔄 Verileri Güncelle"):
        st.cache_data.clear()
        st.rerun()

bist_pc, usd_pc = get_market_data()

# 5. PİYASA ÖZETİ
bist_color = "#10b981" if bist_pc >= 0 else "#ef4444"
usd_color = "#10b981" if usd_pc >= 0 else "#ef4444"

st.markdown(f"""
<div style="display: flex; align-items: center; margin-bottom: 35px; gap: 10px; margin-top: 10px;">
    <h2 style="color: white; margin: 0; margin-right: 25px; font-family: sans-serif; opacity: 0.9; font-size: 1.6em; font-weight: 300;">Piyasa Özeti</h2>
    <div class="market-chip" style="background-color: {bist_color}22; color: {bist_color}; border-color: {bist_color}44;">
        BIST100: {bist_pc:+.2f}%
    </div>
    <div class="market-chip" style="background-color: {usd_color}22; color: {usd_color}; border-color: {usd_color}44;">
        USDTRY: {usd_pc:+.2f}%
    </div>
</div>
""", unsafe_allow_html=True)

# 6. FONLAR
funds = {
    "TLY": {"name": "Tera Portföy Birinci Serbest", "beta": 0.88, "fixed": 0.04},
    "DFI": {"name": "Atlas Portföy Serbest Fon", "beta": 0.75, "fixed": 0.06},
    "PHE": {"name": "Pusula Portföy Hisse Fon", "beta": 1.08, "fixed": 0.01},
    "PBR": {"name": "Pusula Portföy Birinci Değişken", "beta": 0.45, "fixed": 0.16},
    "KHA": {"name": "İstanbul Portföy Birinci Değişken", "beta": 0.58, "fixed": 0.14}
}

# 7. KARTLAR
cols = st.columns(len(funds))
for i, (code, info) in enumerate(funds.items()):
    prediction = (bist_pc * info['beta']) + info['fixed']
    with cols[i]:
        bg, border, glow = ("#064e3b", "#10b981", "rgba(16, 185, 129, 0.25)") if prediction >= 0 else ("#450a0a", "#ef4444", "rgba(239, 68, 68, 0.25)")
        st.markdown(f"""
        <div style="background-color: {bg}; padding: 25px 20px; border-radius: 20px; border-left: 8px solid {border}; min-height: 220px; box-shadow: 0 10px 25px {glow};">
            <span style="color: #ffffff; font-weight: 800; font-size: 1.6em;">{code}</span>
            <p style="color: #ffffff; font-size: 0.85em; opacity: 0.8; height: 45px;">{info['name']}</p>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); margin-top: 15px; padding-top: 15px;">
                <p style="color: #ffffff; font-size: 0.7em; font-weight: bold; opacity: 0.6;">GÜNLÜK BEKLENTİ</p>
                <h2 style="color: #ffffff; margin: 0; font-size: 2.3em; font-weight: 900;">%{prediction:+.2f}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)
st.markdown(f"""
    <div style="background-color: rgba(255,255,255,0.05); padding: 10px 20px; border-radius: 10px; display: inline-block;">
        <span style="color: #10b981;">●</span> 
        <span style="color: white; font-size: 0.9em; font-weight: bold;"> Son Güncelleme : {simdi_tr}</span>
    </div>
""", unsafe_allow_html=True)
