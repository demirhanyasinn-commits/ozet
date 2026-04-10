import streamlit as st
import pandas as pd
import yfinance as yf
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# Sayfa Ayarları
st.set_page_config(page_title="PRO Fon Takip", layout="wide", initial_sidebar_state="collapsed")

# Premium CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #0e0e0e; font-family: 'Inter', sans-serif; }
    .ticker-container { background-color: #161616; padding: 12px 20px; border-radius: 12px; display: flex; justify-content: space-between; border: 1px solid #262626; margin-bottom: 25px; overflow-x: auto; }
    .ticker-item { text-align: center; min-width: 125px; border-right: 1px solid #333; }
    .ticker-item:last-child { border-right: none; }
    .fund-card { background-color: #161616; border-radius: 12px; padding: 22px; margin-bottom: 20px; border-left: 5px solid #007bff; border: 1px solid #262626; border-left: 5px solid #007bff; }
    .est-value { color: #00ff88; font-size: 2.2rem; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def fetch_data():
    # Piyasadan canlı veriler (BIST, USD, Altın)
    symbols = {"USDTRY": "USDTRY=X", "BIST100": "XU100.IS"}
    market = {}
    for k, s in symbols.items():
        try:
            h = yf.Ticker(s).history(period="2d")
            last, prev = h['Close'].iloc[-1], h['Close'].iloc[-2]
            market[k] = {"val": last, "pct": ((last - prev) / prev) * 100}
        except: market[k] = {"val": 0, "pct": 0}
    return market

def main():
    m = fetch_data()
    bist_pct = m["BIST100"]["pct"]
    usd_pct = m["USDTRY"]["pct"]

    # GÖRSELDEKİ FORMÜLE GÖRE GÜNCEL PORTFÖY YAPISI
    # Fonun içindeki ters hareket eden hisseleri (TPKGY vb.) dengelemek için 
    # Hisse Etki Katsayısını (Beta) 0.65 - 0.70 bandına çekiyoruz.
    portfoy = {
        "TLY": {"Hisse": 0.68, "Dolar": 0.05, "Nakit": 0.27, "ad": "Tera Portföy Birinci Serbest"},
        "DFI": {"Hisse": 0.15, "Dolar": 0.70, "Nakit": 0.15, "ad": "Atlas Portföy Serbest Fon"},
        "PHE": {"Hisse": 0.72, "Dolar": 0.03, "Nakit": 0.25, "ad": "Pusula Portföy Hisse Fonu"},
        "PBR": {"Hisse": 0.35, "Dolar": 0.40, "Nakit": 0.25, "ad": "Pusula Portföy Birinci Değişken"}
    }

    st.markdown(f'<div class="ticker-container">BIST100: %{bist_pct:+.2f} | USDTRY: %{usd_pct:+.2f}</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, (code, c) in enumerate(portfoy.items()):
        # HASSAS HESAPLAMA
        # 1. Hisse getirisi (Endeksten arındırılmış, fon içi hisse dengesi gözetilmiş katsayı)
        hisse_etki = c["Hisse"] * bist_pct * 0.78 
        
        # 2. Dolar etkisi
        dolar_etki = c["Dolar"] * usd_pct
        
        # 3. Nakit/Repo sabit getirisi (Günlük %0.13 civarı)
        nakit_etki = c["Nakit"] * 0.13
        
        # Toplam Tahmin
        tahmin = hisse_etki + dolar_etki + nakit_etki

        with cols[i]:
            st.markdown(f"""
                <div class="fund-card">
                    <div style="color:white; font-weight:700;">{code}</div>
                    <div style="color:#666; font-size:0.7rem; margin-bottom:10px;">{c['ad']}</div>
                    <div style="color:#999; font-size:0.7rem;">GÜNLÜK BEKLENTİ</div>
                    <div class="est-value">%{tahmin:+.2f}</div>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
