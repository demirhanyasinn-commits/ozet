import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import requests
import random
import re

# 1. SAYFA AYARLARI
st.set_page_config(page_title="YA 34 YA 39 | Fon Takip", layout="wide", initial_sidebar_state="collapsed")

# 2. ÖZEL CSS
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .market-chip {
        padding: 10px 20px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
        margin-right: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stButton>button {
        background-color: #10b981;
        color: white;
        border-radius: 12px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BAŞLIK
st.markdown("""
    <div style="text-align: left; margin-top: -30px; margin-bottom: 5px;">
        <h1 style="font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 68px; color: #ffffff; letter-spacing: 12px;">
            YA 34 YA 39
        </h1>
    </div>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

# 4. GOOGLE FINANCE ÜZERİNDEN VERİ ÇEKME (EN HIZLI METOT)
@st.cache_data(ttl=1)
def get_google_finance_data(symbol):
    try:
        # Google Finance sayfasını doğrudan sorgula
        url = f"https://www.google.com/finance/quote/{symbol}"
        response = requests.get(url, headers={'User-Agent': f'Mozilla/5.0-{random.randint(100,999)}'})
        
        # Değişim yüzdesini HTML içinden çek (Regex ile)
        # Örnek: data-percentage-change="+0.52"
        pattern = r'data-percentage-change="([^"]+)"'
        matches = re.findall(pattern, response.text)
        
        if matches:
            return float(matches[0].replace('%', ''))
        return 0.0
    except:
        return 0.0

# 5. GÜNCELLEME PANELİ
tr_tz = timezone(timedelta(hours=3))
simdi_tr = datetime.now(tr_tz).strftime('%H:%M:%S')

col1, col_btn = st.columns([0.8, 0.2])

# BIST ve USD verilerini Google üzerinden çek
# BIST: INDEXBIST:XU100, USD: USD-TRY
bist_pc = get_google_finance_data("XU100:INDEXBIST")
usd_pc = get_google_finance_data("USD-TRY")

with col_btn:
    if st.button("🔄 VERİLERİ ZORLA GÜNCELLE"):
        st.cache_data.clear()
        st.rerun()

# 6. PİYASA ÖZETİ
b_col = "#10b981" if bist_pc >= 0 else "#ef4444"
st.markdown(f"""
<div style="display: flex; align-items: center; margin-bottom: 40px;">
    <h2 style="color: white; margin-right: 20px; opacity: 0.8;">Piyasa Özeti</h2>
    <div class="market-chip" style="background-color: {b_col}22; color: {b_col}; border-color: {b_col}44;">
        BIST100: {bist_pc:+.2f}%
    </div>
</div>
""", unsafe_allow_html=True)

# 7. FON KATSAYILARI (FVT ve fontahmin.com.tr Görsellerine Göre Optimize Edildi)
funds = {
    "TLY": {"name": "Tera Portföy Birinci Serbest", "beta": 0.98, "fixed": 0.04},
    "DFI": {"name": "Atlas Portföy Serbest Fon", "beta": 0.85, "fixed": 0.06},
    "PHE": {"name": "Pusula Portföy Hisse Fon", "beta": 1.20, "fixed": 0.01},
    "PBR": {"name": "Pusula Portföy Birinci Değişken", "beta": 0.50, "fixed": 0.17},
    "KHA": {"name": "İstanbul Portföy Birinci Değişken", "beta": 0.65, "fixed": 0.14}
}

# 8. KARTLAR
cols = st.columns(len(funds))
for i, (code, info) in enumerate(funds.items()):
    prediction = (bist_pc * info['beta']) + info['fixed']
    with cols[i]:
        bg, border = ("#064e3b", "#10b981") if prediction >= 0 else ("#450a0a", "#ef4444")
        st.markdown(f"""
        <div style="background-color: {bg}; padding: 25px; border-radius: 20px; border-left: 10px solid {border}; min-height: 240px;">
            <span style="color: #ffffff; font-weight: 800; font-size: 1.8em;">{code}</span>
            <p style="color: #ffffff; font-size: 0.85em; opacity: 0.8; height: 50px;">{info['name']}</p>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); margin-top: 20px; padding-top: 20px;">
                <h2 style="color: #ffffff; margin: 0; font-size: 2.5em; font-weight: 900;">%{prediction:+.2f}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f"""
    <div style="margin-top: 30px; padding: 10px; color: gray;">
        🚀 <b>Google Finance Altyapısı</b> | Son Güncelleme: {simdi_tr}
    </div>
""", unsafe_allow_html=True)
