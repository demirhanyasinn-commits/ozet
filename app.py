import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="Fon Takip", layout="wide", initial_sidebar_state="collapsed")

# Veri çekme fonksiyonu
def get_live_data():
    # BIST100 ve USD/TRY verileri
    bist = yf.Ticker("XU100.IS").history(period="1d")
    usd = yf.Ticker("USDTRY=X").history(period="1d")
    
    bist_change = ((bist['Close'].iloc[-1] / bist['Open'].iloc[-1]) - 1) * 100
    usd_change = ((usd['Close'].iloc[-1] / usd['Open'].iloc[-1]) - 1) * 100
    
    return bist_change, usd_change

# Fon ağırlıklarını tanımla (Örnektir, KAP verilerine göre güncellemelisin)
# Formül: (BIST_Değişim * Hisse_Oranı) + (Repo_Oranı * Günlük_Faiz) + (USD_Değişim * Döviz_Oranı)
def calculate_expectation(bist_pc, usd_pc):
    funds = {
        "TLY": {"name": "Tera Portföy Birinci Serbest", "weight": 0.95},
        "DFI": {"name": "Atlas Portföy Serbest Fon", "weight": 0.80},
        "PHE": {"name": "Pusula Portföy Hisse Fon", "weight": 0.98},
        "PBR": {"name": "Pusula Portföy Birinci Değişken", "weight": 0.70},
        "KHA": {"name": "İstanbul Portföy Birinci Değişken", "weight": 0.85} # Yeni eklenen
    }
    
    results = {}
    for code, info in funds.items():
        # Basit bir hesaplama mantığı: Fonun hisse ağırlığına göre beklenti
        prediction = bist_pc * info['weight']
        results[code] = {"name": info['name'], "val": prediction}
    return results

# UI Kısmı
bist_pc, usd_pc = get_live_data()

st.markdown(f"**BIST100: %{bist_pc:+.2f} | USDTRY: %{usd_pc:+.2f}**")

cols = st.columns(5) # KHA eklendiği için 5 sütun
fund_results = calculate_expectation(bist_pc, usd_pc)

for i, (code, data) in enumerate(fund_results.items()):
    with cols[i]:
        st.markdown(f"""
        <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32;">
            <p style="color: #ffffff; font-weight: bold; margin-bottom: 0;">{code}</p>
            <p style="color: #888888; font-size: 0.8em;">{data['name']}</p>
            <p style="color: #888888; font-size: 0.7em; margin-bottom: 5px;">GÜNLÜK BEKLENTİ</p>
            <h2 style="color: #00ff00; margin-top: 0;">%{data['val']:+.2f}</h2>
        </div>
        """, unsafe_allow_status=True)
