import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="Fon Takip", layout="wide", initial_sidebar_state="collapsed")

# Veri çekme fonksiyonu
def get_live_data():
    try:
        # BIST100 ve USD/TRY verileri
        bist = yf.Ticker("XU100.IS").history(period="2d")
        usd = yf.Ticker("USDTRY=X").history(period="2d")
        
        # Değişim hesaplama (Son kapanış / Bir önceki kapanış)
        bist_change = ((bist['Close'].iloc[-1] / bist['Close'].iloc[-2]) - 1) * 100
        usd_change = ((usd['Close'].iloc[-1] / usd['Close'].iloc[-2]) - 1) * 100
        return bist_change, usd_change
    except:
        return 0.0, 0.0

# Fon Listesi ve Katsayılar (Tahmini ağırlıklar)
def get_fund_estimates(bist_pc, usd_pc):
    # Bu katsayılar fonların BIST100'e duyarlılığını temsil eder
    funds = {
        "TLY": {"name": "Tera Portföy Birinci Serbest", "beta": 0.90},
        "DFI": {"name": "Atlas Portföy Serbest Fon", "beta": 0.75},
        "PHE": {"name": "Pusula Portföy Hisse Fon", "beta": 1.05},
        "PBR": {"name": "Pusula Portföy Birinci Değişken", "beta": 0.65},
        "KHA": {"name": "İstanbul Portföy Birinci Değişken", "beta": 0.80}
    }
    
    results = {}
    for code, info in funds.items():
        # Beklenti = BIST Değişimi * Beta (Hisse yoğunluğu)
        prediction = bist_pc * info['beta']
        results[code] = {"name": info['name'], "val": prediction}
    return results

# Uygulama Başlığı ve Veriler
bist_pc, usd_pc = get_live_data()

st.markdown(f"### BIST100: %{bist_pc:+.2f} | USDTRY: %{usd_pc:+.2f}")
st.write("---")

# Kartları Oluşturma
fund_results = get_fund_estimates(bist_pc, usd_pc)
cols = st.columns(len(fund_results))

for i, (code, data) in enumerate(fund_results.items()):
    with cols[i]:
        # Renk belirleme (Pozitifse yeşil, negatifse kırmızı)
        color = "#00ff00" if data['val'] >= 0 else "#ff4b4b"
        
        st.markdown(f"""
        <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid {color}; min-height: 180px;">
            <p style="color: #ffffff; font-weight: bold; margin-bottom: 0; font-size: 1.2em;">{code}</p>
            <p style="color: #888888; font-size: 0.8em; height: 40px;">{data['name']}</p>
            <p style="color: #888888; font-size: 0.7em; margin-bottom: 5px; font-weight: bold;">GÜNLÜK BEKLENTİ</p>
            <h2 style="color: {color}; margin-top: 0;">%{data['val']:+.2f}</h2>
        </div>
        """, unsafe_allow_html=True) # Hatalı yer burasıydı, düzeltildi.
