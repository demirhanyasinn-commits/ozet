import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
import requests
import random

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="YA 34 YA 39 | Fon Takip", layout="wide", initial_sidebar_state="collapsed")

# 2. ÖZELLEŞTİRİLMİŞ TASARIM (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .market-chip {
        padding: 10px 20px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
        margin-right: 15px;
        font-size: 1em;
        border: 1px solid rgba(255,255,255,0.1);
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background-color: #10b981;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #059669;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ANA BAŞLIK
st.markdown("""
    <div style="text-align: left; margin-top: -30px; margin-bottom: 5px;">
        <h1 style="
            font-family: 'Orbitron', sans-serif; 
            font-weight: 900; 
            font-size: 68px; 
            color: #ffffff; 
            text-shadow: 0 0 20px rgba(255,255,255,0.15);
            letter-spacing: 12px;
            margin-bottom: 0;
        ">
            YA 34 YA 39
        </h1>
    </div>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

# 4. GÜÇLENDİRİLMİŞ VERİ ÇEKME FONKSİYONU (YENİLENMİŞ)
@st.cache_data(ttl=1)
def get_market_data():
    try:
        rand_val = random.randint(1000, 9999)
        session = requests.Session()
        session.headers.update({'User-Agent': f'Mozilla/5.0-{rand_val}'})
        
        bist_t = yf.Ticker("XU100.IS", session=session)
        usd_t = yf.Ticker("USDTRY=X", session=session)
        
        # History ile son dakikayı zorlayalım
        b_hist = bist_t.history(period="1d", interval="1m")
        u_hist = usd_t.history(period="1d", interval="1m")
        
        if not b_hist.empty:
            b_price = b_hist['Close'].iloc[-1]
            b_prev = bist_t.fast_info.get('previous_close', b_hist['Open'].iloc[0])
            b_pc = ((b_price / b_prev) - 1) * 100
        else:
            b_pc = 0.60 # Veri gelmezse anlık gördüğünü buraya elle yazabilirsin
            
        if not u_hist.empty:
            u_price = u_hist['Close'].iloc[-1]
            u_prev = usd_t.fast_info.get('previous_close', u_hist['Open'].iloc[0])
            u_pc = ((u_price / u_prev) - 1) * 100
        else:
            u_pc = 0.05

        return float(b_pc), float(u_pc)
    except:
        return 0.60, 0.05

# 5. GÜNCELLEME PANELİ
tr_tz = timezone(timedelta(hours=3))
simdi_tr = datetime.now(tr_tz).strftime('%H:%M:%S')

col_title, col_btn = st.columns([0.80, 0.20])
bist_pc, usd_pc = get_market_data()

with col_btn:
    if st.button("🔄 VERİLERİ GÜNCELLE"):
        st.cache_data.clear()
        st.rerun()

# 6. PİYASA ÖZETİ
b_col = "#10b981" if bist_pc >= 0 else "#ef4444"
u_col = "#10b981" if usd_pc >= 0 else "#ef4444"

st.markdown(f"""
<div style="display: flex; align-items: center; margin-bottom: 40px; gap: 10px; margin-top: 5px;">
    <h2 style="color: white; margin: 0; margin-right: 30px; font-family: sans-serif; opacity: 0.8; font-size: 1.5em; font-weight: 300;">Piyasa Özeti</h2>
    <div class="market-chip" style="background-color: {b_col}22; color: {b_col}; border-color: {b_col}44;">
        BIST100: {bist_pc:+.2f}%
    </div>
    <div class="market-chip" style="background-color: {u_col}22; color: {u_col}; border-color: {u_col}44;">
        USDTRY: {usd_pc:+.2f}%
    </div>
</div>
""", unsafe_allow_html=True)

# 7. FON TANIMLARI
# FVT verilerine daha yakın tahminler için güncellenmiş katsayılar
funds = {
    "TLY": {"name": "Tera Portföy Birinci Serbest", "beta": 0.90, "fixed": 0.04}, # Beta biraz artırıldı
    "DFI": {"name": "Atlas Portföy Serbest Fon", "beta": 0.78, "fixed": 0.06},
    "PHE": {"name": "Pusula Portföy Hisse Fon", "beta": 1.15, "fixed": 0.01},
    "PBR": {"name": "Pusula Portföy Birinci Değişken", "beta": 0.40, "fixed": 0.18}, # Sabit getiri payı artırıldı
    "KHA": {"name": "İstanbul Portföy Birinci Değişken", "beta": 0.52, "fixed": 0.16}
}

# 8. FON KARTLARI
cols = st.columns(len(funds))
for i, (code, info) in enumerate(funds.items()):
    prediction = (bist_pc * info['beta']) + info['fixed']
    with cols[i]:
        bg, border, glow = ("#064e3b", "#10b981", "rgba(16, 185, 129, 0.3)") if prediction >= 0 else ("#450a0a", "#ef4444", "rgba(239, 68, 68, 0.3)")
        st.markdown(f"""
        <div style="background-color: {bg}; padding: 28px 22px; border-radius: 24px; border-left: 10px solid {border}; min-height: 240px; box-shadow: 0 12px 30px {glow};">
            <span style="color: #ffffff; font-weight: 800; font-size: 1.8em; letter-spacing: -1px;">{code}</span>
            <p style="color: #ffffff; font-size: 0.85em; opacity: 0.8; height: 50px; margin-top: 15px;">{info['name']}</p>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); margin-top: 20px; padding-top: 20px;">
                <p style="color: #ffffff; font-size: 0.75em; font-weight: bold; opacity: 0.5;">GÜNLÜK BEKLENTİ</p>
                <h2 style="color: #ffffff; margin: 0; font-size: 2.5em; font-weight: 900;">%{prediction:+.2f}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 9. ALT BİLGİ
st.write("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
    <div style="background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 12px 25px; border-radius: 15px; display: inline-block;">
        <span style="color: #10b981; font-size: 1.2em;">●</span> 
        <span style="color: white; font-size: 1em; font-weight: bold;"> Son Güncelleme (İstanbul): {simdi_tr}</span>
        <span style="color: gray; font-size: 0.8em; margin-left: 15px;">| Veriler yfinance üzerinden 15dk gecikmeli çekilmektedir.</span>
    </div>
""", unsafe_allow_html=True)
