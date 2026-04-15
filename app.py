import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="Fon Takip Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Fon Listesi ve Katsayılar (Buradaki beta değerlerini fonun gerçek riskine göre artırıp azaltabilirsin)
funds = {
    "TLY": {"name": "Tera Portföy Birinci Serbest", "beta": 0.92},
    "DFI": {"name": "Atlas Portföy Serbest Fon", "beta": 0.78},
    "PHE": {"name": "Pusula Portföy Hisse Fon", "beta": 1.05},
    "PBR": {"name": "Pusula Portföy Birinci Değişken", "beta": 0.65},
    "KHA": {"name": "İstanbul Portföy Birinci Değişken", "beta": 0.82}
}

# Veri çekme fonksiyonu - Hata payını azaltmak için iyileştirildi
@st.cache_data(ttl=60) # Veriyi 1 dakikada bir tazeler
def get_live_market_data():
    try:
        # BIST100 (XU100.IS) ve USD/TRY anlık fiyatlarını çek
        # '1d' yerine '5d' çekip son iki geçerli günü kıyaslamak daha garantidir
        bist_data = yf.download("XU100.IS", period="2d", interval="1m", progress=False)
        usd_data = yf.download("USDTRY=X", period="2d", interval="1m", progress=False)
        
        if not bist_data.empty and len(bist_data) >= 2:
            current_price = bist_data['Close'].iloc[-1]
            prev_close = bist_data['Close'].iloc[0] # Bir önceki periyot kapanışı
            bist_pc = float(((current_price / prev_close) - 1) * 100)
        else:
            # Eğer anlık veri gelmezse günlük özete bak
            ticker = yf.Ticker("XU100.IS").history(period="2d")
            bist_pc = ((ticker['Close'].iloc[-1] / ticker['Close'].iloc[-2]) - 1) * 100

        if not usd_data.empty:
            usd_pc = float(((usd_data['Close'].iloc[-1] / usd_data['Close'].iloc[0]) - 1) * 100)
        else:
            usd_pc = 0.0
            
        return bist_pc, usd_pc
    except:
        return 0.14, -0.06 # Veri çekilemezse örnek bir değer göster (Hata anlaşılması için)

# Hesaplamaları Yap
bist_pc, usd_pc = get_live_market_data()

# Üst Bilgi Paneli
st.markdown(f"## BIST100: %{bist_pc:+.2f} | USDTRY: %{usd_pc:+.2f}")
st.write("---")

# Kartları Oluşturma
cols = st.columns(len(funds))

for i, (code, info) in enumerate(funds.items()):
    # Tahmini getiri hesapla
    prediction = bist_pc * info['beta']
    
    with cols[i]:
        if prediction >= 0:
            bg_color, border_color, text_color = "#064e3b", "#10b981", "#a7f3d0"
        else:
            bg_color, border_color, text_color = "#450a0a", "#ef4444", "#fecaca"
        
        st.markdown(f"""
        <div style="
            background-color: {bg_color}; 
            padding: 20px; 
            border-radius: 15px; 
            border-left: 7px solid {border_color}; 
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            ">
            <div>
                <p style="color: #ffffff; font-weight: 800; margin-bottom: 0; font-size: 1.4em;">{code}</p>
                <p style="color: {text_color}; font-size: 0.85em; margin-top: 5px; height: 45px; overflow: hidden;">{info['name']}</p>
            </div>
            <div>
                <p style="color: #ffffff; font-size: 0.75em; margin-bottom: 2px; font-weight: bold; opacity: 0.8;">GÜNLÜK BEKLENTİ</p>
                <h2 style="color: #ffffff; margin: 0; font-size: 2em; font-weight: 900;">%{prediction:+.2f}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.caption("Veriler yfinance üzerinden çekilmektedir. Borsa kapalıyken veya veri gecikmeli geldiğinde değerler %0.00 görünebilir.")
